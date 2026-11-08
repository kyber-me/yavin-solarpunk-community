# Persistência de conversas e seleção de agentes

**Natureza:** plano técnico aprovado pelo Idealizador; orientação de desenvolvimento e estudo.
**Data:** 07/11/2026.
**Estado:** plano executado e posteriormente revisado sob autorizações pontuais;
chat, mensagens e histórico integrados, schema aplicado e dois turnos reais validados.
As revisões abaixo são históricas; para o estado de encerramento, usar
[o ponto de retomada](retomada-2026-11-07.md). Não representam novas autorizações.

## Estado de encerramento

O schema inicial já foi aplicado, preservando os checkpoints anteriores. A política
posterior do frontend eliminou registros locais: conversas e mensagens vêm apenas
do PostgreSQL, rascunhos só em memória e reuniões bloqueadas. Servidores encerrados
por solicitação do Idealizador. Fontes atuais: [guia da infraestrutura](../src/infra/db/relational/README.md),
[histórico exclusivamente persistido](persistencia-frontend-2026-11-07.md) e
[teste real](silas_test_responses/http-real-2026-11-07.md).

## Consolidação do schema inicial e validação HTTP

Data: 07/11/2026.
Questão: evitar uma cadeia de alterações intermediárias antes da primeira aplicação.
Opções consideradas: manter os quatro scripts ou consolidar o estado final.
Decisão: substituir os scripts anteriores por `001_initial_schema.sql`, criando
conversas e mensagens já com ULID puro e unicidade parcial da dupla ativa.
Motivo: o Idealizador confirmou que nenhuma migração foi aplicada e só há dados
do checkpointer, que a migração inicial não modifica.
O que continua aberto: aplicação ao banco do projeto e validação com modelo real.
Próximo passo: aplicar o schema inicial após aprovação. A partir da primeira
aplicação mantida, usar novas migrações incrementais para evolução.

Esta decisão substitui os caminhos de migração das revisões históricas abaixo.
O fluxo HTTP com PostgreSQL, lifecycle e checkpoints reais e grafo simulado foi
validado. Evidência e limites em [validação HTTP](validacao-http-2026-11-07.md).

## Revisão aprovada — IDs sem prefixos

Data: 07/11/2026.
Questão: simplificar os IDs das entidades persistidas.
Opções consideradas: manter prefixos por entidade ou usar somente ULID.
Decisão: IDs de conversas e mensagens usam ULID puro, sem prefixo. A migração `004`
substitui as restrições antigas e converte IDs legados e referências no mesmo commit.
Motivo: eliminar convenção redundante; a tabela e o contexto já identificam a entidade.
O que continua aberto: aplicação explícita ao banco do projeto e atualização de
referências externas antigas. Identificadores provisórios dos participantes e
checkpoints agênticos não são reescritos.
Próximo passo: revisar e aplicar as migrações pendentes no ambiente escolhido.

Esta revisão substitui o formato `Conv_<ULID>` mencionado no plano histórico abaixo.
As gerações atuais de IDs de conversas, mensagens e agentes já usam `str(ULID())`.

## Revisão aprovada — dupla ativa sem lookup persistida

Data: 07/11/2026.
Questão: simplificar a unicidade de conversas e acompanhar as rotas atuais.
Opções consideradas: lookup JSON persistida, UNIQUE simples dos participantes ou
índice único parcial sobre a dupla normalizada.
Decisão: usar `LEAST(sender_id, participant_id)` e `GREATEST(sender_id, participant_id)`
no índice `conversations_active_pair_uq`, com `WHERE active`; remover a coluna
`look_up_key` pela migração `002_active_conversation_pair.sql`, após a `001`.
Motivo: garantir uma conversa ativa por dupla sem direção, inclusive sob concorrência,
sem manter um campo derivado. Histórico inativo continua permitido.
O que continua aberto: demais pendências de integração da API, incluindo catálogo,
chat por ID persistido e tradução HTTP do conflito.
Próximo passo: aplicar explicitamente as migrações necessárias no banco escolhido
pelo Idealizador e realizar outra rodada de revisão da integração.

O repositório passa a oferecer `get_active_by_participants(sender_id, participant_id)`.
As rotas consumidas pelo frontend são `POST /conversation/create` e
`POST /conversation/talk`; os payloads acordados permanecem os mesmos.
O assistente foi autorizado a adaptar infraestrutura, registro e construção do
registro no serviço de criação para esta mudança. Não aplicar migrações ao banco
real nesta entrega. O plano original abaixo fica preservado como histórico;
esta revisão substitui suas referências à lookup e aos endereços antigos.

## Objetivo e responsabilidades

Entregar o primeiro fluxo de conversa persistida: escolher um agente, criar a conversa no PostgreSQL e utilizar seu ID para enviar mensagens.

- **Implementação do assistente:** infraestrutura PostgreSQL, testes dessa infraestrutura e frontend.
- **Implementação do Idealizador, com mentoria:** entidades, DTOs, catálogo de agentes, serviços e rotas, seguindo os contratos abaixo.
- Persistir apenas conversas neste incremento. Mensagens do domínio, encerramento e execução de reuniões ficam para depois.

## Infraestrutura proposta

**Psycopg com SQL explícito, sem ORM.** Reutilizar a dependência existente e manter visíveis consultas, transações e mapeamentos.

- Criar um `PostgresConversationRepository` em `src/infra/db/relational/`, com operações `create`, `get_by_id` e `get_active_by_lookup`.
- Usar apenas essa implementação concreta; adiar repositório genérico, classe base, implementação em memória e unidade de trabalho.
- Receber o pool por injeção. O repositório não carrega `.env`, não cria agentes e não conhece HTTP ou checkpointers.
- Retornar registros tipados com os campos persistidos. O Idealizador fará a adaptação desses registros às entidades e aos serviços.
- Usar operações síncronas, executadas fora do event loop pela integração nas rotas.
- Criar pool compartilhado por processo: mínimo zero, máximo quatro conexões, espera máxima de cinco segundos e redução de conexões ociosas após 60 segundos. Abrir e fechar o pool no ciclo de vida da API.
- Cada operação adquire e devolve sua conexão, com commit ou rollback. Nenhuma transação fica aberta durante a chamada ao modelo.
- Manter o checkpointer atual separado; não modificar suas tabelas nem seu mecanismo de conexão neste incremento.

### Dados e integridade

Criar uma primeira migração SQL versionada, aplicada explicitamente pelo Idealizador no banco de desenvolvimento, sem execução automática na inicialização.

A tabela `yavin.conversations` conterá:

- `id`: chave primária textual, com o padrão existente `Conv_<ULID>`.
- `sender_id` e `participant_id`: IDs dos dois participantes.
- `look_up_key`: representação JSON canônica da lista dos dois IDs ordenados, armazenada como texto; isso evita ambiguidades de concatenação e torna A/B equivalente a B/A.
- `thread_id`: identificador único, gerado no servidor e mantido internamente.
- `created_at`, `start_date` e `end_date`: timestamps com fuso; criação obrigatória, demais inicialmente nulos.
- `active`: obrigatório, inicialmente verdadeiro.

Adicionar restrição para participantes distintos e índice único de `look_up_key` apenas nas linhas ativas. Isso protege também contra criações concorrentes.

A criação consultará a conversa ativa para antecipar o conflito, mas também tratará a violação do índice. O repositório traduzirá esse caso em erro específico com o registro existente. Outros erros de banco não serão tratados como duplicidade.

Não criar tabelas de agentes ou chaves estrangeiras para os JSONs provisórios.

## Contratos para o Idealizador implementar no backend

Preservar o envelope `{data, error}`.

| Operação | Contrato |
|---|---|
| `GET /agents` | Retorna `data.agents`, lista de `{id, name}` dos agentes disponíveis para conversar. Inicialmente, apenas Silas. |
| `POST /create-conversation` | Recebe `{sender_id, participant_id}`. Retorna HTTP `201` com `data: {conversation_id, participant_id, created_at}`. |
| Dupla já ativa | Retorna HTTP `409`, código `CONVERSATION_ALREADY_ACTIVE` e, em `error.details`, os mesmos metadados da conversa existente. |
| `POST /chat` | Recebe `{conversation_id, sender_id, message}`. Busca a conversa persistida e resolve participante e `thread_id` no servidor. |

- A criação valida o participante contra o catálogo; participante indisponível ou inválido resulta em `422`.
- O chat não cria conversas implicitamente. Conversa inexistente resulta em `404`; inativa, em `409`; remetente fora da dupla, em `403`.
- Manter a resposta atual do chat com `data.content`.
- Não aceitar `thread_id` fornecido pelo cliente no novo contrato.
- IDs retornados pelo catálogo são opacos para o frontend. Manter `idealizador` como remetente local neste incremento.
- Tratar como pré-requisitos os problemas identificados no lookup, na inicialização do DTO Pydantic e no uso de serviço assíncrono dentro de `run_in_threadpool`.

## Frontend e compatibilidade

- Ao abrir “Iniciar conversa”, buscar o catálogo e oferecer seleção de um agente, com estados de carregamento, falha com nova tentativa e catálogo vazio.
- Criar a conversa somente após confirmação da API; bloquear submissões repetidas enquanto a criação estiver pendente.
- Em `409`, mostrar que já existe uma conversa e oferecer **Abrir conversa existente**, reutilizando a entrada local correspondente ao ID quando disponível.
- Guardar o ID do servidor separadamente do ID local. Enviar mensagens somente em conversas com ID persistido confirmado.
- Exibir o nome do agente selecionado nos rótulos, mensagens e campos; usar representação visual genérica quando não houver avatar conhecido.
- Preservar históricos e rascunhos anteriores como registros locais consultáveis. Não associá-los automaticamente a conversas novas nem reenviar suas mensagens.
- Ao retomar uma conversa sem histórico naquele navegador, informar que o histórico exibido é local; não apresentar a conversa como contexto vazio do agente.
- O clique em Silas no mapa seleciona Silas no fluxo de abertura, sem criar conversa apenas por abrir o drawer.
- Reuniões continuam locais e identificadas como tal.
- Para consumo dos novos endpoints GET, o Idealizador ajustará também o CORS da API.

## Validação e sequência de entrega

1. Implementar e revisar a infraestrutura isoladamente; o Idealizador aplica a migração em ambiente de teste.
2. Validar criação, leitura após reconexão, timestamps, rollback, devolução de conexão e duplicidade com participantes invertidos e inserções concorrentes.
3. O Idealizador integra serviços e rotas; o assistente implementa o frontend usando respostas controladas dos contratos acordados.
4. Validar o fluxo integrado: catálogo → criação → envio por `conversation_id` → recuperação da thread correta.
5. Conferir falhas de rede, `409`, isolamento entre duplas, histórico local preservado e navegação entre mapa e laboratório.
6. Executar build do frontend e análise de tipos dos arquivos envolvidos; adaptar os testes que ainda dependem do contrato antigo.
7. Atualizar backlog e guias de execução. Não executar migrações em dados reais nem chamadas ao modelo como parte dos testes automatizados.

Não haverá autorização implícita para refatorações adicionais do backend. Os limites do pool são valores iniciais para uso local; a primeira entrega não inclui autenticação, importação de conversas antigas ou alteração dos checkpoints existentes.

## Referências de estudo

- [Pools de conexão no Psycopg](https://www.psycopg.org/psycopg3/docs/advanced/pool.html).
- [Transações no Psycopg](https://www.psycopg.org/psycopg3/docs/basic/transactions.html).
- [Índices parciais no PostgreSQL](https://www.postgresql.org/docs/current/indexes-partial.html).
- [Guia de uso da infraestrutura](../src/infra/db/relational/README.md).

O texto acima preserva o plano aprovado, com responsabilidades identificadas por papel. O acompanhamento da entrega e as pendências de integração estão no backlog e no guia da infraestrutura.
