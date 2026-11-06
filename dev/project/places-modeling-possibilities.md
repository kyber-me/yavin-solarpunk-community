# Possibilidades para a modelagem de places

**Natureza:** referência de modelagem e hipóteses de trabalho  
**Data:** 04 de novembro de 2026  
**Estado:** não constitui decisão de arquitetura nem contrato definitivo do domínio

## Objetivo

Registrar possibilidades para a evolução de `src/infra/places.json` sem antecipar
decisões sobre o mundo persistente, os ambientes experimentais ou a arquitetura
definitiva de Yavin.

Os arquivos em `src/infra/` continuam sendo configurações em desenvolvimento.
Este documento existe para preservar o raciocínio e orientar uma decisão posterior.

## Estado atual

O arquivo possui um lugar inicial:

```json
{
  "id": "plac_01M6M3WY7SKG1M98TJSKTTY1XA",
  "name": "Central Lab",
  "type": "Laboratory",
  "status": "active",
  "aproximmate_size": null,
  "position": {
    "x": 0,
    "y": 0,
    "z": 0
  }
}
```

O identificador do lugar já utiliza um prefixo próprio (`plac_`), separado do
identificador de cidadão. O campo `aproximmate_size` ainda contém um erro de
grafia e não tem formato definido.

## Possibilidades registradas

### Identidade

- Manter IDs estáveis e distintos por tipo de entidade, como `plac_...` para
  lugares e `cit_...` para cidadãos.
- Usar nomes legíveis para lugares sem depender deles como identificadores.
- Considerar futuramente um campo de descrição quando houver conteúdo
  institucional ou histórico próprio do lugar.

### Classificação

O campo `type` pode distinguir categorias de lugar, por exemplo:

```text
laboratory
building
district
experimental_environment
natural_area
infrastructure
```

Usar valores padronizados em minúsculas evita que `Laboratory`, `laboratory` e
outras variações sejam tratados como categorias diferentes. A lista acima é
apenas uma possibilidade; ainda não é um vocabulário aprovado.

### Estado

O campo `status` pode indicar o estado operacional do lugar:

```text
planned
active
experimental
inactive
decommissioned
```

Os valores devem ser definidos somente quando houver comportamento associado a
eles. No estágio atual, `active` descreve a estação apresentada no protótipo,
mas não comprova que exista um ciclo de vida implementado.

### Tamanho

`aproximmate_size` pode ser:

- corrigido para `approximate_size`;
- removido enquanto a noção de tamanho não for necessária;
- substituído por uma estrutura explícita, caso seja necessário distinguir área,
  volume, escala visual ou capacidade.

Não é recomendável escolher uma unidade ou formato antes de saber se o campo
representará o espaço conceitual, físico ou visual do lugar.

### Posição e representação

`position` parece descrever a representação espacial no mapa. A estrutura
tridimensional atual pode ser preservada para o protótipo:

```json
"position": {
  "x": 0,
  "y": 0,
  "z": 0
}
```

Mais adiante, pode ser necessário separar a identidade do lugar de sua
representação em uma interface, especialmente se o mesmo lugar tiver posições
ou visualizações diferentes em mapas ou ambientes experimentais.

### Espaço de pertencimento

Quando o sistema representar mais de um ambiente, pode ser útil registrar onde
o lugar existe:

```json
"space": "persistent_world"
```

Possíveis valores:

```text
persistent_world
experimental_environment
laboratory
```

Esse campo não deve ser adicionado apenas para antecipar a arquitetura. Ele se
torna relevante quando o backend precisar diferenciar o mundo persistente dos
ambientes temporários e do laboratório que conduz as investigações.

## Estrutura possível para uma etapa futura

Caso os conceitos acima se tornem necessários, uma forma de organização seria:

```json
{
  "places": [
    {
      "id": "plac_central_lab",
      "name": "Central Laboratory",
      "type": "laboratory",
      "status": "active",
      "space": "persistent_world",
      "position": {
        "x": 0,
        "y": 0,
        "z": 0
      }
    }
  ]
}
```

Este exemplo é ilustrativo. Não substitui o arquivo atual nem deve ser tratado
como schema aprovado.

## Questões em aberto

- `type` representa uma categoria física, institucional, visual ou uma combinação
  dessas dimensões?
- `status` terá comportamento no domínio ou será apenas metadado de configuração?
- `position` pertence ao lugar ou ao mapa que o exibe?
- O laboratório está no mundo persistente ou é um ambiente separado?
- Será necessário modelar relações entre lugares, como pertencimento,
  vizinhança ou conexão?
- O tamanho será necessário para o MVP ou pode permanecer ausente?

## Próximo passo sugerido

Antes de transformar este arquivo em um contrato efetivo, escolher um único uso
concreto para `places`: carregar o lugar inicial no modelo de mundo, exibi-lo no
frontend ou apenas catalogá-lo como configuração. A modelagem deve evoluir a
partir desse uso observado.
