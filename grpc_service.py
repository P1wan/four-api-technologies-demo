# grpc_service.py
from concurrent import futures
import grpc
import json
import time
from grpc_reflection.v1alpha import reflection

# Importar o código gerado pelo protoc
import streaming_pb2
import streaming_pb2_grpc

# --- Funções para Carregar Dados ---
# Movemos a lógica de carregamento para dentro do serviço para simplificar.

def carregar_musicas():
    with open('data/musicas.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def carregar_playlists():
    with open('data/playlists.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def carregar_usuarios():
    with open('data/usuarios.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# --- Implementação do Serviço gRPC ---

class StreamingService(streaming_pb2_grpc.StreamingServiceServicer):
    """Implementa o serviço StreamingService definido em streaming.proto."""

    def __init__(self):
        self.musicas = carregar_musicas()
        self.playlists = carregar_playlists()
        self.usuarios = carregar_usuarios()
        print("Dados carregados. Serviço gRPC pronto.")

    def ListarTodasMusicas(self, request, context):
        """Retorna todas as músicas."""
        print("gRPC: Recebido pedido para ListarTodasMusicas.")
        musicas_proto = []
        for musica in self.musicas:
            musicas_proto.append(streaming_pb2.Musica(
                id=musica.get('id'),
                nome=musica.get('nome'),
                artista=musica.get('artista'),
                duracao_segundos=musica.get('duracao_segundos')
            ))
        return streaming_pb2.MusicasResponse(musicas=musicas_proto)
    
    def ListarTodosUsuarios(self, request, context):
        """Retorna todos os usuários."""
        print("gRPC: Recebido pedido para ListarTodosUsuarios.")
        usuarios_proto = []
        for usuario in self.usuarios:
            usuarios_proto.append(streaming_pb2.Usuario(
                id=usuario.get('id'),
                nome=usuario.get('nome'),
                idade=usuario.get('idade')
            ))
        return streaming_pb2.UsuariosResponse(usuarios=usuarios_proto)

    # Adicione as outras implementações de RPC aqui, seguindo o mesmo padrão.
    # Exemplo para ListarPlaylistsUsuario:    def ListarPlaylistsUsuario(self, request, context):
        """Retorna as playlists de um usuário específico."""
        print(f"gRPC: Recebido pedido para ListarPlaylistsUsuario para o usuário {request.id_usuario}.")
        playlists_usuario = [p for p in self.playlists if p.get('id_usuario') == request.id_usuario]
        
        playlists_proto = []
        for playlist in playlists_usuario:
            playlists_proto.append(streaming_pb2.Playlist(
                id=playlist.get('id'),
                nome=playlist.get('nome'),
                id_usuario=playlist.get('id_usuario'),
                musicas=playlist.get('musicas', [])
            ))
        return streaming_pb2.PlaylistsResponse(playlists=playlists_proto)    # TODO: Implementar as funções restantes:
    # - ListarMusicasPlaylist
    # - ListarPlaylistsComMusica
    # - ObterEstatisticas
    # - StreamMusicas

    def ListarMusicasPlaylist(self, request, context):
        """Retorna as músicas de uma playlist específica."""
        print(f"gRPC: Recebido pedido para ListarMusicasPlaylist para a playlist {request.id_playlist}.")
        playlist = next((p for p in self.playlists if p.get('id') == request.id_playlist), None)
        
        if not playlist:
            return streaming_pb2.MusicasResponse(musicas=[])
        
        musicas_proto = []
        for musica_id in playlist.get('musicas', []):
            musica = next((m for m in self.musicas if m.get('id') == musica_id), None)
            if musica:
                musicas_proto.append(streaming_pb2.Musica(
                    id=musica.get('id'),
                    nome=musica.get('nome'),
                    artista=musica.get('artista'),
                    duracao_segundos=musica.get('duracao_segundos')
                ))
        return streaming_pb2.MusicasResponse(musicas=musicas_proto)

    def ListarPlaylistsComMusica(self, request, context):
        """Retorna as playlists que contêm uma música específica."""
        print(f"gRPC: Recebido pedido para ListarPlaylistsComMusica para a música {request.id_musica}.")
        playlists_com_musica = [p for p in self.playlists if request.id_musica in p.get('musicas', [])]
        
        playlists_proto = []
        for playlist in playlists_com_musica:
            playlists_proto.append(streaming_pb2.Playlist(
                id=playlist.get('id'),
                nome=playlist.get('nome'),
                id_usuario=playlist.get('id_usuario'),
                musicas=playlist.get('musicas', [])
            ))
        return streaming_pb2.PlaylistsResponse(playlists=playlists_proto)

    def ObterEstatisticas(self, request, context):
        """Retorna estatísticas gerais do serviço."""
        print("gRPC: Recebido pedido para ObterEstatisticas.")
        total_usuarios = len(self.usuarios)
        total_musicas = len(self.musicas)
        total_playlists = len(self.playlists)
        
        # Calcular média de músicas por playlist
        total_musicas_em_playlists = sum(len(p.get('musicas', [])) for p in self.playlists)
        media_musicas_por_playlist = total_musicas_em_playlists / total_playlists if total_playlists > 0 else 0.0
        
        return streaming_pb2.EstatisticasResponse(
            total_usuarios=total_usuarios,
            total_musicas=total_musicas,
            total_playlists=total_playlists,
            media_musicas_por_playlist=media_musicas_por_playlist,
            tecnologia="gRPC"
        )

    def StreamMusicas(self, request_iterator, context):
        """Stream de músicas baseado nos IDs fornecidos."""
        print("gRPC: Recebido pedido para StreamMusicas.")
        for request in request_iterator:
            musica = next((m for m in self.musicas if m.get('id') == request.id_musica), None)
            if musica:
                yield streaming_pb2.Musica(
                    id=musica.get('id'),
                    nome=musica.get('nome'),
                    artista=musica.get('artista'),
                    duracao_segundos=musica.get('duracao_segundos')
                )
            else:
                print(f"Música não encontrada: {request.id_musica}")
                # Em caso de música não encontrada, ainda assim continuamos o stream

    # ========== CRUD OPERATIONS FOR USERS ==========

    def ObterUsuario(self, request, context):
        """Obtém um usuário específico por ID."""
        print(f"gRPC: Recebido pedido para ObterUsuario para o usuário {request.id_usuario}.")
        usuario = next((u for u in self.usuarios if u.get('id') == request.id_usuario), None)
        if usuario:
            return streaming_pb2.Usuario(
                id=usuario.get('id'),
                nome=usuario.get('nome'),
                idade=usuario.get('idade')
            )
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details('Usuário não encontrado')
        return streaming_pb2.Usuario()

    def CriarUsuario(self, request, context):
        """Cria um novo usuário."""
        print(f"gRPC: Recebido pedido para CriarUsuario: {request.nome}, {request.idade}.")
        import uuid
        
        # Validações
        if not request.nome or len(request.nome.strip()) == 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Nome é obrigatório')
            return streaming_pb2.Usuario()
        
        if request.idade < 0 or request.idade > 150:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Idade deve estar entre 0 e 150 anos')
            return streaming_pb2.Usuario()
        
        # Para demonstração: simular criação sem modificar dados originais
        novo_id = f"user-{len(self.usuarios) + 1}"
        novo_usuario = {
            "id": novo_id,
            "nome": request.nome.strip(),
            "idade": request.idade
        }
        
        return streaming_pb2.Usuario(
            id=novo_id,
            nome=request.nome.strip(),
            idade=request.idade
        )

    def AtualizarUsuario(self, request, context):
        """Atualiza um usuário existente."""
        print(f"gRPC: Recebido pedido para AtualizarUsuario para o usuário {request.id_usuario}.")
        
        # Verificar se usuário existe
        usuario = next((u for u in self.usuarios if u.get('id') == request.id_usuario), None)
        if not usuario:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Usuário não encontrado')
            return streaming_pb2.Usuario()
        
        # Validações
        if not request.nome or len(request.nome.strip()) == 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Nome é obrigatório')
            return streaming_pb2.Usuario()
        
        if request.idade < 0 or request.idade > 150:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Idade deve estar entre 0 e 150 anos')
            return streaming_pb2.Usuario()
        
        # Para demonstração: retornar versão atualizada sem modificar dados originais
        return streaming_pb2.Usuario(
            id=request.id_usuario,
            nome=request.nome.strip(),
            idade=request.idade
        )

    def DeletarUsuario(self, request, context):
        """Remove um usuário do sistema."""
        print(f"gRPC: Recebido pedido para DeletarUsuario para o usuário {request.id_usuario}.")
        
        # Verificar se usuário existe
        usuario = next((u for u in self.usuarios if u.get('id') == request.id_usuario), None)
        if not usuario:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Usuário não encontrado')
            return streaming_pb2.BooleanResponse(success=False, message='Usuário não encontrado')
        
        # Para demonstração: simular remoção sem modificar dados originais
        return streaming_pb2.BooleanResponse(
            success=True,
            message=f"Usuário '{usuario.get('nome')}' removido com sucesso"
        )

    # ========== CRUD OPERATIONS FOR MUSIC ==========

    def ObterMusica(self, request, context):
        """Obtém uma música específica por ID."""
        print(f"gRPC: Recebido pedido para ObterMusica para a música {request.id_musica}.")
        musica = next((m for m in self.musicas if m.get('id') == request.id_musica), None)
        if musica:
            return streaming_pb2.Musica(
                id=musica.get('id'),
                nome=musica.get('nome'),
                artista=musica.get('artista'),
                duracao_segundos=musica.get('duracao_segundos')
            )
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details('Música não encontrada')
        return streaming_pb2.Musica()

    def CriarMusica(self, request, context):
        """Cria uma nova música."""
        print(f"gRPC: Recebido pedido para CriarMusica: {request.nome}, {request.artista}, {request.duracao_segundos}.")
        
        # Validações
        if not request.nome or len(request.nome.strip()) == 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Nome da música é obrigatório')
            return streaming_pb2.Musica()
        
        if not request.artista or len(request.artista.strip()) == 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Artista é obrigatório')
            return streaming_pb2.Musica()
        
        if request.duracao_segundos <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Duração deve ser maior que zero')
            return streaming_pb2.Musica()
        
        # Para demonstração: simular criação sem modificar dados originais
        novo_id = f"music-{len(self.musicas) + 1}"
        
        return streaming_pb2.Musica(
            id=novo_id,
            nome=request.nome.strip(),
            artista=request.artista.strip(),
            duracao_segundos=request.duracao_segundos
        )

    def AtualizarMusica(self, request, context):
        """Atualiza uma música existente."""
        print(f"gRPC: Recebido pedido para AtualizarMusica para a música {request.id_musica}.")
        
        # Verificar se música existe
        musica = next((m for m in self.musicas if m.get('id') == request.id_musica), None)
        if not musica:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Música não encontrada')
            return streaming_pb2.Musica()
        
        # Validações
        if not request.nome or len(request.nome.strip()) == 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Nome da música é obrigatório')
            return streaming_pb2.Musica()
        
        if not request.artista or len(request.artista.strip()) == 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Artista é obrigatório')
            return streaming_pb2.Musica()
        
        if request.duracao_segundos <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Duração deve ser maior que zero')
            return streaming_pb2.Musica()
        
        # Para demonstração: retornar versão atualizada sem modificar dados originais
        return streaming_pb2.Musica(
            id=request.id_musica,
            nome=request.nome.strip(),
            artista=request.artista.strip(),
            duracao_segundos=request.duracao_segundos
        )

    def DeletarMusica(self, request, context):
        """Remove uma música do sistema."""
        print(f"gRPC: Recebido pedido para DeletarMusica para a música {request.id_musica}.")
        
        # Verificar se música existe
        musica = next((m for m in self.musicas if m.get('id') == request.id_musica), None)
        if not musica:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Música não encontrada')
            return streaming_pb2.BooleanResponse(success=False, message='Música não encontrada')
        
        # Para demonstração: simular remoção sem modificar dados originais
        return streaming_pb2.BooleanResponse(
            success=True,
            message=f"Música '{musica.get('nome')}' removida com sucesso"
        )

    # ========== CRUD OPERATIONS FOR PLAYLISTS ==========

    def ObterPlaylist(self, request, context):
        """Obtém uma playlist específica por ID."""
        print(f"gRPC: Recebido pedido para ObterPlaylist para a playlist {request.id_playlist}.")
        playlist = next((p for p in self.playlists if p.get('id') == request.id_playlist), None)
        if playlist:
            return streaming_pb2.Playlist(
                id=playlist.get('id'),
                nome=playlist.get('nome'),
                id_usuario=playlist.get('id_usuario'),
                musicas=playlist.get('musicas', [])
            )
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details('Playlist não encontrada')
        return streaming_pb2.Playlist()

    def CriarPlaylist(self, request, context):
        """Cria uma nova playlist."""
        print(f"gRPC: Recebido pedido para CriarPlaylist: {request.nome}, {request.id_usuario}.")
        
        # Validações
        if not request.nome or len(request.nome.strip()) == 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Nome da playlist é obrigatório')
            return streaming_pb2.Playlist()
        
        if not request.id_usuario or len(request.id_usuario.strip()) == 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('ID do usuário é obrigatório')
            return streaming_pb2.Playlist()
        
        # Verificar se usuário existe
        usuario = next((u for u in self.usuarios if u.get('id') == request.id_usuario), None)
        if not usuario:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Usuário não encontrado')
            return streaming_pb2.Playlist()
        
        # Verificar se todas as músicas existem
        for id_musica in request.musicas:
            musica = next((m for m in self.musicas if m.get('id') == id_musica), None)
            if not musica:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f'Música não encontrada: {id_musica}')
                return streaming_pb2.Playlist()
        
        # Para demonstração: simular criação sem modificar dados originais
        novo_id = f"playlist-{len(self.playlists) + 1}"
        
        return streaming_pb2.Playlist(
            id=novo_id,
            nome=request.nome.strip(),
            id_usuario=request.id_usuario,
            musicas=list(request.musicas)
        )

    def AtualizarPlaylist(self, request, context):
        """Atualiza uma playlist existente."""
        print(f"gRPC: Recebido pedido para AtualizarPlaylist para a playlist {request.id_playlist}.")
        
        # Verificar se playlist existe
        playlist = next((p for p in self.playlists if p.get('id') == request.id_playlist), None)
        if not playlist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Playlist não encontrada')
            return streaming_pb2.Playlist()
        
        # Validações
        if not request.nome or len(request.nome.strip()) == 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Nome da playlist é obrigatório')
            return streaming_pb2.Playlist()
        
        # Verificar se todas as músicas existem
        for id_musica in request.musicas:
            musica = next((m for m in self.musicas if m.get('id') == id_musica), None)
            if not musica:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f'Música não encontrada: {id_musica}')
                return streaming_pb2.Playlist()
        
        # Para demonstração: retornar versão atualizada sem modificar dados originais
        return streaming_pb2.Playlist(
            id=request.id_playlist,
            nome=request.nome.strip(),
            id_usuario=playlist.get('id_usuario'),
            musicas=list(request.musicas)
        )

    def DeletarPlaylist(self, request, context):
        """Remove uma playlist do sistema."""
        print(f"gRPC: Recebido pedido para DeletarPlaylist para a playlist {request.id_playlist}.")
        
        # Verificar se playlist existe
        playlist = next((p for p in self.playlists if p.get('id') == request.id_playlist), None)
        if not playlist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Playlist não encontrada')
            return streaming_pb2.BooleanResponse(success=False, message='Playlist não encontrada')
        
        # Para demonstração: simular remoção sem modificar dados originais
        return streaming_pb2.BooleanResponse(
            success=True,
            message=f"Playlist '{playlist.get('nome')}' removida com sucesso"
        )

def servir(porta=50051):
    """Inicia o servidor gRPC na porta especificada."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    streaming_pb2_grpc.add_StreamingServiceServicer_to_server(StreamingService(), server)
    
    # Habilitar a reflexão do servidor (útil para ferramentas como grpcurl)
    SERVICE_NAMES = (
        streaming_pb2.DESCRIPTOR.services_by_name['StreamingService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    server.add_insecure_port(f'[::]:{porta}')
    server.start()
    print(f"Servidor gRPC iniciado na porta {porta}.")
    server.wait_for_termination()

if __name__ == '__main__':
    servir()