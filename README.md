# RADAR — NOTÍCIAS

Agregador pessoal de notícias, com fontes configuráveis. Interface responsiva, PWA para iPhone, links para artigos originais e ordenação por **data/hora de publicação da fonte**. Sem instalações no computador.

## Alojamento gratuito (GitHub Pages)

**Custo: 0 €, se utilizares um repositório público GitHub Free e estiveres dentro das condições/limites dos serviços.** O repositório e a página ficam públicos. O website é personalizado para ti, mas **não tem acesso privado protegido**. Não inclui dados pessoais sensíveis.

1. Cria uma conta gratuita em https://github.com/ se ainda não tiveres.
2. Em https://github.com/new cria um repositório **público** com o nome `radar-noticias`. Escolhe a opção de criar `README` ou inicializa o repositório com um ficheiro.
3. No repositório, usa **Add file → Upload files** e carrega todos os ficheiros e pastas deste pacote, preservando a pasta oculta `.github/workflows`. (Podes arrastar a pasta de projeto para a área de upload; confirma que `.github/workflows/radar.yml` ficou no sítio correto.) Faz *Commit changes* na ramificação `main`.
4. Em **Settings → Pages → Build and deployment → Source**, seleciona **GitHub Actions**.
5. Em **Actions**, escolhe **Radar — atualizar e publicar → Run workflow**. A tarefa recolhe os artigos e publica a página.
6. O endereço estará em **Settings → Pages** (habitualmente `https://<utilizador>.github.io/radar-noticias/`). Não inventes o endereço: consulta o que o GitHub mostrar.
7. No Chrome, abre esse endereço. No Safari do iPhone, usa **Partilhar → Adicionar ao ecrã principal**.

Se o GitHub bloquear a publicação por causa de permissões, verifica em `Settings → Actions → General` as permissões de leitura/escrita do token da tarefa, e volta a executar o workflow. O GitHub pode ajustar as políticas de publicação.

## Atualização e ordem

- Tarefa automática agendada aproximadamente de **30 em 30 minutos**; os trabalhos agendados do GitHub podem atrasar-se ou não executar sob carga.
- O navegador verifica a existência de um novo `news.json` a cada **2 minutos**, quando aberto. O feed não consulta diretamente os websites do utilizador.
- A data/hora mostrada em Portugal corresponde à informação RSS/Atom da fonte, convertida para `Europe/Lisbon`.
- **A hora de deteção NUNCA substitui a hora da publicação.** Artigos sem hora oficial aparecem em secção separada e não são ordenados falsamente como se a tivessem.
- No Correio de Azeméis, quando só há data, apresenta o dia e «hora não indicada»; leitura depende da estrutura HTML pública.
- Alguns sites podem bloquear acesso RSS ou não ter RSS. São classificados como `sem_rss` ou `erro`. Não inventamos artigos.
- O GitHub pode **desativar ações agendadas após 60 dias de inatividade** num repositório público; reativa a tarefa em Actions se necessário.

## Funcionalidades

- Página adaptada a Chrome Windows e Safari iPhone (PWA instalável).
- Feed por ordem decrescente de data/hora original, pesquisa, categorias, filtragem por fontes, notícias guardadas, modo compacto, tema escuro.
- Estado de cada fonte, contagem de notícias e data de atualização.
- Persistência de notícias no repositório, com deduplicação e retenção de 60 dias, até 100 notícias por fonte.
- As notícias guardadas são locais ao navegador, não sincronizadas entre dispositivos.
- Os feeds são públicos; não há passwords, contas externas, paywalls contornados nem scraping agressivo.

## O JOGO — distribuição indireta pelo Google Notícias

A fonte **O JOGO** usa o RSS de pesquisa do Google Notícias (`site:ojogo.pt when:1d`), não um RSS do jornal.
O leitor apresenta **a data/hora do Google Notícias**, devidamente identificada; **não** garante a hora original de publicação de O JOGO. Os links passam pelo Google Notícias e poderão redirecionar para o artigo do jornal.
A pesquisa não garante cobertura integral nem deteção instantânea. Não há tentativa de contornar restrições do website do jornal.
Não estão garantidas fotografias da fonte; sem imagem válida aparece a identificação da publicação.

O RSS do Google Notícias declara utilização para apresentação de resultados num leitor pessoal e não comercial. Esta integração destina-se apenas à consulta pessoal, sem revenda, distribuição comercial ou reutilização do feed noutros produtos. Caso a utilização deixe de ser pessoal, deve ser desligada ou substituída por acesso autorizado.

## Fontes e categorias — outubro de 2026

O Radar tem **38 publicações** e apresenta a navegação agrupada por categoria:
FC Porto (4), Desporto (8), Futebol (6), Ciclismo (4), Ténis (3),
Futsal (3), F1 (4), Hóquei em patins (1), Música (1), Tecnologia (1),
Atualidade (1), Atualidade local (1) e Xadrez (1).

Foram acrescentadas TNT Sports, OneFootball, BBC Sport, TopCycling, Cyclingnews,
Cycling Weekly, Velo, Raquetc, Tennis365, FutsalPlanet, F1PT, PlanetF1,
The Race, HóqueiPT, SPORT TV, DAZN Portugal e Flashscore Portugal.

**Integração das fontes:** RSS/Atom quando o editor publica feeds válidos;
extração de metadados públicos quando aplicável; pesquisa indireta
no Google Notícias como alternativa para determinadas fontes sem RSS público.
Os resultados indiretos incluem hora do Google, **não** hora oficial do editor,
e ligações através do Google Notícias. Alguns sites podem não aparecer
quando não têm notícias recentes ou não existe fonte automática fiável.
Os sites que não permitem leitura fiável ficam marcados como indisponíveis
na lista de fontes, nunca com notícias inventadas.

## Adicionar novas fontes — sem instalar programas

**Método mais fácil:** envia o endereço do site ao ChatGPT para confirmar o RSS, configurar e validar a recolha.

**Método autónomo no GitHub:**

1. Abre [sources.json](https://github.com/manpbrand/radar-noticias/edit/main/sources.json) com sessão iniciada no GitHub.
2. Acrescenta, no fim da lista, um novo objeto (separa os objetos por vírgulas, sem vírgula a seguir ao último):

```json
{
  "id": "novo-site",
  "name": "Novo Site",
  "website": "https://exemplo.pt/",
  "feedUrl": "https://exemplo.pt/feed/",
  "category": "Atualidade"
}
```

3. Substitui as informações pelas da publicação. O `id` deve ser único e estável; usa apenas letras minúsculas, algarismos e hífen. O `feedUrl` tem de ser um RSS/Atom existente e testado. Se for desconhecido, podes usar `null`; o Radar tentará descobrir um RSS/Atom declarado na página inicial.
4. Clica em **Commit changes**, guardando diretamente na ramificação `main`. O workflow [Radar — recolher e publicar](https://github.com/manpbrand/radar-noticias/actions) será executado automaticamente, sem Python no teu computador.
5. Abre o [Radar](https://manpbrand.github.io/radar-noticias/) e verifica o indicador de estado da nova fonte. O serviço de recolha também consulta as fontes aproximadamente de 30 em 30 minutos.

**Importante:** adicionar um endereço não significa que a fonte vai produzir notícias. Sem RSS/Atom público, poderá ser necessário implementar uma integração específica, respeitando o acesso e as condições do editor. Não inventes o endereço do feed. O site pode apresentar a fonte mas sinalizá-la como `sem_rss`.

Para gestão avançada, a recolha está em `scripts/collect.py`, a interface em `index.html` e `assets/app.js`, e o aspeto em `assets/styles.css`.

## Testar

No GitHub, executa o workflow manualmente. O script pode ser testado com `python scripts/collect.py --test` (Python necessário **apenas para desenvolvimento**, não para consultar o Radar). O browser não necessita de extensões ou Python. Para abrir o HTML diretamente sem servidor, a política de segurança do browser pode impedir carregar `news.json`; a utilização prevista é através de GitHub Pages.

## Nota sobre a precisão

Nem todos os RSS disponibilizam timestamp com fuso horário. Alguns sites podem editar a data, usar `updated` em vez de `published`, ou publicar conteúdos com atraso. A aplicação não pode garantir que todos os artigos dos websites configurados surgem, nem assegurar hora original quando o site não a publica. A fonte deve ser sempre consultada no link original para confirmar.