# Yavin — Instruções para agentes de desenvolvimento

Este arquivo consolida o contexto operacional necessário para o Codex ou outra plataforma
agêntica retomar o desenvolvimento de Yavin. Ele não faz parte da base de conhecimento
dos agentes da simulação.

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

**Estado após a reorganização:** os cinco documentos em `src/agents/base_knowledge/`
foram recuperados de cópias e registros locais. A proveniência está em
`dev/recuperacao-memoria-2026-11-05.md`. A identidade disponível está em
`src/agents/prompts/IDENTIDADE_ID_SILAS.md`.

1. [`README.md`](./README.md) — síntese e estado geral do projeto.
2. [`BACKLOG.md`](./BACKLOG.md) — prioridades, pendências e critérios de conclusão.
3. [`src/agents/base_knowledge/atas/ATA_001_Fundacao_de_Yavin.md`](./src/agents/base_knowledge/atas/ATA_001_Fundacao_de_Yavin.md) —
   conclusões e questões abertas da fundação.
4. [`src/agents/base_knowledge/transcriptions/CONVERSA_001_A_Fundacao_de_Yavin.md`](./src/agents/base_knowledge/transcriptions/CONVERSA_001_A_Fundacao_de_Yavin.md) —
   argumentos, correções e evolução das ideias.
5. [`src/agents/prompts/IDENTIDADE_ID_SILAS.md`](./src/agents/prompts/IDENTIDADE_ID_SILAS.md) —
   orientação inicial do agente Silas.
6. [`src/agents/base_knowledge/projeto/PROJETO_DE_PESQUISA_YAVIN.md`](./src/agents/base_knowledge/projeto/PROJETO_DE_PESQUISA_YAVIN.md) —
   pergunta central, objetivo e limites da pesquisa; orientação técnica para humanos e agentes.
7. [`src/agents/base_knowledge/manifestos/`](./src/agents/base_knowledge/manifestos/) — referências conceituais
   da comunidade.

## Fronteira de responsabilidade

O Idealizador é responsável pelo backend, incluindo:

- arquitetura;
- orquestração de agentes;
- lógica interna;
- persistência;
- integrações;
- execução e evolução do agente Silas.

A colaboração agêntica atualmente solicitada concentra-se em documentação de produto,
identidade visual, mockups e implementação incremental do frontend. Não altere o backend
por iniciativa própria sem solicitação explícita.

## Estado do frontend

O frontend possui uma primeira SPA local em `frontend/`, construída com React, Vite e
TypeScript. Ela tem uma entrada visual com mapa mínimo e estação científica clicável,
vista de conversas e reuniões, históricos e rascunhos locais.

O modelo visual aprovado é a estação científica descrita em
[`frontend/sketches/laboratorio-v3.md`](./frontend/sketches/laboratorio-v3.md). O mapa usa ilustração 2D,
grid isométrico, panning limitado e zoom de 65% a 100%. Conversas individuais já
chamam a API local de Silas; a validação integrada e a continuidade entre requisições
permanecem pendentes. Reuniões continuam locais.

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

Não tratar a tentativa rejeitada como direção visual aprovada. Preservar as
funcionalidades, rotas, dados e acessibilidade, mas não presumir que a composição
visual atual precise ser mantida. A agressividade deve vir da atitude, do ritmo,
da modularidade e da presença, mantendo luz, acolhimento, legibilidade e o
otimismo solarpunk.

## Estado do backend

A estrutura inicial do backend está organizada em camadas provisórias:

- `src/domain/` — entidades e comportamento do domínio;
- `src/services/` — serviços de aplicação;
- `src/infra/` — arquivos de infraestrutura e configuração em desenvolvimento;
- `src/agents/` — implementação agêntica, tools e prompts.
- `src/agents/tools.py` — ferramentas disponíveis aos agentes.

Essa organização ainda não é uma arquitetura definitiva. Os arquivos JSON em
`src/infra/db/relational/` (`citizens.json`, `places.json` e `tools.json`) são configurações em
desenvolvimento e ainda não constituem um contrato oficial ou uma fonte única de verdade
do domínio.

A implementação concreta de `Agent` está em
[`src/agents/main.py`](./src/agents/main.py). A classe carrega como
base de conhecimento da simulação apenas:

```text
src/agents/base_knowledge/atas/
src/agents/base_knowledge/manifestos/
src/agents/base_knowledge/transcriptions/
```

O documento de entrada da pesquisa está na categoria `src/agents/base_knowledge/projeto/`.
Essa categoria ainda não é carregada por `Agent`; sua inclusão no contexto está
pendente e permanece sob responsabilidade do Idealizador. Não acomodar esse documento
em atas ou manifestos apenas para fazê-lo entrar no carregador existente.

A identidade de Silas está em:

```text
src/agents/prompts/IDENTIDADE_ID_SILAS.md
```

`src/agents/base_knowledge/` é reservado à documentação da comunidade simulada. Este `AGENTS.md`,
`README.md` e `BACKLOG.md` são suporte ao desenvolvimento e não devem ser incluídos
automaticamente no contexto dos agentes da simulação.

O `main.py` da raiz é um entrypoint provisório da API e ainda não representa uma
interface de execução definitiva.

## Retomada

Antes de implementar:

1. leia este arquivo, o README e o backlog;
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
