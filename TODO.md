# Guia de Validação de Serviços - Próximos Passos

## 🎯 Objetivo
Validar sistematicamente todos os serviços (REST, SOAP, gRPC) após as correções aplicadas ao GraphQL e ao sistema de dataloaders, garantindo funcionamento completo antes de implementar testes de carga com K6.

---

## ✅ Status Atual
- **GraphQL**: ✅ Totalmente validado (13/13 testes passando)
- **DataLoaders**: ✅ Corrigido com persistência temporária e CRUD completo
- **REST**: ✅ Totalmente validado (24/24 testes passando) 
- **SOAP**: ⏳ Pendente validação  
- **gRPC**: ⏳ Pendente validação

---

## 📋 Plano de Validação Sistemática

### ✅ Etapa 1: Validação do Serviço REST - CONCLUÍDA

#### ✅ 1.1 Testes Automatizados - CONCLUÍDA
```bash
# ✅ REALIZADO: Executar testes unitários do REST
python -m pytest test_rest_service.py -v

# ✅ RESULTADO: Todos os 24 testes passando (100%)
# ✅ CORREÇÕES APLICADAS:
# - Removido return incorreto dos testes test_create_song e test_create_playlist
# - Adicionada validação de usuário no endpoint de criação de playlist
# - Serviço REST 100% funcional com operações CRUD completas
```

#### 1.2 Testes Manuais com Postman
**Configuração:**
- Base URL: `http://localhost:8001`
- Content-Type: `application/json`

**Testes Essenciais:**

**Usuários:**
```
GET    /users           # Listar todos
GET    /users/1         # Obter específico
POST   /users           # Criar novo
PUT    /users/1         # Atualizar
DELETE /users/1         # Deletar
```

**Músicas:**
```
GET    /musicas         # Listar todas
GET    /musicas/1       # Obter específica
POST   /musicas         # Criar nova
PUT    /musicas/1       # Atualizar
DELETE /musicas/1       # Deletar
```

**Playlists:**
```
GET    /playlists       # Listar todas
GET    /playlists/1     # Obter específica
POST   /playlists       # Criar nova
PUT    /playlists/1     # Atualizar
DELETE /playlists/1     # Deletar
```

#### ✅ 1.3 Verificações Específicas - CONCLUÍDA
- [x] Códigos de status HTTP corretos (200, 201, 404, 500)
- [x] Formato JSON válido nas respostas
- [x] Paginação funcionando corretamente
- [x] Tratamento de erros adequado
- [x] Validação de dados de entrada

---

## 📊 Resumo do Progresso Atual

### ✅ SERVIÇOS COMPLETAMENTE VALIDADOS:
1. **GraphQL**: 13/13 testes passando
   - Schema, queries e mutations funcionais
   - DataLoaders integrados corretamente
   
2. **DataLoaders**: Sistema de persistência temporária 
   - CRUD completo em memória
   - Arquivos JSON como fonte inicial (somente leitura)
   
3. **REST**: 24/24 testes passando
   - Todas as operações CRUD funcionais
   - Validação de entrada implementada
   - Códigos de status HTTP corretos
   - Tratamento de erros adequado

### 🎯 PRÓXIMO FOCO: Validação SOAP
**Meta**: Garantir que o serviço SOAP esteja funcionando corretamente com os dataloaders atualizados.

---

### Etapa 2: Validação do Serviço SOAP

#### 2.1 Testes Automatizados
```bash
# Executar testes unitários do SOAP
python -m pytest test_soap_service.py -v

# Verificar se todas as operações WSDL funcionam
```

#### 2.2 Testes Manuais com Postman
**Configuração:**
- URL: `http://localhost:8002/soap`
- Content-Type: `text/xml`
- SOAPAction: `"http://streaming.com/obter_usuarios"` (ajustar conforme operação)

**Exemplo de Teste - Obter Usuários:**
```xml
POST /soap
SOAPAction: "http://streaming.com/obter_usuarios"

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <obter_usuarios xmlns="http://streaming.com/" />
  </soap:Body>
</soap:Envelope>
```

**Operações a Testar:**
- [ ] `obter_usuarios` - Listar usuários
- [ ] `obter_usuario` - Obter usuário específico
- [ ] `criar_usuario` - Criar novo usuário
- [ ] `atualizar_usuario` - Atualizar usuário
- [ ] `deletar_usuario` - Deletar usuário
- [ ] Repetir para `musicas` e `playlists`

#### 2.3 Verificações Específicas
- [ ] Envelope SOAP válido nas respostas
- [ ] WSDL acessível em `/soap?wsdl`
- [ ] Namespace correto nas operações
- [ ] Tratamento de erros SOAP (faults)
- [ ] Conversão adequada de tipos de dados

---

### Etapa 3: Validação do Serviço gRPC

#### 3.1 Testes Automatizados
```bash
# Executar testes unitários do gRPC
python -m pytest test_grpc_service.py -v

# Verificar se todos os métodos gRPC funcionam
```

#### 3.2 Testes Manuais com Postman
**Configuração:**
- URL: `localhost:50051`
- Protocolo: gRPC
- Importar arquivo: `streaming.proto`

**Métodos a Testar:**
- [ ] `GetUsuarios` - Listar usuários
- [ ] `GetUsuario` - Obter usuário específico
- [ ] `CreateUsuario` - Criar novo usuário
- [ ] `UpdateUsuario` - Atualizar usuário
- [ ] `DeleteUsuario` - Deletar usuário
- [ ] Repetir para `GetMusicas`, `GetPlaylists`, etc.

#### 3.3 Verificações Específicas
- [ ] Serialização/deserialização protobuf
- [ ] Conversão de nomenclatura (camelCase ↔ snake_case)
- [ ] Tratamento de erros gRPC (status codes)
- [ ] Validação de tipos de dados
- [ ] Stubs atualizados (`streaming_pb2.py`, `streaming_pb2_grpc.py`)

---

### Etapa 4: Verificação de Consistência Entre Serviços

#### 4.1 Testes de Consistência de Dados
Para cada operação, verificar se os resultados são consistentes:

**Exemplo - Obter Usuário ID 1:**
```bash
# REST
curl http://localhost:8001/users/1

# GraphQL
# Query: { usuario(id: 1) { id, nome, email } }

# SOAP
# obter_usuario com id=1

# gRPC  
# GetUsuario com id=1
```

#### 4.2 Verificações Críticas
- [ ] Mesmos dados retornados por todos os serviços
- [ ] Formato de datas consistente
- [ ] Nomenclatura de campos respeitada (camelCase vs snake_case)
- [ ] Tratamento de IDs inválidos
- [ ] Comportamento com dados vazios

---

### Etapa 5: Preparação para Testes de Carga K6

#### 5.1 Documentação de Endpoints
Criar arquivo `endpoints_summary.md` com:
- [ ] Lista completa de endpoints de cada serviço
- [ ] Exemplos de requisições e respostas
- [ ] Códigos de status esperados
- [ ] Payloads de teste padrão

#### 5.2 Scripts de Teste Base
Criar estrutura para scripts K6:
```
k6_tests/
├── rest_test.js
├── graphql_test.js  
├── soap_test.js
├── grpc_test.js
└── shared/
    ├── test_data.js
    └── utils.js
```

#### 5.3 Métricas de Baseline
Antes dos testes de carga, capturar métricas básicas:
- [ ] Tempo de resposta médio de cada serviço
- [ ] Uso de memória durante operações
- [ ] Latência de startup dos serviços

---

## 🚀 Comandos Rápidos de Validação

### Iniciar Todos os Serviços
```bash
python main.py
```

### Executar Todos os Testes Automatizados
```bash
# Todos os testes em sequência
python -m pytest test_rest_service.py test_soap_service.py test_grpc_service.py test_graphql_service.py -v

# Com relatório detalhado
python -m pytest test_rest_service.py test_soap_service.py test_grpc_service.py test_graphql_service.py -v --tb=short
```

### Verificação Rápida de Serviços
```bash
# REST
curl http://localhost:8001/users

# SOAP WSDL
curl http://localhost:8002/soap?wsdl

# GraphQL Schema
curl -X POST http://localhost:8003/graphql -H "Content-Type: application/json" -d '{"query":"{ __schema { types { name } } }"}'
```

---

## ⚠️ Pontos de Atenção

### Possíveis Problemas Herdados
1. **Nomenclatura de Campos**: Verificar se REST/SOAP seguem a convenção de camelCase do JSON
2. **Conversões de Dados**: Especialmente em gRPC (snake_case ↔ camelCase)
3. **Tratamento de Erros**: Garantir que todos os serviços usam os dataloaders corretamente
4. **Persistência Temporária**: Verificar se CREATE/UPDATE/DELETE funcionam em todos os serviços

### Critérios de Sucesso
- [ ] Todos os testes automatizados passando (100%)
- [ ] Operações CRUD funcionando em todos os serviços
- [ ] Respostas consistentes entre serviços para mesmos dados
- [ ] Tratamento de erros adequado em todos os serviços
- [ ] Performance aceitável em operações básicas

---

## 📁 Estrutura de Arquivos para Testes

```
tests_validation/
├── postman_collections/
│   ├── REST_Collection.json
│   ├── SOAP_Collection.json
│   ├── GraphQL_Collection.json
│   └── gRPC_Collection.json
├── test_results/
│   ├── rest_validation.md
│   ├── soap_validation.md
│   ├── grpc_validation.md
│   └── consistency_check.md
└── k6_preparation/
    ├── baseline_metrics.json
    └── test_scenarios.md
```

---

## 🎯 Próximo Marco: Testes de Carga K6

Após validação completa, implementar:
1. Scripts K6 para cada tecnologia
2. Cenários de carga progressiva
3. Comparação de métricas (latência, throughput, erro)
4. Relatórios de performance comparativa
5. Análise de escalabilidade

---

*Este guia deve ser seguido sequencialmente para garantir que todos os serviços estão funcionais antes de iniciar os testes de performance com K6.*