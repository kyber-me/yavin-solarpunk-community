# Rubrica de classificação — versão 1

**Natureza:** decisão provisória de método de desenvolvimento, calibrável pelo uso.
**Data:** 08/11/2026.
**Escopo:** implementações delegadas no backend; consumidores frontend são considerados na análise de impacto.

## Complexidade

Dificuldade de compreender, implementar e verificar a mudança. Considere lógica,
acoplamento, integrações, incerteza e dificuldade de validação.

| Nota | Âncora |
|---|---|
| 1 | Alteração localizada, solução conhecida e verificação direta. |
| 2 | Pequena mudança com algumas partes relacionadas e abordagem conhecida. |
| 3 | Coordenação entre componentes, decisões técnicas relevantes ou integração a verificar. |
| 4 | Mudança ampla ou com incerteza significativa, exigindo investigação e implementação por etapas. |
| 5 | Problema pouco definido ou com múltiplas incertezas técnicas; exige experimentos antes de consolidar a solução. |

## Risco

Consequência de uma implementação incorreta e dificuldade de recuperar o estado
anterior. Considere alcance, persistência, compatibilidade, segurança e reversibilidade
no ambiente real da tarefa.

| Nota | Âncora |
|---|---|
| 1 | Efeito restrito, facilmente reversível e sem impacto em dados persistidos. |
| 2 | Possível regressão localizada, com recuperação simples. |
| 3 | Pode comprometer um fluxo importante ou afetar consumidores de um contrato. |
| 4 | Pode causar inconsistência persistida, indisponibilidade relevante ou recuperação trabalhosa. |
| 5 | Pode provocar perda irreversível de dados, exposição de informações sensíveis ou impacto amplo de difícil recuperação. |

## Aplicação

- Escolha as âncoras sustentadas pelas evidências. Quantidade de arquivos, linhas
  ou conexões não determina as notas.
- Use `nivel = max(complexidade, risco)`, preservando ambas as justificativas.
  A regra é conservadora e ainda não foi calibrada empiricamente.
- Avalie falhas plausíveis no escopo observado, sem elevar risco por cenários
  hipotéticos sem relação concreta com a mudança.
- Informação insuficiente torna a classificação provisória; não implica nível 5.
  Explique a lacuna e a investigação necessária.
- Decompor a tarefa não elimina a avaliação da integração e do risco do conjunto.

Exemplos orientativos: corrigir texto estático pode ser 1/1 quando o efeito
restrito for confirmado; uma pequena operação SQL pode ter complexidade baixa e
risco alto sobre dados mantidos. Alterar um DTO exige investigar seus consumidores,
inclusive frontend. Um módulo muito conectado pode receber uma mudança isolada
e reversível. Os exemplos não substituem inspeção.
