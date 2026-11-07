# Backlog de Yavin

**Atualizado em:** 07 de novembro de 2026
**Estado:** pendências e prioridades sugeridas para o MVP; não define arquitetura definitiva.

## Recorte do MVP

Validar Silas como colaborador de investigação: conversar com contexto de Yavin,
distinguir referências, hipóteses, propostas e decisões, e ajudar a formular um próximo
passo verificável sobre energia. Uma interface de terminal é suficiente para essa
primeira validação. A concepção visual pode avançar em paralelo, conforme a direção registrada em
[AGENTS.md](AGENTS.md).
O primeiro ciclo visual já foi implementado e aprovado: mapa com estação científica,
acesso ao chat, grid, panning limitado e zoom. Conversas individuais já chamam a API local, mas a validação real de Silas e a
continuidade entre requisições permanecem pendentes; reuniões ainda são locais.

Prioridades:

- **P0:** necessário para uma execução confiável e uma validação básica do agente.
- **P1:** necessário para tornar o ciclo de investigação útil e repetível.
- **P2:** evolução após validar o núcleo do MVP.
- **Futuro:** fora do escopo inicial, sem compromisso de implementação.

## Marca ASCII do README

- [x] **Definir a marca ASCII de Yavin no README.** Composição aprovada pelo
  Idealizador em 05/11/2026: símbolo solar arredondado com raios ampliados ao lado
  do nome YAVIN. Sete linhas, até 63 colunas, apenas caracteres ASCII e bloco de
  código `text` para preservar a fonte monoespaçada. Caracteres, largura e ausência
  de tabs e espaços finais conferidos. Entrega registrada em commit dedicado.

## Retomada sugerida — próxima sessão

**Natureza:** planejamento de desenvolvimento sugerido em 05/11/2026; não define
novas decisões técnicas da simulação.

O ciclo visual foi entregue: identidade reformulada, mapa expandido, chat em drawer
e Silas no chat e no mapa. A possibilidade de interiores de `places` está registrada
para o futuro. Esta sessão também deixa uma primeira orientação técnica da pesquisa.

1. Revisar o [projeto de pesquisa](src/agents/base_knowledge/projeto/PROJETO_DE_PESQUISA_YAVIN.md),
   especialmente a pergunta central e a distinção entre investigar a comunidade e
   investigar o processo de conversas e decisões.
2. Formular com o Idealizador uma primeira pergunta pequena sobre energia, explicitando
   apenas os parâmetros necessários; registrar o que for hipótese de cenário.
3. Com o Idealizador, disponibilizar a orientação de pesquisa ao agente e verificar
   continuidade de contexto entre mensagens. O código atual não carrega `projeto/`
   e o serviço cria uma nova instância de `Citizen` a cada requisição.
4. Executar as perguntas de referência e uma conversa curta de investigação, guardando
   resultados e limitações. Orquestração multiagêntica permanece uma evolução posterior.

O backend continua sob responsabilidade do Idealizador; esta sequência é planejamento,
sem autorização implícita para modificá-lo.

## P0 — Executar e validar o núcleo

- [x] **Preparar infraestrutura PostgreSQL e frontend para criação de conversas.**
  Entrega de desenvolvimento em 07/11/2026: pool limitado, repositório concreto,
  lookup simétrico, migração SQL e testes em PostgreSQL descartável. Frontend busca
  agentes pela API, cria antes de enviar, trata `409` e preserva registros locais
  anteriores para consulta. [Plano completo](dev/plano-persistencia-conversas.md)
  e [guia da infraestrutura](src/infra/db/relational/README.md). Testes de contrato
  no frontend usam respostas controladas. Nenhuma migração aplicada no banco do
  `.env`; serviços, entidades, DTOs e rotas preservados para o Idealizador.

- [ ] **Integrar a criação persistida de conversas no backend.** Responsabilidade
  do Idealizador, com mentoria: corrigir lookup/DTO e execução async versus threadpool,
  fornecer pool/repositório aos serviços, implementar catálogo `GET /agents`,
  habilitar GET no CORS e retornar `201`/`409` com metadados. `/chat` deve resolver
  a thread a partir de `conversation_id`, validando participação e atividade, sem
  criar conversa implicitamente. Aplicar a migração explicitamente em ambiente
  de desenvolvimento e validar o fluxo completo com o frontend. Mensagens do
  domínio, encerramento e reuniões conectadas permanecem para etapas futuras.

- [x] **Manter os checkpoints de Silas em PostgreSQL.** Revisão de desenvolvimento
  em 06/11/2026: `PostgresSaver` compartilhado durante o ciclo de vida da API,
  `setup()` na inicialização e fechamento na parada. Recuperação confirmada após
  fechar e reabrir a conexão, usando grafo de teste sem chamada ao modelo; thread
  temporária removida. Contexto documental inicial não é repetido a cada turno.
  Corrigidos os construtores Pydantic que bloqueavam o chat e aceita a mensagem
  simples enviada pelo frontend. Três testes automatizados e build aprovados.
  O histórico do grafo é persistente; `CHAT_CACHE` e entidades do domínio continuam
  em memória. A validação conversacional real com Silas permanece pendente.

- [ ] **Revisar os campos temporais das entidades de chat.** `created_at` ainda usa
  `datetime.time()` (meia-noite), sem representar o instante de criação. Definir
  timestamps e fuso antes de persistir essas entidades como registros do domínio.

- [x] **Recuperar a base documental ausente após a reorganização.** Os cinco
  documentos foram recuperados em `src/agents/base_knowledge/`, usando cópias
  anteriores, mensagens de contexto em `dev/messages.pretty.json` e registros de
  leitura/criação das sessões. Origem e ajustes documentados em
  [`dev/recuperacao-memoria-2026-11-05.md`](dev/recuperacao-memoria-2026-11-05.md).
  A inclusão de `projeto/` no carregador permanece uma tarefa separada.

- [ ] **Disponibilizar o documento de pesquisa no contexto de Silas.** O documento
  está em `src/agents/base_knowledge/projeto/PROJETO_DE_PESQUISA_YAVIN.md`, categoria
  ainda não lida pelo carregador. O Idealizador deverá definir sua inclusão como
  orientação de projeto, preservando a distinção entre propósito, referência,
  hipótese e decisão. Concluído quando Silas puder reconhecer a pergunta central,
  a razão do início quase vazio e os limites de inferência da simulação.

- [ ] **Implementar a recuperação de cidadãos e lugares.** Criar uma abstração para
  carregar `citizens` e `places`, começando por implementações baseadas nos arquivos
  JSON de `src/infra/` e preservando um contrato que permita migrar posteriormente
  para uma base de dados sem acoplar o domínio ao mecanismo de persistência.
- [x] **Resolver caminhos a partir dos arquivos do projeto.** A classe concreta em
  `src/agents/main.py` resolve a raiz com base em `__file__` e carrega a
  base de conhecimento comunitária a partir de `src/agents/base_knowledge/`. A identidade de
  Silas está em `src/agents/prompts/IDENTIDADE_ID_SILAS.md`. Os arquivos de suporte ao
  desenvolvimento ficam na raiz (`AGENTS.md`, `README.md` e `BACKLOG.md`) e permanecem
  fora da base de conhecimento da simulação.
- [ ] **Documentar uma execução reproduzível.** Registrar no README instalação com
  `uv`, configuração mínima e comando de inicialização de Silas. Disponibilizar
  `.env.example` sem credenciais reais. Concluído quando for possível seguir os passos
  em um ambiente novo; esclarecer que o `main.py` da raiz é um entrypoint provisório
  da API e ainda não representa uma interface de execução definitiva.
- [ ] **Tornar falhas de contexto e execução explícitas.** Hoje pastas ausentes são
  ignoradas e falhas de recuperação documental podem resultar em contexto vazio. Definir quais documentos
  são obrigatórios e apresentar falhas de leitura, configuração e API de forma clara,
  preservando a causa do erro. Concluído quando a execução não aparentar sucesso sem
  contexto obrigatório ou sem resposta.
- [ ] **Validar o comportamento de Silas com perguntas de referência.** Verificar
  identidade, propósito de Yavin, primeira investigação e distinção entre proposta e
  decisão. Incluir uma pergunta sobre algo ainda indefinido, como localização. Guardar
  perguntas e resultados em `dev/silas_test_responses/`. Concluído quando Silas
  demonstrar contexto correto e reconhecer o que permanece aberto.
- [ ] **Criar o primeiro commit.** Revisar os arquivos que entrarão no histórico,
  preservando a exclusão de `.env`, ambiente virtual e arquivos locais. Concluído
  quando a base atual estiver versionada.

## P1 — Sustentar uma investigação curta

- [ ] **Aprofundar os mecanismos de classe em Python.** Natureza: planejamento
  de estudo do Idealizador, registrado em 07/11/2026 a partir das dúvidas sobre
  os serviços. Revisar herança, métodos de instância, `classmethod`, `staticmethod`,
  `ABC` e `abstractmethod`; distinguir declaração da classe, instanciação e chamada
  de métodos. Entender os limites da imposição de contratos em execução e da análise
  estática com Pyright/Pylance, incluindo assinaturas e métodos assíncronos.
  Explorar `__init_subclass__` como alternativa, avaliando sua necessidade antes de
  adotá-lo. Concluído quando o Idealizador conseguir explicar essas diferenças e
  justificar o modelo dos serviços com pequenos exemplos. Estudo acompanhado por
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
- [ ] **Selecionar e identificar o contexto documental.** Avaliar a identificação de
  origem e natureza dos documentos em `src/agents/base_knowledge/`; carregar os arquivos em ordem
  estável e distinguir instruções de identidade, referências e registros históricos.
  Os arquivos de suporte ao desenvolvimento na raiz não devem ser enviados
  automaticamente aos agentes da simulação. Leitura direta de Markdown é suficiente
  nesta etapa.
- [ ] **Permitir conversa com continuidade na sessão do backend.** Adicionar múltiplos turnos e
  reaproveitar o histórico enquanto o processo estiver aberto. Concluído quando uma
  pergunta de acompanhamento puder usar a resposta anterior. Persistência entre
  execuções pode esperar.
- [ ] **Limpar a saída do terminal.** Mostrar a resposta legível e reservar instruções
  completas, mensagens internas e resultados brutos para um modo de depuração.
  Concluído quando uma conversa comum puder ser acompanhada sem ruído técnico.
- [ ] **Realizar a primeira investigação sobre energia.** Escolher uma pergunta
  pequena, registrar referências, hipótese, incertezas e próximo experimento. Salvar
  o resultado em Markdown revisado pelo Idealizador. Concluído quando houver um
  registro útil para retomar o trabalho; não exige banco de dados ou escrita autônoma.
- [ ] **Conectar o painel ao Silas com o Idealizador.** Definir o contrato de mensagens,
  identidade de sessão e estados de envio, resposta e falha. Concluído quando uma
  mensagem na SPA gerar uma resposta real sem misturar históricos de conversas.
  A área de reuniões já existe visualmente; execução de múltiplos agentes é outra etapa.
- [ ] **Finalizar a integração do agente Silas com o frontend.** Implementar o
  roteamento de mensagens para Silas e, quando necessário, para grupos de agentes,
  preservando a separação entre conversas, participantes, estados de envio e falhas.

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
  Avaliar depois uma orientação estável em `src/agents/prompts/IDENTIDADE_ID_SILAS.md` e um
  plano de execução separado. Implementação do backend permanece com o Idealizador.

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
  `src/infra/places.json`.
- [ ] **Definir o centro da área de trabalho e um possível menu.** Avançar uma parte
  de cada vez com o Idealizador; não usar o mockup anterior como autorização para
  implementar toda a plataforma. Memória institucional navegável permanece uma possibilidade.
- [x] **Avaliar a identidade da segunda tentativa de redesign da SPA.** Implementada em 05/11/2026,
  com nova composição editorial, navegação lateral, mapa em módulo próprio, referência
  da oficina solar urbana e painel de conversa dividido entre diretório e histórico.
  Build e fluxos verificados no navegador. O Idealizador avaliou positivamente
  a força da identidade e solicitou o refinamento do mapa em modo expandido.
  Registro e capturas em [`frontend/sketches/redesign-oficina-v2.md`](frontend/sketches/redesign-oficina-v2.md).
- [ ] **Salvar e retomar sessões do backend, se houver necessidade demonstrada.** Escolher a
  forma mais simples de persistência local suficiente para o uso observado.
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

## Entregas e correções já realizadas

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
  `src/agents/prompts/IDENTIDADE_ID_SILAS.md`. Referências aos estudos visuais e
  arquivos de desenvolvimento foram ajustadas para `frontend/sketches/` e `dev/`.
  Base documental ausente registrada como pendência separada. Rascunhos comentados
  mantidos como referências históricas, sem reativação.

- [x] **Recuperar `src/agents/prompts/IDENTIDADE_ID_SILAS.md` após exclusão.** Restaurada a
  última versão revisada disponível nesta conversa. O arquivo foi renomeado ou
  movido durante a revisão; alterações simultâneas do Idealizador foram preservadas.
  A validação pelo construtor foi impedida pelo import atual `agents.tools` ao
  importar o módulo pela raiz. Sem chamada ao modelo. Localização final e
  carregamento da identidade precisam ser conferidos após a reorganização.

- [x] **Recuperar `src/agents/main.py` após sobrescrita com as tools.** Restaurada
  a última implementação de `Citizen` lida nesta conversa; tools preservadas em
  `src/agents/tools.py`. Raiz ajustada à localização atual do arquivo.
  Importação de `Citizen` e registro das tools conferidos sem chamar o modelo.
  A revisão dos imports antigos e a recuperação dos documentos ausentes permanecem
  fora desta restauração pontual.

- [x] **Restaurar o arquivo de tools do agente.** Recuperado de conteúdo lido
  anteriormente na conversa em `src/agents/tools.py`, com `test`,
  `common`, `get_agent_state` e as listas usadas pelos imports atuais. Imports,
  registro e execução de `common` e `test` verificados sem chamada ao modelo.

- [x] **Revisar e renomear a identidade de Silas.** `IDENTIDADE.md` revisado, com
  referências documentais corrigidas e distinção entre projeto de pesquisa e
  referências culturais. Serviço de chat, execução direta de `Citizen` e `World`
  apontam para o novo arquivo. O caminho de `World` também foi corrigido para
  resolução a partir de `__file__`. Verificação estática de sintaxe e caminhos;
  sem chamada ao modelo.

- [x] **Documentar o objetivo da pesquisa de Yavin.** Criada a orientação técnica
  em `src/agents/base_knowledge/projeto/PROJETO_DE_PESQUISA_YAVIN.md`: pergunta central,
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
  em `src/agents/prompts/IDENTIDADE_ID_SILAS.md` por meio de `specialized_instructions_path`.
- [x] **Interromper a inicialização quando a leitura da identidade falhar.** O
  construtor agora propaga uma exceção, em vez de retornar com um objeto incompleto.
- [x] **Substituir a interface provisória.** A implementação concreta está em
  `src/agents/main.py`; `src/interfaces/citizen.py` permanece documentado
  como obsoleto e não deve ser usado por código novo.

Essas correções foram conferidas no código. A validação integrada do agente continua
prevista em P0. A implementação do backend permanece sob responsabilidade do
Idealizador; este backlog registra trabalho, sem autorizar alterações adicionais.
