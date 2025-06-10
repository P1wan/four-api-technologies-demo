"""gRPC Backend Service
===================

Implementation of the gRPC service for the streaming platform.
Uses Protocol Buffers for message definitions and gRPC for communication.
"""

from concurrent import futures
import grpc
import time
from typing import List, Dict, Any
from grpc_reflection.v1alpha import reflection

from data_loader import get_data_loader

# Import generated gRPC code
import streaming_pb2
import streaming_pb2_grpc

data_loader = get_data_loader()

class StreamingService(streaming_pb2_grpc.StreamingServiceServicer):
    """Implementation of the StreamingService defined in streaming.proto."""

    def __init__(self):
        self.loader = data_loader

    def ListarTodosUsuarios(self, request, context):
        """List all users."""
        try:
            usuarios = self.loader.listar_todos_usuarios()
            response = streaming_pb2.UsuariosResponse()
            for usuario in usuarios:
                user_proto = streaming_pb2.Usuario(
                    id=usuario['id'],
                    nome=usuario['nome'],
                    idade=usuario['idade']
                )
                response.usuarios.append(user_proto)
            return response
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.UsuariosResponse()

    def ListarTodasMusicas(self, request, context):
        """List all songs."""
        try:
            musicas = self.loader.listar_todas_musicas()
            response = streaming_pb2.MusicasResponse()
            for musica in musicas:
                musica_proto = streaming_pb2.Musica(
                    id=musica['id'],
                    nome=musica['nome'],
                    artista=musica['artista'],
                    duracao_segundos=musica['duracaoSegundos']
                )
                response.musicas.append(musica_proto)
            return response
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.MusicasResponse()

    def ListarPlaylistsUsuario(self, request, context):
        """List all playlists for a user."""
        try:
            playlists = self.loader.listar_playlists_usuario(request.id_usuario)
            response = streaming_pb2.PlaylistsResponse()
            for playlist in playlists:
                playlist_proto = streaming_pb2.Playlist(
                    id=playlist['id'],
                    nome=playlist['nome'],
                    id_usuario=playlist['idUsuario'],
                    musicas=playlist['musicas']
                )
                response.playlists.append(playlist_proto)
            return response
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.PlaylistsResponse()

    def ListarMusicasPlaylist(self, request, context):
        """List all songs in a playlist."""
        try:
            musicas = self.loader.listar_musicas_playlist(request.id_playlist)
            response = streaming_pb2.MusicasResponse()
            for musica in musicas:
                musica_proto = streaming_pb2.Musica(
                    id=musica['id'],
                    nome=musica['nome'],
                    artista=musica['artista'],
                    duracao_segundos=musica['duracaoSegundos']
                )
                response.musicas.append(musica_proto)
            return response
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.MusicasResponse()

    def ListarPlaylistsComMusica(self, request, context):
        """List all playlists containing a specific song."""
        try:
            playlists = self.loader.listar_playlists_com_musica(request.id_musica)
            response = streaming_pb2.PlaylistsResponse()
            for playlist in playlists:
                playlist_proto = streaming_pb2.Playlist(
                    id=playlist['id'],
                    nome=playlist['nome'],
                    id_usuario=playlist['idUsuario'],
                    musicas=playlist['musicas']
                )
                response.playlists.append(playlist_proto)
            return response
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.PlaylistsResponse()

    def ObterEstatisticas(self, request, context):
        """Get service statistics."""
        try:
            stats = self.loader.obter_estatisticas()
            # Defensive: provide zeros for missing keys
            return streaming_pb2.EstatisticasResponse(
                total_usuarios=stats.get('total_usuarios', 0),
                total_musicas=stats.get('total_musicas', 0),
                total_playlists=stats.get('total_playlists', 0),
                media_musicas_por_playlist=stats.get('media_musicas_por_playlist', 0.0),
                tecnologia="gRPC"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return streaming_pb2.EstatisticasResponse()

    def StreamMusicas(self, request_iterator, context):
        """Stream songs as they are requested."""
        try:
            for request in request_iterator:
                musica = self.loader.obter_musica(request.id_musica)
                if musica:
                    yield streaming_pb2.Musica(
                        id=musica['id'],
                        nome=musica['nome'],
                        artista=musica['artista'],
                        duracao_segundos=musica['duracaoSegundos']
                    )
                time.sleep(0.1)  # Simulate processing time
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

def servir(porta: int = 50051) -> None:
    """Start the gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    streaming_pb2_grpc.add_StreamingServiceServicer_to_server(
        StreamingService(), server
    )
    
    # Add reflection service
    SERVICE_NAMES = (
        streaming_pb2.DESCRIPTOR.services_by_name['StreamingService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    server.add_insecure_port(f"[::]:{porta}")
    server.start()
    print(f"gRPC server started on port {porta}")
    server.wait_for_termination()

if __name__ == "__main__":
    servir()
