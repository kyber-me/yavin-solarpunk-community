---
name: classificar-tarefa
description: Classifica tarefas de implementação delegadas no backend de 1 a 5 por complexidade e risco, com evidências do código e apoio opcional do Graphify. Use antes de implementar features ou alterações no backend; exclui frontend, perguntas conceituais e retomadas de contexto.
---

# Classificar tarefa

**Natureza:** procedimento de desenvolvimento, fora do contexto dos agentes da simulação.

Leia [a rubrica](references/rubrica.md) antes de atribuir notas. O modo de
colaboração está fora da classificação: este fluxo parte da delegação no backend.
Tarefas exclusivas de frontend não passam por este fluxo. Em tarefas mistas,
classifique a parcela do backend e considere os consumidores frontend como
evidência de impacto dos contratos.

## Procedimento

1. Identifique objetivo, comportamento esperado, limites e instruções aplicáveis
   do projeto. Inspecione arquivos, contratos e verificações relacionados, sem
   implementar ou executar módulos com efeitos colaterais.
2. Investigue o alcance por busca e leitura. Quando houver Graphify disponível,
   siga [a orientação de análise](references/graphify.md). Consulte apenas o
   subgrafo pertinente; confirme no código as relações relevantes.
3. Atribua complexidade e risco segundo a rubrica. Justifique cada nota com
   arquivos/símbolos e consequências concretas; separe fatos de hipóteses.
4. Calcule `nivel = max(complexidade, risco)`. Informe incertezas, se a avaliação
   é provisória e qual investigação poderia mudar a nota. Não invente evidências.
5. Persista e apresente a classificação antes das edições. A nota não concede autorização
   de implementação: respeite as atribuições e autorizações do projeto.
   Reclassifique quando escopo, dependências ou consequências mudarem.

## Resultado

Valide o resultado segundo [o schema](references/classificacao.schema.json).
Salve cada classificação em
`dev/harness/AAAA-MM-DD/HHMMSS-slug-da-tarefa/classificacao.json`, na raiz do
repositório. Use a data local e timestamps ISO 8601 com fuso explícito.
O diretório identifica a tarefa (`task_id`); resolva colisões com sufixo único,
sem sobrescrever arquivos existentes. Registre a revisão Git, lembrando que
arquivos locais podem diferir dela. Esses registros devem ser versionáveis.

Reclassificações da mesma tarefa geram `classificacao-002.json`, `-003.json`
etc. no mesmo diretório, com novo horário e justificativa da mudança no campo
`observacoes`. Preserve registros anteriores. Não grave segredos ou conteúdo
de arquivos de ambiente.

Inclua `schema_version: 1`, `task_id`, `registrado_em`, `avaliado_em`,
`origem_registro`, `revisao_git` e `observacoes`, além dos campos abaixo.
Use `origem_registro: "contemporanea"` quando registrar no momento da avaliação.
Ao recuperar uma classificação já apresentada, use `"retrospectiva"`,
`avaliado_em: null` se o horário original for desconhecido e explique a origem;
não simule um registro anterior às edições. Se a gravação falhar, informe o
impedimento antes de prosseguir com a implementação.

Exemplo ilustrativo dos campos de avaliação (acrescente os metadados acima
para produzir um registro completo):

```json
{
  "tarefa": "Alterar uma operação SQL",
  "complexidade": 2,
  "risco": 4,
  "nivel": 4,
  "justificativas": {
    "complexidade": "Operação localizada com abordagem conhecida.",
    "risco": "Modifica dados mantidos cuja recuperação exige preparação."
  },
  "evidencias": [
    {"arquivo": "caminho/relativo.sql", "simbolo": null, "observacao": "Operação que modifica registros existentes."}
  ],
  "incertezas": ["Compatibilidade dos dados ainda não verificada."],
  "classificacao_provisoria": true,
  "graphify": {
    "utilizado": false,
    "motivo": "Indisponível; usada busca e leitura.",
    "versao_ferramenta": null,
    "revisao_codigo": null,
    "estado_arquivos": null,
    "atualidade": "nao_verificada",
    "limitacoes": []
  }
}
```

Notas são inteiros de 1 a 5. Use caminhos reais nas evidências; `simbolo` pode ser
`null`. Registre versões e revisões desconhecidas como `null`. Em `estado_arquivos`,
descreva alterações locais e evidências de correspondência do índice quando
disponíveis. `atualidade` aceita `confirmada`, `desatualizada` ou `nao_verificada`.

## Transição para planejamento

Após salvar e validar a classificação, apresente o nível e o caminho do JSON.
Sugira ao Idealizador que altere a sessão para o modo Plan e, depois da alteração,
dê seu OK para iniciar o protocolo de planejamento. Aguarde esse OK: não invoque
[planejar-tarefa](../planejar-tarefa/SKILL.md) automaticamente nem comece a implementar.
Esta transição vale para todos os níveis; o nível define o detalhe do plano.

A skill não altera o modo da sessão. Confirme o modo pelas informações do ambiente;
não considere um OK prova técnica da alteração. Se a sessão ainda estiver fora do
modo Plan ou a troca não estiver disponível, explicite isso e aguarde a alteração
ou uma exceção expressa do Idealizador para planejar fora desse modo.

O OK autoriza elaborar o plano, não executar código. Após ele, siga a skill de
planejamento. A aprovação da execução será solicitada para a versão concreta do
plano apresentada. Roteamento de modelos, revisão adversarial e interface continuam
como incrementos separados.
