# Método de desenvolvimento agêntico — classificação e Graphify

**Natureza:** decisão provisória de método e registro operacional de desenvolvimento;
não pertence à base de conhecimento dos agentes da simulação.

Data: 08/11/2026.
Questão: como classificar tarefas delegadas e investigar o alcance das alterações?
Opções consideradas: classificador especializado (Jev ou alternativa aberta),
rubrica aplicada pelo agente, busca/leitura e grafo de relações como evidência auxiliar.
Decisão: criar uma skill local com rubrica versionada de complexidade e risco,
ambos de 1 a 5, usando o maior valor como nível da tarefa. Incluir Graphify como
apoio opcional, confirmado pelo código, com fallback por busca/leitura.
Motivo: disponibilizar critérios explícitos ao agente sem exigir serviço de
classificação, instalação de ferramenta ou chamadas adicionais a modelos.
O que continua aberto: calibração da rubrica, avaliação prática do Graphify,
planejamento por nível, revisão adversarial, roteamento, ciclos de correção e interface.
Próximo passo: aplicar a classificação a uma tarefa real e avaliar as evidências
antes de ampliar o harness.

## Mudança de prioridade e atribuições

A prioridade imediata passou da orquestração de Silas para o processo de desenvolvimento.
O Idealizador continua responsável pelo backend e prioriza aprendizado em
orquestração, RAG, fine-tuning, embeddings, bancos vetoriais e bases de conhecimento.
O assistente mantém o frontend, consumindo os contratos estipulados pelo backend.
Implementações pontuais do backend podem ser delegadas para liberar atenção do
Idealizador; esta orientação não concede autorização permanente.

## Incremento entregue

A skill ainda não existia no repositório; a estrutura discutida na conversa foi
materializada neste incremento autorizado de skill e documentação:

- [Procedimento](../.agents/skills/classificar-tarefa/SKILL.md): inspeção anterior
  às edições, justificativas e resultado JSON, sem modo de colaboração na nota.
- [Rubrica](../.agents/skills/classificar-tarefa/references/rubrica.md): âncoras
  das notas, regra do maior valor e distinção entre evidência e incerteza.
- [Graphify](../.agents/skills/classificar-tarefa/references/graphify.md): uso
  opcional, análise estrutural inicial, atualidade e limites de cobertura.
- `AGENTS.md`: entrada para o procedimento em pedidos de implementação delegada.
- `BACKLOG.md`: nova prioridade, entrega e pendências do método.

## Limites da integração

Referência: [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) e
[documentação de funcionamento](https://github.com/Graphify-Labs/graphify/blob/v8/docs/how-it-works.md).
A documentação distingue extração estrutural local de código de análise semântica
que pode consumir tokens. A skill orienta começar pela estrutura e não autoriza
instalação, mudança de dependências ou chamadas pagas.

Na primeira entrega não houve instalação, indexação ou teste de cobertura do Graphify em Yavin.
A integração inicial era procedural, não um adaptador executável. O grafo não
substitui leitura, validação de contratos ou testes; quantidade de conexões não
determina a nota. Deve-se conferir também arquivos locais ainda sem commit.

Na entrega inicial, o JSON era apenas um contrato de apresentação, sem schema
executável ou persistência. O incremento posterior abaixo acrescenta esses registros;
a interface permanece pendente.
Os registros de 07/11/2026 permanecem como histórico técnico; sua antiga indicação
de próxima prioridade foi substituída pela orientação deste registro.

## Incremento posterior — ferramenta e recorte do backend

**Natureza:** decisão de escopo e estado operacional de desenvolvimento.

Data: 08/11/2026.
Questão: onde aplicar o fluxo e como disponibilizar o grafo do backend?
Opções consideradas: aplicar a todo o projeto ou somente ao backend; usar a
instalação isolada existente ou adicionar dependência à aplicação.
Decisão: por diretiva do Idealizador, aplicar o fluxo apenas a implementações
delegadas no backend. Reaproveitar Graphify 0.9.71 isolado e completar seu parser SQL.
Gerar grafo estático local de Python e SQL, incluindo testes, sem chamadas a modelos.
Motivo: apoiar análise de impacto preservando as dependências e a execução de Yavin.
O que continua aberto: utilidade prática na classificação, automação de atualização
e eventual migração para uma pasta `backend/`, sugerida mas não executada.
Próximo passo: usar o grafo em uma classificação real, conferindo sua atualidade.

O resultado, reprodução e limitações estão em [dev/graphs/README.md](graphs/README.md).
Não houve mudança de código do backend, movimentação de diretórios ou execução da
aplicação. A skill permanece local a Yavin. Tarefas mistas consideram consumidores
frontend como impacto dos contratos, sem aplicar o fluxo ao desenvolvimento
exclusivo de frontend.

## Incremento posterior — registros datados e migração

**Natureza:** decisão de método e estado operacional, 08/11/2026.

Por diretiva do Idealizador, cada classificação deve gerar um JSON datado em
`dev/harness/AAAA-MM-DD/HHMMSS-slug/classificacao.json`, validado pelo schema da
skill. Reclassificações preservam o histórico em arquivos numerados. Os registros
iniciais são retrospectivos e declaram que o horário da avaliação é desconhecido.
Veja [a organização](harness/README.md).

A migração para `backend/` foi posteriormente autorizada e executada; a possibilidade
registrada acima passou a entrega. [Registro e validações](migracao-backend-2026-11-08.md).

## Segunda fase — planejamento persistido

**Natureza:** decisão de método de desenvolvimento.

Data: 08/11/2026.
Questão: tornar explícita a decomposição da implementação e disponibilizá-la à interface futura.
Opções consideradas: sequência em mensagens ou categoria JSON versionada ligada à classificação.
Decisão: adicionar skill local `planejar-tarefa` e `planejamento.json` no diretório
da tarefa, com objetivo, escopo, fases, subtarefas, dependências, arquivos esperados,
critérios de aceitação e validações. Usar o nível consolidado, maior entre complexidade
e risco: mínimo no 1, abordagem discutida no 2, decomposição nos níveis 3 a 5.
Motivo: permitir revisão, rastreabilidade e renderização do grafo do plano sem
confundir intenção, execução e aprovação.
O que continua aberto: aplicação contemporânea numa nova tarefa, runner, revisão
adversarial, relatório de execução, roteamento e interface.
Próximo passo: persistir o próximo plano antes de editar o backend e confrontar
o resultado com os critérios registrados.

O modo Plan não foi formalmente ativado durante a migração. Seu novo planejamento
é retrospectivo e declara esse fato. A skill exige usar o modo quando disponível
nos níveis 3 a 5; se indisponível, registrar a limitação e produzir o JSON. Uma
sequência em mensagens não é evidência de ativação do modo. Replanejamentos criam
arquivos numerados e preservam o plano anterior.

## Refinamento — transição explícita para o protocolo

**Natureza:** decisão de colaboração e método de desenvolvimento.

Data: 08/11/2026.
Questão: quando iniciar o planejamento e quando começar a execução?
Opções consideradas: iniciar o protocolo automaticamente após classificar ou
aguardar a mudança para Plan e o OK do Idealizador.
Decisão: após salvar e validar a classificação, sugerir a troca para modo Plan
e aguardar o OK do Idealizador depois dela. Só então iniciar a elaboração do
planejamento. Depois de apresentar a versão concreta, solicitar aprovação de
execução e respeitar o conjunto de fases autorizado.
Motivo: separar classificação, início do protocolo de planejamento e autorização
de implementação, deixando as transições sob controle explícito do Idealizador.
O que continua aberto: schemas/persistência de autorização e execução, revisão
adversarial e interface. As categorias `autorizacao.json` e `execucao.json` continuam propostas.
Próximo passo: aplicar essas transições em uma nova tarefa delegada no backend.

Esta decisão substitui o início automático e o fallback automático de planejamento
fora do modo Plan descritos na orientação anterior. A transição vale para todos
os níveis; a nota determina a profundidade do plano. Conferir o modo pelas
informações reais do ambiente. Se indisponível ou não ativado, aguardar troca
ou exceção expressa. O OK de planejamento não autoriza executar. Aprovação de
todas as fases dispensa repetir o pedido entre fases já autorizadas.

As skills e o guia do harness foram ajustados; registros JSON retrospectivos
anteriores não foram alterados para simular essas novas condições.

## Terceira fase — protocolo do revisor

**Natureza:** estado de implementação do método, 08/11/2026.

A skill local `revisar-implementacao` e seu schema de `revisao-NNN.json` foram
adicionados. A revisão ocorre após execução efetiva de entregas de níveis 3 a 5,
com agente de contexto novo, requisitos, código, plano e evidências. Refactoring
é apoiado por fontes primárias de Fowler e práticas de revisão do Google.
O revisor não edita código nem substitui aprovação/revisão humana.

[Registro, fontes e validação sintética](revisor-harness-2026-11-08.md).
Este incremento substitui a pendência de criação do protocolo, mas não implementa
roteamento, loop automático ou persistência das respostas do implementador.
A próxima revisão real continua pendente; a migração anterior não recebeu
retroativamente uma revisão independente.

## Consolidação posterior — relatório final

**Natureza:** estado do método, 08/11/2026.
A evolução posterior do protocolo adicionou o loop limitado, a revisão real da
migração (ver registro do revisor) e agora a skill `relatar-implementacao`.
O relatório final consolida a entrega aprovada para futura interface, com IDs,
arquivos, fases executadas, validações, anotações e fluxo opcional. O estado de
revisão humana permanece pendente, separado da aprovação técnica.
[Contrato, limites e validação](relatorio-final-harness-2026-11-08.md).
