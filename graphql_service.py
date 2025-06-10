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
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import List, Optional
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime

# Data loader used by all backends
from data_loader import get_data_loader
from dataloaders import GraphQLDataLoaders

# ========== TIPOS GRAPHQL ==========

@dataclass
class ValidationError(Exception):
    """Custom validation error for GraphQL"""
    message: str
    field: str

def validate_nome(nome: str, field: str = "nome") -> None:
    """Validates a name field"""
    if not nome or len(nome.strip()) == 0:
        raise ValidationError("Nome não pode ser vazio", field)
    if len(nome) > 100:
        raise ValidationError("Nome muito longo (máximo 100 caracteres)", field)

def validate_idade(idade: int) -> None:
    """Validates age field"""
    if idade < 0 or idade > 120:
        raise ValidationError("Idade inválida (deve estar entre 0 e 120)", "idade")

def validate_duracao(duracao: int) -> None:
    """Validates song duration"""
    if duracao <= 0 or duracao > 3600:
        raise ValidationError("Duração inválida (deve estar entre 1 e 3600 segundos)", "duracao")

@strawberry.type
class Usuario:
    id: str
    nome: str
    idade: int

@strawberry.input
class UsuarioInput:
    nome: str
    idade: int

@strawberry.type
class Musica:
    id: str
    nome: str
    artista: str
    duracao_segundos: int

@strawberry.input
class MusicaInput:
    nome: str
    artista: str
    duracao_segundos: int

@strawberry.type
class Playlist:
    id: str
    nome: str
    id_usuario: str
    musicas: List[str]  # IDs das músicas

@strawberry.input
class PlaylistInput:
    nome: str
    id_usuario: str
    musicas: List[str]

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

# ========== CONTEXT ==========

@dataclass
class GraphQLContext:
    """GraphQL context with DataLoaders"""
    loaders: GraphQLDataLoaders

    def __init__(self, loaders: GraphQLDataLoaders):
        self.loaders = loaders

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
        print(f"Loaded {len(self.usuarios)} users, {len(self.musicas)} songs, {len(self.playlists)} playlists")
        print("Sample playlist data:", self.playlists[0] if self.playlists else "No playlists")

    def get_usuario(self, id: str) -> Optional[dict]:
        """Get user by ID with error handling"""
        usuario = next((u for u in self.usuarios if u["id"] == id), None)
        if not usuario:
            raise ValidationError(f"Usuário não encontrado: {id}", "id")
        return usuario

    def get_musica(self, id: str) -> Optional[dict]:
        """Get music by ID with error handling"""
        musica = next((m for m in self.musicas if m["id"] == id), None)
        if not musica:
            raise ValidationError(f"Música não encontrada: {id}", "id")
        return musica

    def get_playlist(self, id: str) -> Optional[dict]:
        """Get playlist by ID with error handling"""
        playlist = next((p for p in self.playlists if p["id"] == id), None)
        if not playlist:
            raise ValidationError(f"Playlist não encontrada: {id}", "id")
        return playlist

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
    async def usuarios(self, info) -> List[Usuario]:
        """List all users"""
        usuarios = info.context["loaders"].data_loader.usuarios
        return [
            Usuario(id=u["id"], nome=u["nome"], idade=u["idade"])
            for u in usuarios
        ]

    @strawberry.field
    async def musicas(self, info) -> List[Musica]:
        """List all songs"""
        musicas = info.context["loaders"].data_loader.musicas
        return [
            Musica(
                id=m["id"],
                nome=m["nome"],
                artista=m["artista"],
                duracao_segundos=m["duracaoSegundos"]
            )
            for m in musicas
        ]

    @strawberry.field
    async def usuario(self, info, id: str) -> Optional[Usuario]:
        """Get user by ID"""
        try:
            usuario_data = await info.context.loaders.get_usuario(id)
            return Usuario(
                id=usuario_data["id"],
                nome=usuario_data["nome"],
                idade=usuario_data["idade"]
            )
        except ValidationError:
            return None

    @strawberry.field
    async def playlists_usuario(self, info, id_usuario: str) -> List[Playlist]:
        """List playlists for a user"""
        try:
            # Get playlists directly from data loader
            playlists = [
                p for p in info.context["loaders"].data_loader.playlists 
                if p["idUsuario"] == id_usuario
            ]
            
            if not playlists:
                print(f"No playlists found for user {id_usuario}")
                return []
            
            return [
                Playlist(
                    id=p["id"],
                    nome=p["nome"],
                    id_usuario=p["idUsuario"],
                    musicas=p["musicas"]
                )
                for p in playlists
            ]
        except Exception as e:
            print(f"Error in playlists_usuario resolver: {str(e)}")
            return []

    @strawberry.field
    async def musicas_playlist(self, info, id_playlist: str) -> List[Musica]:
        """List songs in a playlist"""
        try:
            playlist = await info.context["loaders"].get_playlist(id_playlist)
            musicas = await info.context["loaders"].get_musicas(playlist["musicas"])
            return [
                Musica(
                    id=m["id"],
                    nome=m["nome"],
                    artista=m["artista"],
                    duracao_segundos=m["duracaoSegundos"]
                )
                for m in musicas
            ]
        except ValidationError:
            return []

    @strawberry.field
    async def playlists_com_musica(self, info, id_musica: str) -> List[Playlist]:
        """List playlists containing a song"""
        try:
            await info.context["loaders"].get_musica(id_musica)  # Validate song exists
            playlists = [
                p for p in info.context["loaders"].data_loader.playlists 
                if id_musica in p["musicas"]
            ]
            return [
                Playlist(
                    id=p["id"],
                    nome=p["nome"],
                    id_usuario=p["idUsuario"],
                    musicas=p["musicas"]
                )
                for p in playlists
            ]
        except ValidationError:
            return []

    @strawberry.field
    async def playlist_completa(self, info, id_playlist: str) -> Optional[PlaylistCompleta]:
        """Get playlist with complete data"""
        try:
            playlist = await info.context["loaders"].get_playlist(id_playlist)
            usuario = await info.context["loaders"].get_usuario(playlist["idUsuario"])
            musicas = await info.context["loaders"].get_musicas(playlist["musicas"])
            
            return PlaylistCompleta(
                id=playlist["id"],
                nome=playlist["nome"],
                usuario=Usuario(
                    id=usuario["id"],
                    nome=usuario["nome"],
                    idade=usuario["idade"]
                ),
                musicas=[
                    Musica(
                        id=m["id"],
                        nome=m["nome"],
                        artista=m["artista"],
                        duracao_segundos=m["duracaoSegundos"]
                    )
                    for m in musicas
                ]
            )
        except ValidationError:
            return None

    @strawberry.field
    async def estatisticas(self, info) -> Estatisticas:
        """Get service statistics"""
        total_musicas_em_playlists = sum(
            len(p["musicas"]) 
            for p in info.context["loaders"].data_loader.playlists
        )
        usuarios_com_playlists = len(set(
            p["idUsuario"] 
            for p in info.context["loaders"].data_loader.playlists
        ))

        return Estatisticas(
            total_usuarios=len(info.context["loaders"].data_loader.usuarios),
            total_musicas=len(info.context["loaders"].data_loader.musicas),
            total_playlists=len(info.context["loaders"].data_loader.playlists),
            usuarios_com_playlists=usuarios_com_playlists,
            media_musicas_por_playlist=total_musicas_em_playlists / len(info.context["loaders"].data_loader.playlists) if info.context["loaders"].data_loader.playlists else 0,
            tecnologia="GraphQL"
        )

# ========== MUTATIONS (Opcional) ==========

@strawberry.type
class Mutation:

    @strawberry.mutation
    def criar_usuario(self, input: UsuarioInput) -> Usuario:
        """Creates a new user with validation"""
        try:
            validate_nome(input.nome)
            validate_idade(input.idade)
            
            novo_id = f"user{len(data_loader.usuarios) + 1}"
            novo_usuario = {
                "id": novo_id,
                "nome": input.nome,
                "idade": input.idade
            }
            data_loader.usuarios.append(novo_usuario)
            
            return Usuario(**novo_usuario)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @strawberry.mutation
    def criar_musica(self, input: MusicaInput) -> Musica:
        """Creates a new song with validation"""
        try:
            validate_nome(input.nome, "nome")
            validate_nome(input.artista, "artista")
            validate_duracao(input.duracao_segundos)
            
            novo_id = f"music{len(data_loader.musicas) + 1}"
            nova_musica = {
                "id": novo_id,
                "nome": input.nome,
                "artista": input.artista,
                "duracaoSegundos": input.duracao_segundos
            }
            data_loader.musicas.append(nova_musica)
            
            return Musica(**nova_musica)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @strawberry.mutation
    def criar_playlist(self, input: PlaylistInput) -> Playlist:
        """Creates a new playlist with validation"""
        try:
            validate_nome(input.nome)
            
            # Validate user exists
            data_loader.get_usuario(input.id_usuario)
            
            # Validate all music IDs exist
            for id_musica in input.musicas:
                data_loader.get_musica(id_musica)
            
            novo_id = f"playlist{len(data_loader.playlists) + 1}"
            nova_playlist = {
                "id": novo_id,
                "nome": input.nome,
                "idUsuario": input.id_usuario,
                "musicas": input.musicas
            }
            data_loader.playlists.append(nova_playlist)
            
            return Playlist(**nova_playlist)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @strawberry.mutation
    def atualizar_usuario(self, id: str, input: UsuarioInput) -> Usuario:
        """Updates an existing user with validation"""
        try:
            validate_nome(input.nome)
            validate_idade(input.idade)
            
            usuario = data_loader.get_usuario(id)
            usuario.update({
                "nome": input.nome,
                "idade": input.idade
            })
            
            return Usuario(**usuario)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @strawberry.mutation
    def atualizar_musica(self, id: str, input: MusicaInput) -> Musica:
        """Updates an existing song with validation"""
        try:
            validate_nome(input.nome, "nome")
            validate_nome(input.artista, "artista")
            validate_duracao(input.duracao_segundos)
            
            musica = data_loader.get_musica(id)
            musica.update({
                "nome": input.nome,
                "artista": input.artista,
                "duracaoSegundos": input.duracao_segundos
            })
            
            return Musica(**musica)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @strawberry.mutation
    def atualizar_playlist(self, id: str, input: PlaylistInput) -> Playlist:
        """Updates an existing playlist with validation"""
        try:
            validate_nome(input.nome)
            
            # Validate user exists
            data_loader.get_usuario(input.id_usuario)
            
            # Validate all music IDs exist
            for id_musica in input.musicas:
                data_loader.get_musica(id_musica)
            
            playlist = data_loader.get_playlist(id)
            playlist.update({
                "nome": input.nome,
                "idUsuario": input.id_usuario,
                "musicas": input.musicas
            })
            
            return Playlist(**playlist)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @strawberry.mutation
    def deletar_usuario(self, id: str) -> bool:
        """Deletes a user and their playlists"""
        try:
            usuario = data_loader.get_usuario(id)
            data_loader.usuarios.remove(usuario)
            
            # Remove user's playlists
            data_loader.playlists = [
                p for p in data_loader.playlists 
                if p["idUsuario"] != id
            ]
            
            return True
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @strawberry.mutation
    def deletar_musica(self, id: str) -> bool:
        """Deletes a song and removes it from all playlists"""
        try:
            musica = data_loader.get_musica(id)
            data_loader.musicas.remove(musica)
            
            # Remove song from all playlists
            for playlist in data_loader.playlists:
                if id in playlist["musicas"]:
                    playlist["musicas"].remove(id)
            
            return True
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @strawberry.mutation
    def deletar_playlist(self, id: str) -> bool:
        """Deletes a playlist"""
        try:
            playlist = data_loader.get_playlist(id)
            data_loader.playlists.remove(playlist)
            return True
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

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
async def get_context():
    return {"loaders": GraphQLDataLoaders(data_loader)}

graphql_app = GraphQLRouter(
    schema,
    graphiql=True,
    context_getter=get_context
)
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