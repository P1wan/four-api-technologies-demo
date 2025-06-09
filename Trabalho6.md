Claro, aqui está o documento em português, com as informações do PDF e da transcrição da aula, priorizando a transcrição:

**Trabalho 6: Comparação de Tecnologias de Invocação de Serviços Remotos**

**I. Objetivo**

O principal objetivo deste trabalho é comparar e ilustrar as principais similaridades e diferenças entre quatro tecnologias de invocação de serviços remotos: SOAP, REST, GraphQL e gRPC. Esta comparação será realizada através de:

* Pesquisa sobre a origem, principais características, vantagens e desvantagens de cada tecnologia.  
* Implementação de um serviço de streaming de músicas utilizando cada uma das tecnologias.  
* Realização de testes de carga para comparar o desempenho das diferentes tecnologias sob diversas cargas de trabalho.

**II. Formação de Grupos**

Os alunos deverão se organizar em grupos de 2 a 5 integrantes. (Informação da transcrição, o PDF indica 2-3 alunos. A transcrição verbal do professor permite grupos maiores para facilitar a divisão de tarefas).

**III. Serviço a Ser Implementado: Serviço de Streaming de Músicas**

O serviço a ser implementado deve permitir o gerenciamento (criação, consulta, alteração e remoção) de três tipos de recursos: usuários, músicas e playlists. Estes recursos devem estar relacionados de acordo com o diagrama abaixo:

* **Usuários**: Possuem ID, Nome e Idade.  
* **Músicas**: Possuem ID, Nome e Artista.  
* **Playlists**: Possuem ID e Nome. Um usuário pode ter 0 ou mais playlists, e uma playlist pode ter 0 ou mais músicas.

O serviço deverá ser capaz de realizar as seguintes consultas a partir da invocação de suas operações:

* Listar os dados de todos os usuários do serviço.  
* Listar os dados de todas as músicas mantidas pelo serviço.  
* Listar os dados de todas as playlists de um determinado usuário.  
* Listar os dados de todas as músicas de uma determinada playlist.  
* Listar os dados de todas as playlists que contêm uma determinada música.

Os alunos deverão pré-cadastrar dados (usuários, músicas, playlists) para os testes. Embora o serviço deva suportar operações CRUD completas, os testes de carga focarão principalmente em operações de consulta para evitar alterações de estado. Para os testes de carga, é recomendado utilizar uma quantidade significativa de dados (ex: 1000 músicas, 1000 usuários) para que as diferenças de desempenho sejam mais evidentes.

**IV. Requisitos de Implementação**

* **Implementação em Duas Linguagens**: As versões do servidor e dos clientes para as quatro tecnologias devem ser implementadas em pelo menos duas linguagens de programação diferentes. Por exemplo, o *backend* pode ser feito em Java e os clientes em Python, ou vice-versa. (Informação da transcrição, o PDF não especifica a quantidade de linguagens, apenas "uma mesma linguagem de programação, a ser escolhida pela equipe" ).  
* **Serviços Separados por Tecnologia**: Cada uma das quatro tecnologias (SOAP, REST, GraphQL e gRPC) deverá ter sua própria implementação do serviço de música. Isso significa que haverá quatro versões distintas do serviço rodando, cada uma acessível através de uma das tecnologias de invocação remota.  
* **Clientes Separados por Tecnologia**: Para cada tecnologia de serviço, um cliente correspondente será implementado para invocar esse serviço específico. Ou seja, um cliente SOAP para o serviço SOAP, um cliente REST para o serviço REST, e assim por diante.  
* **Exemplos de Código**: A apresentação deve incluir exemplos de código na(s) linguagem(ns) de programação escolhida(s) para cada tecnologia de invocação remota.

**V. Entregáveis**

O principal entregável será uma apresentação de slides, compartilhada no Google Drive, contendo:

1. Identificação dos membros de cada equipe.  
2. Descrição da origem, características, e vantagens e desvantagens de cada tecnologia de invocação remota.  
3. Exemplos de código em uma mesma linguagem de programação, a ser escolhida pela equipe (para cada tecnologia).  
4. Análise crítica das quatro tecnologias, baseada na experiência da equipe na implementação do serviço de streaming de músicas na linguagem escolhida e nos resultados dos testes de carga.  
5. Gráficos ilustrando os resultados dos testes de carga.

**VI. Testes de Carga**

Os testes de carga são uma parte fundamental do trabalho, visando comparar o desempenho das diferentes tecnologias. Será necessário simular múltiplos clientes (ex: 100 clientes) realizando chamadas concorrentes aos *backends* para medir o tempo de resposta e observar as diferenças de desempenho entre SOAP, REST, GraphQL e gRPC. A metodologia exata dos testes de carga será definida posteriormente.

