# Persistência de conversas

<!-- Comandos e caminhos src/ deste guia são relativos a backend/. -->

A camada de mensagens e seu adaptador estão descritos em
[Persistência de mensagens](MESSAGES.md). Conversas e mensagens estão integradas
ao chat; ambas são criadas por `migrations/001_initial_schema.sql`.

**Natureza:** referência técnica de desenvolvimento e guia de integração.
**Data:** 07/11/2026.
**Estado:** integrada à API, schema aplicado ao banco do projeto e dois turnos
reais validados. Servidores encerrados ao final da sessão; detalhes de retomada em
[registro operacional](../../../../../dev/retomada-2026-11-07.md).

O [plano completo aprovado](../../../../../dev/plano-persistencia-conversas.md) registra
as escolhas, os contratos HTTP e a divisão de responsabilidades. Não há ORM:
as consultas são SQL explícito executado pelo Psycopg.

## As três responsabilidades

1. `conversation_pool.py` administra a disponibilidade das conexões. Não lê `.env`;
   recebe a URI da aplicação e fecha seus recursos ao sair do contexto.
2. `conversation_repository.py` converte operações de conversa em consultas. Recebe
   o pool pronto e devolve `ConversationRecord`, um registro tipado e imutável.
3. `migrations/001_initial_schema.sql` prepara a estrutura do banco. Não é
   executada pelo pool ou pelo repositório.

`ConversationRecord` representa os dados usados pelo repositório. O serviço decide
quando criar a conversa e gera seus IDs; uma entidade adicional não é exigida por este adaptador.
O repositório não conhece FastAPI, Silas, ferramentas, LangGraph ou `AppError`.

## Como uma operação usa a conexão

```text
Inicialização da API → abre o contexto do pool → guarda o recurso na aplicação

Requisição → serviço → repositório → empresta conexão → SQL → commit/rollback
                                    ← devolve conexão ← resultado/erro

Encerramento da API → sai do contexto do pool → fecha conexões e workers
```

O pool abre entre zero e quatro conexões por processo, com espera máxima de cinco
segundos por uma conexão e `max_idle=60`. A redução de conexões ociosas é realizada
pelo pool, não é um cronômetro exato por conversa. Há verificação de conexão antes
do empréstimo; criar o pool com mínimo zero não comprova que o banco está acessível.
A primeira operação pode falhar por indisponibilidade ou configuração.

Cada método do repositório encerra sua transação e devolve a conexão antes de
retornar. Não mantenha uma transação de domínio aberta durante uma chamada ao modelo.
O pool é exclusivo destas operações; a conexão do checkpointer permanece separada.
Uma instância de repositório pode ser compartilhada: ela guarda apenas a referência
para o pool, sem armazenar cursor, transação ou conversa corrente.

## Aplicar a migração inicial

O schema foi consolidado em `migrations/001_initial_schema.sql` porque o Idealizador
confirmou que os scripts anteriores nunca haviam sido aplicados e só existiam
dados do checkpointer à época. O arquivo cria diretamente conversas e mensagens, IDs ULID puros,
chave estrangeira e índice único parcial da dupla ativa sem direção.

Aplicar explicitamente uma única vez ao banco escolhido. Não é idempotente e não
roda na inicialização. Não altera tabelas nem dados do checkpointer.
Se `DATABASE_URI` estiver exportada no shell, executar na raiz:

```sh
psql "$DATABASE_URI" --set=ON_ERROR_STOP=1 --file=src/persistence/db/relational/migrations/001_initial_schema.sql
```

Ter a variável em `.env` não a exporta para o shell. Não há executor automático
nem tabela de versões. A migração foi aplicada ao banco do projeto em 07/11/2026, preservando os 15
checkpoints existentes; não executar novamente nesse banco.
Depois da primeira aplicação em ambiente mantido, preservar este script e criar
novas migrações incrementais para evoluir estruturas ou dados.

## Uso do repositório

Exemplo isolado de uso; as rotas atuais já usam o repositório:

```python
from datetime import UTC, datetime
from ulid import ULID
from src.infra.db.relational.conversation_pool import open_conversation_pool
from src.infra.db.relational.conversation_repository import (
    ActiveConversationExists,
    ConversationRecord,
    PostgresConversationRepository,
)

# db_uri, sender_id e participant_id vêm da configuração e do serviço.
with open_conversation_pool(db_uri) as pool:
    repository = PostgresConversationRepository(pool)
    candidate = ConversationRecord(
        id=str(ULID()),
        sender_id=sender_id,
        participant_id=participant_id,
        thread_id=str(ULID()),
        created_at=datetime.now(UTC),
    )
    try:
        saved = repository.create(candidate)
    except ActiveConversationExists as error:
        existing = error.conversation
```

No uso real, o contexto do pool abrange a vida da API, não cada chamada do serviço.
O exemplo não é uma recomendação de criar outro pool por requisição.

- `create(record)`: confirma a gravação antes de devolver o registro persistido.
- `get_by_id(id)`: devolve um registro ou `None`; serve para resolver a conversa
  recebida em `/conversation/message` e acessar seu `thread_id` interno.
- `get_active_by_participants(sender_id, participant_id)`: devolve a conversa ativa da dupla ou `None`.
- `list_by_participant(id, limit=100, offset=0)`: lista conversas em que o ID aparece
  em qualquer ponta, incluindo inativas, por criação e ID decrescentes.

Os timestamps precisam conter fuso. Use `datetime.now(UTC)` para criação.
A distinção entre `created_at` e `start_date` permanece explícita: neste incremento
só a criação é obrigatória; início e fim ficam nulos até existir uma regra de domínio.
Novas conversas devem ser criadas com `active=True` (o padrão do registro).

## Dupla ativa e concorrência

A migração inicial cria um índice único parcial sobre
`LEAST(sender_id, participant_id)` e `GREATEST(sender_id, participant_id)`, somente
nas linhas ativas. A/B e B/A entram em conflito; linhas inativas não impedem outra
conversa ativa. A consulta usa as mesmas expressões e o filtro `active`.
Não há coluna `look_up_key`. IDs de conversas e mensagens são ULIDs puros.

A consulta antecipada melhora a identificação de duplicidade, mas duas requisições
podem observar ausência simultaneamente. O índice único parcial decide qual gravação
é aceita. A tentativa perdedora faz rollback e consulta a vencedora, levantando
`ActiveConversationExists` com seu registro. Somente o conflito desse índice é
traduzido; duplicidade de ID ou thread e outros erros de banco continuam sendo erros.

Não há método de encerramento. Uma futura implementação poderá desativar o registro
e preencher o fim, liberando a dupla para outra conversa. Isso não autoriza criar
uma rota ou um botão de encerramento agora.

## Integração atual e limites

O catálogo é compartilhado por listagem e criação. Participante indisponível retorna
422; dupla ativa retorna 409 com metadados. O chat recebe `conversation_id`, verifica
existência, participação e atividade e resolve `thread_id` internamente. Não há
criação implícita. As rotas GET de conversas/mensagens consultam o banco e paginam;
a SPA não mantém históricos locais. Há cobertura HTTP integrada e dois turnos reais.

Continuam abertos: autenticação, reconciliação de falhas/novas tentativas, validação
de uso real do compositor da SPA, testes legados e caminho de inspeção do LangGraph.
Não reexecutar a migração inicial nem chamar o modelo só para conferir esta memória.
O [backlog](../../../../../BACKLOG.md) e o ponto de retomada registram o próximo passo.

## Testes

Na raiz, os testes novos que não usam banco podem ser executados com:

```sh
uv run python -m unittest discover -s tests -p test_conversation_repository.py -v
```

Os testes PostgreSQL exigem explicitamente `YAVIN_TEST_DB_URI` apontando para um
banco descartável sem `yavin.conversations`. Não leem `DB_URI`, não carregam `.env`
e recusam uma tabela já existente. A suíte aplica `001_initial_schema.sql` nesse banco e remove
seus registros ao final; a tabela continua lá, portanto outra execução exige um
banco descartável novo. Nunca aponte essa variável para dados de desenvolvimento
que deseje preservar.

```sh
uv run python -m unittest discover -s tests -v
uv run pyright --pythonpath .venv/bin/python src/persistence/db/relational/conversation_pool.py src/persistence/db/relational/conversation_repository.py
```

A suíte atual cobre configuração do pool, reconexão, isolamento de duplas,
concorrência, participantes invertidos, timestamps, rollback, histórico inativo,
ausência de transações ociosas e inserção direta invertida sem passar pelo repositório.
O banco do `.env` não é acessado. O fluxo HTTP com PostgreSQL e checkpoints reais,
mas modelo simulado, foi validado em `tests/test_http_integration.py`; dois turnos com o modelo real e recarga do histórico no frontend também passaram.
