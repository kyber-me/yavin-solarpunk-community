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

- Criar e alternar conversas com Silas e reuniões com participantes informados pelo nome.
- Históricos e rascunhos separados, persistidos em `localStorage`, na chave
  `yavin.conversations.v1`; sem migração ou mudança do formato dos dados.
- Conversas individuais enviam `POST /chat` para `VITE_API_URL`, cujo padrão é
  `http://127.0.0.1:8000`. Payload: `message`, `sender_id`, `thread_id`.
- Respostas usam o envelope `{ data, error }`. Estados de envio, falha e resposta
  vazia são apresentados; o envio é bloqueado enquanto uma resposta está pendente.
- Enter envia; Shift + Enter insere uma linha. A sugestão sobre energia é editável.
- Reuniões registram mensagens apenas localmente. Nomes não provisionam agentes.
- Uma única instância do painel atende mapa e laboratório. Recolher o drawer
  preserva seleção, mensagens, rascunhos e respostas em andamento. Abrir transfere
  foco ao painel; fechar devolve ao botão Conversar.
- Retornar ao mapa preserva seleção, mensagens e rascunhos.

O drawer integra visualmente mapa e conversa; comandos que alterem o mapa e um
agente Engenheiro permanecem possibilidades futuras, sem execução implementada.

A interface não verifica a disponibilidade da API antes do envio. O backend cria
uma nova instância de `Agent` por requisição e injeta o checkpointer compartilhado
pela aplicação. O `PostgresSaver` recupera o estado pelo `thread_id`; em 06/11/2026,
a recuperação foi verificada após fechar e reabrir a conexão, sem chamada ao modelo.
A validação conversacional integrada permanece pendente. A validação visual do
redesign usou respostas controladas, sem chamar o modelo.

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
