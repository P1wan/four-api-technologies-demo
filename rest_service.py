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
from fastapi.responses import HTMLResponse
from typing import List, Dict, Optional
import json
import os
from contextlib import asynccontextmanager

# Importa o carregador real de dados gerados em ``data/``
from data_loader import get_data_loader

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
    description="API REST para gerenciamento de usuários, músicas e playlists",
    version="1.0.0",
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

@app.get("/usuarios", response_model=List[Dict])
async def listar_todos_usuarios():
    """
    Lista todos os usuários do serviço.

    **Princípio REST**: Recurso /usuarios acessado via GET
    """
    return data_loader.usuarios

@app.get("/musicas", response_model=List[Dict])
async def listar_todas_musicas():
    """
    Lista todas as músicas disponíveis no serviço.

    **Princípio REST**: Recurso /musicas acessado via GET
    """
    return data_loader.musicas

@app.get("/usuarios/{id_usuario}/playlists", response_model=List[Dict])
async def listar_playlists_usuario(id_usuario: str):
    """
    Lista todas as playlists de um usuário específico.

    **Princípio REST**: Recurso aninhado /usuarios/{id}/playlists
    """
    # Verificar se usuário existe
    usuario_existe = any(u["id"] == id_usuario for u in data_loader.usuarios)
    if not usuario_existe:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    playlists_usuario = [p for p in data_loader.playlists if p["idUsuario"] == id_usuario]
    return playlists_usuario

@app.get("/playlists/{id_playlist}/musicas", response_model=List[Dict])
async def listar_musicas_playlist(id_playlist: str):
    """
    Lista todas as músicas de uma playlist específica.

    **Princípio REST**: Recurso aninhado /playlists/{id}/musicas
    """
    # Encontrar a playlist
    playlist = next((p for p in data_loader.playlists if p["id"] == id_playlist), None)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist não encontrada")

    # Buscar as músicas da playlist
    musicas_da_playlist = []
    for id_musica in playlist["musicas"]:
        musica = next((m for m in data_loader.musicas if m["id"] == id_musica), None)
        if musica:
            musicas_da_playlist.append(musica)

    return musicas_da_playlist

@app.get("/musicas/{id_musica}/playlists", response_model=List[Dict])
async def listar_playlists_com_musica(id_musica: str):
    """
    Lista todas as playlists que contêm uma música específica.

    **Princípio REST**: Recurso aninhado /musicas/{id}/playlists
    """
    # Verificar se música existe
    musica_existe = any(m["id"] == id_musica for m in data_loader.musicas)
    if not musica_existe:
        raise HTTPException(status_code=404, detail="Música não encontrada")

    playlists_com_musica = [p for p in data_loader.playlists if id_musica in p["musicas"]]
    return playlists_com_musica

@app.get("/stats")
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

# ========== ENDPOINTS CRUD OPCIONAIS (Para demonstração) ==========

@app.post("/usuarios", response_model=Dict)
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

@app.get("/usuarios/{id_usuario}", response_model=Dict)
async def obter_usuario(id_usuario: str):
    """
    Obtém um usuário específico por ID.

    **Princípio REST**: GET em recurso específico
    """
    usuario = next((u for u in data_loader.usuarios if u["id"] == id_usuario), None)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

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