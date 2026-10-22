#!/usr/bin/env python3
"""Radar: recolha pública, sem credenciais, sem dependências extra."""
import concurrent.futures,datetime as dt,email.utils,hashlib,html,json,re,sys,time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin,urlsplit
from urllib.request import Request,urlopen
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
NOW=lambda:dt.datetime.now(dt.timezone.utc)
STAMP=lambda t=None:(t or NOW()).astimezone(dt.timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
def local(tag):return tag.rsplit('}',1)[-1].lower()
def text(node,*fields):
    for child in node:
        if local(child.tag) in fields:return ''.join(child.itertext()).strip()
    return ''
def tidy(s,n=260):
    s=re.sub(r'<(script|style)\b.*?</\1\s*>',' ',s or '',flags=re.S|re.I)
    return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]*>',' ',s))).strip()[:n]
def valid_url(raw):
    try:
        p=urlsplit(raw)
        if p.scheme not in ('http','https') or not p.hostname or p.username or p.password:return ''
        if p.hostname in ('localhost','127.0.0.1','::1'):return ''
        return raw.split('#')[0]
    except (TypeError,ValueError):return ''
def request(url):
    if not valid_url(url):raise ValueError('URL inválido')
    req=Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; RadarNoticias/1.0)','Accept':'application/rss+xml,application/atom+xml,application/xml,text/xml,text/html;q=0.9,*/*;q=0.1'})
    with urlopen(req,timeout=12) as response:
        b=response.read(2600001)
        if len(b)>2600000:raise ValueError('Conteúdo demasiado grande')
        return b.decode(response.headers.get_content_charset() or 'utf-8','replace')
def datetime_original(value):
    if not value:return None
    try:t=dt.datetime.fromisoformat(value.strip().replace('Z','+00:00'))
    except ValueError:
        try:t=email.utils.parsedate_to_datetime(value.strip())
        except (TypeError,ValueError,IndexError):return None
    if not t or not t.tzinfo or t.year<1990 or t>NOW()+dt.timedelta(days=1):return None
    return STAMP(t)
def record(s,title,link,when,summary='',precision='minute',localdate=None):
    url=valid_url(link)
    if not title or not url:return None
    uid=hashlib.sha256((s['id']+'|'+url).encode()).hexdigest()[:24]
    return {'id':uid,'sourceId':s['id'],'title':tidy(title,210),'url':url,'publishedAt':when,'datePrecision':precision if when or precision=='day' else 'unknown','localDate':localdate,'summary':tidy(summary,260),'firstSeenAt':STAMP()}
class Feeds(HTMLParser):
    def __init__(self,site):super().__init__();self.site=site;self.candidates=[]
    def handle_starttag(self,tag,attrs):
        if tag!='link':return
        a=dict(attrs);typ=a.get('type','').lower()
        if ('rss' in typ or 'atom' in typ) and a.get('href'):
            url=valid_url(urljoin(self.site,a['href']))
            if url:
                h=urlsplit(url).hostname or '';original=urlsplit(self.site).hostname or ''
                if h.removeprefix('www.')==original.removeprefix('www.'):self.candidates.append(url)
def parse_feed(s,raw):
    root=ET.fromstring(raw)
    kind=local(root.tag)
    if kind not in ('rss','feed','rdf'):raise ValueError('Resposta sem formato RSS/Atom')
    channel=next((c for c in root if local(c.tag)=='channel'),root)
    parent=root if kind in ('feed','rdf') else channel
    result=[]
    for node in list(parent):
        if local(node.tag) not in ('entry','item'):continue
        title=tidy(text(node,'title'),210)
        link=text(node,'link')
        for c in node:
            if local(c.tag)=='link' and c.attrib.get('href') and c.attrib.get('rel','alternate')=='alternate':
                link=c.attrib['href'];break
        if not link:link=text(node,'guid','id')
        link=valid_url(urljoin(s['website'],link))
        pub=datetime_original(text(node,'pubdate','published','issued','date'))
        description=text(node,'description','summary','encoded','content')
        a=record(s,title,link,pub,description)
        if a:result.append(a)
        if len(result)>=130:break
    if not result:raise ValueError('Feed sem artigos legíveis')
    return result
class Correio(HTMLParser):
    def __init__(self):super().__init__();self.items=[];self.entry=None;self.depth=0
    def handle_starttag(self,tag,attrs):
        if self.entry is not None:
            if tag not in ('img','br','meta','input','hr','source','link'):self.depth+=1
            return
        if tag!='a':return
        attrs=dict(attrs);url=urljoin('https://correiodeazemeis.sapo.pt/ultimas-noticias',attrs.get('href',''))
        if urlsplit(url).hostname=='correiodeazemeis.sapo.pt' and urlsplit(url).path.startswith('/noticias/'):
            self.entry=[valid_url(url),[],attrs.get('title','')];self.depth=0
    def handle_data(self,data):
        if self.entry:self.entry[1].append(data)
    def handle_endtag(self,tag):
        if self.entry is None:return
        if self.depth>0:self.depth-=1
        elif tag=='a':self.items.append(self.entry);self.entry=None
def correio(s):
    parser=Correio();parser.feed(request('https://correiodeazemeis.sapo.pt/ultimas-noticias'))
    result=[];seen=set()
    for url,parts,alt in parser.items:
        if url in seen:continue
        body=tidy(' '.join(parts),550)
        date=re.search(r'\b([0-3]?\d/[01]?\d/\d{4})\b',body)
        if not date:continue
        try:d=dt.datetime.strptime(date.group(1),'%d/%m/%Y').date()
        except ValueError:continue
        if d>NOW().date():continue
        title=tidy(alt or body.replace(date.group(1),''),210)
        if len(title)<10:continue
        a=record(s,title,url,None,precision='day',localdate=d.isoformat())
        if a:result.append(a);seen.add(url)
    if not result:raise ValueError('Listagem sem artigos datados reconhecíveis')
    return result[:100]

# Integrações específicas: usar exclusivamente páginas públicas e metadados da origem.
class ArticleLinks(HTMLParser):
    def __init__(self,base):
        super().__init__();self.base=base;self.links=[];self.entry=None;self.depth=0
    def handle_starttag(self,tag,attrs):
        if self.entry is not None:
            if tag not in ('img','br','meta','hr','source','input','link','wbr'):self.depth+=1
            return
        if tag=='a':
            a=dict(attrs);url=valid_url(urljoin(self.base,a.get('href','')))
            if url:self.entry=[url,[],a.get('title','')];self.depth=0
    def handle_data(self,data):
        if self.entry is not None:self.entry[1].append(data)
    def handle_endtag(self,tag):
        if self.entry is None:return
        if self.depth>0:self.depth-=1
        elif tag=='a':
            url,parts,title=self.entry
            self.links.append((url,tidy(' '.join(parts),400),tidy(title,210)))
            self.entry=None
def iso_day(s):
    try:
        x=dt.date.fromisoformat(s)
        if x>NOW().date()+dt.timedelta(days=1) or x.year<2000:return None
        return x.isoformat()
    except (ValueError,TypeError):return None
def metadata_from_article(url):
    raw=request(url)
    for key in ('article:published_time','datePublished','dateCreated','publish_date','pubdate'):
        patterns=[
          r'<meta[^>]+(?:property|name)=["\x27]'+re.escape(key)+r'["\x27][^>]+content=["\x27]([^"\x27]+)',
          r'<meta[^>]+content=["\x27]([^"\x27]+)["\x27][^>]+(?:property|name)=["\x27]'+re.escape(key)+r'["\x27]',
          r'["\x27]'+re.escape(key)+r'["\x27]\s*:\s*["\x27]([^"\x27]+)'
        ]
        for pat in patterns:
            m=re.search(pat,raw,re.I)
            if m:
                value=html.unescape(m.group(1))
                timestamp=datetime_original(value)
                if timestamp:return timestamp,None
                day=iso_day(value[:10])
                if day:return None,day
    return None,None
def listing(s,page,allowed,max_entries=14,default_day=None):
    raw=request(page);p=ArticleLinks(page);p.feed(raw);unique={}
    for url,body,alt in p.links:
        u=urlsplit(url);host=(u.hostname or '').removeprefix('www.')
        if host!=urlsplit(s['website']).hostname.removeprefix('www.'):continue
        if not allowed(u.path):continue
        clean=url.split('?')[0].rstrip('/')
        title=alt if len(alt)>12 else body
        if s['id']=='afatv':
            title=re.sub(r'^.*?\b[0-3]?\d/[01]?\d/\d{4}\b\s*','',body)
        title=re.sub(r'\s+',' ',title).strip()[:205]
        if len(title)<22:continue
        if clean not in unique:unique[clean]=(title,body)
    result=[]
    for url,(title,body) in list(unique.items())[:max_entries]:
        date=None;when=None
        if s['id']=='fcporto':
            m=re.search(r'/noticias/(\d{4})(\d{2})(\d{2})-',url)
            if m:date=iso_day('-'.join(m.groups()))
        if s['id']=='afatv':
            m=re.search(r'\b([0-3]?\d)/([01]?\d)/(\d{4})\b',body)
            if m:date=iso_day(f'{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}')
        try:
            exact,article_day=metadata_from_article(url)
            if exact:when=exact
            elif article_day:date=article_day
        except Exception:pass
        if not date and default_day:date=default_day
        if when:
            a=record(s,title,url,when)
        else:
            a=record(s,title,url,None,precision='day' if date else 'unknown',localdate=date)
        if a:result.append(a)
    if not result:raise ValueError('Listagem sem artigos reconhecidos')
    return result
def expresso_blitz(s):
    # O acesso às páginas é recusado (HTTP 403); sitemap apenas se contiver títulos e datas originais.
    raw=request('https://expresso.pt/sitemap/news.xml')
    root=ET.fromstring(raw);rows=[]
    for item in root.iter():
        if local(item.tag)!='url':continue
        loc=text(item,'loc')
        if '/blitz/' not in loc and '/blitz-' not in loc:continue
        news=next((c for c in item if local(c.tag)=='news'),None)
        if news is None:continue
        pub=text(news,'publication_date')
        title=tidy(text(news,'title'),210)
        date=datetime_original(pub)
        if title and date:
            a=record(s,title,loc,date)
            if a:rows.append(a)
    if not rows:raise ValueError('Sitemap disponível, mas sem notícias BLITZ com data de publicação')
    return rows[:70]
def html_integration(s):
    sid=s['id']
    if sid=='bolamarela':
        return listing(s,'https://bolamarela.pt/noticias/',lambda p:bool(re.fullmatch(r'/[^/]+/?',p)) and p.rstrip('/') not in ('/noticias','/contactos','/sobre','/author'),15)
    if sid=='record':
        return listing(s,'https://www.record.pt/ultimas-noticias',lambda p:'/detalhe/' in p,16)
    if sid=='fcporto':
        return listing(s,'https://www.fcporto.pt/pt/noticias',lambda p:bool(re.match(r'^/pt/noticias/\d{8}-',p)),12)
    if sid=='afatv':
        return listing(s,'https://afatv.pt/news',lambda p:p.startswith('/news-details/'),18)
    if sid=='futsalportugal':
        return listing(s,'https://futsalportugal.com/pt/noticias',lambda p:bool(re.match(r'^/(?:pt/)?news/\d+/',p)),18)
    if sid=='blitz':return expresso_blitz(s)
    raise ValueError('Integração não implementada')

def collect(s):
    status={k:s[k] for k in ('id','name','website','category')}
    status.update(status='pending',checkedAt=STAMP(),items=0,reason='',feedUrl=None)
    if s.get('mode')=='listing-html':
        try:
            entries=html_integration(s);status.update(status='ok',items=len(entries));return status,entries
        except Exception as exc:status.update(status='erro',reason=str(exc)[:150]);return status,[]
    if s.get('mode')=='correio-html':
        try:
            entries=correio(s);status.update(status='ok',items=len(entries));return status,entries
        except Exception as exc:status.update(status='erro',reason=str(exc)[:150]);return status,[]
    candidates=[s['feedUrl']] if s.get('feedUrl') else []
    try:
        parser=Feeds(s['website']);parser.feed(request(s['website']))
        candidates.extend(parser.candidates[:3])
    except Exception:pass
    if not candidates:status.update(status='sem_rss',reason='Não foi detetado feed RSS/Atom público.');return status,[]
    errors=[]
    for url in dict.fromkeys(candidates):
        try:
            articles=parse_feed(s,request(url))
            status.update(status='ok',items=len(articles),feedUrl=url)
            return status,articles
        except Exception as exc:errors.append((str(exc) or type(exc).__name__)[:75])
    status.update(status='erro',reason=' | '.join(errors)[:150])
    return status,[]
def main():
    sources=json.loads((ROOT/'sources.json').read_text('utf-8'))
    dst=ROOT/'news.json'
    try:previous=json.loads(dst.read_text('utf-8'))
    except (OSError,ValueError):previous={}
    articles={a['id']:a for a in previous.get('articles',[]) if isinstance(a,dict) and a.get('id')}
    statuses={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        futures={pool.submit(collect,s):s for s in sources}
        for future in concurrent.futures.as_completed(futures):
            s=futures[future]
            try:status,new=future.result()
            except Exception as exc:
                status={k:s[k] for k in ('id','name','website','category')}
                status.update(status='erro',reason=str(exc)[:150],checkedAt=STAMP(),items=0)
                new=[]
            statuses[s['id']]=status
            for item in new:
                if item['id'] in articles:item['firstSeenAt']=articles[item['id']].get('firstSeenAt',item['firstSeenAt'])
                articles[item['id']]=item
            print(s['name'],status['status'],len(new),status.get('reason',''),file=sys.stderr)
    cutoff=NOW()-dt.timedelta(days=60)
    active={s['id'] for s in sources}
    filtered=[]
    for a in articles.values():
        if a.get('sourceId') not in active:continue
        try:
            ts=dt.datetime.fromisoformat((a.get('publishedAt') or a['firstSeenAt']).replace('Z','+00:00'))
            if ts<cutoff:continue
        except (ValueError,TypeError,KeyError):continue
        filtered.append(a)
    final=[]
    for source in active:
        rows=[a for a in filtered if a['sourceId']==source]
        rows.sort(key=lambda a:a.get('publishedAt') or a.get('firstSeenAt') or '',reverse=True)
        final.extend(rows[:100])
    final.sort(key=lambda a:a.get('publishedAt') or a.get('firstSeenAt') or '',reverse=True)
    data={'schemaVersion':1,'updatedAt':STAMP(),'sourceCount':len(sources),'sources':[statuses[s['id']] for s in sources],'articles':final}
    dst.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(f"Radar: {len(final)} artigos, {sum(1 for s in data['sources'] if s['status']=='ok')} fontes operacionais")
if __name__=='__main__':main()
