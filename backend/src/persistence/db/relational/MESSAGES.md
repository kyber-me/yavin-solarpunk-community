# Persistência simples de mensagens

<!-- Comandos e caminhos src/ deste guia são relativos a backend/. -->

**Natureza:** referência técnica e decisão de desenvolvimento, não memória da simulação.

Data: 07/11/2026.
Questão: persistir mensagens com adaptação explícita entre Pydantic e SQL.
Opções consideradas: usar diretamente o modelo Pydantic na infraestrutura ou
separar modelo, registro e adaptação.
Decisão: manter o `Message` atual no DTO, acrescentar `MessageRecord`, adaptador e
repositório síncrono concreto, reutilizando o pool de conversas.
Motivo: tornar visíveis os limites de validação, contexto de autoria e persistência
sem criar ORM, repositório genérico ou um segundo pool.
O que continua aberto: política de novas tentativas, edição e exclusão.
Histórico HTTP paginado e dois turnos com modelo real foram validados.
Próximo passo: aprofundar tratamento de falhas e reconciliação; o serviço já integra
o adaptador e o repositório, e o schema inicial foi aplicado sob aprovação.

## Responsabilidades

- `Message` em `src/types/dtos/chat_service_request.py`: modelo Pydantic existente,
  com identidade, conteúdo e datas; timestamps agora exigem fuso, com criação em UTC.
- `message_record.py`: dataclass imutável com os campos persistidos, incluindo
  `conversation_id` e `sender_id`. Não depende de Pydantic nem valida tipos automaticamente.
- `src/services/message_mapper.py`: `message_to_record` acrescenta o contexto da
  conversa e autoria; `message_from_record` reconstrói o modelo e preserva ID e datas.
  O contexto permanece disponível no registro, não é incorporado ao `Message` atual.
- `message_repository.py`: grava e consulta registros; não conhece DTO, HTTP ou agente.
  Usa cursor com `class_row(MessageRecord)` sem alterar a row factory do pool.

## Migração e operações

Aplicar somente `001_initial_schema.sql`, uma única vez. O schema foi consolidado
após confirmação de que nenhuma migração anterior havia sido aplicada ao banco do
projeto. IDs de mensagens e conversas são ULIDs puros. A migração não é executada
automaticamente. Foi aplicada ao banco do projeto em 07/11/2026; não repetir.
Há chave estrangeira para a conversa; mensagens impedem apagar sua conversa por
exclusão física direta. Não há exclusão em cascata.

- `create(record)`: confirma a transação e retorna o registro salvo. ID repetido
  gera erro de unicidade; não há upsert nem reenvio idempotente implícito.
- `get_by_id(id)`: retorna um registro ou `None`.
- `list_by_conversation(id, limit=100, offset=0)`: retorna mensagens paginadas por
  `created_at, id`, com limite entre 1 e 1000. Inclui metadados de exclusão;
  não oculta linhas automaticamente. Essa ordenação não representa uma sequência
  causal garantida de requisições concorrentes. A paginação atual é por offset,
  não por cursor; o serviço HTTP devolve `next_offset` e omite mensagens marcadas
  como excluídas.

`updated_at` e `deleted_at` são armazenados, mas não atualizados automaticamente;
não foram criados métodos de edição ou exclusão. A camada não verifica atividade
ou participação na conversa: o serviço deve validar essas regras antes de gravar.

## Exemplo de adaptação já usada pelo serviço

```python
from src.infra.db.relational.message_repository import PostgresMessageRepository
from services.helpers.message_mapper import message_to_record
from src.types.dtos.send_message_service_request import Message

# conversation e sender_id precisam ter sido validados pelo serviço.
# Gerar o modelo no servidor evita aceitar IDs e datas arbitrários do cliente.
message = Message(content=content)
record = message_to_record(
  message, conversation_id=conversation.id, sender_id=sender_id,
)
repository = PostgresMessageRepository(pool)
saved = repository.create(record)
```

Essas operações síncronas devem executar fora do event loop. Cada operação devolve
a conexão antes de retornar. Não envolver a chamada a Silas em uma transação aberta.
Persistir uma mensagem não a insere no checkpoint do agente, nem o contrário.
O serviço grava a entrada antes de chamar o agente; se a chamada falhar, a entrada
permanece no banco. Ainda não há política de reenvio ou reconciliação: mensagens
e checkpoints não são uma transação única.

## Verificação

```sh
.venv/bin/python -B -m unittest discover -s tests -p test_message_repository.py -v
```

Três testes não precisam de banco. Cinco exigem `YAVIN_TEST_DB_URI` apontando para
um banco descartável vazio, sem `yavin.conversations`. A suíte aplica a migração inicial e mantém as tabelas; outra execução exige um banco novo. Não lê `.env`.
Os oito testes passaram em PostgreSQL descartável, assim como os nove testes de
regressão de conversas executados em outro banco descartável. A análise estrita
de tipos dos arquivos da camada também passou. Nenhuma chamada ao modelo foi feita.

## Estado ao encerrar a sessão

Integração real do serviço validada em dois turnos; quatro mensagens persistidas
na conversa técnica, recuperadas pelo frontend. API e Vite foram encerrados a pedido
do Idealizador. [Ponto de retomada](../../../../../dev/retomada-2026-11-07.md).
A autorização desta entrega não é permanente para alterar o backend.
