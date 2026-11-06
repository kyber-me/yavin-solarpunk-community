# Arte do laboratório

`laboratorio.png` é o elemento isolado da estação científica aprovada no
[sketch v3](../../sketches/laboratorio-v3.md).

- Formato: PNG RGBA, 1536 × 1024, com transparência real.
- Conteúdo: edifício, equipamentos, vegetação e terreno imediato.
- Geração: ferramenta integrada de imagens, usando a v3 como origem.
- [Prompt integral](../../sketches/laboratorio-asset.prompt.txt).

Os textos, botões, foco e área clicável são construídos separadamente em HTML/SVG
no componente `MapView`. A arte não contém a interface. O SVG usa o mesmo sistema
de coordenadas 1536 × 1024 para manter a área interativa alinhada ao edifício.

A ilustração é uma representação visual, não um projeto arquitetônico executável.

## Referência da oficina solar urbana

**Natureza:** referência visual fornecida pelo Idealizador; não é registro de
moradores, instalações ou atividades reais de Yavin.

`oficina-solar.jpg` é uma cópia otimizada (805 × 1000, aproximadamente 348 kB) de
`sketches/Gemini_Generated_Image_fn1i5dfn1i5dfn1i.jpg`, também anexada pelo
Idealizador durante a segunda tentativa de redesign. O arquivo original foi
preservado. A versão de interface foi redimensionada e comprimida, sem geração
ou alteração do conteúdo da cena.

O componente `WorkshopReference` usa recorte responsivo e uma legenda explícita
de referência visual. A imagem orienta a convivência entre pessoas, materiais,
ferramentas, energia e vegetação, sem atribuir identidades fictícias aos retratados.

## Silas

**Natureza:** assets visuais aprovados para aplicação inicial pelo Idealizador.

- `silas-avatar.png`: 256 × 256, derivado do avatar amarelo pixelado.
- `silas-mapa.png`: 512 × 768, com alpha preservado, derivado da figura de corpo inteiro.

Os originais, prompts de geração e registro de aplicação estão em
[`sketches/silas/`](../../sketches/silas/README.md). Os derivados foram
redimensionados para uso na interface; o conteúdo do personagem foi preservado.
A figura de mapa permanece estática e compartilha o plano da estação no SVG.
