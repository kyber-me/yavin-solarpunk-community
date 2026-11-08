# Backlog de Yavin

**Atualizado em:** 08 de novembro de 2026
**Natureza:** acompanhamento e planejamento de desenvolvimento.
**Estado:** pendências e prioridades sugeridas para o MVP; não define arquitetura definitiva.

Pendências ficam no início, por prioridade; entregas concluídas ficam no final.
Ponto de retomada: [estado atual](dev/retomada-2026-11-08.md). Servidores parados;
autorizações anteriores consumidas. A prioridade foi redirecionada em 08/11/2026
para o método de desenvolvimento agêntico, conforme o registro abaixo.

## Frente atual — método de desenvolvimento agêntico

**Natureza:** desenvolvimento do processo de delegação no backend; separado dos agentes da simulação.
[Registro e limites](dev/metodo-desenvolvimento-agentico-2026-11-08.md).

- [ ] **Calibrar a classificação em tarefas reais.** Usar a rubrica de complexidade
  e risco, verificar justificativas e ajustar quando houver evidência de classificação
  inadequada. A validação estrutural da skill não comprova qualidade das notas.
- [ ] **Avaliar a utilidade do Graphify na classificação real.** Grafo estrutural
  do backend gerado e consulta de `ChatService` conferida; calibrar sua contribuição
  em tarefas concretas. Frontend está fora do recorte inicial. Atualidade deve ser
  conferida pelos hashes dos arquivos, incluindo mudanças locais.
- [ ] **Validar o planejamento em uma nova tarefa.** A skill e o schema estão
  disponíveis; o primeiro plano documenta retrospectivamente a migração. Conferir
  utilidade de fases, subtarefas, critérios e dependências num registro anterior
  à implementação, incluindo o estado real do modo Plan.
  Após salvar a classificação, aguardar mudança de modo e OK para iniciar o
  protocolo; depois do plano concreto, obter aprovação separada para execução.
- [ ] **Definir cadeia de estados para revisão.** Proposta do Idealizador:
  disponibilizar as últimas três versões relevantes ao revisor. Delimitar o que
  constitui estado (implementação ou rodada), registrar snapshots/diffs de código
  e grafos correspondentes, sem confundir mudança estrutural com comportamento.
  Não há captura automática ou histórico completo de código implementado ainda.
- [ ] **Validar o loop em execução delegada real.** Diretrizes, eventos e IDs
  definidos na skill revisora; falta exercitar correção autorizada com executor,
  nova revisão e contador central, sem confundir contrato com runner autônomo.
- [ ] **Validar relatório final em entrega nova e construir a interface.** Skill
  e schema definidos; experimentar o resumo dos arquivos, fases, anotações,
  validações e fluxo opcional. Persistência da revisão humana ainda pendente.
- [ ] **Definir os próximos contratos do harness.** Roteamento de modelos segue pendente.
  Definir também schemas e persistência de `autorizacao.json` e `execucao.json`;
  essas categorias ainda não estão implementadas.

## P0 — Executar e validar o núcleo

- [ ] **Atualizar os testes legados de checkpoints após a reorganização.**
  `backend/tests/test_chat_checkpoint.py` ainda importa `TextMessage` removido, aponta mocks
  para `src.agents.agent.py.create_agent` e trata `_retrieval_knowledge` como método
  em vez de função do módulo. Corrigir sob autorização e validar sem modelo externo.
  A bateria integrada recente cobre persistência e retomada, mas não permite
  declarar a suíte global aprovada enquanto esses testes estiverem desatualizados.

- [ ] **Definir falhas e novas tentativas no chat.** Entrada e resposta já são
  persistidas, com autoria, UTC e verificação de participação. A entrada é mantida
  se o agente falha. Definir tratamento de reenvios e divergência entre mensagens
  e checkpoints, incluindo falha ao salvar a resposta após sucesso do modelo;
  revisar classificação de erros internos sem manter transação durante a chamada.

- [ ] **Completar a validação de uso conversacional pela SPA.** Dois turnos reais
  por HTTP já confirmaram contexto após reabrir as conexões; quatro mensagens
  persistidas foram recuperadas pela interface após recarregar. Retomada por `409`
  e exclusão de histórico local verificadas no navegador. Falta validar envio real
  a partir da SPA e realizar as perguntas de referência de Silas; QA do compositor
  desta rodada usou resposta controlada para não gerar novas chamadas ao modelo.
  Evidência em `dev/local/silas_test_responses`.

- [ ] **Concluir a revisão dos campos temporais de chat.** O `Message` atual exige
  timestamps com fuso e cria em UTC; seu registro persiste essas datas. O registro
  de conversa também cria em UTC. Restam alinhar modelos legados e o campo
  `updated_at` da conversa, que ainda não faz parte das operações SQL atuais.

- [ ] **Disponibilizar o documento de pesquisa no contexto de Silas.** O documento
  está em `backend/src/agents/base_knowledge/projeto/PROJETO_DE_PESQUISA_YAVIN.md`, categoria
  ainda não lida pelo carregador. O Idealizador deverá definir sua inclusão como
  orientação de projeto, preservando a distinção entre propósito, referência,
  hipótese e decisão. Concluído quando Silas puder reconhecer a pergunta central,
  a razão do início quase vazio e os limites de inferência da simulação.

- [ ] **Concluir a documentação de execução reproduzível.** O README já descreve
  instalação com `uv`, variáveis mínimas e comandos da API e do frontend. Falta
  disponibilizar `.env.example` sem credenciais reais, alinhar os passos à criação
  persistida e à aplicação explícita da migração e verificá-los em ambiente novo.
  Esclarecer que o `backend/main.py` é um entrypoint provisório da API.

- [ ] **Tornar falhas de contexto e execução explícitas.** Hoje pastas ausentes são
  ignoradas e falhas de recuperação documental podem resultar em contexto vazio. Definir quais documentos
  são obrigatórios e apresentar falhas de leitura, configuração e API de forma clara,
  preservando a causa do erro. Concluído quando a execução não aparentar sucesso sem
  contexto obrigatório ou sem resposta.

- [ ] **Validar o comportamento de Silas com perguntas de referência.** Verificar
  identidade, propósito de Yavin, primeira investigação e distinção entre proposta e
  decisão. Incluir uma pergunta sobre algo ainda indefinido, como localização. Guardar
  perguntas e resultados em `dev/local/silas_test_responses`. Concluído quando Silas
  demonstrar contexto correto e reconhecer o que permanece aberto.

## P1 — Sustentar uma investigação curta

- [ ] **Delimitar o primeiro incremento de orquestração com o Idealizador.**
  Em 08/11/2026, esta frente foi adiada em favor do método de desenvolvimento agêntico.
  Preferência expressa no encerramento de 07/11/2026: dedicar mais atenção à lógica
  de orquestração agora que o chat está integrado. Revisar `Agent.invoke`, identificar
  um objetivo pequeno e combinar entradas, saídas e critério de parada antes de
  implementar. Não presume múltiplos agentes nem autonomia. Próximo passo sugerido,
  sem autorização de código em aberto.

- [ ] **Revisar a vida útil do checkpointer na inspeção LangGraph/LangSmith.**
  O caminho em `backend/langgraph.json` foi corrigido na migração para
  `backend/src/agents/langsmith/agent_factory.py`. O grafo retornado pela factory usa um
  checkpointer fechado ao sair do contexto. `backend/src/main.py` tem execução de modelo
  no corpo do módulo; não usar como teste de import sem avaliar seus efeitos.
  Corrigir apenas se necessário ao próximo exercício e após autorização.

- [ ] **Implementar a recuperação de cidadãos e lugares conforme a necessidade.**
  O catálogo mínimo necessário à conversa com Silas faz parte da integração P0.
  A recuperação geral de `citizens` e `places` fica para depois: começar pelos
  JSONs de `backend/src/infra/` e preservar a separação entre domínio e persistência,
  sem bloquear a primeira validação do agente com modelagem geral de lugares.

- [ ] **Aprofundar os mecanismos de classe em Python.** Natureza: planejamento
  de estudo do Idealizador, registrado em 07/11/2026 a partir das dúvidas sobre
  os serviços. Revisar herança, métodos de instância, `classmethod`, `staticmethod`,
  `ABC` e `abstractmethod`; distinguir declaração da classe, instanciação e chamada
  de métodos. Entender os limites da imposição de contratos em execução e da análise
  estática com Pyright/Pylance, incluindo assinaturas e métodos assíncronos.
  Explorar `__init_subclass__` como alternativa, avaliando sua necessidade antes de
  adotá-lo. Concluído quando o Idealizador conseguir explicar essas diferenças e
  justificar o modelo dos serviços com pequenos exemplos. Aprofundar também a
  distinção entre Record como papel de dados e BaseModel como ferramenta de validação,
  usando o adaptador de mensagens como exemplo, sem exigir modelos duplicados.
  Estudo acompanhado por
  mentoria; não autoriza alterações no backend.

- [ ] **Consolidar os encaminhamentos desta sessão em memória institucional.**
  Registrar as orientações de pesquisa e decisões pertinentes à comunidade em
  uma nova ata, distinguindo-as das entregas técnicas já descritas neste backlog.
  Preservar os registros da fundação; uma eventual conversa editorial deve declarar
  sua natureza e não inventar falas. Ainda não há esse novo registro na base agêntica.

- [ ] **Estudar e aplicar arquitetura hexagonal conforme a necessidade.** Revisar
  rapidamente portas, adaptadores e limites de dependência e aplicar somente as
  separações necessárias ao fluxo que estiver sendo implementado, sem introduzir
  uma arquitetura definitiva prematuramente.

- [ ] **Desacoplar `Citizen` da implementação da lógica agêntica.** Separar o
  conceito de cidadão do adaptador responsável por LangChain/LangGraph, preservando
  uma porta estável para invocação, identidade, contexto e estado da conversa.
  A implementação concreta atual se chama `Agent`; a renomeação, por si só, não
  comprova esse desacoplamento.

- [ ] **Selecionar e identificar o contexto documental.** Avaliar a identificação de
  origem e natureza dos documentos em `backend/src/agents/base_knowledge/`; carregar os arquivos em ordem
  estável e distinguir instruções de identidade, referências e registros históricos.
  Os arquivos de suporte ao desenvolvimento na raiz não devem ser enviados
  automaticamente aos agentes da simulação. Leitura direta de Markdown é suficiente
  nesta etapa.

- [ ] **Limpar a saída do terminal.** Mostrar a resposta legível e reservar instruções
  completas, mensagens internas e resultados brutos para um modo de depuração.
  Concluído quando uma conversa comum puder ser acompanhada sem ruído técnico.

- [ ] **Realizar a primeira investigação sobre energia.** Escolher uma pergunta
  pequena, registrar referências, hipótese, incertezas e próximo experimento. Salvar
  o resultado em Markdown revisado pelo Idealizador. Concluído quando houver um
  registro útil para retomar o trabalho; não exige banco de dados ou escrita autônoma.

## P2 — Evoluir após a validação

- [ ] **Revisar a proposta de especialização de Silas por ciclos finitos de estudo.**
  Natureza: proposta para revisão futura, registrada em 05/11/2026; não autoriza
  execução nem alteração da identidade. Dar a Silas espaço para escolher uma
  especialidade útil a Yavin, justificando sua contribuição e mantendo a escolha
  provisória e revisável. O ciclo proposto tem início, meio e fim: triagem de áreas
  e materiais, escolha de uma pergunta delimitada, estudo, síntese e encerramento.
  O conhecimento produzido poderá compor uma biblioteca especializada consultável,
  com fontes, interpretações, incertezas e limitações identificadas. Antes de executar,
  revisar ativação pelo Idealizador, orçamento, teto de chamadas totais ao modelo
  (incluindo intermediárias e tentativas), quantidade de fontes e critérios de parada.
  Uma pergunta por ciclo, até três áreas candidatas e até seis fontes são sugestões
  iniciais, não limites aprovados. Encerrar por entrega, limite atingido ou impedimento,
  registrando resultado parcial quando necessário; sem extensão ou novo ciclo automático.
  Avaliar depois uma orientação estável em `backend/src/agents/prompts/IDENTIDADE_ID_SILAS.md` e um
  plano de execução separado. Implementação do backend permanece com o Idealizador.

- [ ] **Definir o centro da área de trabalho e um possível menu.** Avançar uma parte
  de cada vez com o Idealizador; não usar o mockup anterior como autorização para
  implementar toda a plataforma. Memória institucional navegável permanece uma possibilidade.

- [ ] **Adicionar uma ferramenta útil à investigação.** Escolher a capacidade a
  partir do primeiro estudo de energia. As ferramentas `common` e `test` atuais
  apenas confirmam disponibilidade; não realizam pesquisa ou simulação.

- [ ] **Ampliar a fundamentação e elaborar o manifesto autoral de Yavin.** Usar os
  estudos e as investigações para propor princípios e prioridades ao Idealizador.
  O manifesto solarpunk existente permanece uma referência de estudo.

## Futuro — Fora do MVP

- **Possibilidade de visão interna para cada `place` clicável.** Ao acessar um
  lugar pelo mapa, apresentar uma representação de seu interior junto ao conteúdo
  da página aberta por aquele componente. Natureza: hipótese de experiência
  sugerida pelo Idealizador em 05/11/2026, sem compromisso de implementação.
  Composição, formato visual, interação e relação entre interior e conteúdo
  permanecem abertos; avaliar a partir de um lugar concreto, como o laboratório.
- Expansão do mapa além da estação, novas construções e eventual engine espacial.
- Simulação energética e integração com dados ambientais reais.
- Voz, execução de múltiplos agentes e iniciativa autônoma do laboratório.
- Possibilidade de enviar comandos pelo chat e acompanhar efeitos no mapa, por
  exemplo com um agente Engenheiro. Direção de produto sugerida pelo Idealizador;
  contrato de comandos, execução e aprovação permanecem abertos.
- Alterações autônomas no mundo persistente e fluxos completos de deliberação.
- Modelos de economia e governança da comunidade.
- Infraestrutura de produção, autenticação e operação multiusuário.
- Busca vetorial/RAG, banco de memória ou orquestração adicional, caso o uso justifique.

## Recorte do MVP

Validar Silas como colaborador de investigação: conversar com contexto de Yavin,
distinguir referências, hipóteses, propostas e decisões, e ajudar a formular um próximo
passo verificável sobre energia. Uma interface de terminal é suficiente para essa
primeira validação. A concepção visual pode avançar em paralelo, conforme a direção registrada em
[AGENTS.md](AGENTS.md).
O ciclo visual já foi entregue e recebeu avaliação positiva: identidade editorial,
mapa com estação científica, modo expandido, chat em drawer e representação de Silas.
Catálogo, criação persistida de conversas e consultas de histórico estão integrados
entre API e frontend. A interface exibe apenas conversas e mensagens do banco;
rascunhos ficam em memória. Dois turnos reais por HTTP confirmaram continuidade
após reabrir as conexões, e o histórico foi recuperado pela SPA após recarregar.
Ainda faltam validar o envio real pelo compositor e as perguntas de referência de
Silas. Reuniões estão bloqueadas até haver persistência.

Prioridades:

- **P0:** necessário para uma execução confiável e uma validação básica do agente.
- **P1:** necessário para tornar o ciclo de investigação útil e repetível.
- **P2:** evolução após validar o núcleo do MVP.
- **Futuro:** fora do escopo inicial, sem compromisso de implementação.

## Estado atual e próximas prioridades

**Natureza:** diagnóstico e planejamento sugerido, revisados em 08/11/2026;
não definem novas decisões técnicas da simulação.

A preparação de versionamento parte de `d9f1f31`, com alterações compartilhadas
de persistência ainda não commitadas da rodada anterior. A rodada atual agrupa
backend/migração, frontend, harness e documentação em commits por escopo; consultar
`git log`/`git status` para os hashes e arquivos remanescentes, sem presumir árvore limpa.

Chat, catálogo, criação, tratamento 409/422 e consultas de histórico estão
integrados. A única migração inicial foi aplicada no banco do projeto preservando
os 15 checkpoints anteriores; dois turnos reais confirmaram contexto após reabrir
as conexões. O frontend recupera exclusivamente registros do banco. Os oito testes
do frontend, build e baterias específicas do backend passaram; a suíte global não
foi declarada aprovada e tem testes legados desatualizados.

API e Vite foram encerrados a pedido do Idealizador; portas 8000 e 5173 livres.
Não reiniciar, executar modelos ou modificar backend apenas por retomar a sessão.
Não há implementação já autorizada para a próxima etapa.

1. Ler o [ponto de retomada](dev/retomada-2026-11-08.md) e preservar o chat funcional.
2. Delimitar a próxima tarefa do harness, com prioridade na cadeia de estados
   e no exercício real do protocolo. Orquestração de Silas foi adiada.
3. Completar, quando solicitado, o envio real pela SPA e as perguntas de referência.
4. Disponibilizar a orientação de pesquisa ao agente sob autorização e formular
   a primeira investigação pequena de energia. Não assumir arquitetura multiagêntica.

### Validação do frontend — 07/11/2026

Antes desta atualização, `npm test` e `npm run build` foram repetidos. A execução
padrão voltou a falhar com `SecItemCopyMatching failed -50`; o Vite também encerrou
com falha de segmentação. O Node 25.2.1 indicava uso do repositório de certificados
do sistema. Com a opção temporária abaixo, os seis testes de contrato passaram e
o build completo (TypeScript e Vite) foi concluído:

```sh
cd frontend
NODE_OPTIONS='--use-bundled-ca --no-use-system-ca' npm test
NODE_OPTIONS='--use-bundled-ca --no-use-system-ca' npm run build
```

Nenhuma configuração ou dependência foi alterada. A opção usa os certificados
incluídos no Node, mantendo a verificação TLS. A causa específica da falha de
acesso ao Keychain não foi investigada além dessa comparação. Os testes usam
respostas controladas; esta validação não comprova integração real com a API e
não incluiu nova inspeção no navegador.

## Entregas e correções já realizadas

- [x] **Preparar relatório final após aprovação técnica.** Skill local
  `relatar-implementacao`, schema de `relatorio-final.json` e transição a partir
  do loop aprovado. IDs e snapshot vinculam arquivos alterados, fases, critérios,
  validações, anotações e fluxo funcional opcional. Revisão humana começa pendente.
  Não constrói interface nem reescreve relatórios históricos.
  [Registro](dev/relatorio-final-harness-2026-11-08.md).

- [x] **Definir coordenação limitada de correções na skill revisora.** Diretrizes
  de três tentativas totais, IDs por implementação/revisão, eventos imutáveis e
  autorização explícita antes de delegar executor. Schema de revisão v2 preserva
  v1 histórica. Revisor e executor retornam ao coordenador sem recursão.
  [Protocolo](.agents/skills/revisar-implementacao/references/loop-correcoes.md).

- [x] **Aplicar o revisor independente à migração real.** Agente em contexto novo
  produziu `revisao-001.json`: parecer `aprovar`, cinco critérios atendidos e uma
  ressalva documental não bloqueante. Comparação própria de OpenAPI, testes,
  snapshot e grafo; limites da base Git registrados. O implementador aceitou R1
  e corrigiu o texto da pendência da factory neste backlog, sem alterar backend.
  [Relatório](dev/harness/2026-11-08/005655-migracao-backend/revisao-001.json) e
  [resposta](dev/harness/2026-11-08/005655-migracao-backend/resposta-revisao-001.md).

- [x] **Criar o protocolo do revisor independente.** Skill local
  `revisar-implementacao`, fontes primárias de Fowler/Google e categoria
  `revisao-NNN.json`. Entrada após execução, isolamento de contexto, snapshot por
  hashes, achados localizados e critérios de aceite. Não altera backend nem
  implementa loop/roteamento automático. Validada em fixture com subagente de
  contexto novo: dois defeitos de contrato detectados apesar dos testes básicos
  aprovados, sem edição de código. Schema e referências conferidos.
  [Registro](dev/revisor-harness-2026-11-08.md).

- [x] **Persistir planejamento por fases no harness.** Em 08/11/2026: skill local
  `planejar-tarefa`, JSON Schema e categoria `planejamento.json` por tarefa, com
  fases, subtarefas, dependências, arquivos e critérios verificáveis. Níveis 3 a 5
  exigem decomposição. Registro da migração marcado retrospectivo e modo Plan não
  utilizado. Replanejamentos preservam versões anteriores. Não implementa runner,
  revisão adversarial ou interface. [Organização](dev/harness/README.md).
  Refinamento posterior: após classificar, sugerir mudança para Plan e aguardar
  OK antes do protocolo; solicitar autorização de execução para o plano concreto.

- [x] **Migrar o projeto Python para `backend/` e persistir classificações.**
  Em 08/11/2026, sob autorização: código, testes, configurações e estado local
  movidos; ambiente recriado pelo lock; caminhos ativos e grafo atualizados.
  OpenAPI idêntico e mesmos resultados da bateria sem banco. Registros JSON
  datados e schema da classificação adicionados para o harness.
  [Verificações e limites](dev/migracao-backend-2026-11-08.md).

- [x] **Gerar o grafo estrutural do backend com Graphify.** Em 08/11/2026:
  reaproveitada instalação isolada `graphifyy==0.9.71`, adicionado parser SQL
  `tree-sitter-sql==0.3.11`. Analisados 36 arquivos Python/SQL, incluindo testes:
  268 nós, 632 relações e 13 comunidades na saída agrupada. JSON, relatório e HTML
  locais em `dev/graphs/backend/`, ignorados pelo Git; reprodução e limites em
  [dev/graphs/README.md](dev/graphs/README.md). Consulta de `ChatService` verificada.
  Skill restrita ao backend. Sem modelo, banco, API, alteração de dependências do
  projeto ou migração de diretórios.

- [x] **Criar a skill de classificação com apoio opcional do Graphify.** Em
  08/11/2026: `.agents/skills/classificar-tarefa/`, rubrica de complexidade e risco,
  nível pelo maior valor, resultado JSON e referência de análise de impacto.
  Inclui confirmação no código, atualidade do índice e fallback por busca/leitura.
  Nenhuma instalação ou indexação do Graphify e nenhuma alteração no backend.

Registros de conclusão preservados; pendências atuais estão nas seções iniciais.

### P0 — Executar e validar o núcleo

- [x] **Concluir integração persistida e eliminar históricos locais do frontend.**
  Autorização pontual em 07/11/2026: endpoints paginados de conversas por participante
  e mensagens com verificação de acesso, definidos no backend e consumidos pela SPA.
  Conversas e mensagens exibem apenas IDs e datas do servidor; sem leitura ou escrita
  de históricos/rascunhos em localStorage. A chave antiga é removida; rascunhos só
  em memória. Reuniões bloqueadas até persistência. Após envio, com sucesso ou erro,
  a interface consulta as mensagens gravadas, sem acrescentar mensagens provisórias.
  Migração inicial aplicada no banco configurado: 15 checkpoints preservados.
  Dois turnos reais com fechamento/reabertura de conexões, palavra-chave recuperada
  e quatro mensagens persistidas. 22 testes de persistência/HTTP, oito do frontend,
  build e análise de tipos da nova camada aprovados. No navegador: recarga, histórico
  local antigo invisível/removido, 409, reuniões bloqueadas e resposta não persistida
  nunca adicionada ao histórico. [Registro](dev/persistencia-frontend-2026-11-07.md).


- [x] **Consolidar o schema inicial e testar o fluxo HTTP integrado.** Em 07/11/2026,
  após o Idealizador confirmar que só há dados do checkpointer e nenhuma migração
  aplicada: quatro scripts intermediários substituídos por `001_initial_schema.sql`.
  Testes de migração legada substituídos pela verificação do schema final e
  preservação de checkpoints anteriores à criação de `yavin`. Quatro testes HTTP,
  oito de mensagens e nove de conversas aprovados em PostgreSQL descartável.
  Lifespan, pool, repositórios e checkpoints reais; grafo do modelo e contexto
  documental simulados. Retomada, isolamento, autoria, UTC, erros, conservação
  da entrada em falha e fechamento de recursos verificados. Sem acesso ao banco
  do projeto ou modelo externo. [Evidência](dev/validacao-http-2026-11-07.md).
  Referências às migrações anteriores nas entregas abaixo são históricas.

- [x] **Validar disponibilidade do participante na criação.** Autorização pontual
  em 07/11/2026: catálogo mínimo centralizado em `backend/src/services/agent_catalog.py`,
  compartilhado por `GET /agents` e pelo serviço de criação. ID indisponível retorna
  `422`/`AGENT_UNAVAILABLE` antes de gerar ULIDs ou acessar o repositório; comparação
  exata de IDs, sem normalização implícita. Fluxos `201` e `409` preservados.
  Oito testes do backend e seis do frontend aprovados, incluindo fonte compartilhada
  e rejeição sem efeitos. Análise de tipos dos módulos do catálogo e criação aprovada.
  Sem banco ou modelo reais; frontend e comentários existentes preservados.

- [x] **Disponibilizar GET /agents e habilitar GET no CORS.** Autorização pontual
  em 07/11/2026: catálogo mínimo tipado com apenas Silas, usando o identificador
  estável provisório `silas`; sem instanciar agente ou usar JSONs de rascunho como
  fonte oficial. CORS permite GET e POST nas duas origens locais já configuradas.
  Três testes novos cobrem resposta estável, preflight, acesso por origem permitida
  e rejeição de origem/método não configurados. Sete testes de regressão HTTP e
  seis do frontend aprovados; análise de tipos do contrato aprovada. Sem banco
  ou modelo reais; nenhuma alteração no frontend ou remoção de comentários.

- [x] **Tratar duplicidade de conversa ativa como HTTP 409.** Autorização pontual
  em 07/11/2026, após reorganizar este backlog: o serviço traduz somente
  `ActiveConversationExists` para `CONVERSATION_ALREADY_ACTIVE`, com ID, participante
  solicitado e data da conversa existente em `error.details`. O AppError e o
  handler transportam esses metadados; IDs de thread não são expostos. Criação
  continua com `201`. Três testes novos aprovados, inclusive dupla invertida e
  erro de outro índice; sete testes de regressão do chat e seis do frontend
  aprovados. Análise de tipos do serviço de criação e AppError aprovada. Sem acesso
  a banco ou modelo nesta etapa. Comentários do Idealizador preservados.

- [x] **Preparar infraestrutura PostgreSQL e frontend para criação de conversas.**
  Entrega de desenvolvimento em 07/11/2026: pool limitado, repositório concreto,
  lookup simétrico, migração SQL e testes em PostgreSQL descartável. Frontend busca
  agentes pela API, cria antes de enviar, trata `409` e preserva registros locais
  anteriores para consulta. [Plano completo](dev/plano-persistencia-conversas.md)
  e [guia da infraestrutura](backend/src/infra/db/relational/README.md). Testes de contrato
  no frontend usam respostas controladas; seis testes e build revalidados conforme
  registro acima. A entrega não aplicou migração no banco do `.env`; serviços,
  entidades, DTOs e rotas ficaram a cargo do Idealizador e estão em edição local.

- [x] **Atualizar rotas do frontend e simplificar a restrição de conversa ativa.**
  Incremento autorizado em 07/11/2026: frontend usa `/conversation/create` e
  `/conversation/talk`. A migração `002_active_conversation_pair.sql`, após a `001`,
  substitui a lookup persistida por índice único parcial da dupla normalizada com
  `LEAST`/`GREATEST` e `WHERE active`. Registro, repositório e construção do registro
  no serviço de criação foram adaptados. Comentários do Idealizador preservados.
  Seis testes do frontend, build, nove testes de infraestrutura (oito em PostgreSQL
  descartável) e análise de tipos da infraestrutura aprovados. A suíte verifica
  corrida, inversão de dupla inclusive por SQL direto, rollback e histórico inativo.
  Nenhuma migração aplicada ao banco do projeto; nenhuma chamada ao modelo.

- [x] **Restabelecer o carregamento da API pela raiz — primeira etapa.**
  Autorização pontual do Idealizador em 07/11/2026: corrigidos os três imports
  `infra...` para `src.infra...` no serviço de chat. Verificados `import main`,
  geração do schema OpenAPI e presença das rotas de criação e chat, sem executar
  lifespan, acessar banco ou chamar o modelo. Comentários preservados. Essa
  verificação não valida requisições; a próxima etapa depende de nova aprovação.

- [x] **Alinhar payload e passagem de Request — segunda etapa.**
  Autorização pontual do Idealizador em 07/11/2026: `ChatServiceRequest.message`
  recebe texto, conforme o frontend; o serviço cria `Message` no servidor antes
  da adaptação, gerando ID e datas próprios. A rota entrega o `Request` ao serviço
  no threadpool. Três testes novos aprovados sem lifespan, banco ou modelo:
  payload HTTP, repasse do Request, rejeição de metadados no lugar do texto e
  criação do modelo antes da adaptação. Seis testes do frontend e análise de tipos
  do DTO aprovados. Comentários preservados; execução integral do chat ainda pendente.

- [x] **Corrigir autoria, UTC e preservação de AppError — terceira etapa.**
  Autorização pontual do Idealizador em 07/11/2026: resposta atribuída ao outro
  participante persistido da dupla, nas duas ordens possíveis; timestamp padrão
  de `MessageRecord` em UTC; `AppError` propagado sem tradução pelos dois níveis
  de tratamento. Três testes novos e seis testes de regressão sem banco aprovados;
  análise de tipos do registro aprovada. Os cinco testes PostgreSQL de mensagens
  não foram repetidos nesta etapa. Sem acesso a banco ou modelo; comentários
  preservados. Autorização e atividade da conversa continuam pendentes.

- [x] **Validar participação e atividade antes da gravação — quarta etapa.**
  Autorização pontual do Idealizador em 07/11/2026: conversa inexistente retorna
  `404`/`CONVERSATION_NOT_FOUND`; remetente informado fora da dupla retorna
  `403`/`CONVERSATION_FORBIDDEN`; conversa inativa retorna
  `409`/`CONVERSATION_INACTIVE`. Participação é verificada antes da atividade.
  As verificações precedem criação, adaptação e persistência de mensagens e chamada
  ao agente. Sete testes de contrato e serviço aprovados, incluindo quatro cenários
  HTTP de rejeição sem efeitos e regressão de autoria nas duas ordens da dupla.
  Sem banco ou modelo reais. Não implementa autenticação do remetente informado.

- [x] **Padronizar IDs persistidos como ULID sem prefixo.** Decisão autorizada em
  07/11/2026: revisadas conversas e mensagens, as duas entidades com tabelas próprias.
  A geração já usava ULID puro; a migração `004` remove prefixos legados, atualiza
  referências e impõe ULID canônico nas chaves primárias. Não altera threads nem
  referências provisórias de participantes. Testes atualizados: 20 aprovados em
  PostgreSQL descartável, incluindo conversão de dados, vínculos e rollback em
  colisões ou valores inválidos. Migração não aplicada ao banco do projeto.
  Atualizar referências externas antigas após aplicação; não há alteração automática
  do armazenamento do navegador. Migrações históricas preservadas.

- [x] **Criar a camada simples de persistência de mensagens.** Incremento autorizado
  em 07/11/2026: `Message` Pydantic com datas com fuso, `MessageRecord`, adaptação
  explícita nos dois sentidos e repositório síncrono para criar, buscar por ID e
  listar por conversa com limite. Migração `003` cria tabela, vínculo com conversa
  e índice de histórico. Reutiliza o pool com row factory específica por cursor.
  Oito testes de mensagens, nove de regressão de conversas e análise de tipos
  aprovados. PostgreSQL descartável; nenhum acesso ao banco do projeto ou ao modelo.
  [Guia e limites](backend/src/infra/db/relational/MESSAGES.md).

- [x] **Manter os checkpoints de Silas em PostgreSQL.** Revisão de desenvolvimento
  em 06/11/2026: `PostgresSaver` compartilhado durante o ciclo de vida da API,
  `setup()` na inicialização e fechamento na parada. Recuperação confirmada após
  fechar e reabrir a conexão, usando grafo de teste sem chamada ao modelo; thread
  temporária removida. Contexto documental inicial não é repetido a cada turno.
  Naquela entrega foram corrigidos os construtores Pydantic que bloqueavam o chat
  e passou a ser aceita a mensagem simples enviada pelo frontend. Três testes automatizados e
  build aprovados à época; esse resultado não valida as alterações locais posteriores.
  O histórico do grafo é persistente; `CHAT_CACHE` e entidades do domínio continuam
  em memória. A validação conversacional real com Silas permanece pendente.

- [x] **Recuperar a base documental ausente após a reorganização.** Os cinco
  documentos foram recuperados em `backend/src/agents/base_knowledge/`, usando cópias
  anteriores, mensagens de contexto em `dev/local/messages.pretty.json` e registros de
  leitura/criação das sessões. Origem e ajustes documentados em
  [`dev/recuperacao-memoria-2026-11-05.md`](dev/recuperacao-memoria-2026-11-05.md).
  A inclusão de `projeto/` no carregador permanece uma tarefa separada.

- [x] **Resolver caminhos a partir dos arquivos do projeto.** A classe concreta em
  `backend/src/agents/agent.py` resolve a raiz com base em `__file__` e carrega a
  base de conhecimento comunitária a partir de `backend/src/agents/base_knowledge/`. A identidade de
  Silas está em `backend/src/agents/prompts/IDENTIDADE_ID_SILAS.md`. Os arquivos de suporte ao
  desenvolvimento ficam na raiz (`AGENTS.md`, `README.md` e `BACKLOG.md`) e permanecem
  fora da base de conhecimento da simulação.

### P2 — Evoluir após a validação

- [x] **Aplicar a representação visual de Silas.** Após aceite do Idealizador,
  avatar pixelado amarelo integrado ao chat e figura estática transparente ao lado
  da estação. Clicar na figura abre a conversa individual no drawer. Ambos
  acompanham o mesmo personagem; documentos e originais em `frontend/sketches/silas/`.
  Build, teclado, câmera e apresentação em desktop e celular verificados.

- [x] **Registrar possibilidades para a modelagem de lugares.** As alternativas para
  identidade, tipo, estado, tamanho, posição e pertencimento a um espaço estão
  documentadas em
  [`dev/project/places-modeling-possibilities.md`](dev/project/places-modeling-possibilities.md).
  O documento é uma referência provisória e não define um contrato para
  `backend/src/infra/places.json`.

- [x] **Avaliar a identidade da segunda tentativa de redesign da SPA.** Implementada em 05/11/2026,
  com nova composição editorial, navegação lateral, mapa em módulo próprio, referência
  da oficina solar urbana e painel de conversa dividido entre diretório e histórico.
  Build e fluxos verificados no navegador. O Idealizador avaliou positivamente
  a força da identidade e solicitou o refinamento do mapa em modo expandido.
  Registro e capturas em [`frontend/sketches/redesign-oficina-v2.md`](frontend/sketches/redesign-oficina-v2.md).

### Marca ASCII do README

- [x] **Definir a marca ASCII de Yavin no README.** Composição aprovada pelo
  Idealizador em 05/11/2026: símbolo solar arredondado com raios ampliados ao lado
  do nome YAVIN. Sete linhas, até 63 colunas, apenas caracteres ASCII e bloco de
  código `text` para preservar a fonte monoespaçada. Caracteres, largura e ausência
  de tabs e espaços finais conferidos. Entrega registrada em commit dedicado.

### Entregas anteriores

- [x] **Versionar a base do projeto.** O repositório já possui histórico de commits,
  incluindo frontend, documentação, checkpoints e infraestrutura de conversas.
  A antiga pendência de primeiro commit foi encerrada nesta revisão; alterações
  locais em andamento continuam sem commit e não foram incluídas automaticamente.

- [x] **Transformar o README em apresentação pública do projeto.** Revisão editorial
  em 06/11/2026: propósito, orientação solarpunk, método, estágio do protótipo,
  tecnologias e execução local. Marca ASCII preservada e foto da oficina solar
  urbana incluída como referência visual. Instruções e recuperação documental
  permanecem em `AGENTS.md` e no registro de recuperação; detalhes e histórico
  visual foram concentrados em `frontend/README.md` e nos estudos já existentes.
  Pendências permanecem neste backlog. Não foi criado um README interno adicional.
  Descrições de persistência alinhadas ao checkpointer implementado; nenhum código
  ou configuração de backend foi alterado.

- [x] **Alinhar imports e caminhos à nova estrutura.** Imports ativos usam
  `src.agents.main` e `src.agents.tools`; identidade aponta para
  `backend/src/agents/prompts/IDENTIDADE_ID_SILAS.md`. Referências aos estudos visuais e
  arquivos de desenvolvimento foram ajustadas para `frontend/sketches/` e `dev/`.
  Base documental ausente registrada como pendência separada. Rascunhos comentados
  mantidos como referências históricas, sem reativação.

- [x] **Recuperar `backend/src/agents/prompts/IDENTIDADE_ID_SILAS.md` após exclusão.** Restaurada a
  última versão revisada disponível nesta conversa. O arquivo foi renomeado ou
  movido durante a revisão; alterações simultâneas do Idealizador foram preservadas.
  A validação pelo construtor foi impedida pelo import atual `agents.tools` ao
  importar o módulo pela raiz. Sem chamada ao modelo. Localização final e
  carregamento da identidade precisam ser conferidos após a reorganização.

- [x] **Recuperar `backend/src/agents/agent.py` após sobrescrita com as tools.** Restaurada
  a última implementação de `Citizen` lida nesta conversa; tools preservadas em
  `backend/src/agents/tools.py`. Raiz ajustada à localização atual do arquivo.
  Importação de `Citizen` e registro das tools conferidos sem chamar o modelo.
  A revisão dos imports antigos e a recuperação dos documentos ausentes permanecem
  fora desta restauração pontual.

- [x] **Restaurar o arquivo de tools do agente.** Recuperado de conteúdo lido
  anteriormente na conversa em `backend/src/agents/tools.py`, com `test`,
  `common`, `get_agent_state` e as listas usadas pelos imports atuais. Imports,
  registro e execução de `common` e `test` verificados sem chamada ao modelo.

- [x] **Revisar e renomear a identidade de Silas.** `IDENTIDADE.md` revisado, com
  referências documentais corrigidas e distinção entre projeto de pesquisa e
  referências culturais. Serviço de chat, execução direta de `Citizen` e `World`
  apontam para o novo arquivo. O caminho de `World` também foi corrigido para
  resolução a partir de `__file__`. Verificação estática de sintaxe e caminhos;
  sem chamada ao modelo.

- [x] **Documentar o objetivo da pesquisa de Yavin.** Criada a orientação técnica
  em `backend/src/agents/base_knowledge/projeto/PROJETO_DE_PESQUISA_YAVIN.md`: pergunta central,
  objetivos, justificativa do início quase vazio, questões de investigação, observação
  do processo e limites da simulação. Documento de entrada vinculado no README;
  inclusão no contexto do agente continua pendente.

- [x] **Gerar dois estudos visuais de Silas.** Avatar de chat e figura de mapa
  gerados com a ferramenta integrada de imagens, preservando a identidade visual
  entre as aplicações. Imagens, prompts e limites registrados em
  `frontend/sketches/silas/README.md`. Aplicações integradas após o aceite do Idealizador.

- [x] **Integrar o chat ao mapa como drawer recolhível.** Controle Conversar no
  mapa normal e expandido; painel acoplado no desktop e camada inferior no celular.
  Uma única instância mantém conversa selecionada, rascunhos e respostas em andamento
  ao navegar entre mapa e laboratório. Fechar ou Escape recolhe e devolve o foco.
  Build e fluxos verificados com respostas controladas; nenhuma ação de agente
  sobre o mapa foi implementada. Registro em `frontend/sketches/chat-drawer.md`.

- [x] **Adicionar modo expandido ao mapa.** Ocupa a área disponível, mantendo
  cabeçalho e navegação lateral. Controle Expandir/Recolher e saída com Escape.
  Expandido inicia em 65%; normal inicia e retorna em 100%. Os controles continuam
  livres após a troca. Acesso ao laboratório e retorno ao modo expandido preservados.
  Build e verificação no navegador em desktop, celular e paisagem concluídos.

- [x] **Implementar uma segunda proposta de redesign.** Página inicial, navegação e
  bancada de conversa recompostas a partir do prompt e da avaliação anterior. Rotas,
  dados locais, interação com o mapa e chamada individual a `POST /chat` preservados.
  Verificação com respostas controladas; execução real de Silas não validada nesta
  entrega. Implementação concluída não equivale à aprovação da direção visual.

- [x] **Aprovar a direção visual do laboratório.** Estação científica hexagonal v3,
  com cobertura facetada, claraboia e integração com vegetação.
- [x] **Implementar a primeira SPA.** React + TypeScript + Vite, conversas e reuniões
  locais, históricos e rascunhos persistidos no navegador.
- [x] **Integrar a entrada visual e refinar a navegação.** Arte transparente, acesso
  ao chat e retorno, mapa abaixo de todo o header, grid isométrico, panning limitado,
  feedback de grab e zoom de 65% a 100%. Legenda acompanha o edifício; seleção e arraste
  nativo bloqueados no mapa. Ciclo aprovado pelo Idealizador e verificado no navegador.

- [x] **Aplicar a identidade de Silas.** O construtor concreto recebe a identidade
  em `backend/src/agents/prompts/IDENTIDADE_ID_SILAS.md` por meio de `specialized_instructions_path`.
- [x] **Interromper a inicialização quando a leitura da identidade falhar.** O
  construtor agora propaga uma exceção, em vez de retornar com um objeto incompleto.
- [x] **Substituir a interface provisória.** A implementação concreta está em
  `backend/src/agents/agent.py`; `backend/src/interfaces/citizen.py` permanece documentado
  como obsoleto e não deve ser usado por código novo.

Essas correções foram conferidas no código. A validação integrada do agente continua
prevista em P0. A implementação do backend permanece sob responsabilidade do
Idealizador; este backlog registra trabalho, sem autorizar alterações adicionais.
