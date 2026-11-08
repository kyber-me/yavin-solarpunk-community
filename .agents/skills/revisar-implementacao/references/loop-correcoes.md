# Loop de correções — versão 1

**Natureza:** decisão operacional do harness, 08/11/2026.

## Papéis e entrada

O agente que recebe esta skill atua como coordenador, revisor ou executor,
conforme o papel explícito do pacote. Somente o coordenador chama agentes e
escreve o controle do loop. O revisor produz o parecer e retorna; o executor
corrige e retorna. Nenhum filho cria outro agente ou reinicia o ciclo.

O coordenador lê esta referência antes de qualquer chamada. Requer classificação,
plano, entrega identificada e autorização explícita do Idealizador cobrindo as
correções dentro do escopo. Aprovar uma revisão, solicitar uma revisão ou aprovar
um plano sem correções previstas não concede autorização automática para corrigir.
Sem cobertura clara, prepare a proposta concreta e aguarde.

Esta referência é um protocolo executado pelo agente com ferramentas de colaboração,
não um serviço ou runner autônomo. Se não houver ferramentas de delegação ou
persistência disponível, informe o impedimento; não finja uma chamada realizada.

## Identidade e rastreabilidade

- `task_id`: identidade estável do objetivo.
- `implementation_id`: ULID puro novo para cada entrega/tentativa.
- `parent_implementation_id`: ID da tentativa anterior; null na inicial.
- `review_id`: ULID novo para cada relatório, associado à implementação examinada.
- Classificação e plano são versões da tarefa. Referencie os arquivos exatos
  em cada controle, sem duplicá-los nem inventar um ID de implementação anterior
  à sua existência.
- Use a versão 2 de [revisao.schema.json](revisao.schema.json) para novas revisões
  do loop. A versão 1 permanece válida para relatórios históricos e revisões
  avulsas; sem vincular inequivocamente uma revisão à entrega, não acione correção.

Gere ULIDs com biblioteca já disponível, por exemplo `from ulid import ULID`.
Não altere dependências da aplicação para registrar IDs do harness.

## Limite ratificado

Máximo de **três tentativas com revisão por tarefa**: entrega inicial, primeira
correção, segunda correção. Não são três correções além da inicial. O contador
é por tarefa e não é zerado por novo agente, plano, dia, ID ou reclassificação.

Reserve a tentativa e registre o controle ANTES de delegar. Falhas técnicas não
autorizam chamadas ilimitadas: não repita automaticamente uma chamada que falhou
ou tenha resultado desconhecido. Pare como impedido; eventual retomada exige
reconciliar agentes ativos e registros para evitar duas execuções da mesma entrega.

Uma tentativa é reservada mesmo se seu executor falhar. Uma revisão técnica
concluída gera um relatório. Se o revisor falhar, o coordenador preserva a reserva
e registra impedimento; não cria um parecer fictício ou uma quarta chamada.
Não há chamadas adicionais automáticas para debater contestações. Divergência
não resolvida vai ao Idealizador.

## Registro de controle

Antes e depois de cada transição, salve um novo `loop-001.json`, `loop-002.json`
etc. no diretório da tarefa, pelo [schema](loop.schema.json). São eventos imutáveis;
não sobrescreva o anterior. `anterior_ref` aponta ao evento imediatamente anterior.
O primeiro evento tem null e inclui a tentativa inicial já entregue para revisão.

Mantenha um único coordenador escritor. Antes de retomar, percorra todos os eventos,
confira sequência, IDs, task_id e contadores. Evento incompleto, duas cadeias,
chamada pendente ou registro inválido impedem nova delegação até reconciliação.
Nunca reutilize um ID para código diferente. Registre hashes por arquivo e a
fonte de evidência da execução; nova entrega é um novo ID/snapshot.

Estados: `aguardando_revisao`, `aguardando_executor`, `aprovado_tecnicamente`,
`aguardando_idealizador`, `impedido`.
Não use aprovação técnica para representar revisão humana ou autorização.

## Decisão após o parecer

1. Valide relatório, IDs, critérios, hashes e versão do plano. Se o código mudou
   desde o snapshot, não aplicar feedback cegamente: registre impedimento e
   apresente a reconciliação necessária.
2. `aprovar`: registre aprovado tecnicamente e encerre o loop de correções.
   Aplique [relatar-implementacao](../../relatar-implementacao/SKILL.md) para gerar
   o relatório final da entrega aprovada. Falha ao gerar o relatório não reabre
   correções nem cria outra tentativa: informe a pendência documental.
   Melhorias opcionais não disparam executor automaticamente.
3. `inconclusiva`: registre impedimento com evidências ausentes; não execute
   correção com base em defeito presumido.
4. `solicitar_correcoes`: confirme bloqueios/requisitos não atendidos.
   Se precisar extrapolar escopo, houver contestação não resolvida ou já existirem
   três tentativas, registre aguardando Idealizador e pare.
5. Se houver autorização e orçamento, reserve novo implementation_id ligado ao
   anterior, grave aguardando executor e invoque executor com contexto novo
   (`fork_turns: "none"` quando disponível). Use o pacote abaixo.
6. Aguarde o executor; confira seu relato, diff e testes. Falha/interrupção ou
   resultado inconsistente encerra em impedimento. Ao concluir, registre os hashes
   e evidências da entrega; grave aguardando revisão e chame um revisor em contexto
   novo. Repita a decisão, sempre com o mesmo contador.

Se atingir o limite, preserve pendências e evidências, sem declarar sucesso.
Novas rodadas só após decisão explícita do Idealizador e revisão do protocolo;
o teto deste schema não é ampliado silenciosamente.

## Pacote mínimo para o executor

Inclua task_id, novo implementation_id e parent, versões de classificação/plano,
objetivo e restrições, referência exata da autorização, critérios e seu estado,
relatório do revisor e achados bloqueantes, snapshot/diff da entrega e tentativas
restantes. Forneça resumo factual curto, com links para os registros completos.
O resumo é derivado, não substitui evidências. Não incluir segredos ou histórico
completo da conversa. Grafos/snapshots anteriores só quando disponíveis;
a captura automática das últimas três versões ainda não foi implementada.

Instrua o executor:
- conferir o snapshot antes de editar, preservando alterações compartilhadas;
- corrigir somente o escopo autorizado e executar validações pertinentes;
- responder por achado: corrigido (com arquivos e validações), contestado (com
  evidência) ou adiado (apenas não bloqueante); nunca marcar corrigido sem evidência;
- não apagar perguntas/comentários autorais sem autorização, alterar contratos
  ou dependências fora do plano, chamar modelos/banco sem cobertura explícita;
- não delegar nem iniciar outra revisão; retornar ao coordenador com resumo,
  arquivos alterados, hashes e evidências de execução.

A resposta é salva pelo coordenador como `resposta-revisao-NNN.md`, vinculando IDs
e relatório. Este incremento não define schema de respostas nem execucao.json.
