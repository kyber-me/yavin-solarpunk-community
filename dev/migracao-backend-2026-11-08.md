# Migração do projeto Python para backend/

**Natureza:** decisão e registro operacional de desenvolvimento.

Data: 08/11/2026.
Questão: separar o backend no monorepo sem alterar os contratos e dados de Yavin.
Opções consideradas: manter Python na raiz ou dedicar `backend/` ao projeto Python.
Decisão: migração autorizada pelo Idealizador para `backend/`.
Motivo: separar código, ambiente, testes e configuração do backend do frontend e
do processo de desenvolvimento mantido na raiz.
O que continua aberto: testes legados de checkpoint, vida útil do checkpointer na
factory LangGraph, revisão adversarial e execução integrada com banco/modelo.
Próximo passo: desenvolver a partir de `backend/`, usando o ambiente local recriado
e os registros datados do harness.

## Classificação e escopo

Complexidade 3, risco 3, nível 3, apresentados antes das edições. O grafo anterior
foi conferido por hashes e a consulta de `Agent` foi comparada ao código.
A classificação foi posteriormente persistida em `dev/harness/2026-11-08/`,
explicitamente como registro retrospectivo, conforme nova diretiva do Idealizador.
O [planejamento por fases](harness/2026-11-08/005655-migracao-backend/planejamento.json)
também foi consolidado retrospectivamente: quatro fases e oito subtarefas. Não
houve ativação formal do modo Plan nesta execução.

## Movimentações

- `src/`, `tests/`, `main.py`, `pyproject.toml`, `uv.lock`, `.python-version` e
  `langgraph.json` passaram da raiz para `backend/`.
- `.env` local e `.langgraph_api/` foram movidos com seu conteúdo preservado;
  não há cópia de credenciais neste documento ou nos registros do harness.
- `backend/.venv` foi criado com `uv sync --frozen --project backend` e o
  interpretador Python 3.14.4 já disponível. Não houve atualização do lock.
  A antiga `.venv/` na raiz foi preservada como ambiente legado e não é a ativa.
- Frontend, instruções, documentação pública, backlog e `dev/` permanecem na raiz.
  O index Git anterior não foi reescrito nem foi criado commit; as movimentações
  estão no working tree. Não restaurar arquivos antigos do index sobre a migração.

## Ajustes de caminhos

`backend/main.py` carrega explicitamente `backend/.env` com base em `__file__`.
As raízes já calculadas em `Agent` e `ChatService` passam naturalmente a apontar
para `backend/`; a identidade e os documentos continuam sob seu `src/`.
Os imports `src.*` permanecem válidos com `backend/` como diretório de trabalho.

`backend/pyproject.toml` referencia `../README.md`. O `langgraph.json` aponta para
`src/agents/langsmith/agent_factory.py`; apenas o caminho foi corrigido. O problema
pré-existente de a factory retornar um checkpointer fechado permanece pendente.
O import do entrypoint experimental `src/main.py` foi alinhado a `src.agents`;
esse módulo continua com efeitos externos no corpo e não foi executado.

Referências ativas no README, AGENTS, backlog, guia do frontend e guias SQL foram
ajustadas. Registros históricos em `dev/` mantêm caminhos antigos como história;
o ponto de retomada contém aviso da migração. Configurações locais do IDE não foram
reescritas; selecione `backend/.venv/bin/python` e diretório de trabalho `backend/`
nas configurações de execução que dependam dos caminhos antigos.

## Execução atual

Na raiz, abra um terminal e execute somente quando desejar iniciar a API:

```sh
cd backend
uv sync --frozen
uv run python main.py
```

Para testes sem banco externo, a partir de `backend/`:

```sh
env -u YAVIN_TEST_DB_URI LANGSMITH_TRACING=false \
  .venv/bin/python -B -m unittest discover -s tests -v
```

O comando de descoberta ainda termina com a falha legada abaixo. A pasta `src/`
nos testes e guias SQL é relativa a `backend/`. Não reaplicar a migração inicial
no banco mantido. API e Vite não foram iniciados nesta tarefa.

## Evidências e limites

- Antes e depois: 38 itens descobertos, com 19 aprovados, 18 ignorados por exigirem
  PostgreSQL descartável e 1 erro de import do teste legado `test_chat_checkpoint`.
  A falha por `TextMessage` removido já existia antes da movimentação.
- OpenAPI comparado integralmente ao snapshot anterior: idêntico.
- Imports da API/factory, raízes, localização da configuração e sintaxe Python
  conferidos com criação de agentes e abertura de recursos externos bloqueadas.
- Cinco documentos comunitários preservados por hash; os mesmos quatro documentos
  são carregados. `projeto/` continua fora do carregador, conforme pendência anterior.
- Todos os arquivos do snapshot anterior existem na nova árvore. Só sete conteúdos
  foram ajustados: `main.py`, `pyproject.toml`, `langgraph.json`, `src/main.py`,
  comentários de caminho em `chat_service.py` e os dois guias SQL. `.env`, lock,
  identidade, documentos e estado local do LangGraph foram preservados por hash.
- Grafo regenerado no novo recorte; veja [instruções e proveniência](graphs/README.md).

Não houve chamada a modelo, acesso ao banco, alteração de schema ou teste integrado
real. A revisão desta migração foi feita pelo implementador; não representa revisão
adversarial independente, cujo fluxo ainda não está implementado.
