# Integridade do relatório final

**Natureza:** referência operacional de validação do harness, 08/11/2026.

JSON Schema verifica estrutura; o coordenador confere também estas relações:

1. O task_id corresponde ao diretório e a todos os registros vinculados.
   As referências de artefatos no relatório são relativas à raiz do repositório,
   enquanto referências internas do plano/revisão mantêm seu contrato próprio.
   Proibir caminhos absolutos, fuga por `..` e links para segredos.
2. Implementação/revisão e versões de plano/classificação coincidem no evento final
   do loop. Última tentativa está revisada, com snapshot entregue e revisão v2
   apontando à mesma implementação. IDs ULID não são reutilizados para outro conteúdo.
3. A revisão referenciada recomenda aprovar, com critérios atendidos, contexto novo,
   snapshot estável e nenhum bloqueio. O evento final deve estar
   `aprovado_tecnicamente`; parecer e controle não podem divergir.
4. Confira hashes do snapshot da revisão contra a entrega e os arquivos atuais,
   sem ler/emitir conteúdos sensíveis. Snapshot do relatório copia as evidências
   do snapshot aprovado, sem gerar uma aprovação implícita para estado novo.
   Arquivos removidos/renomeados requerem evidência da ausência no caminho anterior.
5. IDs de fases, tarefas e critérios remetem ao plano exato. Cada critério do plano
   aparece uma única vez e está atendido. Fases/tarefas omitidas exigem explicação;
   se a omissão contraria aceite, não gerar relatório final.
6. IDs de arquivos alterados, validações, anotações e nós são únicos em sua categoria.
   Arquivos das fases e anotações referenciam IDs da lista `arquivos_alterados`.
   Todo arquivo alterado tem fase correspondente e evidência de mudança da tarefa.
   Caminho de arquivo lido para revisão não prova que ele foi alterado.
7. Toda aresta referencia nós existentes. Arquivo do nó, quando presente, é caminho
   relativo real da implementação (pode ser dependência não modificada).
   `fluxo.disponivel: false` exige motivo e arrays vazios; quando true, exige nós,
   arestas e evidências da relação. Não precisa ser DAG: um fluxo funcional pode
   conter repetição; não confundir isso com ciclo inválido de dependências do plano.
8. Referências locais de evidências e diffs devem existir. Descreva evidência
   originada em mensagem em um registro persistido; não usar memória do agente
   como substituto de evidência. Quando faltar execucao.json, usar o relato
   explícito permitido pelo protocolo de revisão.
9. `revisao_humana` permanece pendente. Aprovação técnica não é aprovação de
   publicação, merge, execução externa ou futuras alterações.

Validações falhas ou não executadas podem constar, desde que não contrariem os
critérios e o parecer. Nunca remover essas limitações para deixar o resumo positivo.
