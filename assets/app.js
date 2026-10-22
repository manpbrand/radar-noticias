(() => {
'use strict';
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const STORE='radar-v1';
const defaults={view:'all',selectedSource:'all',category:'all',query:'',sort:'newest',compact:false,saved:[],theme:'light'};
let pref={...defaults},data={articles:[],sources:[],sourceCount:21,updatedAt:null},loading=false;
try{pref={...pref,...JSON.parse(localStorage.getItem(STORE)||'{}')}}catch{}
if(!Array.isArray(pref.saved))pref.saved=[];
if(pref.view==='unread')pref.view='all';
const save=()=>{try{localStorage.setItem(STORE,JSON.stringify(pref))}catch{}};
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c]));
const lookup=id=>data.sources.find(s=>s.id===id)||{name:id,category:''};
const format=new Intl.DateTimeFormat('pt-PT',{day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit',timeZone:'Europe/Lisbon',hour12:false});
const valid=v=>{const d=new Date(v||'');return Number.isNaN(d.getTime())?null:d};
const aurl=v=>{try{const u=new URL(v);return ['http:','https:'].includes(u.protocol)?u.href:'#'}catch{return '#'}};
function article(a){
 const src=lookup(a.sourceId),saved=pref.saved.includes(a.id);
 const exact=a.datePrecision==='minute'&&valid(a.publishedAt);
 const date=exact?format.format(valid(a.publishedAt)):a.datePrecision==='day'&&a.localDate?a.localDate.split('-').reverse().join('/')+' · hora não indicada':'Data/hora não indicada';
 const abbr=src.name.replace(/[^\p{L}\p{N} ]/gu,'').split(' ').filter(Boolean).slice(0,2).map(x=>x[0]).join('').toUpperCase();
 const url=esc(aurl(a.url)),image=a.imageUrl?aurl(a.imageUrl):'#';
 const cover='<a class="article-image" target="_blank" rel="noopener noreferrer" href="'+url+'" aria-label="Abrir notícia original: '+esc(a.title)+'"><span class="source-avatar">'+esc(abbr)+'</span>'+(image!=='#'?'<img src="'+esc(image)+'" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer" width="116" height="82">':'')+'</a>';
 return '<article class="article" data-id="'+esc(a.id)+'">'+cover+'<div class="article-content"><div class="article-meta"><span class="publisher">'+esc(src.name)+'</span><span>·</span><time>'+esc(date)+'</time><span>·</span><span>'+esc(src.category)+'</span></div><h3><a target="_blank" rel="noopener noreferrer" href="'+url+'">'+esc(a.title)+'</a></h3>'+(a.summary?'<p>'+esc(a.summary)+'</p>':'')+'</div><div class="article-controls"><button class="save-btn '+(saved?'saved':'')+'" data-save="'+esc(a.id)+'" aria-label="'+(saved?'Remover dos guardados':'Guardar notícia')+'">'+(saved?'★':'☆')+'</button></div></article>';
}
function render(){
 document.documentElement.classList.toggle('theme-dark',pref.theme==='dark');
 const cats=[...new Set(data.sources.map(s=>s.category).filter(Boolean))];
 $('#stat-articles').textContent=data.articles.length.toLocaleString('pt-PT');
 $('#stat-sources').textContent=$('#sources-number').textContent=data.sources.length;
 $('#hero-sources').textContent=$('#about-sources').textContent=data.sources.length;
 $('#stat-active').textContent=data.sources.filter(s=>s.status==='ok').length;
 $('#category').innerHTML='<option value="all">Todas as categorias</option>'+cats.map(c=>'<option value="'+esc(c)+'">'+esc(c)+'</option>').join('');
 $('#category').value=cats.includes(pref.category)?pref.category:'all';
 $('#filter-row').innerHTML='<button class="chip '+(pref.category==='all'?'active':'')+'" data-cat="all">Todas</button>'+cats.map(c=>'<button class="chip '+(pref.category===c?'active':'')+'" data-cat="'+esc(c)+'">'+esc(c)+'</button>').join('');
 const sourceHtml=s=>'<button class="source '+(pref.selectedSource===s.id?'selected':'')+'" data-source="'+esc(s.id)+'" title="'+esc(s.name+': '+(s.reason||s.status||'Por verificar'))+'"><span class="source-abbr">'+esc(s.name.slice(0,2).toUpperCase())+'</span><span class="source-name">'+esc(s.name)+'</span><span class="source-status '+esc(s.status||'pending')+'"></span></button>';
 $('#source-list').innerHTML=sourceHtml({id:'all',name:'Todas as fontes',status:'ok'})+data.sources.map(sourceHtml).join('');
 let list=data.articles.filter(a=>a&&a.id&&a.url&&a.title);
 if(pref.selectedSource!=='all')list=list.filter(a=>a.sourceId===pref.selectedSource);
 if(pref.category!=='all')list=list.filter(a=>lookup(a.sourceId).category===pref.category);
 if(pref.view==='saved')list=list.filter(a=>pref.saved.includes(a.id));
 if(pref.query){const needle=pref.query.toLocaleLowerCase('pt-PT');list=list.filter(a=>[a.title,a.summary,lookup(a.sourceId).name].join(' ').toLocaleLowerCase('pt-PT').includes(needle))}
 const exact=list.filter(a=>a.datePrecision==='minute'&&valid(a.publishedAt));
 const other=list.filter(a=>a.datePrecision!=='minute'||!valid(a.publishedAt));
 const direction=pref.sort==='newest'?-1:1;
 exact.sort((a,b)=>direction*(new Date(a.publishedAt)-new Date(b.publishedAt)));
 other.sort((a,b)=>direction*(a.localDate||a.firstSeenAt||'').localeCompare(b.localDate||b.firstSeenAt||''));
 $('#article-list').innerHTML=exact.length?exact.map(article).join(''):'<div class="empty"><div class="empty-orbit">⌁</div><h3>'+(!data.articles.length?'A aguardar notícias reais':'Sem notícias com estes filtros')+'</h3><p>'+(!data.articles.length?'A recolha automática ainda não produziu artigos. Consulta o estado das fontes.':'Experimenta alterar a categoria, a pesquisa ou a publicação.')+'</p></div>';
 $('#undated-wrap').hidden=!other.length;$('#undated-count').textContent='('+other.length+')';$('#undated-list').innerHTML=other.map(article).join('');
 $('#section-title').firstChild.textContent=pref.view==='saved'?'Guardadas ':pref.selectedSource!=='all'?lookup(pref.selectedSource).name+' ':'Últimas notícias ';
 $('#result-count').textContent=list.length+' artigos';$('#nav-all').textContent=data.articles.length;
 $('#nav-saved').textContent=data.articles.filter(a=>pref.saved.includes(a.id)).length;
 $$('[data-view]').forEach(el=>el.classList.toggle('active',el.dataset.view===pref.view));
 $$('[data-mobile-view]').forEach(el=>el.classList.toggle('active',el.dataset.mobileView===pref.view));
 $('#compact').classList.toggle('active',pref.compact);
 $$('#article-list,#undated-list').forEach(el=>el.classList.toggle('compact-mode',pref.compact));
 $('#sort').value=pref.sort;$('#search').value=pref.query;
 const date=valid(data.updatedAt),stale=!date||Date.now()-date.getTime()>120*60000;
 $('#freshness').textContent=(date?'Última recolha: '+format.format(date):'Ainda não foi executada a recolha inicial')+' · Datas e horas provenientes dos sites originais; artigos sem hora estão separados.';
 $('#health-pill').classList.toggle('offline',stale);
 $('#health-pill').innerHTML='<span class="status-led"></span>'+(stale?'A aguardar atualização':'Dados atualizados');
 save();
}
async function refresh(){
 if(loading)return;loading=true;$('#refresh-btn').disabled=true;$('#refresh-btn span').textContent='A atualizar…';
 try{
  const response=await fetch('./news.json?_= '+Date.now(),{cache:'no-store'});
  if(!response.ok)throw Error('HTTP '+response.status);
  const payload=await response.json();
  if(!Array.isArray(payload.articles)||!Array.isArray(payload.sources))throw Error('Dados inválidos');
  data=payload;render();
 }catch(err){$('#freshness').textContent='Falha ao obter as notícias: '+err.message}
 finally{loading=false;$('#refresh-btn').disabled=false;$('#refresh-btn span').textContent='Atualizar'}
}
function setView(v){pref.view=v==='saved'?'saved':'all';save();render()}
document.addEventListener('click',e=>{
 const el=e.target.closest('button,a');if(!el)return;
 if(el.dataset.view)setView(el.dataset.view);
 if(el.dataset.mobileView)setView(el.dataset.mobileView);
 if(el.dataset.source){pref.selectedSource=el.dataset.source;$('.sidebar').classList.remove('open');render()}
 if(el.dataset.cat){pref.category=el.dataset.cat;render()}
 if(el.dataset.save){pref.saved=pref.saved.includes(el.dataset.save)?pref.saved.filter(x=>x!==el.dataset.save):[...pref.saved,el.dataset.save];render()}
});
document.addEventListener('error',e=>{if(e.target instanceof HTMLImageElement&&e.target.closest('.article-image'))e.target.remove()},true);
$('#search').addEventListener('input',e=>{pref.query=e.target.value;render()});
$('#category').addEventListener('change',e=>{pref.category=e.target.value;render()});
$('#sort').addEventListener('change',e=>{pref.sort=e.target.value;render()});
$('#compact').addEventListener('click',()=>{pref.compact=!pref.compact;render()});
$('#refresh-btn').addEventListener('click',refresh);
$('#theme-toggle').addEventListener('click',()=>{pref.theme=pref.theme==='light'?'dark':'light';render()});
$('#about-toggle').addEventListener('click',()=>$('#about-dialog').showModal());
$('#close-about').addEventListener('click',()=>$('#about-dialog').close());
$('#dialog-ok').addEventListener('click',()=>$('#about-dialog').close());
$('#mobile-sources').addEventListener('click',()=>$('.sidebar').classList.toggle('open'));
if('serviceWorker' in navigator)navigator.serviceWorker.register('./sw.js').catch(()=>{});
refresh();setInterval(refresh,120000);
})();
