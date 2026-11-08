# Yavin · Oficina de futuros possíveis

**Natureza:** guia de desenvolvimento e referência da interface.

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

**Atualização de desenvolvimento:** 07/11/2026. O PostgreSQL é a fonte dos históricos.
O frontend não lê nem grava conversas, mensagens ou rascunhos no `localStorage`.
A chave antiga `yavin.conversations.v1` é removida ao abrir; registros locais antigos
não são importados nem exibidos. Rascunhos existem apenas na memória da página.

O backend define os contratos, sempre no envelope `{ data, error }`:

- `GET /agents`: catálogo de participantes disponíveis; atualmente apenas Silas.
- `POST /conversation/create`: cria antes de permitir envio; `201` confirma o
  registro, `409 / CONVERSATION_ALREADY_ACTIVE` oferece abrir a conversa existente.
- `GET /conversations?sender_id=idealizador`: lista as conversas persistidas da dupla
  de que o remetente participa, incluindo inativas para consulta.
- `GET /conversations/{id}/messages?sender_id=idealizador`: verifica participação
  e devolve mensagens persistidas com seus IDs, autores e timestamps reais.
- As consultas usam `limit` (até 100) e `offset`; a interface segue `next_offset`
  até recuperar o histórico completo. Falhas não usam histórico local como fallback.
- `POST /conversation/talk`: recebe `conversation_id`, `sender_id` e `message` como
  texto. Após sucesso ou falha, a interface consulta o histórico novamente: a entrada
  pode ter sido gravada mesmo se o agente falhar. Não cria mensagens provisórias.

A seleção, rascunhos e erros são estado de sessão. Recarregar busca os registros no
servidor. Títulos são derivados do participante; não há título personalizado salvo
somente no navegador. Conversas encerradas são consultáveis, com envio bloqueado.
Reuniões ficam indisponíveis até existir persistência; não criam registros locais.

O projeto Python está em `../backend/`. Para executar a API em outro terminal,
use `cd backend` a partir da raiz e `uv run python main.py`. A migração de pasta
não altera os contratos HTTP.

A URL da API vem de `VITE_API_URL` e usa `http://127.0.0.1:8000` por padrão.
Mapa e laboratório mantêm a mesma instância do painel. Enter envia e Shift + Enter
insere uma linha; uma resposta em andamento permanece vinculada à conversa de origem.

### Verificação

```sh
npm test
npm run build
```

Oito testes do frontend e build aprovados. Testes HTTP e PostgreSQL descartável
cobrem leitura, paginação, isolamento, recarga e rejeição de acesso. Com Ego Browser,
verificados no ambiente real: quatro mensagens do banco após recarregar, remoção de
entrada local antiga, reuniões bloqueadas e retomada pelo conflito `409`.
A migração inicial foi aplicada com preservação dos 15 checkpoints anteriores;
dois turnos reais com Silas recuperaram contexto após reabrir as conexões.
Evidência em `../dev/local/silas_test_responses`.

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
- `src/conversations.ts`: tipos de apresentação e remoção da chave local legada.
- `src/chatApi.ts`: contratos e leitura paginada das conversas/mensagens no servidor.
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

## Retomada após a sessão de 07/11/2026

API (8000) e Vite (5173) foram encerrados por solicitação do Idealizador; as portas
foram conferidas livres. A aba de resultado foi deixada para consulta, mas o site
não responde até os servidores serem iniciados novamente. Não há tarefa rodando
em segundo plano a ser retomada pelo assistente.

O envio real de dois turnos foi feito por HTTP em processo; o navegador verificou
recarga/retomada do histórico e fez QA controlado do compositor, sem novas chamadas
ao modelo. Envio real pelo compositor ainda é uma pendência, distinta da validação
já concluída do backend. Consulte [o ponto de retomada](../dev/retomada-2026-11-07.md).

Para os erros de Keychain observados no ambiente, testes e build passaram com
`NODE_OPTIONS='--use-bundled-ca --no-use-system-ca'` apenas no comando; TLS segue
habilitado e nenhuma configuração permanente do Node foi alterada.
