# Padronização de Nomenclatura - APIs de Streaming

## Objetivo

Este documento define a padronização **otimizada** de nomenclatura que será seguida em todo o projeto de comparação de APIs (SOAP, REST, GraphQL, gRPC), **eliminando conversões desnecessárias** e garantindo máxima performance nos testes de carga.

## 🎯 Estratégia Definitiva: snake_case Nativo

### Princípio Fundamental

**Eliminar conversões redundantes** que impactam performance:

```
❌ ANTES: JSONs (snake_case) → DataLoader (camelCase) → APIs (snake_case)
✅ AGORA: JSONs (snake_case) → DataLoader (snake_case) → APIs (snake_case)
```

### Benefícios da Nova Estratégia

1. **🚀 Performance**: Elimina overhead de conversões string durante testes de carga
2. **🔧 Simplicidade**: Reduz complexidade e pontos de falha
3. **📊 Consistência**: Formato único em todo o pipeline de dados
4. **🧪 Confiabilidade**: Menos conversões = menos bugs

## 📋 Análise dos Requisitos por Tecnologia

### Todas as APIs Aceitam snake_case? ✅ **SIM!**

| **Tecnologia** | **Aceita snake_case?** | **Evidência** |
|----------------|------------------------|---------------|
| **REST (FastAPI)** | ✅ **SIM** - Padrão nativo | `duracao_segundos: int` nos models |
| **SOAP (Spyne)** | ✅ **SIM** - Flexível | Campos podem ter qualquer nome |
| **GraphQL (Strawberry)** | ✅ **SIM** - Padrão Python | Convenção snake_case |
| **gRPC (Protocol Buffers)** | ✅ **SIM** - Padrão proto | `duracao_segundos` no .proto |

## 🔧 Padrões Definitivos

### 1. DataLoader (Nova Abordagem)

**ANTES (com conversões redundantes):**
```python
# ❌ Conversões desnecessárias
musica["duracaoSegundos"] = musica_json["duracao_segundos"]
playlist["idUsuario"] = playlist_json["id_usuario"]
```

**DEPOIS (formato nativo):**
```python
# ✅ Mantém formato original
musica = {
    "id": str,
    "nome": str,
    "artista": str,
    "duracao_segundos": int  # ← snake_case nativo
}

playlist = {
    "id": str,
    "nome": str,
    "id_usuario": str,      # ← snake_case nativo
    "musicas": List[str]
}
```

### 2. Serviços (Todos Compatíveis)

#### REST (FastAPI) ✅
```python
# ✅ Já usa snake_case nativamente
class MusicaCreate(BaseModel):
    duracao_segundos: int

# ✅ Direto do DataLoader, sem conversões
return {
    "duracao_segundos": musica["duracao_segundos"]  # Direto!
}
```

#### SOAP (Spyne) ✅
```python
# ✅ Flexível, aceita qualquer nomenclatura
return Musica(
    duracao=musica["duracao_segundos"],  # snake_case OK
    usuario=playlist["id_usuario"]       # snake_case OK
)
```

#### GraphQL (Strawberry) ✅
```python
# ✅ Convenção Python é snake_case
@strawberry.type
class Musica:
    duracao_segundos: int  # snake_case nativo

# ✅ Direto do DataLoader
Musica(duracao_segundos=m["duracao_segundos"])  # Sem conversão!
```

#### gRPC (Protocol Buffers) ✅
```python
# ✅ Proto já define snake_case
message Musica {
    int32 duracao_segundos = 4;  # snake_case nativo
}

# ✅ Direto do DataLoader
duracao_segundos=musica["duracao_segundos"]  # Sem conversão!
```

## 🚀 Plano de Refatoração

### Passo 1: DataLoader (Prioridade Máxima)
```python
# ❌ REMOVER conversões
def _carregar_musicas(self):
    # ANTES: musica["duracaoSegundos"] = musica_json["duracao_segundos"]
    # DEPOIS: Manter formato original
    pass
```

### Passo 2: Verificar Serviços
- **REST**: ✅ Já compatível
- **SOAP**: Atualizar para usar `duracao_segundos`, `id_usuario`
- **GraphQL**: ✅ Já compatível
- **gRPC**: Conectar ao DataLoader em vez de ler JSONs diretamente

### Passo 3: Validação
- Executar testes de unidade
- Confirmar performance otimizada
- Validar testes de carga k6

## 📐 Convenções Finais

### Nomenclatura de Dados
```python
# ✅ PADRÃO ÚNICO: snake_case
{
    "id": str,
    "nome": str,
    "artista": str,
    "duracao_segundos": int,  # Sempre snake_case
    "id_usuario": str         # Sempre snake_case
}
```

### Nomenclatura de Código

| Aspecto | Convenção | Exemplo |
|---------|-----------|---------|
| **Campos de Dados** | `snake_case` | `duracao_segundos` |
| **Métodos/Funções** | `snake_case` | `listar_musicas()` |
| **Classes** | `PascalCase` | `StreamingDataLoader` |
| **Variáveis** | `snake_case` | `nova_musica` |
| **Endpoints REST** | `snake_case` | `/usuarios/{id_usuario}` |
| **Campos SOAP** | `snake_case` | `<duracao_segundos>` |
| **Schema GraphQL** | `snake_case` | `duracao_segundos: Int` |
| **Mensagens gRPC** | `snake_case` | `duracao_segundos` |

### Idioma
- **Campos de Negócio**: Português (`duracao_segundos`, `id_usuario`)
- **Código Técnico**: Inglês (`data_loader`, `endpoint`)
- **Documentação**: Português (este projeto)

## ⚠️ Regras Críticas

1. **NUNCA** converter entre `snake_case` ↔ `camelCase` desnecessariamente
2. **SEMPRE** usar o formato que o DataLoader fornece
3. **MANTER** compatibilidade com testes existentes
4. **PRIORIZAR** performance sobre "padronização estética"
5. **VALIDAR** impacto nos testes de carga k6

## 🔍 Impacto nos Testes de Performance

### Antes da Refatoração
```
📊 Overhead estimado por requisição:
- Conversão string: ~0.1ms
- Múltiplos campos: ~0.3ms
- Em 1000 req/s: 300ms overhead total
```

### Após Refatoração
```
📊 Overhead eliminado:
- Conversões: 0ms ✅
- Acesso direto aos dados ✅
- Performance máxima para k6 ✅
```

## 📚 Conclusão

Esta padronização **eliminará conversões desnecessárias** e garantirá que os testes de carga k6 meçam a **performance real** das tecnologias API, não o overhead de conversões de string.

**Resultado esperado**: Código mais simples, performance otimizada, e dados consistentes em todo o pipeline.

---

**Status**: 🔄 **Pronto para refatoração**  
**Próximo passo**: Implementar mudanças no DataLoader  
**Impacto**: Redução significativa de overhead computacional 