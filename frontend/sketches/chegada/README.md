# Chegada de Yavin — observatório de futuros

**Natureza:** proposta visual e registro de protótipo de frontend, sujeita à avaliação.
**Data:** 08/11/2026.
**Estado:** paisagem, cachoeira, reflexos nos vidros e lente convexa aprovados visualmente pelo Idealizador; publicação do estado da visita pendente.

Data: 08/11/2026.
Questão: criar uma chegada imersiva para visitantes, distinta do atelier do Idealizador.
Opções consideradas: botão sobre uma paisagem; visor de observação; dispositivo solar; sinalizador.
Decisão: experimentar o visor de observação, com paisagem ilustrada e ambiência opcional.
Motivo: o gesto de olhar se relaciona à investigação e à experiência de observar Yavin.
O que continua aberto: trilha definitiva e contratos de publicação do backend.
Próximo passo: definir o estado público da visita com o Idealizador em etapa própria.

A [direção artística e as referências](../direcao-artistica.md) estão preservadas
para a evolução das artes do mapa, conforme solicitado pelo Idealizador.

## Referências

- [Dear Alice, THE LINE](https://thelinestudio.com/work/chobani): atitude da ilustração, vida cotidiana, tecnologia e vegetação.
- [Conceitos de Braydan Barrett](https://braydanbarrett.artstation.com/projects/5XDNnz): objetos e robôs como parte da identidade artística.
- [Vegetal City, Luc Schuiten](https://www.vegetalcity.net/vegetal-city/): panorama e arquitetura orgânica.
- [Centro Educativo Burle Marx, Arquitetos Associados](https://arquitetosassociados.arq.br/centro-educativo-burle-marx/): integração entre arquitetura e paisagismo no Brasil.
- [Paper Planes](https://paperplanes.world/): ação simples, contemplação e ambiência. Não foram reutilizados código, gravação ou imagens.
- [Choo-Choo World, Lusion](https://lusion.co/projects/choo_choo_world/): objetos que convidam à interação.

## Protótipo

- `/` e `#/`: chegada de tela inteira, título, partículas discretas e resposta ao cursor.
- Refinamento solicitado pelo Idealizador: removidos slogans auxiliares, subtítulo,
  rótulo do visor e rodapé. Manter espaço livre para a paisagem, sem preencher cada
  região com texto. O título principal, a marca, o CTA e o controle de som permanecem.
- A lente frontal foi percebida como bússola; a tentativa de perspectiva em SVG
  também foi rejeitada. A versão atual usa uma luneta 3D local em Three.js, com
  câmera, iluminação, orientação e sombra reais. O conjunto visual atual foi aprovado.
- Arraste a luneta ou use as setas para direcionar; Home retorna à estação.
  Tocar em uma parte da paisagem também aponta para ela, considerando o recorte
  e a transformação da imagem. A ampliação varia entre 2× e 6×. A ocular e a
  janela óptica acompanham o ponto observado.
- `Entrar` é uma ação separada da exploração. A transição parte da região da
  luneta, escurece e revela `#/visita`. Movimento reduzido remove espera e animações.
- Composição refinada a pedido do Idealizador: luneta deslocada para a esquerda,
  sem encostar na borda, sobre o piso da varanda. Botão `Entrar` separado no lado
  oposto; controle de ampliação permanece junto da luneta. Desktop e celular
  conferidos sem sobreposição entre controles.
- Parallax com até 34 px horizontais e 22 px verticais, resposta de 0,4 s e
  arraste por toque. A sensibilidade foi reduzida em cerca de 20% após avaliação
  do Idealizador. O fundo continua sendo a imagem aprovada, sem alteração do asset.
- Cachoeira discreta, reflexos na água, passagem de luz pelos vidros do telhado e
  variação suave de luz são desenhados em canvas transparente sobre a paisagem.
  O mesmo quadro alimenta a lupa e a ocular 3D em tempo real. A lente recebeu
  brilho, borda e sombreamento para sugerir uma superfície convexa, sem deformar
  a imagem observada. O Idealizador aprovou visualmente o resultado em 08/11.
  O PNG estático permanece intacto; movimento reduzido oculta os efeitos.
- Seleção e arraste nativo bloqueados apenas na chegada, evitando que o gesto
  selecione título e controles. A leitura do manifesto permanece selecionável.
- Rodapé branco e seus textos removidos da visita a pedido do Idealizador;
  o mapa ocupa o espaço liberado. A natureza de prévia visual permanece registrada aqui.
- Título atualizado para “O futuro tem lugar”, conforme solicitação.
- `#/visita`: reaproveita o mapa existente, com câmera e personagens estáticos, sem links para conversa, bancada ou ações de chat. Não monta o painel nem consulta a API numa visita iniciada pela entrada.
- `#/mapa` e `#/laboratorio`: atelier existente preservado, disponível diretamente pelas rotas locais. Ao voltar à chegada, a instância já aberta do atelier continua montada, preservando seus estados; essa retenção pode manter requisições iniciadas anteriormente.
- Som habilitado por padrão por solicitação posterior do Idealizador. Camada
  harmônica original sintetizada pela Web Audio API: tenta reprodução automática;
  quando o navegador bloqueia, começa na primeira interação. O controle distingue
  preferência habilitada de reprodução efetiva ("Som ao interagir" / "Som ligado").
  Mantém a música e a opção de silenciar na transição entre chegada e visita.
  Suspende na aba oculta e encerra ao entrar no atelier. Não é uma gravação nem uma trilha final.

**Relato posterior do Idealizador:** o som não desliga pelo controle. A causa e as
condições ainda não foram investigadas; correção registrada no backlog, sem prioridade.

A separação é de apresentação, não autenticação. As rotas antigas continuam acessíveis
diretamente no protótipo local. Publicação real exige controles de backend.

O mapa desta entrega é uma prévia visual estática. Não representa um estado público
mantido pelo servidor. Conversas públicas e balões não foram simulados nem publicados.
São incrementos dependentes de contratos de backend, fora deste protótipo.

## Paisagem e aprovação

A ferramenta integrada `image_gen` não está disponível nesta sessão. O Idealizador
escolheu Higgsfield. A chamada com modelo `gpt_image_2_6`, proporção `16:9` e uma
imagem foi rejeitada com `Requires basic plan or higher.` (`INVALID_ARGUMENT`).
Não houve imagem gerada ou identificador de job retornado por essa tentativa.
Após autorização explícita, a paisagem foi gerada pela API OpenAI via CLI da skill
`imagegen`, modelo `gpt-image-2`, qualidade alta, tamanho 2048 × 1152, sem alteração
de configuração ou dependências do backend. O Idealizador aprovou a imagem e
estendeu a direção artística às futuras implementações no mapa.

O [prompt](paisagem-v1.prompt.txt) prepara uma ilustração original: comunidade
solarpunk em paisagem tropical, pequenos robôs utilitários, estação científica,
varandas, caminhos e jardins. É uma projeção imaginada, sem definir a localização
real ou atribuir atividades fictícias ao projeto atual.

Asset integrado: `frontend/public/images/yavin-chegada-v1.png`.
O visor é desenhado separadamente para continuar interativo.

O [prompt final](paisagem-v1.final.prompt.txt), inicialmente submetido ao Higgsfield
e depois usado na API OpenAI, preserva a direção do estudo inicial, com composição
panorâmica e área sombreada para o título.

## Verificações desta etapa

- Oito testes existentes aprovados; TypeScript e build Vite concluídos.
- Navegador: som ligado/desligado, entrada por botão e Enter, transição, foco no
  título do mapa, ausência de controles de chat e de chamadas à API no percurso de visita.
- Layout sem overflow horizontal em 1200 × 853 e 390 × 844; movimento reduzido
  remove animações. Conferida ausência de IDs duplicados após abrir atelier e visita.
- Acesso ao atelier e acionamento da expansão preservados. Sem envio de mensagem,
  chamada a Silas, início de API ou modificação do backend.
- Paisagem carregada em 2048 × 1152; composição sem overflow em 1440 × 960 e
  390 × 844. Avaliação da integração do visor, escuta humana da ambiência e
  otimização de mídia permanecem pendentes.
- Ajuste de áudio verificado no navegador: preferência habilitada inicialmente;
  contexto suspenso pelo navegador até o primeiro gesto, reprodução iniciada nesse
  gesto, mesmo contexto mantido ao entrar no mapa; silenciar encerra o contexto e
  permanece ao voltar ao mirante. Reativação e encerramento no atelier conferidos.
- Efeitos de água e luz conferidos na chegada e na lente; movimento reduzido
  limpa a camada animada. Hash SHA-256 do original conferido antes e depois,
  sem mudança.

Performance, formatos e tamanhos de mídia serão avaliados depois da direção visual,
conforme solicitado pelo Idealizador. Three.js e seus tipos foram adicionados ao
frontend para a luneta; o mapa não foi convertido para uma engine 3D. O build
conclui com aviso de bundle acima de 500 kB, registrado para essa etapa posterior.
