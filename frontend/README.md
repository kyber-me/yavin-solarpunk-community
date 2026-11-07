# Yavin · Oficina de futuros possíveis

SPA local em React + TypeScript + Vite. A segunda proposta de redesign foi implementada
em 05/11/2026 e recebeu avaliação positiva do Idealizador quanto à identidade. A estação científica v3
continua sendo a arte aprovada. Refinamentos de composição continuam sendo feitos incrementalmente.

```sh
cd frontend
npm install
npm run dev
```

Abra a URL informada pelo Vite. Para validar tipos e gerar a versão estática:

```sh
npm run build
```

## Composição e navegação

- Página inicial editorial, com chamada para abrir a bancada, referência visual da
  oficina solar urbana e primeiro campo de investigação: energia.
- Mapa interativo em um módulo próprio; edifício e título levam ao laboratório.
- Cabeçalho e navegação lateral entre `#/mapa` e `#/laboratorio`; no celular,
  a navegação permanece no cabeçalho.
- Controle **Conversar** no mapa normal ou expandido abre um drawer recolhível.
  No desktop ele fica ao lado do mapa; no tablet é uma camada lateral e no celular
  uma camada inferior. Fechar ou Escape recolhe o chat antes de recolher o mapa.
- Laboratório com quadro de contexto e painel à direita, dividido entre diretório
  de conversas e histórico. No celular, a conversa ocupa a tela.
- Conteúdo de referência identificado como tal, sem métricas, atividades ou agentes
  fictícios para preencher a interface.

## Conversas e integração

**Atualização de desenvolvimento:** 07/11/2026. O frontend já usa os novos contratos
abaixo; os serviços e rotas correspondentes ainda serão integrados pelo Idealizador.
Sem essa etapa, a criação real pode apresentar falha ao carregar o catálogo ou
iniciar a conversa. Não há fallback para criar conversas apenas locais e enviá-las.

- **Iniciar conversa** carrega `GET /agents` e exige escolher um agente disponível.
  O catálogo tem carregamento, erro com nova tentativa e estado vazio. Hoje somente
  Silas deve ser disponibilizado pela API; outros nomes usados em QA são simulados.
- A confirmação envia `POST /create-conversation` com `sender_id: "idealizador"`
  e `participant_id` escolhido. Apenas a resposta `201` com metadados válidos cria
  uma entrada de conversa no frontend.
- `409` com código `CONVERSATION_ALREADY_ACTIVE` oferece **Abrir conversa existente**.
  Reutiliza a entrada local pelo ID do servidor, sem misturar históricos anteriores.
- O estado local mantém seu UUID e, separadamente, `serverConversationId` e
  `participantId`. `POST /chat` envia apenas `conversation_id`, `sender_id` e
  `message`; não envia UUID local nem `thread_id`.
- Históricos e rascunhos continuam na chave `yavin.conversations.v1`. Os campos novos
  são opcionais para compatibilidade. Conversas antigas sem ID de servidor ficam
  disponíveis para consulta, com seu rascunho preservado e envio bloqueado.
- O nome do agente selecionado acompanha rótulos, mensagens e compositor. Silas
  conserva seu avatar; outros agentes recebem uma inicial, sem imagens inventadas.
- Uma conversa retomada sem histórico local informa que o agente pode ter contexto
  anterior. Não há endpoint de recuperação das mensagens neste incremento.
- Erros de envio preservam o rascunho. `404` ou `409` no chat tornam a conversa
  indisponível para novos envios e oferecem iniciar uma conversa. Uma resposta em
  andamento permanece vinculada à conversa de origem mesmo ao trocar a seleção.
- Enter envia e Shift + Enter insere uma linha. Envios e criações repetidos são
  bloqueados enquanto pendentes; a unicidade real também será protegida pelo banco.
- Reuniões continuam com participantes e mensagens locais; não provisionam agentes
  nem chamam a rota de criação persistida.
- Mapa e laboratório usam a mesma instância de painel. O clique em Silas abre sua
  conversa persistida localmente conhecida, ou o formulário com Silas selecionado
  a partir do catálogo; não cria registros no servidor apenas por abrir o drawer.

A URL da API vem de `VITE_API_URL` e usa `http://127.0.0.1:8000` por padrão.
As respostas preservam o envelope `{ data, error }`. O
[plano aprovado](../dev/plano-persistencia-conversas.md) contém os formatos exatos;
o [guia da infraestrutura](../src/infra/db/relational/README.md) descreve a integração.
Comandos de agentes que alterem o mapa permanecem uma possibilidade futura.

### Verificação deste incremento

```sh
npm test
npm run build
```

Os testes de contrato usam o runner nativo do Node.js com suporte a TypeScript
(Node 22.18+; verificados com Node 25). Não fazem chamadas reais à API ou ao modelo.
O navegador também foi usado com respostas controladas: criação, conflito,
seleção de outro agente, erros de catálogo e envio, preservação de rascunhos e
isolamento da resposta ao trocar de conversa. O histórico local anterior ao QA
é restaurado ao final. A integração HTTP real aguarda o backend.

## Mapa e acessibilidade

O botão **Expandir** ocupa toda a área disponível, preservando o cabeçalho e o
menu lateral. **Recolher** ou Escape retornam à composição editorial. Cada entrada
no modo expandido define o zoom em 65%; o modo normal inicia e retorna em 100%.
Depois da troca, os controles de zoom continuam livres. Ao visitar o laboratório
e voltar, o modo expandido é preservado na sessão.

Silas aparece como figura estática junto à estação, no mesmo plano de pan e zoom.
Clicar nele ou ativá-lo pelo teclado abre a conversa individual no drawer, mesmo
quando a aba de reuniões estava selecionada. O avatar amarelo do mesmo personagem
aparece no chat. [Estudos e aplicação](sketches/silas/README.md).

O mapa preserva a perspectiva fixa, zoom de 65% a 100%, panning limitado, gesto de
arraste com mouse ou toque e área interativa SVG sobre a arte transparente.

Com o mapa focado: setas deslocam, Shift amplia o passo, `+`/`−` alteram zoom,
Home centraliza e Escape encerra o gesto. A roda também altera o zoom. Seleção e
arraste nativo são bloqueados apenas no mapa; textos e campos de conversa continuam
selecionáveis.

Há link para pular ao conteúdo, foco visível, foco transferido nas mudanças de rota,
nomes acessíveis para controles e respeito a movimento reduzido. A página inicial
rola em telas menores; o histórico do chat tem rolagem independente. O compositor
se adapta também à altura reduzida da janela.

## Organização e referências

- `src/main.tsx`: estrutura e navegação.
- `src/components/MapView.tsx`: entrada editorial e mapa.
- `src/components/ConversationPanel.tsx`: diretório, mensagens e integração.
- `src/components/WorkshopReference.tsx`: imagem de referência e legenda.
- `src/conversations.ts`: tipos, recuperação e chave de armazenamento.
- `src/useMapPan.ts`: câmera e gestos do mapa.
- `src/styles.css` e `src/map.css`: tokens, componentes e composição responsiva.
- [Origem dos assets](src/assets/README.md).
- [Registro e capturas do redesign](sketches/redesign-oficina-v2.md).

Barlow Condensed, Space Grotesk e DM Mono são carregadas pelo Google Fonts, com
fallbacks locais. Nenhuma biblioteca de interface ou dependência nova foi adicionada.

## Histórico e estudos visuais

**Natureza:** referências visuais e registros de desenvolvimento, reunidos aqui a
partir da revisão editorial do README público em 06/11/2026.

A primeira tentativa de redesign foi rejeitada por conservar a composição anterior
e concentrar mudanças em cores e detalhes. O
[prompt e a avaliação](../dev/project/redesign-yavin-oficina-de-futuros-prompt.md)
preservam os critérios dessa revisão. A segunda proposta recebeu avaliação positiva
quanto à identidade; sua composição, capturas e verificações estão no
[registro do redesign](sketches/redesign-oficina-v2.md).

- [Conceito de plataforma v2](sketches/yavin-platform-concept-v2.svg): direção
  anterior para organização do atelier.
- [Estação científica v3](sketches/laboratorio-v3.md): modelo visual aprovado e
  origem da arte integrada ao mapa.
- [Conceito inicial](sketches/yavin-frontend-concept.svg): exploração anterior,
  preservada para comparação.
- [Referência atmosférica](sketches/tumblr_na42u3YMgH1s1rw00o6_1280.jpg): inspiração
  para um possível mapa futuro.
- [Chat no mapa](sketches/chat-drawer.md): decisão de interface e verificações.
- [Silas](sketches/silas/README.md): estudos do personagem, prompts e aplicações.

A foto principal do README público utiliza o mesmo asset
`src/assets/oficina-solar.jpg` da interface, sem duplicar o arquivo. Sua origem e
natureza de referência visual estão descritas no [registro dos assets](src/assets/README.md).
