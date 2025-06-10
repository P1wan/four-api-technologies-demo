"""
Serviço GraphQL para Streaming de Músicas - Strawberry
======================================================

Implementação completa do serviço GraphQL usando Strawberry.
Otimizado para execução em ambientes web como Replit.

Para executar:
1. pip install strawberry-graphql[fastapi] uvicorn
2. uvicorn graphql_service:app --host 0.0.0.0 --port 8001
3. Acesse: http://localhost:8001/graphql para GraphiQL
"""

import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import List, Optional
from contextlib import asynccontextmanager

# Loader de dados real utilizado por todos os backends
from data_loader import get_data_loader

# ========== TIPOS GRAPHQL ==========

@strawberry.type
class Usuario:
    id: str
    nome: str
    idade: int

@strawberry.type
class Musica:
    id: str
    nome: str
    artista: str
    duracao_segundos: int

@strawberry.type
class Playlist:
    id: str
    nome: str
    id_usuario: str
    musicas: List[str]  # IDs das músicas

@strawberry.type
class PlaylistCompleta:
    """Playlist com dados completos das músicas"""
    id: str
    nome: str
    usuario: Usuario
    musicas: List[Musica]

@strawberry.type
class Estatisticas:
    total_usuarios: int
    total_musicas: int
    total_playlists: int
    usuarios_com_playlists: int
    media_musicas_por_playlist: float
    tecnologia: str

# ========== DATA LOADER (Simulação) ==========

class GraphQLDataLoader:
    """Loader de dados mock utilizado apenas para ambientes de demonstração."""

    def __init__(self):
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
            {"id": "playlist1", "nome": "Meus Favoritos", "idUsuario": "user1", "musicas": ["music1", "music2", "music5"]},
            {"id": "playlist2", "nome": "Relaxar", "idUsuario": "user1", "musicas": ["music3", "music6", "music8"]},
            {"id": "playlist3", "nome": "Energia Total", "idUsuario": "user2", "musicas": ["music4", "music7", "music1", "music5"]},
            {"id": "playlist4", "nome": "Workout Mix", "idUsuario": "user3", "musicas": ["music2", "music4", "music7"]}
        ]

        print("✅ GraphQL Data Loader (mock) inicializado")

# Instância global: tenta usar dados reais e faz fallback para o mock
try:
    data_loader = get_data_loader()
    print("✅ Dados reais carregados para GraphQL")
except Exception as exc:
    print(f"⚠️  Erro ao carregar dados reais: {exc}")
    print("🔄 Utilizando GraphQLDataLoader mock")
    data_loader = GraphQLDataLoader()

# ========== RESOLVERS ==========

@strawberry.type
class Query:

    @strawberry.field
    def usuarios(self) -> List[Usuario]:
        """
        Lista todos os usuários.

        Exemplo de query:
        {
          usuarios {
            id
            nome
            idade
          }
        }
        """
        return [
            Usuario(id=u["id"], nome=u["nome"], idade=u["idade"])
            for u in data_loader.usuarios
        ]

    @strawberry.field
    def musicas(self) -> List[Musica]:
        """
        Lista todas as músicas.

        Exemplo de query:
        {
          musicas {
            id
            nome
            artista
            duracaoSegundos
          }
        }
        """
        return [
            Musica(
                id=m["id"],
                nome=m["nome"],
                artista=m["artista"],
                duracao_segundos=m["duracaoSegundos"]
            )
            for m in data_loader.musicas
        ]

    @strawberry.field
    def usuario(self, id: str) -> Optional[Usuario]:
        """
        Busca um usuário específico por ID.

        Exemplo de query:
        {
          usuario(id: "user1") {
            id
            nome
            idade
          }
        }
        """
        usuario_data = next((u for u in data_loader.usuarios if u["id"] == id), None)
        if usuario_data:
            return Usuario(
                id=usuario_data["id"],
                nome=usuario_data["nome"],
                idade=usuario_data["idade"]
            )
        return None

    @strawberry.field
    def playlists_usuario(self, id_usuario: str) -> List[Playlist]:
        """
        Lista playlists de um usuário específico.

        Exemplo de query:
        {
          playlistsUsuario(idUsuario: "user1") {
            id
            nome
            musicas
          }
        }
        """
        playlists_usuario = [
            p for p in data_loader.playlists if p["idUsuario"] == id_usuario
        ]

        return [
            Playlist(
                id=p["id"],
                nome=p["nome"],
                id_usuario=p["idUsuario"],
                musicas=p["musicas"]
            )
            for p in playlists_usuario
        ]

    @strawberry.field
    def musicas_playlist(self, id_playlist: str) -> List[Musica]:
        """
        Lista músicas de uma playlist específica.

        Exemplo de query:
        {
          musicasPlaylist(idPlaylist: "playlist1") {
            id
            nome
            artista
            duracaoSegundos
          }
        }
        """
        playlist = next((p for p in data_loader.playlists if p["id"] == id_playlist), None)
        if not playlist:
            return []

        musicas_playlist = []
        for id_musica in playlist["musicas"]:
            musica_data = next((m for m in data_loader.musicas if m["id"] == id_musica), None)
            if musica_data:
                musicas_playlist.append(
                    Musica(
                        id=musica_data["id"],
                        nome=musica_data["nome"],
                        artista=musica_data["artista"],
                        duracao_segundos=musica_data["duracaoSegundos"]
                    )
                )

        return musicas_playlist

    @strawberry.field
    def playlists_com_musica(self, id_musica: str) -> List[Playlist]:
        """
        Lista playlists que contêm uma música específica.

        Exemplo de query:
        {
          playlistsComMusica(idMusica: "music1") {
            id
            nome
            idUsuario
          }
        }
        """
        playlists_com_musica = [
            p for p in data_loader.playlists if id_musica in p["musicas"]
        ]

        return [
            Playlist(
                id=p["id"],
                nome=p["nome"],
                id_usuario=p["idUsuario"],
                musicas=p["musicas"]
            )
            for p in playlists_com_musica
        ]

    @strawberry.field
    def playlist_completa(self, id_playlist: str) -> Optional[PlaylistCompleta]:
        """
        Busca uma playlist com dados completos (usuário e músicas).
        Demonstra a capacidade do GraphQL de buscar dados relacionados em uma query.

        Exemplo de query:
        {
          playlistCompleta(idPlaylist: "playlist1") {
            id
            nome
            usuario {
              id
              nome
              idade
            }
            musicas {
              id
              nome
              artista
              duracaoSegundos
            }
          }
        }
        """
        playlist_data = next((p for p in data_loader.playlists if p["id"] == id_playlist), None)
        if not playlist_data:
            return None

        # Buscar dados do usuário
        usuario_data = next((u for u in data_loader.usuarios if u["id"] == playlist_data["idUsuario"]), None)
        if not usuario_data:
            return None

        usuario = Usuario(
            id=usuario_data["id"],
            nome=usuario_data["nome"],
            idade=usuario_data["idade"]
        )

        # Buscar dados das músicas
        musicas = []
        for id_musica in playlist_data["musicas"]:
            musica_data = next((m for m in data_loader.musicas if m["id"] == id_musica), None)
            if musica_data:
                musicas.append(
                    Musica(
                        id=musica_data["id"],
                        nome=musica_data["nome"],
                        artista=musica_data["artista"],
                        duracao_segundos=musica_data["duracaoSegundos"]
                    )
                )

        return PlaylistCompleta(
            id=playlist_data["id"],
            nome=playlist_data["nome"],
            usuario=usuario,
            musicas=musicas
        )

    @strawberry.field
    def estatisticas(self) -> Estatisticas:
        """
        Retorna estatísticas gerais do serviço.

        Exemplo de query:
        {
          estatisticas {
            totalUsuarios
            totalMusicas
            totalPlaylists
            usuariosComPlaylists
            mediaMusicasPorPlaylist
            tecnologia
          }
        }
        """
        total_musicas_em_playlists = sum(len(p["musicas"]) for p in data_loader.playlists)
        usuarios_com_playlists = len(set(p["idUsuario"] for p in data_loader.playlists))

        return Estatisticas(
            total_usuarios=len(data_loader.usuarios),
            total_musicas=len(data_loader.musicas),
            total_playlists=len(data_loader.playlists),
            usuarios_com_playlists=usuarios_com_playlists,
            media_musicas_por_playlist=total_musicas_em_playlists / len(data_loader.playlists) if data_loader.playlists else 0,
            tecnologia="GraphQL"
        )

# ========== MUTATIONS (Opcional) ==========

@strawberry.type
class Mutation:

    @strawberry.mutation
    def criar_usuario(self, nome: str, idade: int) -> Usuario:
        """
        Cria um novo usuário.

        Exemplo de mutation:
        mutation {
          criarUsuario(nome: "Novo Usuário", idade: 25) {
            id
            nome
            idade
          }
        }
        """
        novo_id = f"user{len(data_loader.usuarios) + 1}"
        novo_usuario = {"id": novo_id, "nome": nome, "idade": idade}
        data_loader.usuarios.append(novo_usuario)

        return Usuario(id=novo_id, nome=nome, idade=idade)

# ========== SCHEMA GRAPHQL ==========

schema = strawberry.Schema(query=Query, mutation=Mutation)

# ========== CONFIGURAÇÃO FASTAPI ==========

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Servidor GraphQL iniciando...")
    yield
    print("🛑 Servidor GraphQL finalizando...")

app = FastAPI(
    title="Serviço de Streaming - GraphQL API",
    description="API GraphQL para gerenciamento de usuários, músicas e playlists",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adicionar router GraphQL
graphql_app = GraphQLRouter(schema, graphiql=True)
app.include_router(graphql_app, prefix="/graphql")

# ========== PÁGINA INICIAL ==========

@app.get("/", response_class=HTMLResponse)
async def home():
    """Página inicial com informações sobre a API GraphQL"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Serviço de Streaming - GraphQL API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            h2 { color: #34495e; border-bottom: 2px solid #8e44ad; padding-bottom: 10px; }
            .query-example { background-color: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; font-family: 'Courier New', monospace; overflow-x: auto; margin: 10px 0; }
            .advantage { background-color: #e8f5e8; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #27ae60; }
            code { background-color: #34495e; color: white; padding: 2px 6px; border-radius: 3px; }
            a { color: #8e44ad; text-decoration: none; font-weight: bold; }
            a:hover { text-decoration: underline; }
            .feature { margin: 15px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎵 Serviço de Streaming - GraphQL API</h1>

            <h2>📊 Status do Serviço</h2>
            <p>✅ <strong>Servidor GraphQL ativo</strong></p>
            <p>📈 Dados carregados: <strong>5 usuários</strong>, <strong>8 músicas</strong>, <strong>4 playlists</strong></p>

            <h2>🚀 Interface GraphiQL</h2>
            <p>
                <a href="/graphql" target="_blank">🔗 Abrir GraphiQL</a> - 
                Interface interativa para testar queries GraphQL
            </p>

            <h2>✨ Principais Vantagens do GraphQL</h2>

            <div class="advantage">
                <strong>🎯 Busca Precisa:</strong> Cliente solicita exatamente os dados que precisa, evitando over-fetching
            </div>

            <div class="advantage">
                <strong>🔗 Queries Relacionadas:</strong> Uma única query pode buscar dados de múltiplas entidades relacionadas
            </div>

            <div class="advantage">
                <strong>📝 Schema Tipado:</strong> Definição clara de tipos e validação automática
            </div>

            <div class="advantage">
                <strong>🔍 Introspección:</strong> O schema é auto-documentado e explorável
            </div>

            <h2>🛠️ Exemplos de Queries</h2>

            <h3>Query Básica - Listar Usuários</h3>
            <div class="query-example">
{
  usuarios {
    id
    nome
    idade
  }
}
            </div>

            <h3>Query Seletiva - Apenas Nomes</h3>
            <div class="query-example">
{
  usuarios {
    nome
  }
}
            </div>

            <h3>Query com Parâmetros - Playlists de um Usuário</h3>
            <div class="query-example">
{
  playlistsUsuario(idUsuario: "user1") {
    id
    nome
    musicas
  }
}
            </div>

            <h3>Query Complexa - Playlist com Dados Completos</h3>
            <div class="query-example">
{
  playlistCompleta(idPlaylist: "playlist1") {
    id
    nome
    usuario {
      id
      nome
      idade
    }
    musicas {
      id
      nome
      artista
      duracaoSegundos
    }
  }
}
            </div>

            <h3>Query de Estatísticas</h3>
            <div class="query-example">
{
  estatisticas {
    totalUsuarios
    totalMusicas
    totalPlaylists
    mediaMusicasPorPlaylist
    tecnologia
  }
}
            </div>

            <h3>Mutation - Criar Usuário</h3>
            <div class="query-example">
mutation {
  criarUsuario(nome: "Novo Usuário", idade: 25) {
    id
    nome
    idade
  }
}
            </div>

            <h2>🔧 Queries Disponíveis</h2>

            <div class="feature">
                <strong>usuarios:</strong> Lista todos os usuários
            </div>

            <div class="feature">
                <strong>musicas:</strong> Lista todas as músicas
            </div>

            <div class="feature">
                <strong>usuario(id: String!):</strong> Busca usuário específico
            </div>

            <div class="feature">
                <strong>playlistsUsuario(idUsuario: String!):</strong> Playlists de um usuário
            </div>

            <div class="feature">
                <strong>musicasPlaylist(idPlaylist: String!):</strong> Músicas de uma playlist
            </div>

            <div class="feature">
                <strong>playlistsComMusica(idMusica: String!):</strong> Playlists que contêm uma música
            </div>

            <div class="feature">
                <strong>playlistCompleta(idPlaylist: String!):</strong> Playlist com dados completos
            </div>

            <div class="feature">
                <strong>estatisticas:</strong> Estatísticas gerais do serviço
            </div>

            <h2>🔧 Mutations Disponíveis</h2>

            <div class="feature">
                <strong>criarUsuario(nome: String!, idade: Int!):</strong> Cria novo usuário
            </div>

            <h2>💡 Como Testar</h2>
            <ol>
                <li>Clique no link <a href="/graphql" target="_blank">GraphiQL</a> acima</li>
                <li>Cole uma das queries de exemplo</li>
                <li>Clique no botão "Play" (▶️)</li>
                <li>Veja o resultado na aba "Response"</li>
                <li>Explore o schema na aba "Schema" ou "Docs"</li>
            </ol>

            <h2>🔧 Tecnologia</h2>
            <p>Esta API foi construída com <strong>Strawberry GraphQL</strong> e demonstra os princípios <strong>GraphQL</strong>:</p>
            <ul>
                <li>📝 <strong>Single Endpoint:</strong> Todas as operações em /graphql</li>
                <li>🎯 <strong>Cliente define a query:</strong> Flexibilidade total na busca</li>
                <li>🔗 <strong>Resolvers:</strong> Funções que buscam dados para cada campo</li>
                <li>📋 <strong>Schema tipado:</strong> Definição clara de tipos e operações</li>
                <li>🔍 <strong>Introspección:</strong> Schema auto-documentado</li>
            </ul>
        </div>
    </body>
    </html>
    """
    return html_content

# ========== FUNÇÃO PARA EXECUTAR SERVIDOR ==========

def executar_servidor():
    """Executa o servidor GraphQL"""
    import uvicorn
    print("🚀 Iniciando servidor GraphQL...")
    print("📍 Acesse: http://localhost:8001")
    print("🔍 GraphiQL: http://localhost:8001/graphql")

    uvicorn.run(
        "graphql_service:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    executar_servidor()