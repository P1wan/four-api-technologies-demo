"""
Serviço GraphQL para Plataforma de Streaming
============================================

Implementação completa do serviço GraphQL usando Strawberry.
Padronizado seguindo convenções Python e boas práticas de desenvolvimento.
"""

import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.schema.config import StrawberryConfig
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import List, Optional
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime

# Data loader usado por todos os backends
from dataloaders import get_data_loader
from dataloaders import GraphQLDataLoaders

# Tipos GraphQL padronizados

@dataclass
class ValidationError(Exception):
    """Erro de validação customizado para GraphQL."""
    message: str
    field: str

def validar_nome(nome: str, campo: str = "nome") -> None:
    """Valida um campo de nome."""
    if not nome or len(nome.strip()) == 0:
        raise ValidationError("Nome não pode ser vazio", campo)
    if len(nome) > 100:
        raise ValidationError("Nome muito longo (máximo 100 caracteres)", campo)

def validar_idade(idade: int) -> None:
    """Valida campo de idade."""
    if idade < 0 or idade > 120:
        raise ValidationError("Idade inválida (deve estar entre 0 e 120)", "idade")

def validar_duracao(duracao: int) -> None:
    """Valida duração da música."""
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
    # Forçar naming snake_case no schema GraphQL
    duracao_segundos: int = strawberry.field(name="duracao_segundos")

@strawberry.input
class MusicaInput:
    nome: str
    artista: str
    duracao_segundos: int = strawberry.field(name="duracao_segundos")

@strawberry.type
class Playlist:
    id: str
    nome: str
    # Forçar naming snake_case no schema GraphQL
    id_usuario: str = strawberry.field(name="id_usuario")
    musicas: List[str]  # IDs das músicas

@strawberry.input
class PlaylistInput:
    nome: str
    id_usuario: str = strawberry.field(name="id_usuario")
    musicas: List[str]

@strawberry.type
class PlaylistCompleta:
    """Playlist com dados completos das músicas."""
    id: str
    nome: str
    usuario: Usuario
    musicas: List[Musica]

@strawberry.type
class Estatisticas:
    total_usuarios: int = strawberry.field(name="total_usuarios")
    total_musicas: int = strawberry.field(name="total_musicas")
    total_playlists: int = strawberry.field(name="total_playlists")
    usuarios_com_playlists: int = strawberry.field(name="usuarios_com_playlists")
    media_musicas_por_playlist: float = strawberry.field(name="media_musicas_por_playlist")
    tecnologia: str

@dataclass
class GraphQLContext:
    """Contexto GraphQL com DataLoaders."""
    loaders: GraphQLDataLoaders

    def __init__(self, loaders: GraphQLDataLoaders):
        self.loaders = loaders

# Instância global do data loader (sempre usar dados reais)
data_loader = get_data_loader()
print("✅ StreamingDataLoader carregado para GraphQL")

# Resolvers GraphQL

@strawberry.type
class Query:
    @strawberry.field
    async def usuarios(self, info) -> List[Usuario]:
        """Lista todos os usuários."""
        usuarios = info.context["loaders"].data_loader.usuarios
        return [
            Usuario(id=u["id"], nome=u["nome"], idade=u["idade"])
            for u in usuarios
        ]

    @strawberry.field
    async def musicas(self, info) -> List[Musica]:
        """Lista todas as músicas."""
        musicas = info.context["loaders"].data_loader.musicas
        return [
            Musica(
                id=m["id"],
                nome=m["nome"],
                artista=m["artista"],
                # ✅ snake_case nativo do DataLoader
                duracao_segundos=m["duracao_segundos"]
            )
            for m in musicas
        ]    
    @strawberry.field
    async def usuario(self, info, id: str) -> Optional[Usuario]:
        """Obtém um usuário por ID."""
        try:
            usuario = info.context["loaders"].data_loader.get_usuario(id)
            if usuario:
                return Usuario(id=usuario["id"], nome=usuario["nome"], idade=usuario["idade"])
            return None
        except Exception:
            return None

    @strawberry.field
    async def playlists_usuario(self, info, id_usuario: str) -> List[Playlist]:
        """Lista playlists de um usuário."""
        try:
            playlists = info.context["loaders"].data_loader.listar_playlists_usuario(id_usuario)
            return [
                Playlist(
                    id=p["id"],
                    nome=p["nome"],
                    id_usuario=p["id_usuario"],
                    musicas=p["musicas"]
                )
                for p in playlists
            ]
        except Exception:
            return []

    @strawberry.field
    async def musicas_playlist(self, info, id_playlist: str) -> List[Musica]:
        """Lista músicas de uma playlist."""
        try:
            musicas = info.context["loaders"].data_loader.listar_musicas_playlist(id_playlist)
            return [
                Musica(
                    id=m["id"],
                    nome=m["nome"],
                    artista=m["artista"],
                    duracao_segundos=m["duracao_segundos"]
                )
                for m in musicas
            ]
        except Exception:
            return []

    @strawberry.field
    async def playlists_com_musica(self, info, id_musica: str) -> List[Playlist]:
        """Lista playlists que contêm uma música."""
        try:
            playlists = info.context["loaders"].data_loader.listar_playlists_com_musica(id_musica)
            return [
                Playlist(
                    id=p["id"],
                    nome=p["nome"],
                    id_usuario=p["id_usuario"],
                    musicas=p["musicas"]
                )
                for p in playlists
            ]
        except Exception:
            return []    
    @strawberry.field
    async def playlist_completa(self, info, id_playlist: str) -> Optional[PlaylistCompleta]:
        """Obtém playlist com dados completos."""
        try:
            # Obter playlist
            playlist = info.context["loaders"].data_loader.get_playlist(id_playlist)
            if not playlist:
                return None

            # Obter usuário
            usuario_data = info.context["loaders"].data_loader.get_usuario(playlist["id_usuario"])

            # Obter músicas
            musicas = info.context["loaders"].data_loader.listar_musicas_playlist(id_playlist)

            return PlaylistCompleta(
                id=playlist["id"],
                nome=playlist["nome"],
                usuario=Usuario(**usuario_data),
                musicas=[
                    Musica(
                        id=m["id"],
                        nome=m["nome"],
                        artista=m["artista"],
                        duracao_segundos=m["duracao_segundos"]
                    )
                    for m in musicas
                ]
            )
        except Exception:
            return None

    @strawberry.field
    async def estatisticas(self, info) -> Estatisticas:
        """Obtém estatísticas do serviço."""
        try:
            stats = info.context["loaders"].data_loader.obter_estatisticas()
            return Estatisticas(
                total_usuarios=stats.get('total_usuarios', 0),
                total_musicas=stats.get('total_musicas', 0),
                total_playlists=stats.get('total_playlists', 0),
                usuarios_com_playlists=stats.get('usuarios_com_playlists', 0),
                media_musicas_por_playlist=stats.get('media_musicas_por_playlist', 0.0),
                tecnologia="GraphQL"
            )
        except Exception:
            return Estatisticas(
                total_usuarios=0,
                total_musicas=0,
                total_playlists=0,
                usuarios_com_playlists=0,
                media_musicas_por_playlist=0.0,
                tecnologia="GraphQL"
            )

@strawberry.type
class Mutation:
    @strawberry.mutation
    def criar_usuario(self, input: UsuarioInput) -> Usuario:
        """Cria um novo usuário."""
        try:
            validar_nome(input.nome)
            validar_idade(input.idade)
            
            # Usar o método CRUD do data_loader
            novo_usuario = data_loader.criar_usuario(input.nome, input.idade)
            
            return Usuario(id=novo_usuario["id"], nome=novo_usuario["nome"], idade=novo_usuario["idade"])
        except ValidationError as e:
            raise Exception(f"Erro de validação: {e.message}")

    @strawberry.mutation
    def criar_musica(self, input: MusicaInput) -> Musica:
        """Cria uma nova música."""
        try:
            validar_nome(input.nome)
            validar_nome(input.artista, "artista")
            validar_duracao(input.duracao_segundos)
            
            # Usar o método CRUD do data_loader
            nova_musica = data_loader.criar_musica(input.nome, input.artista, input.duracao_segundos)
            
            return Musica(
                id=nova_musica["id"],
                nome=nova_musica["nome"],
                artista=nova_musica["artista"],
                duracao_segundos=nova_musica["duracao_segundos"]
            )
        except ValidationError as e:
            raise Exception(f"Erro de validação: {e.message}")    
    @strawberry.mutation
    def criar_playlist(self, input: PlaylistInput) -> Playlist:
        """Cria uma nova playlist."""
        try:
            validar_nome(input.nome)
            
            # Verificar se usuário existe
            usuario = data_loader.get_usuario(input.id_usuario)
            if not usuario:
                raise ValidationError("Usuário não encontrado", "id_usuario")
            
            # Verificar se músicas existem
            for id_musica in input.musicas:
                musica = data_loader.get_musica(id_musica)
                if not musica:
                    raise ValidationError(f"Música {id_musica} não encontrada", "musicas")
            
            # Usar o método CRUD do data_loader
            nova_playlist = data_loader.criar_playlist(input.nome, input.id_usuario, input.musicas)
            
            return Playlist(
                id=nova_playlist["id"],
                nome=nova_playlist["nome"],
                id_usuario=nova_playlist["id_usuario"],
                musicas=nova_playlist["musicas"]
            )
        except ValidationError as e:
            raise Exception(f"Erro de validação: {e.message}")    
    @strawberry.mutation
    def atualizar_usuario(self, id: str, input: UsuarioInput) -> Usuario:
        """Atualiza um usuário existente."""
        try:
            validar_nome(input.nome)
            validar_idade(input.idade)
            
            # Usar o método CRUD do data_loader
            usuario_atualizado = data_loader.atualizar_usuario(id, input.nome, input.idade)
            if not usuario_atualizado:
                raise ValidationError("Usuário não encontrado", "id")
            
            return Usuario(id=usuario_atualizado["id"], nome=usuario_atualizado["nome"], idade=usuario_atualizado["idade"])
            
        except ValidationError as e:
            raise Exception(f"Erro de validação: {e.message}")    
            
    @strawberry.mutation
    def atualizar_musica(self, id: str, input: MusicaInput) -> Musica:
        """Atualiza uma música existente."""
        try:
            validar_nome(input.nome, "nome")
            validar_nome(input.artista, "artista")
            validar_duracao(input.duracao_segundos)
            
            # Usar o método CRUD do data_loader
            musica_atualizada = data_loader.atualizar_musica(id, input.nome, input.artista, input.duracao_segundos)
            if not musica_atualizada:
                raise ValidationError("Música não encontrada", "id")
            
            return Musica(
                id=musica_atualizada["id"],
                nome=musica_atualizada["nome"],
                artista=musica_atualizada["artista"],
                duracao_segundos=musica_atualizada["duracao_segundos"]
            )
            
        except ValidationError as e:
            raise Exception(f"Erro de validação: {e.message}")

    @strawberry.mutation
    def atualizar_playlist(self, id: str, input: PlaylistInput) -> Playlist:
        """Atualiza uma playlist existente."""
        try:
            validar_nome(input.nome)
            
            # Verificar se usuário existe
            usuario = data_loader.get_usuario(input.id_usuario)
            if not usuario:
                raise ValidationError("Usuário não encontrado", "id_usuario")
            
            # Verificar se músicas existem
            for id_musica in input.musicas:
                musica = data_loader.get_musica(id_musica)
                if not musica:
                    raise ValidationError(f"Música {id_musica} não encontrada", "musicas")
            
            # Usar o método CRUD do data_loader
            playlist_atualizada = data_loader.atualizar_playlist(id, input.nome, input.musicas)
            if not playlist_atualizada:
                raise ValidationError("Playlist não encontrada", "id")
            
            return Playlist(
                id=playlist_atualizada["id"],
                nome=playlist_atualizada["nome"],
                id_usuario=playlist_atualizada["id_usuario"],
                musicas=playlist_atualizada["musicas"]
            )
            
        except ValidationError as e:
            raise Exception(f"Erro de validação: {e.message}")

    @strawberry.mutation
    def deletar_usuario(self, id: str) -> bool:
        """Remove um usuário do sistema."""
        try:
            # Usar o método CRUD do data_loader
            sucesso = data_loader.deletar_usuario(id)
            if not sucesso:
                raise ValidationError("Usuário não encontrado", "id")
            
            return True
            
        except ValidationError as e:
            raise Exception(f"Erro de validação: {e.message}")

    @strawberry.mutation
    def deletar_musica(self, id: str) -> bool:
        """Remove uma música do sistema."""
        try:
            # Usar o método CRUD do data_loader
            sucesso = data_loader.deletar_musica(id)
            if not sucesso:
                raise ValidationError("Música não encontrada", "id")
            
            return True
            
        except ValidationError as e:
            raise Exception(f"Erro de validação: {e.message}")

    @strawberry.mutation
    def deletar_playlist(self, id: str) -> bool:
        """Remove uma playlist do sistema."""
        try:
            # Usar o método CRUD do data_loader
            sucesso = data_loader.deletar_playlist(id)
            if not sucesso:
                raise ValidationError("Playlist não encontrada", "id")
            
            return True
            
        except ValidationError as e:
            raise Exception(f"Erro de validação: {e.message}")

# ========== SCHEMA GRAPHQL ==========

# Configuração para manter snake_case em vez de conversão automática para camelCase
schema = strawberry.Schema(
    query=Query, 
    mutation=Mutation,
    config=StrawberryConfig(auto_camel_case=False)
)

# ========== CONFIGURAÇÃO FASTAPI ==========

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Servidor GraphQL iniciando...")
    yield
    # Shutdown
    print("Servidor GraphQL finalizando...")

app = FastAPI(
    title="Serviço GraphQL - Plataforma de Streaming",
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
async def obter_contexto():
    """Retorna o contexto GraphQL com DataLoaders."""
    return {"loaders": GraphQLDataLoaders(data_loader)}

graphql_app = GraphQLRouter(
    schema,
    graphiql=True,
    context_getter=obter_contexto
)
app.include_router(graphql_app, prefix="/graphql")

# ========== PÁGINA INICIAL ==========

@app.get("/", response_class=HTMLResponse)
async def home():
    """Página inicial com informações sobre a API GraphQL."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Serviço GraphQL - Plataforma de Streaming</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            h2 { color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            .query { background-color: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; font-family: monospace; }
            code { background-color: #34495e; color: white; padding: 2px 6px; border-radius: 3px; }
            a { color: #3498db; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Serviço GraphQL - Plataforma de Streaming</h1>

            <h2>Playground GraphQL</h2>
            <p>Acesse o <a href="/graphql">GraphQL Playground</a> para testar as consultas interativamente.</p>

            <h2>Consultas de Exemplo</h2>

            <h3>Listar Usuários</h3>
            <div class="query">
                query {<br>
                &nbsp;&nbsp;usuarios {<br>
                &nbsp;&nbsp;&nbsp;&nbsp;id<br>
                &nbsp;&nbsp;&nbsp;&nbsp;nome<br>
                &nbsp;&nbsp;&nbsp;&nbsp;idade<br>
                &nbsp;&nbsp;}<br>
                }
            </div>

            <h3>Listar Músicas</h3>
            <div class="query">
                query {<br>
                &nbsp;&nbsp;musicas {<br>
                &nbsp;&nbsp;&nbsp;&nbsp;id<br>
                &nbsp;&nbsp;&nbsp;&nbsp;nome<br>
                &nbsp;&nbsp;&nbsp;&nbsp;artista<br>
                &nbsp;&nbsp;&nbsp;&nbsp;duracao_segundos<br>
                &nbsp;&nbsp;}<br>
                }
            </div>

            <h3>Obter Estatísticas</h3>
            <div class="query">
                query {<br>
                &nbsp;&nbsp;estatisticas {<br>
                &nbsp;&nbsp;&nbsp;&nbsp;total_usuarios<br>
                &nbsp;&nbsp;&nbsp;&nbsp;total_musicas<br>
                &nbsp;&nbsp;&nbsp;&nbsp;total_playlists<br>
                &nbsp;&nbsp;&nbsp;&nbsp;media_musicas_por_playlist<br>
                &nbsp;&nbsp;&nbsp;&nbsp;tecnologia<br>
                &nbsp;&nbsp;}<br>
                }
            </div>

            <h2>Mutations de Exemplo</h2>

            <h3>Criar Usuário</h3>
            <div class="query">
                mutation {<br>
                &nbsp;&nbsp;criarUsuario(input: {<br>
                &nbsp;&nbsp;&nbsp;&nbsp;nome: "João Silva"<br>
                &nbsp;&nbsp;&nbsp;&nbsp;idade: 30<br>
                &nbsp;&nbsp;}) {<br>
                &nbsp;&nbsp;&nbsp;&nbsp;id<br>
                &nbsp;&nbsp;&nbsp;&nbsp;nome<br>
                &nbsp;&nbsp;&nbsp;&nbsp;idade<br>
                &nbsp;&nbsp;}<br>
                }
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

# ========== FUNÇÃO PARA EXECUTAR SERVIDOR ==========

def executar_servidor():
    """Executa o servidor GraphQL."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    executar_servidor()