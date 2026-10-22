# RADAR — NOTÍCIAS

Agregador pessoal de notícias, preparado especificamente para 21 fontes escolhidas. Interface responsiva, PWA para iPhone, links para artigos originais e ordenação por **data/hora de publicação da fonte**. Sem instalações no computador.

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
- Feed por ordem decrescente de data/hora original, pesquisa, categorias, filtragem por 21 fontes, leitura/guardados, modo compacto, tema escuro.
- Estado de cada fonte, contagem de notícias e data de atualização.
- Persistência de notícias no repositório, com deduplicação e retenção de 60 dias, até 100 notícias por fonte.
- Guardados e lidos são locais ao navegador, não sincronizados entre dispositivos.
- Os feeds são públicos; não há passwords, contas externas, paywalls contornados nem scraping agressivo.

## Personalizar

Edita `sources.json` para gerir fontes. Cada registo deve ter `id`, `name`, `website`, `category` e opcionalmente `feedUrl`. A recolha procura RSS/Atom declarado nos sites sem `feedUrl`. Não é garantido RSS para todas as fontes. O CSS encontra-se em `assets/styles.css`, a interface em `index.html` e a lógica em `assets/app.js`.

## Testar

No GitHub, executa o workflow manualmente. O script pode ser testado com `python scripts/collect.py --test` (Python necessário **apenas para desenvolvimento**, não para consultar o Radar). O browser não necessita de extensões ou Python. Para abrir o HTML diretamente sem servidor, a política de segurança do browser pode impedir carregar `news.json`; a utilização prevista é através de GitHub Pages.

## Nota sobre a precisão

Nem todos os RSS disponibilizam timestamp com fuso horário. Alguns sites podem editar a data, usar `updated` em vez de `published`, ou publicar conteúdos com atraso. A aplicação não pode garantir que todos os artigos dos 21 websites surgem, nem assegurar hora original quando o site não a publica. A fonte deve ser sempre consultada no link original para confirmar.