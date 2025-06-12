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