# Grafo estrutural do backend

**Natureza:** referência operacional de desenvolvimento.
**Data:** 08/11/2026.

O Graphify está instalado como ferramenta isolada do usuário. Foi reaproveitada
a versão 0.9.71, adicionando o parser SQL 0.3.11; a ferramenta não faz parte das dependências da aplicação.
O projeto Python foi posteriormente movido para `backend/`. A skill de classificação continua
local ao repositório e aplica-se apenas a implementações delegadas no backend.

## Artefatos locais

- [graph.html](backend/graph.html): visualização interativa para abrir no navegador.
- [graph.json](backend/graph.json): grafo consultável.
- [GRAPH_REPORT.md](backend/GRAPH_REPORT.md): relatório gerado pelo Graphify.
- [provenance.json](backend/provenance.json): revisão Git, estado dos arquivos,
  hashes SHA-256 e resumo da geração.

`backend/` neste diretório contém artefatos gerados e está ignorado pelo Git.
O código da aplicação está em `backend/` na raiz do monorepo, separado destes artefatos.
Em outro checkout, gere os artefatos com os comandos abaixo; os links só passam
a existir depois da geração.

## Escopo e resultado verificado

Analisados 36 arquivos em `backend/`: `main.py`, Python sob `src/` e `tests/`, mais o schema SQL.
Os caminhos internos do grafo são relativos a `backend/`, não à raiz do monorepo.
Inclui rascunhos Python e experimentos como `src/main.py`; sua presença no grafo
não significa que sejam código ativo ou aprovado. Nenhum módulo foi importado
ou executado durante a análise.

Excluídos frontend, documentação, prompts/base de conhecimento, JSONs de rascunho,
configurações, dependências e segredos. Não houve acesso ao PostgreSQL ou chamada
a modelo. A cobertura é de código e schema em arquivo, não de todo o backend
operacional nem de contratos frontend por HTTP.

A extração bruta produziu 232 nós e 665 relações. Após a etapa de construção e
agrupamento do Graphify: **268 nós, 633 relações e 13 comunidades**. Essa etapa
adiciona nós de arquivos e consolida relações. O JSON final tem `directed: false`;
não interpretar caminhos como sequência dirigida de execução. Relações inferidas
continuam exigindo confirmação no código. O diagnóstico final não encontrou
arestas com endpoints ausentes ou pendentes; isso não prova completude da extração.

`graphify explain ChatService` foi conferido contra `main.py` e
`src/services/chat_service.py`: rota, repositórios, agente e DTOs estão representados.
Não houve QA visual no navegador nem validação comportamental da aplicação.

## Reprodução

Instalação isolada, caso ainda não exista (pode requerer rede):

```sh
uv tool install --with tree-sitter-sql 'graphifyy==0.9.71'
```

Na raiz do projeto:

```sh
GRAPHIFY_OUT="$PWD/dev/graphs/backend" graphify extract backend \
  --code-only --no-cluster --no-dedup --max-workers 1 \
  --exclude .langgraph_api --exclude src/agents/base_knowledge \
  --exclude src/agents/prompts --exclude src/infra/db/relational/draft \
  --exclude '*.json' --exclude '*.toml' --exclude '*.yaml' \
  --exclude '*.yml' --exclude '*.lock'

GRAPHIFY_OUT="$PWD/dev/graphs/backend" graphify cluster-only backend \
  --graph dev/graphs/backend/graph.json --no-label
```

`--code-only` e `--no-label` evitam extração semântica e nomeação por modelo.
O resultado usa rótulos locais de comunidades. Não execute `graphify install`
ou instale hooks para reproduzir: isso configuraria outras integrações.
Os comandos foram conferidos na versão instalada, não presumidos de outra release.

Consultas:

```sh
graphify explain ChatService --graph dev/graphs/backend/graph.json
graphify query 'ChatService Agent messages' --graph dev/graphs/backend/graph.json
graphify diagnose multigraph --graph dev/graphs/backend/graph.json --json
```

## Atualidade

O grafo representa os arquivos locais da geração, incluindo mudanças sem commit.
Não há atualização automática. Os hashes de `provenance.json` usam caminhos relativos à raiz do monorepo.
Compare esses hashes com os arquivos
atuais e confira arquivos novos/excluídos; o commit sozinho não basta. O Graphify
mantém adicionalmente `manifest.json` e cache próprios. Após regenerar, renove a
proveniência; não reutilize a antiga para certificar um grafo novo. O JSON não
garante fidelidade comportamental e não substitui testes ou revisão dos contratos.

Referências: [repositório oficial](https://github.com/Graphify-Labs/graphify) e
[funcionamento](https://github.com/Graphify-Labs/graphify/blob/v8/docs/how-it-works.md).
