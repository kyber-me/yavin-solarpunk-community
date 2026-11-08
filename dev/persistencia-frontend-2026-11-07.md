# Históricos exclusivamente persistidos e validação real do chat

**Natureza:** decisão e registro técnico de desenvolvimento.

Data: 07/11/2026.
Questão: eliminar conversas e históricos mantidos apenas no navegador antes de
usar o chat real.
Opções consideradas: manter registros locais consultáveis ou consultar apenas
registros confirmados no PostgreSQL.
Decisão: o banco é a fonte das conversas e mensagens; remover a chave legada
`yavin.conversations.v1`, sem ler ou importar seu conteúdo. Rascunhos permanecem
somente na memória da página. Reuniões ficam indisponíveis até serem persistidas.
Motivo: a interface deve refletir o estado realmente salvo e recuperável pelo backend.
O que continua aberto: edição e encerramento, reuniões, autenticação, reconciliação
entre mensagens e checkpoints e política de novas tentativas.
Próximo passo: validar o envio real pelo compositor da SPA em uso normal e avançar
na investigação/orquestração, sob autorizações específicas do Idealizador.

## Contratos definidos no backend

- `GET /conversations?sender_id=...&limit=100&offset=0`: lista apenas conversas de
  que o participante informado faz parte. Inclui conversas inativas para consulta.
- `GET /conversations/{id}/messages?sender_id=...&limit=100&offset=0`: verifica
  existência e participação antes de devolver o histórico. Inativas são consultáveis.
- Ambos retornam `next_offset` ou `null`. A SPA segue as páginas e usa os IDs,
  nomes e timestamps retornados, sem persistência local ou mensagens provisórias.
- Após envio, inclusive em falha do agente, a SPA consulta novamente o histórico.
  Se a entrada foi salva, ela aparece pelo ID do banco e o rascunho correspondente
  é limpo. Falhas de atualização bloqueiam envio até tentar carregar novamente.

Isso não constitui autenticação: o protótipo continua usando `sender_id` informado
no pedido e `idealizador` como remetente da interface.

## Aplicação do schema e modelo real

A migração `001_initial_schema.sql` foi aplicada ao banco configurado sob aprovação.
As 15 linhas de checkpoints anteriores permaneceram intactas na verificação antes
e depois da migração. Não foram aplicados DROP ou limpeza nas tabelas do checkpointer.

Dois turnos reais pela API, com fechamento e reabertura do lifespan entre eles,
produziram quatro mensagens persistidas. O segundo recuperou a palavra-chave do
primeiro. Registro: [teste real](local/silas_test_responses/http-real-2026-11-07.md).

## Evidência de validação

- 22 testes aprovados: cinco HTTP integrados, oito de mensagens e nove de conversas,
  usando PostgreSQL descartável e grafo simulado; inclui paginação e retomada.
- Oito testes do frontend e build aprovados. Análise estrita de tipos das novas
  consultas, contratos e repositórios aprovada.
- No Ego Browser, a conversa real e suas quatro mensagens reapareceram após recarga.
  Uma entrada legada de teste foi removida e nunca apareceu. O conflito de criação
  ofereceu abrir o registro existente; reuniões locais estão bloqueadas.
- QA controlado do compositor interceptou apenas a resposta do POST, sem chamar
  modelo ou gravar dados: nem a entrada nem a resposta não persistidas apareceram.
  O histórico continuou com quatro mensagens consultadas no banco. O fetch original
  foi restaurado ao terminar.
- A aba resultante ficou aberta para o Idealizador, com API em 8000 e Vite em 5173.
  Ações de envio reais nesta rodada ocorreram por HTTP em processo, não pelo
  compositor do navegador; não confundir o QA controlado com uma chamada real.

## Encerramento posterior solicitado pelo Idealizador

Depois das verificações, o Idealizador pediu o encerramento dos dois servidores.
FastAPI/Uvicorn e Vite foram interrompidos e as portas 8000 e 5173 conferidas livres.
A referência acima a serviços em execução descreve o momento da entrega, não o
estado para a próxima sessão. O banco e seus dados persistidos não foram removidos.
As autorizações desta rodada foram pontuais, não permanentes. O ponto atual para
reiniciar o contexto está em [retomada](retomada-2026-11-07.md).
