# Refactoring como apoio à revisão

**Natureza:** referência técnica de desenvolvimento. **Consultado em:** 08/11/2026.

## Fontes primárias

- [Martin Fowler — Refactoring](https://refactoring.com/): mudanças internas em
  passos pequenos, preservando comportamento observável.
- [Catálogo de refactorings](https://refactoring.com/catalog/): localizar uma
  transformação pelo problema concreto, sem aplicar um catálogo inteiro.
- [Extract Function](https://refactoring.com/catalog/extractFunction.html):
  referência possível para uma responsabilidade que merece nome próprio.
- [Replace Nested Conditional with Guard Clauses](https://refactoring.com/catalog/replaceNestedConditionalWithGuardClauses.html):
  referência possível para condicionais aninhadas.
- [Google — padrão de revisão](https://google.github.io/eng-practices/review/reviewer/standard.html):
  avaliar melhoria suficiente e distinguir preferência pessoal de necessidade.
- [Google — o que observar](https://google.github.io/eng-practices/review/reviewer/looking-for.html):
  apoio para examinar design, comportamento e testes no contexto da mudança.

Essas fontes são consultáveis por link, não uma base RAG ou biblioteca embutida.
As notas acima não reproduzem capítulos ou exemplos. Consulte a página pertinente
quando precisar fundamentar uma recomendação específica; registre o link no achado.
Se a fonte estiver inacessível, declare a limitação e não alegue tê-la consultado.

## Aplicação no harness

Antes de propor refactoring, descreva o custo observado de manter a estrutura
atual, a menor transformação útil e como verificar preservação do comportamento.
Considere ordem dos efeitos, exceções, transações, autoria e contratos HTTP.
Uma correção que muda comportamento é correção funcional, mesmo que também
melhore a estrutura.

Não recomendar extração de função só por tamanho, nem guard clauses sem conferir
a ordem das condições. Nome do padrão não é evidência de problema. Aplicar
arquitetura hexagonal, criar interfaces ou duplicar modelos exige necessidade
concreta; não são critérios universais de aceite.

Por padrão, uma sugestão de refatoração é não bloqueante. Só exija mudança
estrutural nesta entrega quando demonstrar necessidade para um critério aprovado,
contrato ou risco concreto do escopo; explicite esse vínculo. Nenhuma sugestão
autoriza implementação ou remoção de comentários.
