# Parecer e achados

**Natureza:** regras operacionais de revisão de desenvolvimento.

- `aprovar`: todos os critérios do plano atendidos com evidência, contexto novo,
  snapshot estável e nenhum achado bloqueante. Podem existir melhorias opcionais.
- `solicitar_correcoes`: existe falha demonstrada em critério ou achado bloqueante
  do escopo. Identifique a menor mudança e o modo de verificar a correção.
- `inconclusiva`: faltam evidências essenciais, isolamento não comprovado ou o
  snapshot mudou. Não preencher lacunas com aprovação nem com defeitos inventados.

Uma falha conhecida pode justificar correção mesmo com outras lacunas; explicite
as limitações. Sem bloqueio demonstrado, critério não verificado leva a parecer
inconclusivo. Critérios sabidamente não atendidos não permitem aprovação.

Gravidade indica consequência: crítica (perda/exposição grave ou bloqueio amplo),
alta (fluxo essencial comprometido), média (efeito delimitado ou manutenção concreta)
e baixa (melhoria pequena). `bloqueante` indica necessidade para aceite desta tarefa,
não apenas gravidade abstrata. Preferências de estilo são sempre não bloqueantes.

Para bloqueio, forneça evidência do código, reprodução ou violação de contrato,
com cenário plausível. Para hipóteses, indique incerteza e investigação em vez de
afirmar falha. Pendência preexistente só impede aceite quando viola requisito
aprovado do escopo ou foi agravada pela mudança, justificando essa relação.

Os achados são recomendações revisáveis. Implementador pode corrigir, contestar
com evidência ou propor adiar item não bloqueante. Não elevar estilo a bloqueio
para encerrar uma divergência. Não exigir perfeição nem cobertura/testes sem
relação com os critérios e riscos observados.

O parecer técnico não encerra a revisão humana e não marca nada como revisado
pelo Idealizador. Persistência de respostas aos achados e revisão humana ainda
precisam de contrato próprio; não inventar esses estados.
