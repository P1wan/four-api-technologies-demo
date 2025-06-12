"""
Serviço GraphQL para Plataforma de Streaming
============================================

Implementação completa do serviço GraphQL usando Strawberry.
Padronizado seguindo convenções Python e boas práticas de desenvolvimento.
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
    # Manter consistência: usar snake_case no GraphQL, converter de camelCase do JSON
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
    """Playlist com dados completos das músicas."""
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

@dataclass
class GraphQLContext:
    """Contexto GraphQL com DataLoaders."""
    loaders: GraphQLDataLoaders

    def __init__(self, loaders: GraphQLDataLoaders):
        self.loaders = loaders

# Data Loader para fallback (somente para demonstração)
class GraphQLDataLoaderFallback:
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

        print("GraphQL Data Loader (fallback) inicializado")

    def obter_usuario(self, id_usuario: str) -> Optional[dict]:
        """Obtém usuário por ID com tratamento de erro."""
        usuario = next((u for u in self.usuarios if u["id"] == id_usuario), None)
        if not usuario:
            raise ValidationError(f"Usuário não encontrado: {id_usuario}", "id")
        return usuario

    def obter_musica(self, id_musica: str) -> Optional[dict]:
        """Obtém música por ID com tratamento de erro."""
        musica = next((m for m in self.musicas if m["id"] == id_musica), None)
        if not musica:
            raise ValidationError(f"Música não encontrada: {id_musica}", "id")
        return musica

    def obter_playlist(self, id_playlist: str) -> Optional[dict]:
        """Obtém playlist por ID com tratamento de erro."""
        playlist = next((p for p in self.playlists if p["id"] == id_playlist), None)
        if not playlist:
            raise ValidationError(f"Playlist não encontrada: {id_playlist}", "id")
        return playlist

# Instância global: tenta usar dados reais e faz fallback para o mock
try:
    data_loader = get_data_loader()
    print("Dados reais carregados para GraphQL")
except Exception as exc:
    print(f"Erro ao carregar dados reais: {exc}")
    print("Utilizando GraphQL fallback")
    data_loader = GraphQLDataLoaderFallback()

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
                # Conversão: duracaoSegundos (JSON) -> duracao_segundos (GraphQL)
                duracao_segundos=m["duracaoSegundos"]
            )
            for m in musicas
        ]    @strawberry.field
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
                    id_usuario=p["idUsuario"],
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
                    duracao_segundos=m["duracaoSegundos"]
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
                    id_usuario=p["idUsuario"],
                    musicas=p["musicas"]
                )
                for p in playlists
            ]
        except Exception:
            return []    @strawberry.field
    async def playlist_completa(self, info, id_playlist: str) -> Optional[PlaylistCompleta]:
        """Obtém playlist com dados completos."""
        try:
            # Obter playlist
            playlist = info.context["loaders"].data_loader.get_playlist(id_playlist)
            if not playlist:
                return None

            # Obter usuário
            usuario_data = info.context["loaders"].data_loader.get_usuario(playlist["idUsuario"])

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
                        duracao_segundos=m["duracaoSegundos"]
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
            
            import uuid
            novo_id = str(uuid.uuid4())
            novo_usuario = {
                "id": novo_id,
                "nome": input.nome,
                "idade": input.idade
            }
            
            # Para demonstração, adicionar à lista local (não persistente)
            data_loader.usuarios.append(novo_usuario)
            
            return Usuario(id=novo_id, nome=input.nome, idade=input.idade)
        except ValidationError as e:
            raise Exception(f"Erro de validação: {e.message}")

    @strawberry.mutation
    def criar_musica(self, input: MusicaInput) -> Musica:
        """Cria uma nova música."""
        try:
            validar_nome(input.nome)
            validar_nome(input.artista, "artista")
            validar_duracao(input.duracao_segundos)
            
            import uuid
            novo_id = str(uuid.uuid4())
            
            # Para demonstração: não modificar dados compartilhados
            # Em produção: salvar no banco de dados
            return Musica(
                id=novo_id,
                nome=input.nome,
                artista=input.artista,
                duracao_segundos=input.duracao_segundos
            )
        except ValidationError as e:
            raise Exception(f"Erro de validação: {e.message}")    @strawberry.mutation
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
            
            import uuid
            novo_id = str(uuid.uuid4())
            
            # Para demonstração: não modificar dados compartilhados
            # Em produção: salvar no banco de dados
            return Playlist(
                id=novo_id,
                nome=input.nome,
                id_usuario=input.id_usuario,
                musicas=input.musicas
            )
        except ValidationError as e:
            raise Exception(f"Erro de validação: {e.message}")    @strawberry.mutation
    def atualizar_usuario(self, id: str, input: UsuarioInput) -> Usuario:
        """Atualiza um usuário existente."""
        try:
            validar_nome(input.nome)
            validar_idade(input.idade)
            
            # Verificar se usuário existe
            usuario = data_loader.get_usuario(id)
            if not usuario:
                raise ValidationError("Usuário não encontrado", "id")
            
            # Para demonstração: retornar versão atualizada sem modificar dados originais
            return Usuario(id=id, nome=input.nome, idade=input.idade)
            
        except ValidationError as e:
            raise Exception(f"Erro de validação: {e.message}")    @strawberry.mutation
    def atualizar_musica(self, id: str, input: MusicaInput) -> Musica:
        """Atualiza uma música existente."""
        try:
            validar_nome(input.nome, "nome")
            validar_nome(input.artista, "artista")
            validar_duracao(input.duracao_segundos)
            
            # Verificar se música existe
            musica = data_loader.get_musica(id)
            if not musica:
                raise ValidationError("Música não encontrada", "id")
            
            # Para demonstração: retornar versão atualizada sem modificar dados originais
            return Musica(
                id=id,
                nome=input.nome,
                artista=input.artista,
                duracao_segundos=input.duracao_segundos
            )
            
        except ValidationError as e:
            raise Exception(f"Erro de validação: {e.message}")

    @strawberry.mutation
    def atualizar_playlist(self, id: str, input: PlaylistInput) -> Playlist:
        """Atualiza uma playlist existente."""
        try:
            validar_nome(input.nome)
            
            # Verificar se playlist existe
            if hasattr(data_loader, 'obter_playlist_por_id'):
                playlist = data_loader.obter_playlist_por_id(id)
            else:
                playlist = data_loader.obter_playlist(id)
            
            if not playlist:
                raise ValidationError("Playlist não encontrada", "id")
            
            # Verificar se usuário existe
            if hasattr(data_loader, 'obter_usuario_por_id'):
                usuario = data_loader.obter_usuario_por_id(input.id_usuario)
            else:
                usuario = data_loader.obter_usuario(input.id_usuario)
                
            if not usuario:
                raise ValidationError("Usuário não encontrado", "id_usuario")
            
            # Verificar se músicas existem
            for id_musica in input.musicas:
                if hasattr(data_loader, 'obter_musica_por_id'):
                    musica = data_loader.obter_musica_por_id(id_musica)
                else:
                    musica = data_loader.obter_musica(id_musica)
                
                if not musica:
                    raise ValidationError(f"Música {id_musica} não encontrada", "musicas")
            
            # Para demonstração: retornar versão atualizada sem modificar dados originais
            return Playlist(
                id=id,
                nome=input.nome,
                id_usuario=input.id_usuario,
                musicas=input.musicas
            )
            
        except ValidationError as e:
            raise Exception(f"Erro de validação: {e.message}")

    @strawberry.mutation
    def deletar_usuario(self, id: str) -> bool:
        """Remove um usuário do sistema."""
        try:
            # Verificar se usuário existe
            if hasattr(data_loader, 'obter_usuario_por_id'):
                usuario = data_loader.obter_usuario_por_id(id)
            else:
                usuario = data_loader.obter_usuario(id)
            
            if not usuario:
                raise ValidationError("Usuário não encontrado", "id")
            
            # Para demonstração: simular remoção sem modificar dados originais
            # Em produção: remover do banco de dados
            return True
            
        except ValidationError as e:
            raise Exception(f"Erro de validação: {e.message}")

    @strawberry.mutation
    def deletar_musica(self, id: str) -> bool:
        """Remove uma música do sistema."""
        try:
            # Verificar se música existe
            if hasattr(data_loader, 'obter_musica_por_id'):
                musica = data_loader.obter_musica_por_id(id)
            else:
                musica = data_loader.obter_musica(id)
            
            if not musica:
                raise ValidationError("Música não encontrada", "id")
            
            # Para demonstração: simular remoção sem modificar dados originais
            # Em produção: remover do banco de dados
            return True
            
        except ValidationError as e:
            raise Exception(f"Erro de validação: {e.message}")

    @strawberry.mutation
    def deletar_playlist(self, id: str) -> bool:
        """Remove uma playlist do sistema."""
        try:
            # Verificar se playlist existe
            if hasattr(data_loader, 'obter_playlist_por_id'):
                playlist = data_loader.obter_playlist_por_id(id)
            else:
                playlist = data_loader.obter_playlist(id)
            
            if not playlist:
                raise ValidationError("Playlist não encontrada", "id")
            
            # Para demonstração: simular remoção sem modificar dados originais
            # Em produção: remover do banco de dados
            return True
            
        except ValidationError as e:
            raise Exception(f"Erro de validação: {e.message}")

# ========== SCHEMA GRAPHQL ==========

schema = strawberry.Schema(query=Query, mutation=Mutation)

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