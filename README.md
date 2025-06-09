
# Serviço de Streaming de Músicas - Demonstração de Tecnologias Distribuídas

Este projeto demonstra diferentes tecnologias de invocação remota através de um serviço de streaming de músicas fictício, implementando **REST**, **GraphQL**, **SOAP** e **gRPC**.

## 🎯 Objetivo

Demonstrar e comparar as principais tecnologias de comunicação distribuída através de um caso de uso prático: um serviço de streaming de músicas com usuários, músicas e playlists.

## 🏗️ Arquitetura

O projeto contém:
- **5.000 usuários fictícios**
- **10.000 músicas fictícias**
- **3.000 playlists com relacionamentos realistas**

### Tecnologias Implementadas

| Tecnologia | Status | Porta | Descrição |
|------------|--------|-------|-----------|
| 🔵 REST | ✅ Funcional | 8000 | API RESTful com FastAPI |
| 🟣 GraphQL | ✅ Funcional | 8001 | API GraphQL com Strawberry |
| 🟡 SOAP | 📋 Demonstração | 8002 | Simulação SOAP com exemplos |
| 🟢 gRPC | 📋 Demonstração | 8002 | Simulação gRPC com exemplos |

## 📁 Estrutura do Projeto

```
.
├── data/                     # Dados JSON gerados
│   ├── usuarios.json        # 5K usuários fictícios
│   ├── musicas.json         # 10K músicas fictícias
│   └── playlists.json       # 3K playlists com relacionamentos
├── data_loader.py           # Carregador e indexador de dados
├── modelagem_dados.py       # Gerador de dados fictícios
├── rest_service.py          # Serviço REST (FastAPI)
├── graphql_service.py       # Serviço GraphQL (Strawberry)
├── soap_grpc_demo.py        # Demonstrações SOAP e gRPC
├── main.py                  # Script principal - executa todos os serviços
├── index.html               # Interface web de demonstração
└── README.md                # Este arquivo
```

## 🚀 Como Executar

### 1. Instalar Dependências

O projeto usa `uv` para gerenciamento de dependências:

```bash
# As dependências são instaladas automaticamente pelo main.py
python main.py
```

### 2. Gerar Dados (Primeira Execução)

```bash
python modelagem_dados.py
```

### 3. Executar Todos os Serviços

```bash
python main.py
```

### 4. Acessar a Interface

Abra o navegador em: `http://localhost:3000` (ou a URL fornecida pelo Replit)

## 🔧 Serviços Individuais

### REST API (Porta 8000)

```bash
python rest_service.py
```

**Endpoints disponíveis:**
- `GET /usuarios` - Lista todos os usuários
- `GET /musicas` - Lista todas as músicas
- `GET /playlists/usuario/{id}` - Playlists de um usuário
- `GET /playlists/{id}/musicas` - Músicas de uma playlist
- `GET /musicas/{id}/playlists` - Playlists que contêm uma música

### GraphQL API (Porta 8001)

```bash
python graphql_service.py
```

**Queries disponíveis:**
```graphql
{
  usuarios { id nome idade }
  musicas { id nome artista duracaoSegundos }
  playlistsUsuario(idUsuario: "user1") { nome musicas }
  estatisticas { totalUsuarios totalMusicas }
}
```

### SOAP & gRPC (Porta 8002)

```bash
python soap_grpc_demo.py
```

Demonstrações conceituais com exemplos de WSDL, .proto e código de implementação.

## 📊 Operações Disponíveis

### Consultas Principais
1. **Listar usuários** - Todos os usuários do sistema
2. **Listar músicas** - Catálogo completo de músicas
3. **Playlists por usuário** - Playlists criadas por um usuário específico
4. **Músicas de playlist** - Conteúdo detalhado de uma playlist
5. **Playlists com música** - Onde uma música específica aparece

### Características dos Dados
- **Usuários**: ID único, nome realista, idade (13-80 anos)
- **Músicas**: ID único, nome, artista, duração (2-6 minutos)
- **Playlists**: ID único, nome, dono, 5-50 músicas cada

## 🎮 Interface de Demonstração

A interface web (`index.html`) permite:
- ✅ Testar APIs REST e GraphQL em tempo real
- 📊 Comparar métricas de performance
- 📋 Ver demonstrações conceituais de SOAP e gRPC
- ⏱️ Medir tempos de resposta
- 📈 Acompanhar estatísticas de uso

## 🛠️ Tecnologias Utilizadas

- **Python 3.11+**
- **FastAPI** - Framework REST moderno e rápido
- **Strawberry GraphQL** - Framework GraphQL para Python
- **Uvicorn** - Servidor ASGI de alta performance
- **Faker** - Geração de dados fictícios realistas
- **CORS** - Habilitado para desenvolvimento web

## 📋 Funcionalidades

### ✅ Implementado
- [x] Geração de dados fictícios em massa
- [x] API REST completa com FastAPI
- [x] API GraphQL com queries complexas
- [x] Interface web interativa
- [x] Métricas de performance em tempo real
- [x] Sistema de indexação para consultas rápidas
- [x] Documentação automática das APIs

### 📋 Demonstração Conceitual
- [x] Exemplos de SOAP com WSDL
- [x] Exemplos de gRPC com .proto
- [x] Comparação teórica das tecnologias

## 🔍 Casos de Uso Demonstrados

1. **REST**: Operações CRUD tradicionais com recursos bem definidos
2. **GraphQL**: Consultas flexíveis e eficientes, evitando over/under-fetching
3. **SOAP**: Contratos formais e interoperabilidade enterprise
4. **gRPC**: Comunicação de alta performance e streaming bidirecional

## 📈 Comparação de Performance

A interface permite comparar:
- **Tempo de resposta** de cada tecnologia
- **Throughput** de requisições por segundo
- **Tamanho das respostas** (JSON vs XML vs Protobuf)
- **Facilidade de uso** e flexibilidade

## 🚀 Deploy no Replit

Este projeto está otimizado para execução no Replit:
- ✅ Configuração automática de dependências
- ✅ Detecção automática de portas
- ✅ Interface web acessível publicamente
- ✅ Logs detalhados para debugging

## 📝 Notas Técnicas

- Os dados são mantidos em memória para performance máxima
- Índices são criados automaticamente para consultas O(1)
- CORS está habilitado para desenvolvimento
- Todas as portas são configuráveis via variáveis de ambiente

## 🎓 Uso Acadêmico

Este projeto serve como:
- **Material didático** para computação distribuída
- **Benchmark** de diferentes tecnologias RPC
- **Exemplo prático** de APIs modernas
- **Base** para extensões e melhorias

## 📞 APIs de Exemplo

### REST
```bash
curl http://localhost:8000/usuarios
curl http://localhost:8000/playlists/usuario/user1
```

### GraphQL
```bash
curl -X POST http://localhost:8001/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ usuarios { nome } }"}'
```

---

**Desenvolvido para demonstração acadêmica de tecnologias de computação distribuída.**
