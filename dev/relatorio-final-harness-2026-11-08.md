# Relatório final do harness

**Natureza:** decisão de método e contrato inicial para interface.

Data: 08/11/2026.
Questão: como apresentar uma implementação aprovada para facilitar revisão humana?
Opções consideradas: usar o parecer técnico diretamente ou consolidar um relatório
curto com referências aos registros completos.
Decisão: criar skill local `relatar-implementacao` e schema de `relatorio-final.json`.
O coordenador gera após aprovação técnica, identificando tarefa, implementação,
revisão e snapshot; inclui resumo, fases realizadas, arquivos alterados, critérios,
validações, anotações e fluxo funcional opcional.
Motivo: oferecer dados simples e navegáveis para a futura interface, sem confundir
parecer técnico, intenção de planejamento e revisão do Idealizador.
O que continua aberto: exercício em entrega nova, interface, persistência separada
da revisão humana, captura de estados e demais contratos de execução/autorização.
Próximo passo: gerar relatório a partir de entrega nova com revisão v2 e loop aprovado.

## Artefatos e integração

- [Skill](../.agents/skills/relatar-implementacao/SKILL.md).
- [Schema](../.agents/skills/relatar-implementacao/references/relatorio-final.schema.json).
- [Integridade semântica](../.agents/skills/relatar-implementacao/references/integridade.md).

O relatório é imutável e versionado por arquivos numerados. A futura avaliação
humana deve apontar para report_id e snapshot, sem modificar o histórico de aprovação.
O campo inicial de revisão humana é sempre pendente. Não há código de interface
ou armazenamento da interação humana entregue neste incremento.

O relatório não omite testes falhos ou não executados. Fluxo funcional é opcional
quando não há representação pertinente; grafo de imports não prova ordem de execução.
As fontes de execução podem ser relatórios explícitos enquanto execucao.json não
existe, mas não se inventam fontes, IDs ou aprovações.

Não houve alteração no backend nem geração retroativa para a migração: seu parecer
v1 não atende ao novo pacote de identidade e controle. O teste inicial do contrato
usa dados sintéticos, sem afirmar aprovação real da aplicação.

## Validação inicial

As skills nova e revisora passaram no validador estrutural; links locais e diff
foram conferidos. Um exemplo sintético completo passou no JSON Schema. Foram
rejeitados seis casos: revisão humana presumida, estado técnico não aprovado,
critério não atendido, fluxo declarado disponível sem nós/relações, ausência de
fluxo sem motivo e implementação sem ID. Vínculos entre artefatos e hashes exigem
também as verificações semânticas da skill; schema sozinho não prova execução.

Não houve teste completo com entrega nova, revisão v2 e eventos reais de loop.
Essa validação continua no backlog, assim como a interface e a revisão humana.
