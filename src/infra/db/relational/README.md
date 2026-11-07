# Persistência de conversas

**Natureza:** referência técnica de desenvolvimento e guia de integração.
**Data:** 07/11/2026.
**Estado:** infraestrutura implementada e testada isoladamente; integração com a API a cargo do Idealizador.

O [plano completo aprovado](../../../../dev/plano-persistencia-conversas.md) registra
as escolhas, os contratos HTTP e a divisão de responsabilidades. Não há ORM:
as consultas são SQL explícito executado pelo Psycopg.

## As três responsabilidades

1. `conversation_pool.py` administra a disponibilidade das conexões. Não lê `.env`;
   recebe a URI da aplicação e fecha seus recursos ao sair do contexto.
2. `conversation_repository.py` converte operações de conversa em consultas. Recebe
   o pool pronto e devolve `ConversationRecord`, um registro tipado e imutável.
3. `migrations/001_create_conversations.sql` prepara a estrutura do banco. Não é
   executada pelo pool ou pelo repositório.

`ConversationRecord` não substitui a entidade de domínio. O serviço deve decidir
quando criar a conversa, gerar seus IDs e adaptar a entidade para o registro.
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

## Aplicar a primeira migração

Abra explicitamente o banco de desenvolvimento ou teste escolhido e execute o
arquivo `migrations/001_create_conversations.sql` no seu cliente PostgreSQL.
Se `DB_URI` estiver exportada no ambiente do terminal, uma alternativa na raiz é:

```sh
psql "$DB_URI" --set=ON_ERROR_STOP=1 --file=src/infra/db/relational/migrations/001_create_conversations.sql
```

Ter a variável em `.env` não a exporta para o terminal. A aplicação lê esse arquivo
via Python; o comando acima requer a variável no ambiente do próprio shell.

A migração cria o schema `yavin`, a tabela `conversations` e o índice de unicidade,
dentro de uma transação. Exige as permissões correspondentes no banco. Ela deve
ser aplicada uma vez: executar novamente falha na criação da tabela em vez de
ocultar uma eventual divergência de schema. Não altera tabelas do checkpointer.
As próximas mudanças estruturais deverão usar novos arquivos numerados; não há
um executor automático nem uma tabela de controle de versões neste incremento.
Não rode a migração automaticamente a cada requisição ou inicialização.

## Uso do repositório

Exemplo de estudo, não conectado às rotas atuais:

```python
from datetime import UTC, datetime
from ulid import ULID
from src.infra.db.relational.conversation_pool import open_conversation_pool
from src.infra.db.relational.conversation_repository import (
    ActiveConversationExists,
    ConversationRecord,
    PostgresConversationRepository,
    conversation_lookup,
)

# db_uri, sender_id e participant_id vêm da configuração e do serviço.
with open_conversation_pool(db_uri) as pool:
    repository = PostgresConversationRepository(pool)
    candidate = ConversationRecord(
        id=f"Conv_{ULID()}",
        sender_id=sender_id,
        participant_id=participant_id,
        look_up_key=conversation_lookup(sender_id, participant_id),
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
  recebida em `/chat` e acessar seu `thread_id` interno.
- `get_active_by_lookup(key)`: devolve a conversa ativa da dupla ou `None`.

Os timestamps precisam conter fuso. Use `datetime.now(UTC)` para criação.
A distinção entre `created_at` e `start_date` permanece explícita: neste incremento
só a criação é obrigatória; início e fim ficam nulos até existir uma regra de domínio.
Novas conversas devem ser criadas com `active=True` (o padrão do registro).

## Lookup e concorrência

`conversation_lookup(A, B)` ordena os IDs sem modificar seu conteúdo e produz JSON
compacto, com caracteres Unicode preservados. O mesmo par sempre gera a mesma
chave, independentemente da ordem. Não há concatenação ambígua por `_`.

O lookup não é o ID da conversa. `id` continua sendo `Conv_<ULID>`; conversas futuras
encerradas poderão compartilhar o mesmo lookup e continuar com IDs distintos.
Use o helper ao gravar por este repositório; não invente outra serialização em SQL
ou em um serviço paralelo. A validação do registro recusa uma chave não canônica.

A consulta antecipada melhora a identificação de duplicidade, mas duas requisições
podem observar ausência simultaneamente. O índice único parcial decide qual gravação
é aceita. A tentativa perdedora faz rollback e consulta a vencedora, levantando
`ActiveConversationExists` com seu registro. Somente o conflito desse índice é
traduzido; duplicidade de ID ou thread e outros erros de banco continuam sendo erros.

Não há método de encerramento. Uma futura implementação poderá desativar o registro
e preencher o fim, liberando a dupla para outra conversa. Isso não autoriza criar
uma rota ou um botão de encerramento agora.

## Integração que falta no backend

O assistente não modificou serviços, entidades, DTOs ou rotas nesta entrega.

1. Ajustar o lookup atual: ele atribui `_id` e lê `__id`. Distinguir a identidade
   da conversa de sua chave de busca e adotar o helper canônico.
2. Corrigir a inicialização Pydantic do DTO de criação; representar datas da entidade
   com timestamps com fuso e transportar os IDs dos participantes para o registro.
3. Abrir o pool no ciclo de vida da aplicação, fornecer sua URI e injetar o
   repositório no serviço. Não reutilizar o parâmetro `checkpointer` para esse fim.
4. Definir a execução dos serviços: `run_in_threadpool` recebe funções síncronas;
   hoje recebe métodos `async`, retornando uma coroutine em vez do resultado esperado.
   As operações deste repositório são síncronas e devem rodar fora do event loop.
5. Implementar `GET /agents` com os agentes realmente disponíveis, sem IDs inventados
   pelo frontend. Habilitar GET no CORS. Os JSONs atuais continuam provisórios.
6. Na criação, validar a dupla e o catálogo, gerar IDs no servidor, chamar `create`
   e devolver `201` com os metadados. Traduzir `ActiveConversationExists` em `409`
   com `error.details` contendo `conversation_id`, `participant_id` e `created_at`.
   `ApiError` já tem `details`, mas `AppError` e seu handler ainda precisam transportá-lo.
7. No chat, exigir `conversation_id`, buscar a conversa, validar participação e
   atividade, resolver o agente e utilizar `thread_id` salvo. Remover a criação
   implícita em `CHAT_CACHE`; não permitir que o cliente escolha a thread.

O plano contém os formatos exatos das respostas e erros. O frontend já usa esses
contratos; o fluxo real só funcionará após essa integração. Não há fallback para o
payload anterior ou envio de registros locais como se fossem persistidos.

## Testes

Na raiz, os testes novos que não usam banco podem ser executados com:

```sh
uv run python -m unittest discover -s tests -p test_conversation_repository.py -v
```

Os testes PostgreSQL exigem explicitamente `YAVIN_TEST_DB_URI` apontando para um
banco descartável sem `yavin.conversations`. Não leem `DB_URI`, não carregam `.env`
e recusam uma tabela já existente. A suíte aplica a migração nesse banco e remove
seus registros ao final; a tabela continua lá, portanto outra execução exige um
banco descartável novo. Nunca aponte essa variável para dados de desenvolvimento
que deseje preservar.

```sh
uv run python -m unittest discover -s tests -v
uv run pyright --pythonpath .venv/bin/python src/infra/db/relational/conversation_pool.py src/infra/db/relational/conversation_repository.py
```

Em 07/11/2026 foram aprovados dez testes desta infraestrutura (três de lookup e
configuração, sete de integração), usando PostgreSQL local descartável. Cobertura:
reconexão, isolamento de duplas, concorrência, participantes invertidos, timestamps,
rollback, histórico inativo e ausência de transações ociosas. O banco do `.env`
não foi acessado. Testes do contrato HTTP real aguardam sua implementação.
