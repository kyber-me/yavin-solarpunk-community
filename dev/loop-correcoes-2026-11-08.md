# Loop limitado de correções

**Natureza:** decisão operacional do método de desenvolvimento.

Data: 08/11/2026.
Questão: como a skill revisora pode devolver correções a um executor sem perder identidade, autorização e limite?
Opções consideradas: revisor criando executores recursivamente ou coordenador
central com papéis separados e eventos persistidos.
Decisão: a skill revisora contém diretrizes lidas pelo coordenador, que delega
revisão e correção em contextos novos. Filhos não delegam. Três tentativas por
tarefa, incluindo a inicial. Cada implementação e relatório recebe ULID.
Motivo: evitar repetição ilimitada, associar feedback ao snapshot correto e
preservar o escopo aprovado pelo Idealizador.
O que continua aberto: exercício real do ciclo, runner autônomo, roteamento,
captura de versões e schema das respostas aos achados.
Próximo passo: executar o protocolo na próxima tarefa cujo plano autorize correções.

[Diretrizes](../.agents/skills/revisar-implementacao/references/loop-correcoes.md),
[schema de eventos](../.agents/skills/revisar-implementacao/references/loop.schema.json)
e [schema de revisão](../.agents/skills/revisar-implementacao/references/revisao.schema.json).

O plano e a classificação continuam pertencendo à tarefa; as tentativas referenciam
suas versões exatas. A revisão v2 adiciona IDs de implementação e relatório, sem
reescrever a revisão histórica v1. `loop-NNN.json` registra cada transição antes
das chamadas, com contador e encadeamento centralizados. O protocolo depende das
ferramentas do agente; não foi implementado serviço que execute o loop sozinho.

Nenhuma correção de Yavin ou nova revisão real foi iniciada neste incremento.
O pedido de configurar o loop não autoriza alterações de backend sob achados
anteriores. A migração já aprovada continua encerrada tecnicamente.
