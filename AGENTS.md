# Yavin — Instruções para agentes de desenvolvimento

Este arquivo consolida o contexto operacional necessário para o Codex ou outra plataforma
agêntica retomar o desenvolvimento de Yavin. Ele não faz parte da base de conhecimento
dos agentes da simulação.

## Retomada atual — 08/11/2026

**Natureza:** orientação operacional de desenvolvimento.
Leia [o ponto de retomada atual](dev/retomada-2026-11-08.md) e o backlog antes de
propor a próxima implementação. O registro de 07/11 é histórico. Backend já está
em `backend/`; a prioridade atual é o harness, não a orquestração de Silas.
As quatro skills e seus schemas são protocolos disponíveis, ainda sem execução
completa de um ciclo contemporâneo do início ao relatório final. Não inventar
registros faltantes, aprovações ou estados anteriores. Commits não autorizam
novas alterações do backend nem iniciam serviços.

## Prioridade atual — método de desenvolvimento agêntico, 08/11/2026

**Natureza:** orientação operacional de desenvolvimento.
O Idealizador redirecionou a próxima frente para o método de delegação e pareamento,
antes da evolução da orquestração de Silas. Continua responsável pelo backend,
com prioridade de aprendizado em orquestração, RAG, fine-tuning, embeddings,
bancos vetoriais e bases de conhecimento. O assistente mantém o frontend,
adaptado aos contratos do backend; implementações no backend exigem delegação
pontual conforme a fronteira abaixo.

Antes de editar arquivos para uma tarefa de implementação delegada no backend, aplique
[a skill de classificação](.agents/skills/classificar-tarefa/SKILL.md): complexidade
e risco de 1 a 5, com nível igual ao maior valor e justificativas concretas.
Cada classificação gera um JSON datado e versionável em `dev/harness/`, antes das
edições, conforme [a organização dos registros](dev/harness/README.md).
Após salvar a classificação, sugira ao Idealizador a mudança para o modo Plan e
aguarde seu OK depois da troca. Só então aplique
[a skill de planejamento](.agents/skills/planejar-tarefa/SKILL.md)
e grave `planejamento.json` na mesma tarefa: plano mínimo no nível 1, abordagem
discutida no nível 2 e fases/subtarefas com dependências e critérios verificáveis
nos níveis 3 a 5. O tratamento usa `nivel = max(complexidade, risco)`.
A transição e o OK são exigidos em todos os níveis. Confira o modo real da sessão;
se indisponível ou não ativado, aguarde a troca ou exceção expressa para planejar
fora dele. Mensagens de planejamento não comprovam ativação do modo.
O OK permite planejar, não implementar. Apresente a versão concreta do plano e
aguarde autorização de execução, respeitando as fases e limites aprovados.
Após a execução efetiva de entregas de níveis 3 a 5, aplique
[a skill de revisão](.agents/skills/revisar-implementacao/SKILL.md) em outro agente,
com contexto novo e pacote delimitado de requisitos, plano, código e evidências.
Persista `revisao-NNN.json` na tarefa. A revisão não autoriza correções fora do
escopo nem substitui revisão humana. Refatorações exigem problema concreto;
preferências de estilo não bloqueiam aceite. Nos níveis 1 e 2, revisar quando
solicitado ou previsto no plano. Sem isolamento, declarar revisão independente pendente.
O coordenador da skill de revisão lê [as diretrizes de loop](.agents/skills/revisar-implementacao/references/loop-correcoes.md)
e pode delegar correções a executor em contexto novo quando cobertas pela
autorização do plano. Limite: três tentativas com revisão por tarefa, incluindo
a inicial. Cada entrega tem ULID `implementation_id`, ligado à anterior;
eventos `loop-NNN.json` são gravados antes das chamadas. Revisor e executor
retornam ao coordenador sem delegar. Limite atingido ou conflito de escopo exige
decisão do Idealizador; nunca equivale a aprovação. Não corrigir por mera revisão solicitada.
Após aprovação técnica e encerramento do loop, aplique
[a skill de relatório final](.agents/skills/relatar-implementacao/SKILL.md).
Grave `relatorio-final.json` na tarefa com implementação/revisão aprovadas,
arquivos alterados, fases executadas, critérios, validações, anotações e referências.
Revisão humana permanece pendente; não presumir leitura ou aprovação do Idealizador.
Graphify é apoio opcional de análise de impacto, com confirmação das relações
no código e fallback por busca/leitura. A skill não instala nem exige a ferramenta.
O fluxo não se aplica a implementações exclusivas de frontend. Em tarefas mistas,
classifique a parcela do backend, considerando seus consumidores na análise de impacto.
Perguntas conceituais e retomadas de contexto não exigem classificação.
O Graphify está disponível como ferramenta isolada; o grafo local do backend e as
instruções de reprodução estão em [dev/graphs/](dev/graphs/README.md).

O registro deste incremento está em
[desenvolvimento agêntico](dev/metodo-desenvolvimento-agentico-2026-11-08.md).
Classificação e planejamento por nível estão documentados em skills com registros
JSON. O protocolo de revisão independente e seu schema também estão disponíveis.
O loop limitado está descrito para execução pelo coordenador via ferramentas de
agentes; não há serviço/runner autônomo. Roteamento de modelos, captura automática
de estados e interface continuam como incrementos posteriores.

## Organização atual — monorepo, 08/11/2026

**Natureza:** estado operacional de desenvolvimento.
O projeto Python está em `backend/`: código, testes, `main.py`, `pyproject.toml`,
`uv.lock`, `.python-version`, `langgraph.json`, `.env` local e estado `.langgraph_api/`.
Execute comandos Python/uv a partir de `backend/`; o ambiente ativo é `backend/.venv/`.
Os imports continuam `src.*`, relativos à pasta do backend. Frontend, instruções,
backlog e documentação de desenvolvimento permanecem na raiz.
Leia [a migração e suas verificações](dev/migracao-backend-2026-11-08.md) junto
ao registro histórico abaixo; comandos e caminhos antigos devem ser interpretados
conforme essa mudança. Não reaplicar migrações de banco.

## Estado técnico de referência — encerramento de 07/11/2026

**Natureza:** estado operacional de desenvolvimento.
Leia [o ponto de retomada](dev/retomada-2026-11-07.md) antes de propor trabalho.
O chat persistido está integrado; schema inicial aplicado, checkpoints preservados
na migração e dois turnos reais com Silas validados. Frontend só mostra registros
do banco, sem históricos locais; reuniões estão bloqueadas. API e Vite foram
encerrados a pedido do Idealizador, portas 8000/5173 livres. Não reiniciá-los ao
simplesmente retomar contexto. O Idealizador quer focar em lógica de orquestração;
primeiro discutir o menor incremento. Autorizações de implementação anteriores
foram pontuais e consumidas: não existe autorização permanente ou etapa já aprovada
para implementar na próxima sessão. O backlog conserva pendências no topo.

## Contexto

Yavin é uma iniciativa experimental de construção progressiva de uma comunidade inspirada
no solarpunk. O projeto combina investigação, documentação, agentes de inteligência
artificial e, futuramente, um laboratório virtual relacionado às condições de um território
real brasileiro.

Yavin não começa como uma cidade virtual pronta. Começa como um laboratório que pesquisa
problemas, formula hipóteses, executa experimentos e delibera sobre possíveis estruturas,
infraestruturas e formas de organização.

O primeiro foco de investigação é energia. O modelo de iniciativa é híbrido: o Idealizador
pode introduzir objetivos, hipóteses, comentários e restrições, enquanto o laboratório
poderá identificar problemas e propor investigações.

> Yavin não precisa nascer sabendo o que é uma comunidade ideal. Ela pode nascer tentando
> descobrir.

## Regras de interpretação

- Avance por decisões pequenas, explícitas e reversíveis.
- Não tente projetar a comunidade, o backend ou o mundo virtual inteiro de uma vez.
- Distinga hipótese, evidência, proposta, deliberação e decisão aprovada.
- “Proposta” não significa “decisão”.
- “Possibilidade” não significa “requisito”.
- Não preencha lacunas com decisões inventadas.
- Quando houver conflito documental, informe a divergência em vez de escolher
  silenciosamente.
- Preserve a diferença entre atas, conversas, manifestos e identidades.
- A continuidade de Silas é documental e operacional, não uma transferência literal de
  consciência ou memória interna.

## Fontes de contexto

Leia, conforme a necessidade:

**Estado após a reorganização:** os cinco documentos em `backend/src/agents/base_knowledge/`
foram recuperados de cópias e registros locais. A proveniência está em
`dev/recuperacao-memoria-2026-11-05.md`. A identidade disponível está em
`backend/src/agents/prompts/IDENTIDADE_ID_SILAS.md`.

1. [`README.md`](./README.md) — apresentação pública, orientação da pesquisa e síntese técnica.
2. [`BACKLOG.md`](./BACKLOG.md) — prioridades, pendências e critérios de conclusão.
3. [`backend/src/agents/base_knowledge/atas/ATA_001_Fundacao_de_Yavin.md`](./backend/src/agents/base_knowledge/atas/ATA_001_Fundacao_de_Yavin.md) —
   conclusões e questões abertas da fundação.
4. [`backend/src/agents/base_knowledge/transcriptions/CONVERSA_001_A_Fundacao_de_Yavin.md`](./backend/src/agents/base_knowledge/transcriptions/CONVERSA_001_A_Fundacao_de_Yavin.md) —
   argumentos, correções e evolução das ideias.
5. [`backend/src/agents/prompts/IDENTIDADE_ID_SILAS.md`](./backend/src/agents/prompts/IDENTIDADE_ID_SILAS.md) —
   orientação inicial do agente Silas.
6. [`backend/src/agents/base_knowledge/projeto/PROJETO_DE_PESQUISA_YAVIN.md`](./backend/src/agents/base_knowledge/projeto/PROJETO_DE_PESQUISA_YAVIN.md) —
   pergunta central, objetivo e limites da pesquisa; orientação técnica para humanos e agentes.
7. [`backend/src/agents/base_knowledge/manifestos/`](./backend/src/agents/base_knowledge/manifestos/) — referências conceituais
   da comunidade.

## Fronteira de responsabilidade

O Idealizador é responsável pelo backend, incluindo:

- arquitetura;
- orquestração de agentes;
- lógica interna;
- persistência;
- integrações;
- execução e evolução do agente Silas.

**Diretiva do Idealizador registrada em 06/11/2026:** jamais altere diretamente o
backend sem consultá-lo primeiro e obter autorização para a alteração proposta.
Pedidos de revisão, diagnóstico ou explicação não autorizam implementação.
Autorizações são pontuais: aplicam-se ao escopo e à etapa aprovados. As autorizações
da rodada encerrada em 07/11/2026 não se estendem a novas alterações.

No backend, atue como mentor: identifique erros e oportunidades de melhoria, explique
as causas e os caminhos possíveis e permita que o Idealizador implemente as mudanças
para desenvolver-se profissionalmente. Antes de editar qualquer código, configuração
ou dependência do backend, apresente a mudança proposta e aguarde sua autorização.

No frontend, a colaboração agêntica permanece responsável pelas implementações
solicitadas, além de documentação de produto, identidade visual e mockups.

## Acordo de mentoria e revisão de código

**Natureza:** decisão de colaboração no desenvolvimento.

Data: 07/11/2026.
Questão: manter uma mentoria consistente que apoie a formação do Idealizador como
programador, engenheiro e arquiteto de software.
Opções consideradas: instruções no `AGENTS.md`, documento separado ou skill reutilizável.
Decisão: registrar o acordo neste `AGENTS.md`.
Motivo: a mentoria é uma orientação permanente de trabalho em Yavin e complementa
a fronteira de responsabilidade já estabelecida.
O que continua aberto: evolução das convenções de comentários e eventual extração
de uma skill, caso o procedimento amadureça e seja útil em outros projetos.
Próximo passo: aplicar o acordo nas revisões incrementais e refiná-lo com o Idealizador.

Nas revisões do backend:

- Quando houver autorização pontual para implementar, explique antes a lógica,
  informe cada intervenção durante a execução e peça aprovação para progredir à
  próxima etapa, conforme solicitado pelo Idealizador.
- Apoie o aprendizado sem assumir a implementação. Revisão ou diagnóstico não
  autorizam alterações, inclusive correções aparentemente simples.
- Explique o problema, sua causa, a consequência prática e a menor correção
  adequada. Relacione o caso a um princípio de engenharia quando isso ajudar
  o Idealizador a aplicar o aprendizado em outras situações.
- Distinga erros que impedem o funcionamento, riscos de manutenção ou desempenho
  e preferências de estilo. Priorize os bloqueios e proponha passos pequenos.
- Reconheça boas decisões com justificativa técnica; explique também seus limites
  e os custos das alternativas.
- Avalie arquitetura, padrões de projeto, desempenho, concorrência e contratos
  conforme a necessidade concreta. Busque o mínimo de bons padrões para o estágio
  atual, sem exigir perfeição ou introduzir abstrações prematuras.
- Diferencie fatos observados, resultados de verificações e hipóteses. Informe
  o alcance da revisão e o que ainda depende de validação integrada.
- Orientação de integração registrada em 07/11/2026: defina e revise contratos
  de API no backend primeiro; o frontend deve consumi-los. Não altere o contrato
  do backend apenas para acomodar o payload existente da interface. Divergências
  exigem explicitar o contrato proposto e respeitar a autorização pontual vigente.

Convenções de comentários autorais do Idealizador:

- Comentários com perguntas ou notas são pautas de mentoria e devem ser abordados
  na revisão do trecho relacionado, mesmo sem repetição da pergunta na conversa.
- Comentários terminados em `(?)` representam conclusões provisórias do Idealizador.
  Indique se estão corretas, parcialmente corretas ou incorretas e explique as
  condições e ressalvas necessárias para consolidar o entendimento.
- Uma pergunta respondida não autoriza apagar o comentário. Comentários resolvidos
  podem ser removidos ou reescritos pelo assistente somente com aprovação do
  Idealizador. Preserve-os até essa aprovação.
- Amplie essas convenções progressivamente, conforme os acordos com o Idealizador;
  não atribua significados novos a marcadores sem combiná-los.

## Estado do frontend

O frontend possui uma primeira SPA local em `frontend/`, construída com React, Vite e
TypeScript. Ela tem uma entrada visual com mapa mínimo e estação científica clicável,
vista de conversas com históricos persistidos no PostgreSQL e rascunhos apenas
em memória. A aba de reuniões informa indisponibilidade até haver persistência.

O modelo visual aprovado é a estação científica descrita em
[`frontend/sketches/laboratorio-v3.md`](./frontend/sketches/laboratorio-v3.md). O mapa usa ilustração 2D,
grid isométrico, panning limitado e zoom de 65% a 100%. Conversas individuais já
chamam a API local de Silas. Os checkpoints em PostgreSQL já tiveram recuperação
verificada entre conexões; dois turnos reais por HTTP confirmaram continuidade.
A recuperação das mensagens pela SPA foi verificada; envio real pelo compositor
ainda não foi validado. Reuniões não criam registros locais.

A direção de produto continua sendo uma plataforma/atelier de investigação, não uma cidade
virtual pronta. O centro da área de trabalho, o menu geral, a expansão do mapa e as
simulações permanecem em aberto. Uma engine 2.5D só deve ser considerada diante de uma
necessidade concreta de câmera, navegação espacial, animação, colisão, iluminação ou
grande quantidade de entidades.

A primeira tentativa de redesign da interface, baseada na direção de uma oficina de
futuros possíveis, foi rejeitada pelo Idealizador. Ela preservou a composição e a
identidade anteriores, fazendo principalmente mudanças de cor e detalhes, e ficou
mais confusa sem produzir a mudança agressiva solicitada. A próxima tentativa deve
reconsiderar composição, hierarquia e presença da página inicial antes de ajustar
tokens visuais. O prompt original e o adendo da avaliação estão em
`dev/project/redesign-yavin-oficina-de-futuros-prompt.md`.

Uma segunda tentativa foi implementada em 05/11/2026: página inicial editorial,
navegação lateral, mapa em módulo próprio e painel com diretório e histórico.
O registro está em `frontend/sketches/redesign-oficina-v2.md`. Foi verificada no navegador,
e recebeu avaliação positiva do Idealizador quanto à força da identidade.
O mapa também possui um modo expandido que mantém cabeçalho e menu lateral,
inicia em 65% de zoom e retorna a 100% ao recolher. O chat também abre como
drawer no mapa normal ou expandido; uma única instância preserva estado entre
mapa e laboratório. No desktop o mapa continua interativo ao lado do chat.
Comandos de agentes que produzam efeitos no mapa são uma possibilidade sugerida,
sem contrato de backend ou execução implementados. Refinamentos continuam incrementais.

Silas possui avatar amarelo pixelado no chat e figura estática transparente no
mapa, junto à estação. Clicar na figura abre a conversa individual no drawer.
O personagem acompanha pan e zoom; não possui movimentação ou simulação autônoma.
Arte, prompts e registro estão em `frontend/sketches/silas/README.md`.

**Direção artística aprovada em 08/11/2026:** o Idealizador aprovou a paisagem
ilustrada da chegada e estendeu essa direção às futuras implementações visuais
no mapa: ilustração solarpunk expressiva, vegetação tropical, tecnologia cotidiana
e robôs com identidade. Referências, asset e prompt estão preservados em
`frontend/sketches/direcao-artistica.md`. Consultar esse repertório ao propor novas
artes; o Idealizador poderá acrescentar referências. A chegada deve ter pouco
texto e dar presença à paisagem. Visor e gesto de entrada continuam em refinamento:
a primeira versão foi percebida como uma bússola sem relação clara com a cena.
A tentativa seguinte em SVG também foi rejeitada por simular mal perspectiva e
profundidade; a versão em avaliação usa uma luneta 3D local em Three.js, sem
converter o mapa. Seleção de texto na entrada foi bloqueada e a sensibilidade do
parallax reduzida após avaliação. O título passou a “O futuro tem lugar”.
A arte do topo da página Manifesto também foi aprovada explicitamente pelo
Idealizador como parte dessa identidade, com a orientação de preservar sua
essência. Paisagem e arte do manifesto são as duas âncoras do guia artístico.
O guia reúne também linguagem por elemento, procedência e propostas de animação;
ele é suporte de desenvolvimento, fora da base de conhecimento da simulação.
O Idealizador pediu animações discretas que preservem todos os componentes da
paisagem aprovada. Manter a imagem estática original; as propostas ainda aguardam
avaliação e vídeo gerado não garante preservação integral entre quadros.

O README contém a marca ASCII aprovada pelo Idealizador em 05/11/2026, com
símbolo solar e o nome YAVIN em sete linhas e até 63 colunas, usando apenas
caracteres ASCII. O núcleo solar é arredondado e os raios foram ampliados.
Essa aprovação se refere à composição textual do README.

Não tratar a tentativa rejeitada como direção visual aprovada. Preservar as
funcionalidades, rotas, dados e acessibilidade, mas não presumir que a composição
visual atual precise ser mantida. A agressividade deve vir da atitude, do ritmo,
da modularidade e da presença, mantendo luz, acolhimento, legibilidade e o
otimismo solarpunk.

## Estado do backend

A estrutura inicial do backend está organizada em camadas provisórias:

- `backend/src/domain/` — entidades e comportamento do domínio;
- `backend/src/services/` — serviços de aplicação;
- `backend/src/infra/` — arquivos de infraestrutura e configuração em desenvolvimento;
- `backend/src/agents/` — implementação agêntica, tools e prompts.
- `backend/src/agents/tools.py` — ferramentas disponíveis aos agentes.

Essa organização ainda não é uma arquitetura definitiva. Os arquivos JSON em
`backend/src/infra/db/relational/draft/` (`citizens.json`, `places.json` e `tools.json`) são configurações em
desenvolvimento e ainda não constituem um contrato oficial ou uma fonte única de verdade
do domínio.

A implementação concreta de `Agent` está em
[`backend/src/agents/agent.py`](backend/src/agents/agent.py). A classe carrega como
base de conhecimento da simulação apenas:

```text
backend/src/agents/base_knowledge/atas/
backend/src/agents/base_knowledge/manifestos/
backend/src/agents/base_knowledge/transcriptions/
```

O documento de entrada da pesquisa está na categoria `backend/src/agents/base_knowledge/projeto/`.
Essa categoria ainda não é carregada por `Agent`; sua inclusão no contexto está
pendente e permanece sob responsabilidade do Idealizador. Não acomodar esse documento
em atas ou manifestos apenas para fazê-lo entrar no carregador existente.

A identidade de Silas está em:

```text
backend/src/agents/prompts/IDENTIDADE_ID_SILAS.md
```

`backend/src/agents/base_knowledge/` é reservado à documentação da comunidade simulada. Este `AGENTS.md`,
`README.md` e `BACKLOG.md` são suporte ao desenvolvimento e não devem ser incluídos
automaticamente no contexto dos agentes da simulação.

O `backend/main.py` é um entrypoint provisório da API e ainda não representa uma
interface de execução definitiva.

A criação do checkpointer fica em
`backend/src/agents/infra/open_checkpointer_helper.py`. O `lifespan` da API mantém um
`PostgresSaver` compartilhado por processo, executa `setup()` na inicialização e
fecha a conexão na parada. O serviço recebe esse recurso e o repassa para `Agent`.
O estado do grafo é persistido por `thread_id`; conversas e mensagens também têm
registros próprios no PostgreSQL. `CHAT_CACHE` é um resquício fora do fluxo ativo. Atualmente, o `.env` é carregado ao importar `backend/src/agents/agent.py`, um
efeito colateral do import. A política de conexões permanece provisória; qualquer
alteração do backend exige consulta prévia ao Idealizador.

## Criação persistida de conversas — incremento de 07/11/2026

**Natureza:** estado de implementação e divisão de responsabilidades aprovada.

O plano está em `dev/plano-persistencia-conversas.md`; a infraestrutura em
`backend/src/infra/db/relational/README.md`. Pool, repositório, migração e frontend foram
implementados pelo assistente sob autorização específica. O Idealizador conectou o pool ao
lifespan e iniciou a integração dos serviços e rotas. `GET /agents` retorna apenas
Silas com o identificador estável provisório `silas`; GET e POST são permitidos no
CORS para as duas origens locais. Listagem e criação usam o catálogo mínimo de
`backend/src/services/agent_catalog.py`; participante indisponível é rejeitado com `422`
antes de acessar o repositório. O fluxo HTTP passou com PostgreSQL e checkpoints
reais em banco descartável e modelo simulado, incluindo retomada e isolamento.
O schema inicial já foi aplicado ao banco do projeto, preservando os 15 checkpoints
anteriores. Dois turnos reais com reabertura das conexões confirmaram continuidade. O frontend
exige `GET /agents`, criação confirmada por `POST /conversation/create` e
`conversation_id` em `/conversation/talk`.
Por diretiva posterior do Idealizador, conversas locais antigas não são exibidas
nem importadas: a chave legada do localStorage é removida ao abrir. Conversas e
mensagens vêm do banco via API; rascunhos ficam apenas em memória. Reuniões estão
bloqueadas até haver persistência. Checkpoints existentes
não foram alterados. Uma conversa ativa por dupla sem direção é a regra inicial;
encerramento e reuniões ficam para depois. O schema inicial consolidado está em
`backend/src/infra/db/relational/migrations/001_initial_schema.sql`: conversas e mensagens,
ULIDs puros, índice único da dupla normalizada com `LEAST`/`GREATEST` e `WHERE active`.
Antes da aplicação, o Idealizador confirmou que nenhum script intermediário havia
sido aplicado e só existiam dados do checkpointer; os scripts foram substituídos pelo schema inicial único.
A migração inicial foi aplicada ao banco do projeto sem alterar seus checkpoints.
As consultas são `GET /conversations` por `sender_id` e
`GET /conversations/{id}/messages`, com paginação e validação de participação.

## Persistência de mensagens — incremento de 07/11/2026

**Incremento de mensagens autorizado em 07/11/2026:** camada simples entregue com
`Message` Pydantic (no DTO atual), `MessageRecord`, adaptador em
`backend/src/services/message_mapper.py` e repositório síncrono. Reutiliza o pool de
conversas com row factory por cursor. O serviço já grava entrada e resposta com
autoria, UTC e verificação de participação e atividade. O fluxo passou com grafo
simulado e com dois turnos reais. A migração inicial foi aplicada ao banco do projeto. Guia e limites em `backend/src/infra/db/relational/MESSAGES.md`.

## Escopo da documentação de desenvolvimento

**Padrão de IDs aprovado em 07/11/2026:** entidades persistidas usam ULID puro,
sem prefixos. O schema inicial único já define esses IDs sem conversão de dados
legados, pois nenhuma migração intermediária foi aplicada ao banco do projeto.
Documentos históricos podem conter o formato antigo e caminhos substituídos.
Referências provisórias de participantes (`idealizador`, `silas`) e checkpoints
existentes não são reescritos por essa migração.

**Natureza:** orientação editorial de desenvolvimento, registrada em 06/11/2026.

O README da raiz é a entrada pública do projeto: propósito, orientação solarpunk,
método de pesquisa, capacidades atuais e síntese técnica. Instruções de retomada,
fronteiras de responsabilidade, particularidades de carregamento e recuperação de
arquivos pertencem a este `AGENTS.md` e aos registros de desenvolvimento citados.
Prioridades e critérios de conclusão pertencem ao `BACKLOG.md`. Detalhes da interface,
controles e estudos visuais pertencem ao `frontend/README.md` e a
`frontend/sketches/`. O histórico de tentativas rejeitadas continua nos registros
visuais, sem ocupar a apresentação pública. Não é necessário um README interno
adicional; estes documentos já cobrem as respectivas responsabilidades.

## Retomada

Antes de implementar:

1. leia este arquivo, `dev/retomada-2026-11-07.md`, o README e o backlog;
2. confira os documentos de fundação relacionados à tarefa;
3. identifique a menor decisão ou mudança necessária;
4. preserve o escopo e valide a alteração;
5. atualize o backlog quando uma tarefa for concluída ou seu estado mudar.

Ao registrar uma nova decisão, use:

```text
Data:
Questão:
Opções consideradas:
Decisão:
Motivo:
O que continua aberto:
Próximo passo:
```

Ao criar ou atualizar documentação, informe sua natureza: ata, conversa, manifesto,
identidade, decisão provisória, hipótese ou referência visual.
