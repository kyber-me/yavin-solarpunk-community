# Revisão Parcial

### 1. Otimização da consulta de agentes

Atualmente, ao listar os agentes para o Frontend, o Backend realiza um `JOIN` com o documento de identidade de cada agente.

**É realmente necessário executar essa operação?**

O documento de identidade, responsável por descrever o comportamento e as características internas do agente, deve ser tratado como uma informação de domínio que não precisa ser exposta ao Cliente.

Como esse documento não é retornado ao Frontend, o `JOIN` representa uma operação desnecessária, que pode ser eliminada para simplificar a consulta e evitar o carregamento de dados que não serão utilizados.

**Proposta:** adicionar um campo de `personality` ao modelo do agente, contendo uma descrição sintética de sua personalidade, identidade e papel. Esse campo será utilizado pelo Frontend para apresentar o agente ao usuário, sem expor seu documento de identidade completo.

### 2. Imagem de perfil do agente

Outro ponto identificado é a ausência de uma URL para a imagem de perfil do agente.

**Proposta:** incluir um campo `avatar_url` na representação do agente e implementar uma solução parametrizável para o armazenamento e a recuperação dessas imagens.

Para isso, podemos adotar uma abordagem baseada em **Adapter**, definindo uma interface abstrata de `Storage` que desacople a lógica de domínio da infraestrutura utilizada para armazenar os arquivos.

A implementação inicial poderá utilizar Google Drive ou outro serviço simples de armazenamento, mantendo a possibilidade de substituição futura sem alterações significativas na lógica da aplicação.

### 3. Ajustes propostos

- Remover o `JOIN` com o documento de identidade na consulta de listagem dos agentes, desde que nenhuma outra etapa da operação dependa desses dados.
- Adicionar o campo `personality` para representar, de forma resumida, a identidade e as características do agente no Frontend.
- Incluir o campo `avatar_url` na representação retornada pela API.
- Definir uma interface de `Storage` para abstrair as operações de armazenamento e recuperação de arquivos.
- Implementar um Adapter inicial para o provedor de armazenamento escolhido, mantendo a infraestrutura configurável e substituível.
