---
name: revisar-implementacao
description: Revisa implementações delegadas no backend após execução, em agente com contexto novo, e gera relatório JSON por rodada. Use no harness para níveis 3 a 5 ou por pedido explícito de revisão. Coordena correções autorizadas em agente executor com limite de três tentativas; revisor não edita código. Exclui frontend exclusivo.
---

# Revisar implementação

**Natureza:** protocolo de revisão de desenvolvimento, fora da memória da simulação.

Avalie se a entrega satisfaz o plano e preserva contratos. Procure falhas e
contraexemplos, sem exigir perfeição. Esta skill não autoriza editar código,
apagar comentários autorais ou ampliar o escopo do backend.

## Coordenação do loop

Leia [as diretrizes de loop](references/loop-correcoes.md) antes de chamar agentes.
O coordenador mantém IDs, eventos e orçamento; revisor e executor retornam a ele
sem delegar. Após parecer de correção, o coordenador pode chamar executor em
contexto novo apenas com autorização e tentativa disponível. Após a entrega,
chama revisor de contexto novo. O revisor técnico continua sem editar código.

## Entrada após execução

Requer classificação e plano persistidos, código entregue e evidências de execução.
A existência de um plano não comprova execução. Enquanto `execucao.json` não
existir, aceite relatório explícito de execução (arquivo ou mensagem identificável)
com arquivos alterados e resultados reais, registrando essa fonte e suas limitações.
Sem esse pacote, informe o que falta e não fabrique uma revisão concluída.

No harness, níveis 3 a 5 passam por este protocolo após a execução. Níveis 1 e 2
podem passar por revisão por pedido explícito ou previsão do plano aprovado.
Revisão não substitui autorização de implementação.

## Contexto independente

Se você implementou a mudança, atue somente como coordenador: prepare o pacote e
invoque outro agente com contexto novo. Quando a API disponível oferecer
`fork_turns`, use `"none"`. Se não puder criar contexto separado, informe que a
revisão independente está pendente; uma releitura própria não a substitui.

O pacote inclui: instruções aplicáveis do projeto, pedido/contratos, versões exatas
de classificação e plano, arquivos/diff do escopo e sua base de comparação,
evidências de execução e permissões de validação. Exclua histórico da conversa,
argumentação do implementador, diagnóstico esperado e segredos. Preserve requisitos
e restrições: contexto novo não significa revisão sem contexto técnico.
O agente deve poder ler dependências pertinentes para confirmar o comportamento.

Se você recebeu o pacote em contexto novo, realize a revisão; não crie
recursivamente outro revisor. Revisor não edita o código. O coordenador pode
persistir sua resposta JSON se o ambiente do revisor for somente leitura,
preservando autoria e conteúdo técnico.

Use o modelo configurado/disponível e registre seu nome somente se conhecido.
Esta skill não implementa roteamento por nível nem presume disponibilidade de um
modelo superior. Contexto independente reduz influência, mas não garante ausência
de vieses nem prova diversidade de modelos.

## Revisão

1. Leia o plano e identifique os critérios de aceitação. Delimite o diff antes de
   revisar: não atribua todo o working tree compartilhado à tarefa.
2. Registre revisão Git quando existir e SHA-256 dos arquivos do escopo. Considere
   mudanças staged, unstaged e novas; commit sozinho não identifica a entrega.
   Compare os hashes no fim. Mudança durante revisão torna a recomendação
   inconclusiva até avaliar o snapshot correto.
3. Inspecione contratos, caminhos de sucesso/falha, limites e integrações relevantes.
   Confira testes e execute apenas verificações permitidas, proporcionais e sem
   efeitos externos não autorizados. Não importar entrypoints experimentais como
   diagnóstico inocente. Distinga validação própria de resultado do implementador.
4. Para cada critério, registre atendido, não atendido ou não verificado, com
   evidência. Observe as perguntas e notas autorais; conclusões com `(?)` devem
   ser discutidas sem apagar comentários.
5. Leia [as referências de refactoring](references/refactoring.md) ao avaliar
   manutenção/refatoração. Use Graphify quando útil e atualizado; confirme relações
   no código. Arquitetura, desempenho e concorrência exigem cenário concreto.
6. Gere achados localizados com problema, causa, consequência prática, evidência
   e menor correção. Separe falha funcional, manutenção/desempenho e estilo.
   Identifique se foi introduzido, preexistente ou não determinado. Não transforme
   pendências antigas fora do escopo em bloqueios novos.
7. Aplique [as regras de parecer](references/parecer.md), valide e entregue o JSON.

Não invente um número mínimo de achados. Relatório sem problemas é válido se
sustentado pelas verificações. Não chamar o modelo de aprovação humana.

## Registro por rodada

Valide pelo [schema](references/revisao.schema.json). Salve
`revisao-001.json`, `revisao-002.json` etc. no diretório datado da tarefa, com
mesmo `task_id`. Referências de classificação/plano são relativas a esse diretório
e apontam para versões exatas. Não sobrescreva rodadas anteriores.
`evidencias_execucao` identifica arquivos ou mensagens concretas, sem copiar segredos.

IDs de achados e de critérios são únicos; critérios devem corresponder exatamente
aos do plano. Achados só referenciam critérios existentes. Arquivos revisados e
locais de achados devem pertencer ao snapshot declarado. Datas incluem fuso.
Registre identidade/modelo desconhecidos como `null`; nunca invente isolamento.

O relatório retorna ao implementador. Corrigir depende do escopo aprovado; revisão
não concede autorização extra. Registre contestação com evidências, não obediência
automática ao revisor. Nova revisão deve verificar o novo snapshot, as correções
e possíveis regressões, mantendo o histórico.

O revisor realiza uma rodada e retorna. O coordenador aplica o loop limitado
descrito na referência: três tentativas totais, incluindo a inicial, com eventos
persistidos antes das chamadas. Não há correção automática sem autorização,
repetição ilimitada ou aprovação por esgotar orçamento. Roteamento continua
pendente. Parecer inconclusivo não equivale a aprovação.


## Relatório após aprovação

Ao validar parecer favorável e encerrar o controle como aprovado tecnicamente,
o coordenador aplica [relatar-implementacao](../relatar-implementacao/SKILL.md).
O relatório reúne arquivos alterados, fases executadas, validações e anotações
para revisão humana, mantendo o parecer e os demais registros originais.
