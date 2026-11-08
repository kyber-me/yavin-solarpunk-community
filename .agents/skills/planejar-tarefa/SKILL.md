---
name: planejar-tarefa
description: Registra planejamento JSON para implementações delegadas no backend após classificação persistida, mudança para modo Plan e OK do Idealizador. Decompõe níveis 3 a 5 em fases e subtarefas; registra abordagem para nível 2 e planejamento mínimo para nível 1. Exclui frontend e perguntas conceituais.
---

# Planejar tarefa

**Natureza:** procedimento de desenvolvimento; fora da memória da simulação.

Leia o registro de classificação da tarefa e valide o plano pelo
[schema](references/planejamento.schema.json). `nivel` é o maior valor entre
complexidade e risco; não reduza o tratamento ao decompor uma tarefa.

## Entrada no protocolo

Só inicie após classificação persistida e OK explícito do Idealizador para
planejar, dado depois da mudança para modo Plan. Confira o modo pelas informações
do ambiente. Se houver apenas classificação, sugira a troca e aguarde; não inicie
o planejamento automaticamente. A regra vale para todos os níveis.

Se o modo Plan estiver indisponível ou não tiver sido efetivamente ativado,
explique e aguarde a troca ou uma exceção expressa para planejar fora desse modo.
Não acione controles da interface para substituir a escolha do Idealizador.
Registre a manifestação recebida em `observacoes`, com a referência ou horário
disponível, sem inventar evidência. O OK para planejar não aprova implementação.

## Tratamento por nível

- **1:** plano mínimo, proporcional ao trabalho; uma fase e uma tarefa podem bastar.
- **2:** discuta a abordagem com o Idealizador e registre o que foi de fato combinado.
  Não descreva propostas como aprovadas. Uma fase pode bastar.
- **3 a 5:** decomponha pragmaticamente em fases e subtarefas verificáveis, antes
  das edições. Uma lista em mensagem ou um JSON não comprovam ativação do modo Plan.
  Preencha `modo_plan` conforme o estado observado. Planejamento fora desse modo
  exige a exceção expressa descrita acima.

## Conteúdo

Defina objetivo, escopo incluído/excluído e critérios observáveis de aceitação.
Cada critério tem ID, descrição e forma de verificação. Cada fase tem ID, objetivo,
dependências de outras fases e tarefas menores. Cada tarefa tem ID estável,
descrição, caminhos de arquivos/diretórios esperados, critérios atendidos por ID
e validações proporcionais. Dependências entre fases permitem renderização como
grafo; não representam o fluxo funcional da aplicação.

Use IDs únicos para todas as fases/tarefas e critérios únicos. Não aceite
dependências ausentes, da própria fase ou ciclos. Todos os critérios referidos
devem existir e todos os critérios do plano devem estar cobertos por tarefas.
Níveis 3 a 5 exigem pelo menos duas fases e duas tarefas no conjunto; não
fragmente por linha ou crie fases artificiais para aumentar o tamanho do plano.

Leia caminhos e contratos reais; indique novos caminhos como destino planejado,
sem alegar que já existem. Identifique riscos e incertezas concretos. Não
modifique contratos, dados ou dependências apenas para elaborar o plano.

## Registro

Salve `planejamento.json` no mesmo diretório datado da tarefa que contém
`classificacao.json`, preservando `task_id`. `classificacao_ref` é o nome relativo
do arquivo de classificação exato usado (incluindo sufixo de revisão). Copie seu
`nivel`, sem recalculá-lo silenciosamente. Se a classificação mudar, registre
nova classificação e revise o plano, sem editar o histórico.

Replanejamentos geram `planejamento-002.json`, `-003.json` etc. com justificativa
em `observacoes`. Nunca sobrescreva registros anteriores. Use timestamps ISO
8601 com fuso; `registrado_em` é o momento da gravação. Registros contemporâneos
têm `planejado_em` preenchido. Ao reconstruir trabalho anterior, use origem
`retrospectiva`, horário original `null` quando desconhecido e declare a fonte.
Não invente aprovações ou uma ativação passada do modo Plan.

Valide schema, IDs, referências, cobertura dos critérios e ausência de ciclos
antes de apresentar o caminho do arquivo. Se não conseguir persistir/validar,
informe o impedimento antes de implementar.

O plano descreve intenção, não certifica execução, testes aprovados ou revisão
humana. Esses resultados pertencem a registros posteriores. Planejar não
autoriza execução além da delegação vigente. O revisor só entra após a execução
e segundo o protocolo abaixo; roteamento de modelos continua pendente.

## Saída e autorização para execução

Depois de elaborar, validar e persistir o plano, apresente o arquivo e sua versão,
fases, limites e critérios de aceitação. Solicite aprovação para executar esse
escopo concreto e aguarde a resposta. Uma delegação genérica anterior e o OK para
planejar não substituem esta aprovação do plano.

Respeite o alcance autorizado: todas as fases ou somente as indicadas. Não repita
o pedido para fases já abrangidas pela aprovação. Mudanças fora do escopo exigem
replanejamento e nova autorização pertinente; dúvidas ou falhas não são aprovação.
Só execute quando o modo e as permissões efetivamente permitirem alterações.
Se o modo Plan impedir gravar o JSON, apresente o plano, informe a persistência
pendente e aguarde condição permitida para salvá-lo antes de implementar.

Os futuros registros `autorizacao.json` e `execucao.json` foram propostos, mas
seus schemas e procedimentos de persistência ainda não foram implementados.
Até esse incremento, preserve a manifestação de aprovação na conversa e não
declare que existe um registro estruturado de execução ou autorização.

## Depois da execução

Concluída efetivamente a implementação entregue nos níveis 3 a 5, o coordenador
prepara o pacote e aplica [revisar-implementacao](../revisar-implementacao/SKILL.md),
com outro agente e contexto novo. Não iniciar revisão por haver apenas plano
ou aprovação. Nos níveis 1 e 2, revisar quando solicitado ou previsto no plano.
O pacote precisa de evidências de execução; enquanto não houver `execucao.json`,
usar relatório explícito identificado, sem alegar que a categoria foi implementada.
O relatório técnico será persistido como `revisao-NNN.json` no mesmo diretório
da tarefa. Revisor não implementa correções; seu parecer retorna ao implementador
e não amplia as fases ou alterações autorizadas.


## Correções previstas no plano

Ao apresentar o plano, declare se a autorização solicitada inclui até duas
correções após a entrega inicial, sempre no mesmo escopo. O limite do protocolo é
três tentativas com revisão por tarefa. Não presumir que autorização anterior
sem essa cobertura permita correções. O coordenador segue
[as diretrizes do loop](../revisar-implementacao/references/loop-correcoes.md),
registrando implementation_id por entrega e referências exatas às versões
de classificação/plano. Revisões e correções não reiniciam o contador.
