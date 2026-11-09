# Registros do harness

**Natureza:** referência operacional de desenvolvimento, fora da memória da simulação.
**Data:** 09/11/2026.

## Ciclo contemporâneo concluído

A tarefa `acesso-area-idealizador`, registrada em
`2026-11-09/041642-acesso-area-idealizador/`, percorreu classificação,
planejamento, três tentativas de implementação, revisão técnica independente e
relatório final. A revisão `revisao-002.json` recomenda `aprovar` e o evento
`loop-005.json` está em `aprovado_tecnicamente`. O relatório final mantém
`revisao_humana` como `pendente`.

Esse ciclo não desativa o harness, não cria `harness.md` e não estabelece um
runner automático. O acesso implementado é uma autenticação mock de frontend
para desenvolvimento; não representa autorização server-side.

Cada classificação de implementação delegada no backend deve gerar um JSON
versionável antes das edições. Organização inicial:

```text
dev/harness/
└── AAAA-MM-DD/
    └── HHMMSS-slug-da-tarefa/
        ├── classificacao.json
        ├── classificacao-002.json
        ├── planejamento.json
        ├── planejamento-002.json
        ├── revisao-001.json
        ├── revisao-002.json
        ├── loop-001.json
        └── relatorio-final.json
```

A data e o horário do diretório usam o fuso local. `task_id` corresponde ao nome
do diretório da tarefa; use sufixo único em caso de colisão. Os timestamps no JSON
incluem fuso explícito. Novas avaliações da mesma tarefa criam arquivos numerados
no diretório original, sem sobrescrever o histórico, mesmo em outro dia.
`registrado_em` identifica a data de cada novo registro.

O contrato inicial está em
[classificacao.schema.json](../../.agents/skills/classificar-tarefa/references/classificacao.schema.json).
Além do schema, confira a regra `nivel = max(complexidade, risco)` e a consistência
entre diretório e `task_id`. A versão 1 registra critérios, evidências, incertezas,
referência Git e uso/limites do Graphify. Nenhum registro deve conter credenciais.

Os primeiros arquivos recuperam classificações já apresentadas no chat para a
migração e a disponibilização do Graphify. São marcados como retrospectivos,
com horário da avaliação original desconhecido (`avaliado_em: null`). Essa exceção
documenta a implantação do registro, sem fingir que existia antes das edições.
Classificações futuras devem ser gravadas no momento da avaliação.

## Planejamento

A sequência tem duas transições explícitas:

1. Salvar e validar a classificação; apresentar o nível e o caminho do JSON.
2. Sugerir que o Idealizador altere para modo Plan e aguardar seu OK após a troca.
3. Elaborar, validar e persistir o planejamento; apresentar a versão concreta.
4. Solicitar e aguardar autorização para executar o plano ou as fases indicadas.
5. Executar somente o escopo autorizado, quando o modo e as permissões permitirem.
6. Após a execução efetiva, revisar em agente com contexto novo nos níveis 3 a 5;
   nos demais, quando solicitado ou previsto no plano.
7. Encerrado o loop com aprovação técnica, gerar `relatorio-final.json` para
   orientar a revisão humana, que continua pendente.

O OK do item 2 inicia o protocolo de planejamento e não aprova a execução.
As etapas de transição valem para todos os níveis. Se Plan estiver indisponível
ou não ativado, aguardar troca ou exceção expressa; não seguir automaticamente.
O modo deve ser conferido no ambiente, sem presumir que uma mensagem o alterou.
Se Plan restringir a escrita do JSON, apresentar o plano e informar a persistência
pendente; gravar em condição permitida antes de implementar.

A [skill de planejamento](../../.agents/skills/planejar-tarefa/SKILL.md) usa a
classificação persistida e salva `planejamento.json` antes das edições. O schema é
[planejamento.schema.json](../../.agents/skills/planejar-tarefa/references/planejamento.schema.json).

- Nível 1: planejamento mínimo, sem decomposição artificial.
- Nível 2: registro da abordagem discutida com o Idealizador.
- Níveis 3 a 5: fases e subtarefas com dependências, arquivos previstos, critérios
  de aceitação e validações. A regra considera o maior valor de complexidade e risco.

`task_id` conecta as categorias; `classificacao_ref` identifica o arquivo de
classificação exato usado pelo plano. IDs de fases e tarefas são únicos; as
dependências entre fases formam um grafo acíclico e cada tarefa referencia critérios
existentes. Todos os critérios precisam estar cobertos. O schema valida estrutura;
essas relações também precisam ser conferidas semanticamente.

Replanejamentos geram arquivos numerados no mesmo diretório, sem sobrescrever o
histórico. A justificativa fica em `observacoes`. O plano descreve intenção;
resultados de implementação, testes e revisão humana são registros distintos.

`modo_plan.estado` informa `utilizado`, `nao_utilizado` ou `indisponivel`, com
justificativa. O uso de JSON ou de listas em mensagens não implica que o ambiente
tenha sido colocado no modo Plan. Planejar fora desse modo exige exceção expressa
do Idealizador, registrada em `observacoes`. O mesmo campo preserva a referência
ou horário disponível do OK para iniciar o protocolo.

O [primeiro planejamento](2026-11-08/005655-migracao-backend/planejamento.json)
contém quatro fases e oito subtarefas da migração. Foi consolidado depois da
execução, com origem retrospectiva e modo Plan `nao_utilizado`; não representa
uma aprovação prévia nem substitui o registro dos resultados.

## Revisão independente

A [skill do revisor](../../.agents/skills/revisar-implementacao/SKILL.md) entrega
uma rodada por invocação, registrada em `revisao-NNN.json` pelo
[schema](../../.agents/skills/revisar-implementacao/references/revisao.schema.json).
Não há revisão real da migração produzida apenas por adicionar esta skill.

O implementador coordena a passagem para outro agente sem histórico herdado.
O pacote preserva requisitos, restrições e evidências, mas não inclui argumentação
do implementador ou uma lista de defeitos esperados. O revisor inspeciona código
e dependências do escopo, registra hashes da entrega, verifica critérios e
devolve achados com localização, consequência e correção mínima. Ele não edita código.

Sem `execucao.json`, uma evidência explícita em relatório ou mensagem identificável
pode compor o pacote; plano salvo não comprova execução. O relatório distingue
checagens próprias das informadas pelo implementador, contexto novo de isolamento
não verificado e aprovação técnica de revisão humana.

Pareceres: `aprovar`, `solicitar_correcoes` ou `inconclusiva`. Aprovar exige todos
os critérios atendidos, snapshot estável e ausência de bloqueios. Sugestões de
refactoring podem ser não bloqueantes; estilo nunca bloqueia. As
[referências especializadas](../../.agents/skills/revisar-implementacao/references/refactoring.md)
conectam o protocolo a Fowler e às práticas de revisão do Google por links, sem
instalar uma base RAG ou copiar livros.

Rodadas anteriores não são sobrescritas. O implementador pode corrigir dentro do
escopo autorizado ou contestar achados com evidências. A revisão humana e o
roteamento de modelos continuam separados do parecer técnico.

## Loop limitado de correções

[Diretrizes](../../.agents/skills/revisar-implementacao/references/loop-correcoes.md)
e [schema dos eventos](../../.agents/skills/revisar-implementacao/references/loop.schema.json).
O coordenador lê as diretrizes e chama revisor ou executor com ferramentas de
delegação. Revisor e executor não criam outros agentes. Este é um protocolo
operacional das skills, não um runner autônomo implementado em código.

- `task_id` permanece estável; cada tentativa recebe novo ULID `implementation_id`
  e `parent_implementation_id`; cada revisão recebe `review_id`.
- Classificação/plano são da tarefa e referenciados em versões exatas; não são
  duplicados a cada tentativa. Revisão v2 vincula os IDs à entrega examinada.
  Revisão v1 histórica continua válida e não é reescrita retroativamente.
- Eventos imutáveis `loop-001.json`, `loop-002.json` etc. registram autorização,
  IDs, contador, estado e snapshots. Reservar e persistir antes de chamar agente.
- Máximo de três tentativas totais: inicial e duas correções. Falhas técnicas ou
  resultado de chamada desconhecido não disparam repetição automática.
- Correções dependem de cobertura explícita da autorização. Parecer de correção
  e pedido de revisão não autorizam mudanças. Fora do escopo, conflito não resolvido
  ou limite atingido: aguardar Idealizador. Parecer inconclusivo: registrar impedimento.
- Pacote curto do executor: objetivo/restrições, autorização, versões do plano e
  classificação, critérios, achados, snapshot/diff, IDs e saldo de tentativas.
  Sumários apontam aos registros completos e não substituem a evidência.

Além do schema, conferir sequência de eventos, referências, IDs únicos, encadeamento
dos pais, numeração contígua de tentativas e ausência de chamadas pendentes.
O estado aprovado requer revisão vinculada com parecer favorável e snapshot estável.
Validar arquivos locais antes de aplicar feedback; código diferente do snapshot
exige reconciliação. Um único coordenador escreve o controle.

Respostas por achado são registradas em `resposta-revisao-NNN.md`, com IDs e
evidências. Schema específico dessas respostas, captura das últimas três versões
e `execucao.json` permanecem pendentes. A migração aprovada anteriormente não foi
reiniciada como loop nem recebeu novos IDs fictícios.

## Relatório final para a interface

A [skill relatar-implementacao](../../.agents/skills/relatar-implementacao/SKILL.md)
gera `relatorio-final.json` após revisão v2 favorável e evento final do loop
aprovado tecnicamente, com os mesmos IDs de tarefa, implementação e revisão.
O contrato está em
[relatorio-final.schema.json](../../.agents/skills/relatar-implementacao/references/relatorio-final.schema.json).

Campos para uma primeira interface simples:

| Conteúdo | Finalidade |
|---|---|
| Título, resumo e IDs | Identificar entrega e comportamento implementado |
| Arquivos alterados e caminhos anteriores | Navegar por adições, mudanças, remoções e renomes |
| Fases executadas e critérios | Relacionar a entrega ao plano, com evidências |
| Validações e anotações | Exibir resultados reais, limites e pendências |
| Referências de registros e diffs | Abrir os detalhes sem duplicá-los no resumo |
| Fluxo funcional opcional | Renderizar nós e relações didáticas quando fundamentadas |
| Snapshot e revisão humana pendente | Identificar a versão que aguarda a leitura do Idealizador |

Todos os caminhos de arquivos/artefatos neste relatório são relativos à raiz do
repositório; fases e anotações referenciam IDs da lista de arquivos alterados.
Planos e revisões preservam suas próprias regras de referências internas.
O schema valida estrutura; a skill também exige conferir vínculos, IDs, hashes,
critérios e evidências. Não emitir aprovação para snapshot que mudou.

`report_id` é ULID novo. Atualizações de consolidação geram
`relatorio-final-002.json` etc., sem sobrescrever histórico. `revisao_humana` nasce
`pendente`; o agente não pode marcá-la como feita. A futura interface deverá
persistir a avaliação humana separada, vinculada ao relatório e à versão do código.
Essa persistência e a interface ainda não foram implementadas.

A migração histórica tem revisão v1 e não possui os IDs/eventos exigidos nesta
nova etapa; não foi gerado relatório final fictício para ela. O primeiro exercício
completo de geração usando uma entrega nova permanece pendente.

Esta pasta é versionada; os grafos e caches locais continuam em `dev/graphs/backend/`,
ignorados pelo Git. Relatórios de execução e revisão humana poderão usar os
diretórios de tarefa, mas seus contratos e a interface ainda serão definidos.
`autorizacao.json` e `execucao.json` são categorias propostas, ainda sem schemas ou
persistência implementados. A aprovação de execução permanece explícita na conversa
até esse incremento; não inferir sua existência por haver um plano salvo.
