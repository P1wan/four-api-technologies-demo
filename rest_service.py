"""
Serviço REST para Streaming de Músicas - FastAPI
================================================

Implementação completa do serviço REST usando FastAPI.
Otimizado para execução em ambientes web como Replit.

Para executar:
1. pip install fastapi uvicorn
2. uvicorn rest_service:app --host 0.0.0.0 --port 8000
3. Acesse: http://localhost:8000/docs para Swagger UI
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List, Dict, Optional
import json
import os
from contextlib import asynccontextmanager

# Importa o carregador real de dados gerados em ``data/``
from dataloaders import get_data_loader

# ---------------------------------------------------------------------------
# Observação sobre o antigo ``SimpleDataLoader``
# ---------------------------------------------------------------------------
# A implementação original deste serviço usava dados "mock" em memória para
# facilitar a execução em ambientes web. Para o trabalho final, os dados devem
# ser carregados a partir dos arquivos JSON gerados por ``modelagem_dados.py``.
# O ``StreamingDataLoader`` providencia consultas otimizadas e é compartilhado
# entre todos os backends. A classe a seguir permanece apenas como referência de
# como os exemplos eram estruturados.
class SimpleDataLoader:
    def __init__(self):
        self.usuarios = []
        self.musicas = []
        self.playlists = []
        self._carregar_dados_mock()

    def _carregar_dados_mock(self):
        """Carrega dados mock para demonstração (substitui arquivos JSON)."""
        self.usuarios = [
            {"id": "user1", "nome": "Ana Silva", "idade": 28},
            {"id": "user2", "nome": "João Santos", "idade": 35},
            {"id": "user3", "nome": "Maria Costa", "idade": 22},
            {"id": "user4", "nome": "Pedro Lima", "idade": 45},
            {"id": "user5", "nome": "Lucia Ferreira", "idade": 31}
        ]

        self.musicas = [
            {"id": "music1", "nome": "Amor Perfeito", "artista": "Ana Silva", "duracaoSegundos": 240},
            {"id": "music2", "nome": "Noite Estrelada", "artista": "João Santos", "duracaoSegundos": 210},
            {"id": "music3", "nome": "Coração Selvagem", "artista": "Maria Costa", "duracaoSegundos": 195},
            {"id": "music4", "nome": "Despertar", "artista": "Pedro Lima", "duracaoSegundos": 280},
            {"id": "music5", "nome": "Liberdade", "artista": "Ana Silva", "duracaoSegundos": 225},
            {"id": "music6", "nome": "Saudade", "artista": "Lucia Ferreira", "duracaoSegundos": 260},
            {"id": "music7", "nome": "Tempestade", "artista": "João Santos", "duracaoSegundos": 190},
            {"id": "music8", "nome": "Serenata", "artista": "Maria Costa", "duracaoSegundos": 175}
        ]

        self.playlists = [
            {
                "id": "playlist1",
                "nome": "Meus Favoritos",
                "idUsuario": "user1",
                "musicas": ["music1", "music2", "music5"]
            },
            {
                "id": "playlist2",
                "nome": "Relaxar",
                "idUsuario": "user1",
                "musicas": ["music3", "music6", "music8"]
            },
            {
                "id": "playlist3",
                "nome": "Energia Total",
                "idUsuario": "user2",
                "musicas": ["music4", "music7", "music1", "music5"]
            },
            {
                "id": "playlist4",
                "nome": "Workout Mix",
                "idUsuario": "user3",
                "musicas": ["music2", "music4", "music7"]
            }
        ]

        print(f"✅ Dados mock carregados: {len(self.usuarios)} usuários, {len(self.musicas)} músicas, {len(self.playlists)} playlists")

# Instância global do data loader
# Sempre que possível utilizamos os arquivos JSON gerados em ``data/``.
# Caso o carregamento falhe (ex.: arquivos ausentes), recai-se para o loader
# simplificado apenas para fins de demonstração.
try:
    data_loader = get_data_loader()
    print("✅ Dados reais carregados do diretório 'data/'")
except Exception as exc:  # pragma: no cover - falha somente em ambiente demo
    print(f"⚠️  Erro ao carregar dados reais: {exc}")
    print("🔄 Utilizando SimpleDataLoader como fallback")
    data_loader = SimpleDataLoader()

# Configuração do FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Servidor REST iniciando...")
    yield
    # Shutdown
    print("🛑 Servidor REST finalizando...")

app = FastAPI(
    title="Serviço de Streaming - REST API",
    description="""
    API REST para gerenciamento de usuários, músicas e playlists.
    
    ## Funcionalidades
    
    * Gerenciamento completo de usuários (CRUD)
    * Gerenciamento completo de músicas (CRUD)
    * Gerenciamento completo de playlists (CRUD)
    * Paginação em todas as listagens
    * Tratamento de erros padronizado
    * Documentação OpenAPI/Swagger
    
    ## Autenticação
    
    Esta API não requer autenticação para demonstração.
    
    ## Endpoints
    
    * `/usuarios` - Gerenciamento de usuários
    * `/musicas` - Gerenciamento de músicas
    * `/playlists` - Gerenciamento de playlists
    * `/stats` - Estatísticas do serviço
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "usuarios",
            "description": "Operações relacionadas a usuários",
        },
        {
            "name": "musicas",
            "description": "Operações relacionadas a músicas",
        },
        {
            "name": "playlists",
            "description": "Operações relacionadas a playlists",
        },
        {
            "name": "estatisticas",
            "description": "Operações relacionadas a estatísticas do serviço",
        }
    ],
    lifespan=lifespan
)

# Configurar CORS para permitir acesso de qualquer origem (necessário para ambiente web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== ENDPOINTS PRINCIPAIS ==========

@app.get("/", response_class=HTMLResponse)
async def home():
    """Página inicial com informações sobre a API"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Serviço de Streaming - REST API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            h2 { color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            .endpoint { background-color: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }
            .get { background-color: #27ae60; }
            .post { background-color: #e74c3c; }
            .put { background-color: #f39c12; }
            .delete { background-color: #e67e22; }
            code { background-color: #34495e; color: white; padding: 2px 6px; border-radius: 3px; }
            a { color: #3498db; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎵 Serviço de Streaming - REST API</h1>

            <h2>📊 Status do Serviço</h2>
            <p>✅ <strong>Servidor REST ativo</strong></p>
            <p>📈 Dados carregados: <strong>5 usuários</strong>, <strong>8 músicas</strong>, <strong>4 playlists</strong></p>

            <h2>📖 Documentação Interativa</h2>
            <p>
                <a href="/docs" target="_blank">🔗 Swagger UI</a> - 
                <a href="/redoc" target="_blank">🔗 ReDoc</a>
            </p>

            <h2>🛠️ Endpoints Disponíveis</h2>

            <div class="endpoint">
                <span class="method get">GET</span> <code>/usuarios</code>
                <p>Lista todos os usuários do serviço</p>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span> <code>/musicas</code>
                <p>Lista todas as músicas disponíveis</p>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span> <code>/usuarios/{id_usuario}/playlists</code>
                <p>Lista todas as playlists de um usuário específico</p>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span> <code>/playlists/{id_playlist}/musicas</code>
                <p>Lista todas as músicas de uma playlist específica</p>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span> <code>/musicas/{id_musica}/playlists</code>
                <p>Lista todas as playlists que contêm uma música específica</p>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span> <code>/stats</code>
                <p>Estatísticas gerais do serviço</p>
            </div>

            <h2>💡 Exemplos de Uso</h2>
            <p>Teste os endpoints acima clicando nos links da documentação ou fazendo requisições HTTP.</p>

            <h2>🔧 Tecnologia</h2>
            <p>Esta API foi construída com <strong>FastAPI</strong> e demonstra os princípios <strong>REST</strong>:</p>
            <ul>
                <li>📝 <strong>Recursos identificados por URIs</strong> (/usuarios, /musicas, /playlists)</li>
                <li>🔗 <strong>Verbos HTTP padronizados</strong> (GET, POST, PUT, DELETE)</li>
                <li>🗂️ <strong>Representação JSON</strong> dos dados</li>
                <li>🔄 <strong>Interface uniforme</strong> e stateless</li>
            </ul>
        </div>
    </body>
    </html>
    """
    return html_content

# ========== PAGINATION AND ERROR HANDLING ==========

class PaginatedResponse:
    def __init__(self, items: List, total: int, page: int, page_size: int):
        self.items = items
        self.total = total
        self.page = page
        self.page_size = page_size
        self.total_pages = (total + page_size - 1) // page_size

    def dict(self):
        return {
            "items": self.items,
            "total": self.total,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": self.total_pages
        }

@app.get("/usuarios", response_model=Dict, tags=["usuarios"])
async def listar_todos_usuarios(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página")
):
    """
    Lista todos os usuários do serviço com paginação.

    **Princípio REST**: Recurso /usuarios acessado via GET
    """
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    usuarios_paginados = data_loader.usuarios[start_idx:end_idx]
    return PaginatedResponse(
        items=usuarios_paginados,
        total=len(data_loader.usuarios),
        page=page,
        page_size=page_size
    ).dict()

@app.get("/musicas", response_model=Dict, tags=["musicas"])
async def listar_todas_musicas(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página")
):
    """
    Lista todas as músicas disponíveis no serviço com paginação.

    **Princípio REST**: Recurso /musicas acessado via GET
    """
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    musicas_paginadas = data_loader.musicas[start_idx:end_idx]
    return PaginatedResponse(
        items=musicas_paginadas,
        total=len(data_loader.musicas),
        page=page,
        page_size=page_size
    ).dict()

@app.get("/playlists", response_model=Dict, tags=["playlists"])
async def listar_todas_playlists(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página")
):
    """
    Lista todas as playlists disponíveis no serviço com paginação.

    **Princípio REST**: Recurso /playlists acessado via GET
    """
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    playlists_paginadas = data_loader.playlists[start_idx:end_idx]
    return PaginatedResponse(
        items=playlists_paginadas,
        total=len(data_loader.playlists),
        page=page,
        page_size=page_size
    ).dict()

@app.get("/usuarios/{id_usuario}/playlists", response_model=List[Dict], tags=["usuarios"])
async def listar_playlists_usuario(id_usuario: str):
    """
    Lista todas as playlists de um usuário específico.

    **Princípio REST**: Recurso aninhado /usuarios/{id}/playlists
    """
    # Verificar se usuário existe
    usuario_existe = any(u["id"] == id_usuario for u in data_loader.usuarios)
    if not usuario_existe:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    playlists_usuario = data_loader.listar_playlists_usuario(id_usuario)
    return playlists_usuario

@app.get("/playlists/{id_playlist}/musicas", response_model=List[Dict], tags=["playlists"])
async def listar_musicas_playlist(id_playlist: str):
    """
    Lista todas as músicas de uma playlist específica.

    **Princípio REST**: Recurso aninhado /playlists/{id}/musicas
    """    # Encontrar a playlist
    playlist = data_loader.get_playlist(id_playlist)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist não encontrada")

    # Buscar as músicas da playlist
    musicas_da_playlist = data_loader.listar_musicas_playlist(id_playlist)
    return musicas_da_playlist

@app.get("/musicas/{id_musica}/playlists", response_model=List[Dict], tags=["musicas"])
async def listar_playlists_com_musica(id_musica: str):
    """
    Lista todas as playlists que contêm uma música específica.

    **Princípio REST**: Recurso aninhado /musicas/{id}/playlists
    """    # Verificar se música existe
    musica_existe = any(m["id"] == id_musica for m in data_loader.musicas)
    if not musica_existe:
        raise HTTPException(status_code=404, detail="Música não encontrada")

    playlists_com_musica = data_loader.listar_playlists_com_musica(id_musica)
    return playlists_com_musica

@app.get("/stats", tags=["estatisticas"])
async def obter_estatisticas():
    """
    Retorna estatísticas gerais do serviço.

    **Princípio REST**: Endpoint adicional para metadados
    """
    total_musicas_em_playlists = sum(len(p["musicas"]) for p in data_loader.playlists)

    return {
        "total_usuarios": len(data_loader.usuarios),
        "total_musicas": len(data_loader.musicas),
        "total_playlists": len(data_loader.playlists),
        "total_musicas_em_playlists": total_musicas_em_playlists,
        "media_musicas_por_playlist": total_musicas_em_playlists / len(data_loader.playlists) if data_loader.playlists else 0,
        "usuarios_com_playlists": len(set(p["idUsuario"] for p in data_loader.playlists)),
        "tecnologia": "REST",
        "framework": "FastAPI",
        "status": "ativo"
    }

# ========== ENDPOINTS CRUD  ==========

@app.post("/usuarios", response_model=Dict, tags=["usuarios"])
async def criar_usuario(nome: str, idade: int):
    """
    Cria um novo usuário.

    **Princípio REST**: POST para criar recursos
    """
    import uuid
    novo_usuario = {
        "id": f"user{len(data_loader.usuarios) + 1}",
        "nome": nome,
        "idade": idade
    }
    data_loader.usuarios.append(novo_usuario)
    return novo_usuario

@app.get("/usuarios/{id_usuario}", response_model=Dict, tags=["usuarios"])
async def obter_usuario(id_usuario: str):
    """
    Obtém um usuário específico por ID.

    **Princípio REST**: GET em recurso específico
    """
    usuario = next((u for u in data_loader.usuarios if u["id"] == id_usuario), None)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

# ========== CRUD OPERATIONS FOR MUSICS ==========

@app.post("/musicas", response_model=Dict, tags=["musicas"])
async def criar_musica(nome: str, artista: str, duracao_segundos: int):
    """
    Cria uma nova música.

    **Princípio REST**: POST para criar recursos
    **Nota**: Para demonstração - em produção seria persistido em banco de dados
    """
    import uuid
    nova_musica = {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "artista": artista,
        "duracaoSegundos": duracao_segundos
    }
    
    # Para demonstração: simular criação sem modificar dados compartilhados
    # Em produção: salvar no banco de dados
    return nova_musica

@app.get("/musicas/{id_musica}", response_model=Dict, tags=["musicas"])
async def obter_musica(id_musica: str):
    """
    Obtém uma música específica por ID.

    **Princípio REST**: GET em recurso específico
    """
    musica = data_loader.get_musica(id_musica)
    if not musica:
        raise HTTPException(status_code=404, detail="Música não encontrada")
    return musica

@app.put("/musicas/{id_musica}", response_model=Dict, tags=["musicas"])
async def atualizar_musica(id_musica: str, nome: str = None, artista: str = None, duracao_segundos: int = None):
    """
    Atualiza uma música existente.

    **Princípio REST**: PUT para atualizar recursos
    **Nota**: Para demonstração - em produção seria persistido em banco de dados
    """
    musica = data_loader.get_musica(id_musica)
    if not musica:
        raise HTTPException(status_code=404, detail="Música não encontrada")
    
    # Criar cópia para demonstração (não modificar dados originais)
    musica_atualizada = musica.copy()
    if nome:
        musica_atualizada["nome"] = nome
    if artista:
        musica_atualizada["artista"] = artista
    if duracao_segundos:
        musica_atualizada["duracaoSegundos"] = duracao_segundos
    
    return musica_atualizada

@app.delete("/musicas/{id_musica}", tags=["musicas"])
async def deletar_musica(id_musica: str):
    """
    Remove uma música do sistema.

    **Princípio REST**: DELETE para remover recursos
    **Nota**: Para demonstração - em produção seria removido do banco de dados
    """
    musica = data_loader.get_musica(id_musica)
    if not musica:
        raise HTTPException(status_code=404, detail="Música não encontrada")
    
    # Para demonstração: simular remoção sem modificar dados compartilhados
    return {"message": f"Música '{musica['nome']}' removida com sucesso"}

# ========== CRUD OPERATIONS FOR PLAYLISTS ==========

@app.post("/playlists", response_model=Dict, tags=["playlists"])
async def criar_playlist(nome: str, id_usuario: str, musicas: List[str] = None):
    """
    Cria uma nova playlist.

    **Princípio REST**: POST para criar recursos
    **Nota**: Para demonstração - em produção seria persistido em banco de dados
    """
    # Verificar se usuário existe
    usuario = data_loader.get_usuario(id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar se todas as músicas existem
    if musicas:
        for id_musica in musicas:
            musica = data_loader.get_musica(id_musica)
            if not musica:
                raise HTTPException(status_code=404, detail=f"Música {id_musica} não encontrada")
    
    import uuid
    nova_playlist = {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "idUsuario": id_usuario,
        "musicas": musicas or []
    }
    
    # Para demonstração: simular criação sem modificar dados compartilhados
    return nova_playlist

@app.get("/playlists/{id_playlist}", response_model=Dict, tags=["playlists"])
async def obter_playlist(id_playlist: str):
    """
    Obtém uma playlist específica por ID.

    **Princípio REST**: GET em recurso específico
    """
    playlist = data_loader.get_playlist(id_playlist)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist não encontrada")
    return playlist

@app.put("/playlists/{id_playlist}", response_model=Dict, tags=["playlists"])
async def atualizar_playlist(id_playlist: str, nome: str = None, musicas: List[str] = None):
    """
    Atualiza uma playlist existente.

    **Princípio REST**: PUT para atualizar recursos
    **Nota**: Para demonstração - em produção seria persistido em banco de dados
    """
    playlist = data_loader.get_playlist(id_playlist)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist não encontrada")
    
    # Criar cópia para demonstração
    playlist_atualizada = playlist.copy()
    if nome:
        playlist_atualizada["nome"] = nome
    if musicas is not None:
        # Verificar se todas as músicas existem
        for id_musica in musicas:
            musica = data_loader.get_musica(id_musica)
            if not musica:
                raise HTTPException(status_code=404, detail=f"Música {id_musica} não encontrada")
        playlist_atualizada["musicas"] = musicas
    
    return playlist_atualizada

@app.delete("/playlists/{id_playlist}", tags=["playlists"])
async def deletar_playlist(id_playlist: str):
    """
    Remove uma playlist do sistema.

    **Princípio REST**: DELETE para remover recursos
    **Nota**: Para demonstração - em produção seria removido do banco de dados
    """
    playlist = data_loader.get_playlist(id_playlist)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist não encontrada")
    
    # Para demonstração: simular remoção sem modificar dados compartilhados
    return {"message": f"Playlist '{playlist['nome']}' removida com sucesso"}

# ========== ERROR HANDLERS ==========

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Handler global para exceções HTTP.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "HTTPException"
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Handler global para exceções não tratadas.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Erro interno do servidor",
                "type": "InternalServerError"
            }
        }
    )

# ========== FUNÇÃO PARA EXECUTAR O SERVIDOR ==========

def executar_servidor():
    """
    Função para executar o servidor REST.
    Use esta função em ambientes que não suportam uvicorn diretamente.
    """
    import uvicorn
    print("🚀 Iniciando servidor REST...")
    print("📍 Acesse: http://localhost:8000")
    print("📖 Documentação: http://localhost:8000/docs")

    uvicorn.run(
        "rest_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    executar_servidor()