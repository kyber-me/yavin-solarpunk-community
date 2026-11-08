# Graphify na classificação

**Natureza:** referência operacional de desenvolvimento.
**Data:** 08/11/2026.
**Ferramenta:** [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify).

## Papel e disponibilidade

Use o Graphify como apoio opcional para investigar arquivos, classes, funções,
imports, chamadas e consumidores afetados. Ele fornece evidências; não atribui
a nota nem comprova segurança da alteração.

A [documentação de funcionamento](https://github.com/Graphify-Labs/graphify/blob/v8/docs/how-it-works.md)
descreve análise estrutural local por parsers, sem chamadas ao modelo, e extração
semântica separada de documentos e outras mídias, que pode consumir tokens.
Comece pela estrutura de código; não ative extração semântica por padrão.

Descubra a integração disponível (CLI, skill ou MCP) e confira versão/ajuda antes
de usar comandos. Não presuma flags de outra versão. Esta skill não autoriza
instalar ferramentas, alterar dependências ou fazer chamadas pagas.
Se indisponível, use busca e leitura; registre o fallback e prossiga.

## Atualidade e escopo

- Confira escopo e exclusões do índice. Registre revisão Git e alterações locais.
  Commit sozinho não comprova atualidade com arquivos staged, unstaged ou novos;
  use hashes de conteúdo/cache ou outra evidência disponível.
- Se não puder confirmar correspondência com os arquivos atuais, use o grafo
  apenas como pista e confirme relações no código. Registre atualidade como
  `nao_verificada` ou `desatualizada`, sem alegar cobertura completa.
- Se gerar/atualizar o índice estiver autorizado, limite os arquivos e identifique
  o destino dos artefatos. Exclua credenciais, arquivos de ambiente com segredos,
  ambientes virtuais, dependências instaladas e dados locais da simulação.
  Não execute a aplicação para construir o grafo estrutural.

## Investigação

1. Localize os símbolos inicialmente afetados.
2. Consulte dependências, chamadas recebidas e consumidores pertinentes.
3. Confirme as relações relevantes lendo código e contratos.
4. Registre evidências para as notas e lacunas ainda abertas. Evite carregar o
   grafo inteiro para uma tarefa localizada.

Separe relações extraídas, inferidas e ambíguas conforme os metadados disponíveis.
Confiança do extrator não é probabilidade de correção da implementação.
Ausência de aresta não comprova isolamento: chamadas dinâmicas, injeção de
dependências e contratos HTTP entre backend e frontend podem exigir inspeção adicional.
Conectividade não equivale a complexidade, risco ou fluxo de execução.

## Uso posterior

O grafo poderá apoiar revisões e visualizações didáticas. Integração com relatório
final e interface ainda não está implementada. Distinga mapa de dependências do
fluxo funcional explicado e validado.

## Grafo local de Yavin

A ferramenta isolada está disponível pelo comando `graphify`. O recorte do backend
fica em `dev/graphs/backend/graph.json`, com visualização `graph.html`. Consulte
`dev/graphs/README.md` para reprodução, escopo e conferência de atualidade.
Use `--graph dev/graphs/backend/graph.json` nas consultas a partir da raiz;
o caminho padrão do Graphify não corresponde a este recorte.
A existência do artefato não comprova que ele continua atualizado.
