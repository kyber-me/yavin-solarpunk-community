```text
       |
  \    |    /     __   __      _      __     __   ___    _   _
   \ .---. /      \ \ / /     / \     \ \   / /  |_ _|  | \ | |
----(     )----    \ V /     / _ \     \ \ / /    | |   |  \| |
   / '---' \        | |     / ___ \     \ V /     | |   | |\  |
  /    |    \       |_|    /_/   \_\     \_/     |___|  |_| \_|
       |
```

<p align="center">
  <img src="frontend/src/assets/oficina-solar.jpg" width="560" alt="Três pessoas em uma oficina numa laje, entre ferramentas, painéis solares e vegetação.">
</p>

*Oficina solar urbana — imagem de referência para o imaginário de Yavin.*

# Yavin

<!-- Natureza: apresentação pública do projeto e do protótipo de pesquisa. -->

Yavin é um laboratório experimental que investiga a construção progressiva de uma
pequena comunidade inspirada no solarpunk. Combina pesquisa, documentação e agentes
de inteligência artificial para explorar uma pergunta:

> É possível construir uma pequena sociedade autossustentável baseada em tecnologia,
> sustentabilidade e cooperação?

O projeto começa com perguntas, referências e um primeiro colaborador agêntico,
Silas. A comunidade, suas infraestruturas e suas formas de organização serão
investigadas ao longo do processo. Futuramente, um laboratório virtual poderá
relacionar os experimentos às condições de um território real brasileiro.

> Yavin não precisa nascer sabendo o que é uma comunidade ideal. Ela pode nascer tentando
> descobrir.

## Orientação solarpunk

O solarpunk oferece a Yavin um horizonte de sustentabilidade, cooperação e autonomia
comunitária. Essa orientação conecta a imaginação de futuros desejáveis às condições
materiais para realizá-los: energia, recursos, manutenção, conhecimento e organização
coletiva.

A tecnologia é examinada junto de suas consequências sociais e ambientais. Uma
solução precisa ser avaliada pelo que entrega, mas também por quem consegue
compreendê-la, mantê-la e ter acesso aos seus benefícios. Autonomia, reparabilidade,
produção local e uso responsável de recursos são questões de investigação.

A [biblioteca conceitual](./backend/src/agents/base_knowledge/manifestos/conceitos-fundamentais.md)
reúne referências como swadeshi, jugaad e low-tech, em diálogo com o
[manifesto solarpunk de referência](./backend/src/agents/base_knowledge/manifestos/manifesto-solarpunk.md).
Esses materiais alimentam a pesquisa; o manifesto autoral de Yavin permanece em elaboração.

## O que estamos investigando

A pesquisa acompanha duas frentes complementares:

- **Viabilidade da comunidade:** necessidades, recursos, infraestruturas, dependências
  externas, decisões recorrentes e pontos de vulnerabilidade.
- **Processo de investigação e decisão:** como humanos e agentes formulam perguntas,
  confrontam alternativas, reconhecem incertezas e preservam as razões de suas escolhas.

Começar quase do zero permite observar como os problemas surgem e por que certas
soluções são escolhidas. A cada etapa, a intenção é formular uma pergunta delimitada,
consultar referências, explicitar hipóteses, comparar alternativas e registrar o
que foi aprendido ou precisa ser revisto.

O modelo de iniciativa previsto é híbrido: o Idealizador pode introduzir objetivos
e restrições, enquanto o laboratório poderá identificar problemas e propor estudos.
Hipóteses, evidências, propostas e decisões aprovadas devem permanecer distinguíveis.
As justificativas e os desacordos também fazem parte do resultado.

Uma hipótese refutada ou uma limitação identificada pode ser uma contribuição útil.
Os resultados dependerão dos dados, cenários e modelos empregados; uma simulação
bem-sucedida não comprova, por si só, viabilidade no mundo real.

O [projeto de pesquisa](./backend/src/agents/base_knowledge/projeto/PROJETO_DE_PESQUISA_YAVIN.md)
detalha os objetivos, o método e os limites dessa investigação.

## Primeiro foco: energia

Geração, armazenamento, distribuição e autonomia energética formam o primeiro
campo de estudo. Ele permite relacionar necessidades materiais e escolhas coletivas:
quanto consumir, como lidar com períodos de baixa geração, o que priorizar diante
da escassez e quais dependências uma infraestrutura introduz.

O primeiro experimento ainda precisa ter sua pergunta e seus parâmetros definidos.
Localização, escala da comunidade e modelo de governança permanecem abertos e
serão aprofundados quando necessários às investigações.

## Silas e a colaboração com agentes

Silas é o primeiro colaborador agêntico de Yavin. Seu papel é ajudar a investigar,
questionar hipóteses e transformar ideias em experimentos verificáveis. Sua
[identidade inicial](./backend/src/agents/prompts/IDENTIDADE_ID_SILAS.md) orienta uma colaboração
curiosa, fundamentada e capaz de discordar, reconhecer incertezas e evitar conclusões
prematuras.

A continuidade de Silas é operacional e documental: combina instruções, referências
e estado de conversa persistido. A coordenação de múltiplos agentes é uma etapa
futura; o protótipo atual oferece conversa individual com Silas.

## Protótipo atual

Yavin está em desenvolvimento experimental. O repositório já reúne:

- Uma interface de laboratório com mapa ilustrado, navegação, modo expandido e
  chat recolhível integrado ao mapa.
- Conversas individuais com Silas por uma API local, com conversas e mensagens
  persistidas em PostgreSQL e históricos recuperados do servidor.
- Checkpoints do agente em PostgreSQL, permitindo recuperar o estado de uma
  conversa pelo seu `thread_id` entre execuções.
- Uma base documental em Markdown com registros da fundação, referências culturais,
  identidade do agente e orientação da pesquisa.

A criação persistida e a recuperação de histórico estão integradas. Dois turnos
reais com Silas confirmaram continuidade após reabrir as conexões; a interface
recupera do banco as mensagens ao recarregar. Rascunhos existem só durante a sessão.
Reuniões aguardam persistência. Simulações energéticas, execução multiagêntica e
comandos que alterem o mapa permanecem possibilidades futuras.

### Base técnica

| Componente | Tecnologias e função |
|---|---|
| Interface | React, TypeScript e Vite; mapa 2D interativo e painel de conversas. |
| API | Python e FastAPI; entrada de mensagens e serviços de aplicação. |
| Agente | LangChain e LangGraph; instruções, contexto documental, ferramentas e execução. |
| Persistência agêntica | PostgreSQL e `PostgresSaver`; checkpoints associados às threads. |
| Conhecimento documental | Markdown versionado; atas, conversas, referências e orientação da pesquisa. |
| Ambiente Python | Dependências e execução gerenciadas com `uv`. |

A arquitetura está evoluindo com o protótipo. Os checkpoints preservam o estado do
grafo; conversas e mensagens do domínio têm tabelas próprias. O frontend consulta
esses registros pela API, sem histórico em armazenamento local do navegador.

### Execução local

Para executar o backend, são necessários Python 3.14 ou superior, `uv`, acesso a um
PostgreSQL e uma chave da OpenAI para o modelo atualmente configurado. Configure
`DATABASE_URI` e `OPENAI_API_KEY` em `backend/.env`, com valores do seu ambiente.
Em ambiente novo, aplique explicitamente `backend/src/infra/db/relational/migrations/001_initial_schema.sql`
uma vez. Na inicialização, o checkpointer prepara suas tabelas; a conexão precisa de permissão
para essa operação. Chamadas ao modelo utilizam a conta associada à chave.

A partir da raiz do repositório:

```sh
cd backend
uv sync
uv run python main.py
```

A API atende em `http://127.0.0.1:8000`; a documentação dos endpoints fica em `/docs`.
Para abrir a interface, com Node.js e npm instalados, use outro terminal na raiz do repositório:

```sh
cd frontend
npm install
npm run dev
```

O frontend utiliza `http://127.0.0.1:8000` como endereço padrão da API. A configuração,
os controles do mapa e os detalhes da interface estão no
[guia do frontend](./frontend/README.md).

## Para conhecer melhor

- [Projeto de pesquisa](./backend/src/agents/base_knowledge/projeto/PROJETO_DE_PESQUISA_YAVIN.md):
  problema, objetivos, recorte e limites.
- [Ata de fundação](./backend/src/agents/base_knowledge/atas/ATA_001_Fundacao_de_Yavin.md):
  diretrizes iniciais e questões abertas.
- [Conversa de fundação](./backend/src/agents/base_knowledge/transcriptions/CONVERSA_001_A_Fundacao_de_Yavin.md):
  reconstrução editorial dos argumentos que deram origem ao projeto.
- [Referências culturais](./backend/src/agents/base_knowledge/manifestos/): estudos que
  alimentam a orientação solarpunk.
- [Backlog](./BACKLOG.md): andamento do desenvolvimento e próximos passos.
