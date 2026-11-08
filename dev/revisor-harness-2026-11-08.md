# Revisor independente do harness

**Natureza:** decisão de método e referência operacional de desenvolvimento.

Data: 08/11/2026.
Questão: como revisar entregas do backend após execução, com apoio especializado em refactoring?
Opções consideradas: reutilizar skill local ou criar protocolo específico. Não foi
encontrada uma skill de revisão de backend nas pastas locais consultadas; a skill
de revisão de interface não cobre este escopo.
Decisão: criar `revisar-implementacao` local ao projeto, com contexto novo, relatório
JSON por rodada e referências primárias de refactoring e práticas de revisão.
Motivo: preservar independência de análise, critérios explícitos e integração com
os registros datados já existentes, sem introduzir infraestrutura de execução nova.
O que continua aberto: aplicar à próxima entrega real, roteamento de modelos,
limite de rodadas, persistência de respostas/correções e revisão humana na interface.
Próximo passo: entregar ao revisor um pacote delimitado após implementação efetiva
de nível 3 a 5, conforme o plano e a autorização vigentes.

## Entrega

- [Skill](../.agents/skills/revisar-implementacao/SKILL.md).
- [Referências de refactoring](../.agents/skills/revisar-implementacao/references/refactoring.md).
- [Regras de parecer](../.agents/skills/revisar-implementacao/references/parecer.md).
- [Schema do relatório](../.agents/skills/revisar-implementacao/references/revisao.schema.json).

O implementador coordena a revisão em outro agente sem histórico herdado. Requisitos,
restrições, código e evidências são mantidos; justificativas do implementador não
compõem a primeira avaliação. Ausência de contexto separado impede declarar uma
revisão independente. Revisor não modifica código; resultados retornam ao implementador.

Fowler fundamenta refactoring como mudança interna que preserva comportamento;
o catálogo serve para procurar transformações pertinentes ao problema observado.
As práticas do Google apoiam o exame contextual da entrega e a distinção entre
necessidade e preferência. Os links são referências consultáveis, não uma biblioteca
RAG, um conteúdo integral incorporado ou autorização de refatoração automática.

## Limites

Sem `execucao.json`, aceita-se evidência explícita de execução em relatório/mensagem
identificável. Não há preenchimento fictício de autorização ou execução estruturada.
O parecer técnico não equivale a revisão humana nem amplia a autorização de correção.
Uma rodada por invocação; orçamento e loop automático ainda não definidos.

Na criação inicial desta skill não foi realizada revisão independente de código
real de Yavin. A validação comportamental inicial usou somente fixture temporária;
seus achados não são defeitos da aplicação nem relatórios reais em `dev/harness/`.

## Validação realizada

Validador de skills aprovou `revisar-implementacao` e a atualização de
`planejar-tarefa`; links locais e whitespace das alterações foram conferidos.
O schema rejeitou aprovações com contexto herdado, snapshot alterado ou critério
não verificado.

Um subagente com `fork_turns: none` recebeu apenas a fixture temporária, requisitos,
classificação, plano, testes e relato de execução. O implementador não forneceu
ao revisor lista de defeitos esperados. O exemplo fazia reserva de estoque com
callback de persistência; dois testes de casos básicos passavam.

O revisor produziu parecer `solicitar_correcoes`, demonstrando por contraexemplos:

- Quantidade zero era aceita e acionava persistência, contrariando o requisito
  de quantidade estritamente positiva sem efeitos para entradas inválidas.
- Falha no callback propagava exceção, mas preservava o débito em memória, em
  desacordo com a exigência de preservar o estoque anterior.
- A reserva bem-sucedida atendia ao terceiro critério.

O relatório passou posteriormente no JSON Schema real e nas conferências de
task_id, critérios, IDs de achados, caminhos do escopo e hashes do snapshot.
Código e testes da fixture foram preservados. Não foram exigidas refatorações
cosméticas ou frameworks novos. Este teste valida um cenário controlado, não
qualidade geral de revisão nem desempenho comparativo de modelos. Não houve
revisão real de Yavin, acesso ao banco ou execução de seu agente/modelo.

## Aplicação posterior — migração real

Por pedido explícito do Idealizador, outro agente com contexto novo revisou a
migração e gerou [revisao-001.json](harness/2026-11-08/005655-migracao-backend/revisao-001.json).
Parecer `aprovar`, com cinco critérios atendidos e um achado documental não
bloqueante. OpenAPI, testes, hashes e grafo foram conferidos pelo revisor.
O implementador validou o schema e a estabilidade do snapshot ao receber o relatório.

[Resposta ao achado](harness/2026-11-08/005655-migracao-backend/resposta-revisao-001.md):
R1 aceito, com correção posterior apenas no backlog. Relatório original preservado;
nenhuma correção de backend ou revisão humana presumida.

O revisor teve acesso ao Git e consultou diffs de nomes do working tree e do index.
A comparação específica usou também o snapshot anterior à movimentação, pois Git
incluía alterações anteriores. Não havia conteúdo anterior completo dos arquivos
ajustados; essa limitação permanece explícita no relatório.

## Próxima possibilidade — cadeia de estados

**Natureza:** proposta para detalhamento, ainda sem implementação.
O Idealizador sugeriu fornecer as últimas três versões relevantes ao revisor.
Snapshots/diffs do código podem registrar conteúdo e grafos correspondentes podem
ajudar a comparar dependências. O grafo isolado não preserva todo o conteúdo nem
prova equivalência de comportamento. Definir estado, referências de versões,
renomes e escopo é necessário antes de implementar captura automática.
