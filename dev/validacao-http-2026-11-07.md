# Validação HTTP com PostgreSQL descartável

**Natureza:** registro técnico de desenvolvimento e evidência de teste.
**Data:** 07/11/2026.

## Escopo e resultado

21 testes aprovados: quatro de integração HTTP, oito de mensagens e nove de
conversas, em bancos descartáveis separados no mesmo PostgreSQL local. O servidor
escutou apenas em socket Unix e foi encerrado ao final. Nenhum acesso ao banco
do projeto nem chamada a modelo externo.

`tests/test_http_integration.py` usa TestClient com o lifespan real da API,
pool, repositórios e PostgresSaver reais. A factory do modelo é substituída por
um StateGraph determinístico que conta mensagens humanas e recupera o primeiro
turno. O carregamento documental recebe uma lista nova de referência por thread;
a qualidade do contexto e a identidade conversacional de Silas não são avaliadas.

| Cenário | Evidência |
|---|---|
| Catálogo e criação | Silas disponível; criação 201; duplicidade 409 com o mesmo ID. |
| Troca de mensagens | Entrada e resposta gravadas, autoria correta e timestamps com fuso. |
| Reinicialização | Após fechar e reabrir o lifespan e conexões, o segundo turno recupera o primeiro pelo checkpoint. |
| Isolamento | Outra dupla recebe uma thread independente, começando no primeiro turno. |
| Rejeições | Participante indisponível 422, conversa ausente 404, remetente externo 403, mensagem em branco 400, conversa inativa 409. Sem mensagens nem execução do agente. |
| Falha do agente | Erro 500, entrada confirmada preservada; uma chamada seguinte consegue prosseguir. |
| Recursos | Pool e conexão do checkpointer fechados ao sair do lifespan. |
| Schema inicial | Checkpoints criados antes da migração permanecem recuperáveis; prefixos são recusados nas chaves primárias. |

Na primeira execução o teste de isolamento falhou por reutilização da lista mutável
da fixture de contexto. A fixture foi corrigida para produzir uma lista nova; a
bateria foi repetida em outro banco vazio e passou. Não houve correção de produção
para esse resultado.

## Reprodução

`YAVIN_TEST_DB_URI` deve apontar explicitamente para banco descartável sem schema
`yavin` nem tabelas de checkpoints. A suíte cria checkpoints de teste, aplica
`001_initial_schema.sql` e mantém os dados para inspeção. Outra execução exige
um banco novo. A variável `DATABASE_URI` é substituída temporariamente no teste.

```sh
.venv/bin/python -B -m unittest discover -s tests -p test_http_integration.py -v
```

As suítes de repositório exigem bancos descartáveis próprios, também vazios.
O teste não inicia servidor TCP, navegador ou frontend; atravessa as rotas ASGI
por HTTP em processo. Não substitui a validação de uso real pela SPA com Silas.

## Atualização posterior e pendências

A primeira bateria descrita acima teve 21 testes; a posterior, com consultas de
histórico, teve 22 (cinco HTTP integrados). Depois, o schema inicial foi aplicado
ao banco do projeto e dois turnos com modelo real passaram, conforme
[registro de integração](persistencia-frontend-2026-11-07.md). API e Vite foram
encerrados a pedido do Idealizador; não permanecem rodando. Política de novas tentativas, reconciliação entre mensagens e checkpoints
e classificação mais precisa de falhas internas continuam abertas. Entrada salva
no domínio não implica que tenha sido incluída no checkpoint se o agente falhou.
