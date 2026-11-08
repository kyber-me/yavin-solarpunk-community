---
name: relatar-implementacao
description: Gera relatorio-final.json para a interface de revisão humana após aprovação técnica independente de implementação no backend. Consolida fases executadas, arquivos alterados, critérios, validações, anotações e referências. Não implementa código nem marca revisão humana como feita.
---

# Relatar implementação aprovada

**Natureza:** procedimento de documentação de desenvolvimento; fora da memória da simulação.

Use o [schema do relatório](references/relatorio-final.schema.json) e
[as regras de integridade](references/integridade.md). O coordenador do harness
gera este artefato após encerrar o loop como aprovado tecnicamente. Não precisa
criar outro agente ou executar novamente a implementação para redigir o relatório.

## Entrada e condição de geração

Requer classificação e plano em versões exatas, implementação identificada por
ULID, revisão v2 aprovada com review_id/implementation_id correspondentes,
evento final do loop aprovado e evidências de execução da entrega examinada.
Não inferir aprovação por ausência de achados, testes verdes, esgotamento do limite
ou relato do implementador. O parecer precisa ser explicitamente `aprovar`.

Valide os registros e confira o snapshot atual antes de gerar. Confirme critérios
atendidos, isolamento do revisor, ausência de bloqueios e de alterações durante
a revisão. Se código/snapshot mudou após a aprovação, informe a divergência e
não emita relatório aprovado sobre a versão nova. Não reeditar o parecer antigo.
Relatórios históricos v1 sem identidade de entrega permanecem legíveis, mas não
ganham IDs/garantias retroativos só para satisfazer esta skill.

## Consolidação para a interface

- Resuma objetivo e comportamento entregue em linguagem simples.
- Liste só arquivos realmente alterados pela tarefa, distinguindo adição,
  modificação, remoção e renomeação, com caminho anterior quando pertinente.
  Não atribua todo o working tree compartilhado à implementação.
- Cruze plano com evidências: fase e tarefa planejadas não comprovam execução.
  Descreva o que foi efetivamente realizado e referencie os registros.
- Relacione critérios atendidos e validações. Preserve falhas conhecidas e checagens
  não executadas; aprovação técnica não equivale a suíte inteira aprovada.
- Anotações explicam decisões, limites, sugestões e pendências não bloqueantes.
  Nenhuma anotação pode ocultar bloqueio aberto ou transformar proposta em decisão.
- Inclua fluxo funcional didático quando sustentado por código/evidências:
  nós com IDs, arquivos e símbolos; arestas com relação e evidências. Não usar
  dependências do plano ou arestas do Graphify como prova de ordem de execução.
  Se não há fluxo funcional útil (p.ex. migração de diretórios), `disponivel: false`,
  explique o motivo e deixe nós/arestas vazios.
- Arquivos, relações e artefatos devem ser navegáveis por caminhos relativos à
  raiz do repositório. `diff_ref` pode ser null se não houver diff preservado;
  explique a lacuna. Não reconstruir conteúdo anterior imaginário.

O relatório é uma projeção resumida dos registros completos, não sua substituição.
Use evidências curtas e links/caminhos de artefatos; não incorpore código completo,
logs extensos, conteúdo de ambiente, segredos ou estado local da simulação.
Identifique dados ausentes e interrompa quando faltarem requisitos de aprovação.

## Persistência e revisão humana

Gere report_id ULID e grave `relatorio-final.json` no diretório datado da tarefa.
Use `relatorio-final-002.json` etc. para nova consolidação, preservando anteriores
e explicando a razão em `observacoes`. Copie task_id, implementation_id e review_id
dos registros; não crie uma nova implementação apenas para escrever o relatório.

`gerado_em` inclui fuso; `status_tecnico` é `aprovado` e `revisao_humana`
começa obrigatoriamente como `pendente`. Não marcar a leitura/revisão do Idealizador
por inferência. O relatório e seus hashes são imutáveis: a futura interface deve
persistir a avaliação humana separadamente, ligada ao report_id e ao snapshot.
Esse mecanismo ainda não foi implementado.

Antes de entregar: valide schema e integridade semântica. Apresente o caminho,
resumo da entrega e limitações relevantes. Se a gravação ou validação falhar,
informe o impedimento; não declare o relatório entregue.

Criar a skill não constrói a interface nem produz relatório retroativo de tarefas
que não possuam o pacote mínimo. Não implementa categorias de execução/autorização
ou captura de versões que ainda estejam pendentes.
