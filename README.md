```text
             .-""""-.
          .-'    |    '-.
        .'   ----+----   '.
       /        |        \
      ;         |         ;
       \        |        /
        '.   ---+---   .'
          '-.    |  .-'
             '-.__.-'
                 YAVIN
```

# Yavin

Yavin é uma iniciativa experimental de construção progressiva de uma comunidade
inspirada no solarpunk. O projeto combina investigação, documentação, agentes de
inteligência artificial e, futuramente, um laboratório virtual relacionado às condições
de um território real brasileiro.

Yavin não começa como uma cidade virtual pronta. Começa como um laboratório que tenta
descobrir, por meio de pesquisa, hipóteses, experimentos e deliberação, quais estruturas,
infraestruturas e formas de organização poderiam compor essa comunidade.

> Yavin não precisa nascer sabendo o que é uma comunidade ideal. Ela pode nascer tentando
> descobrir.

## Documento de entrada da pesquisa

O [Projeto de pesquisa de Yavin](./src/agents/base_knowledge/projeto/PROJETO_DE_PESQUISA_YAVIN.md)
explicita a pergunta central, os objetivos, a razão de começar quase do zero e o
que se pretende observar durante a simulação. É uma orientação técnica para
humanos e agentes, distinta das atas, conversas e referências culturais.

> É possível construir uma pequena sociedade autossustentável baseada em tecnologia,
> sustentabilidade e cooperação?

A pesquisa acompanhará tanto as condições de viabilidade da comunidade quanto o
processo de formular perguntas, conduzir conversas e tomar decisões com participação
humana e futura orquestração multiagêntica. As respostas permanecem abertas.

## Visão do projeto

O laboratório terá um modelo híbrido de iniciativa:

- o Idealizador poderá introduzir objetivos, hipóteses, comentários e restrições;
- o próprio laboratório poderá identificar problemas e propor investigações;
- agentes poderão observar, pesquisar, simular e elaborar propostas;
- propostas não alteram automaticamente o mundo persistente;
- decisões aprovadas deverão preservar suas justificativas, evidências e histórico.

A primeira área de investigação é **energia**, especialmente geração, armazenamento,
distribuição e autonomia energética. O estudo de solarpunk orientará a elaboração do
manifesto e ajudará a restringir o escopo das investigações iniciais.

## Memória institucional

Yavin distingue a orientação da pesquisa dos registros de memória e das referências culturais:

- **Projeto de pesquisa:** problema, pergunta central, objetivos, recorte e limites.
- **Atas:** conclusões, decisões, questões abertas e encaminhamentos.
- **Conversas:** reconstruções editoriais do processo de elaboração, incluindo argumentos,
  correções e mudanças de perspectiva.
- **Manifestos e referências culturais:** fundamentação solarpunk; o manifesto autoral
  de Yavin permanece em elaboração.

**Recuperação após a reorganização:** os cinco documentos de
`src/agents/base_knowledge/` foram recuperados de cópias e registros locais em
05/11/2026. A origem e os ajustes estão no [registro de recuperação](./dev/recuperacao-memoria-2026-11-05.md).
A identidade está em `src/agents/prompts/IDENTIDADE_ID_SILAS.md`.

A documentação comunitária está em [`src/agents/base_knowledge/`](./src/agents/base_knowledge/):

- [`ATA_001_Fundacao_de_Yavin.md`](./src/agents/base_knowledge/atas/ATA_001_Fundacao_de_Yavin.md)
- [`CONVERSA_001_A_Fundacao_de_Yavin.md`](./src/agents/base_knowledge/transcriptions/CONVERSA_001_A_Fundacao_de_Yavin.md)
- [`manifesto-solarpunk.md`](./src/agents/base_knowledge/manifestos/manifesto-solarpunk.md)
- [`conceitos-fundamentais.md`](./src/agents/base_knowledge/manifestos/conceitos-fundamentais.md)
- [`IDENTIDADE.md`](./src/agents/prompts/IDENTIDADE_ID_SILAS.md)

O carregador atual de Silas lê apenas `atas/`, `manifestos/` e `transcriptions/`.
A categoria `projeto/` ainda precisa ser incluída no contexto pelo Idealizador;
criar o documento não o disponibiliza automaticamente ao agente.

## Silas

Silas é o primeiro colaborador agêntico de Yavin. Sua identidade inicial é a de um
colaborador intelectual: ele ajuda o Idealizador a pensar, investigar, questionar
hipóteses e transformar ideias em experimentos verificáveis.

Silas deve:

- demonstrar curiosidade, método e independência intelectual;
- discordar quando houver razões fundamentadas;
- distinguir hipóteses, evidências, propostas e decisões;
- preferir experimentação a conclusões prematuras;
- reconhecer incertezas e evitar complexidade desnecessária.

A continuidade de Silas é **operacional e documental**. Não representa a transferência
literal de uma consciência ou memória interna entre plataformas.

## Estado técnico atual

O repositório contém uma base inicial em Python, gerenciada com `uv`, com LangChain,
ferramentas simples e carregamento de documentos Markdown para fornecer contexto ao
agente. O backend é responsabilidade do Idealizador, incluindo arquitetura,
orquestração de agentes, lógica interna, persistência e integrações.

A estrutura inicial do backend está organizada provisoriamente em `src/domain/`,
`src/services/`, `src/infra/` e `src/agents/`. Os arquivos JSON em `src/infra/db/relational/` são
configurações em desenvolvimento e ainda não constituem um contrato oficial do domínio.
O `main.py` da raiz é um entrypoint provisório da API, não uma interface de execução
definitiva.

O frontend possui uma primeira SPA local em [`frontend/`](./frontend/README.md), com
React + Vite + TypeScript. A entrada apresenta uma estação científica ilustrada
e clicável, baseada no modelo visual v3 aprovado. Ela leva ao painel de conversa
fixo à direita, com conversas independentes e reuniões com múltiplos participantes.
Há retorno ao mapa e navegação pelas rotas `#/mapa` e `#/laboratorio`. Históricos e
rascunhos são salvos no navegador. Conversas individuais já chamam `POST /chat`;
a continuidade do agente entre requisições e a validação integrada permanecem
pendentes. Reuniões continuam locais. O mapa está em um módulo da página inicial,
com grid isométrico discreto, panning limitado e zoom de 65% a 100%. Edifício e legenda acompanham a câmera; a área do
mapa bloqueia seleção e arraste nativo sem interferir nos campos de conversa.
A segunda proposta visual inclui um quadro de contexto ao lado da conversa e
navegação entre território e laboratório; novas ferramentas de trabalho permanecem abertas.

Para executar: `cd frontend`, `npm install` e `npm run dev`.

A direção visual mais ampla continua provisória:

- React + Vite + TypeScript;
- uma plataforma de investigação, não uma cidade virtual pronta;
- o laboratório/atelier como experiência principal;
- Silas como caderno ou colaborador contextual;
- memória institucional e investigações como áreas navegáveis;
- expansão futura do mapa além da estação inicial;
- ilustração 2D com interação em SVG; engine espacial depende de necessidades futuras.

## Avaliação do redesign visual

A primeira tentativa de traduzir Yavin como uma oficina de futuros possíveis foi
rejeitada pelo Idealizador. A mudança ficou próxima demais da interface anterior e
se concentrou em cores e detalhes, sem alterar suficientemente a composição, a
hierarquia e a personalidade da plataforma. O prompt original, com o veredicto e
critérios para uma nova tentativa, está em
[`dev/project/redesign-yavin-oficina-de-futuros-prompt.md`](./dev/project/redesign-yavin-oficina-de-futuros-prompt.md).

Essa avaliação é uma orientação de desenvolvimento, não uma decisão institucional
da comunidade. Em 05/11/2026 foi implementada uma segunda proposta: composição
editorial, navegação lateral, mapa em bancada e painel de conversa com diretório e
histórico lado a lado. A referência da laje aparece identificada como referência
visual. O [registro da proposta e as capturas](./frontend/sketches/redesign-oficina-v2.md)
documentam a entrega. O Idealizador reconheceu a força da nova identidade.
O mapa recebeu um modo expandido que mantém cabeçalho e menu lateral, com zoom
inicial de 65%; ao recolher, retorna a 100%. O chat também pode ser aberto como
um drawer no mapa, usando a mesma conversa do laboratório. A interação do mapa
permanece disponível no desktop enquanto o chat está aberto. A possibilidade de
comandos de agentes produzirem efeitos no mapa foi registrada, mas não implementada.

Os estudos visuais estão em [`frontend/sketches/`](./frontend/sketches/):

- [`yavin-platform-concept-v2.svg`](./frontend/sketches/yavin-platform-concept-v2.svg) é a direção
  anterior para a organização do atelier;
- [`laboratorio-v3.md`](./frontend/sketches/laboratorio-v3.md) registra o modelo aprovado da
  estação científica, cuja arte isolada está integrada ao frontend;
- [`yavin-frontend-concept.svg`](./frontend/sketches/yavin-frontend-concept.svg) é uma exploração
  anterior, preservada para comparação;
- [`tumblr_na42u3YMgH1s1rw00o6_1280.jpg`](./frontend/sketches/tumblr_na42u3YMgH1s1rw00o6_1280.jpg)
  é uma referência atmosférica para um possível mapa futuro, não um modelo da plataforma.

## O que ainda não foi decidido

Não tratar como decisões aprovadas:

- localização de Yavin;
- arquitetura técnica definitiva;
- modelo de governança;
- economia ou moeda própria;
- indicadores ambientais e fontes de dados;
- regras completas do mundo virtual;
- necessidade de uma engine 2.5D;
- implementação de voz;
- autonomia de construção por agentes.

## Retomada do trabalho

Antes de implementar novas partes, leia [`AGENTS.md`](./AGENTS.md), o
[`BACKLOG.md`](./BACKLOG.md) e os documentos de fundação. Use os documentos de fundação
como fonte de contexto, mas não transforme hipóteses ou propostas em decisões sem
confirmação do Idealizador.

`AGENTS.md`, `README.md` e `BACKLOG.md` apoiam o desenvolvimento e não fazem parte da
base de conhecimento carregada automaticamente pelo agente Silas. Atualizar esses
arquivos não altera automaticamente a memória do agente da simulação.
