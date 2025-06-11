import pytest
import grpc
import time
from streaming_pb2 import (
    Empty,
    UsuarioRequest,
    PlaylistRequest,
    MusicaRequest,
    Usuario,
    Musica,
    Playlist,
    UsuariosResponse,
    MusicasResponse,
    PlaylistsResponse,
    EstatisticasResponse
)
from streaming_pb2_grpc import StreamingServiceStub

def create_channel():
    """Create a gRPC channel to the service."""
    return grpc.insecure_channel('localhost:50051')

def test_service_is_running():
    """Test if the gRPC service is running and accessible"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        response = stub.ObterEstatisticas(Empty())
        assert isinstance(response, EstatisticasResponse)
        assert hasattr(response, 'total_usuarios')
        assert hasattr(response, 'total_musicas')
        assert hasattr(response, 'total_playlists')
        assert hasattr(response, 'media_musicas_por_playlist')
        assert hasattr(response, 'tecnologia')

def test_list_users():
    """Test listing users"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        response = stub.ListarTodosUsuarios(Empty())
        assert isinstance(response, UsuariosResponse)
        assert hasattr(response, 'usuarios')
        assert len(response.usuarios) > 0  # Verifica se tem usuários
        for user in response.usuarios:
            assert isinstance(user, Usuario)
            assert hasattr(user, 'id')
            assert hasattr(user, 'nome')
            assert hasattr(user, 'idade')

def test_list_songs():
    """Test listing songs"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        response = stub.ListarTodasMusicas(Empty())
        assert isinstance(response, MusicasResponse)
        assert hasattr(response, 'musicas')
        assert hasattr(response.musicas, '__iter__')
        for song in response.musicas:
            assert isinstance(song, Musica)
            assert hasattr(song, 'id')
            assert hasattr(song, 'nome')
            assert hasattr(song, 'artista')
            assert hasattr(song, 'duracao_segundos')

def test_list_playlists():
    """Test listing playlists for a user"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        users_response = stub.ListarTodosUsuarios(Empty())
        user_id = next(iter(users_response.usuarios)).id
        
        response = stub.ListarPlaylistsUsuario(UsuarioRequest(id_usuario=user_id))
        assert isinstance(response, PlaylistsResponse)
        assert hasattr(response, 'playlists')
        assert hasattr(response.playlists, '__iter__')
        for playlist in response.playlists:
            assert isinstance(playlist, Playlist)
            assert hasattr(playlist, 'id')
            assert hasattr(playlist, 'nome')
            assert hasattr(playlist, 'id_usuario')
            assert hasattr(playlist, 'musicas')

def test_create_and_get_user():
    """Test creating a new user and retrieving it"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        pytest.skip("Create user not implemented in gRPC service")

def test_create_and_get_playlist():
    """Test creating a playlist and retrieving its songs"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        pytest.skip("Create playlist not implemented in gRPC service")

def test_service_stats():
    """Test the stats endpoint"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        response = stub.ObterEstatisticas(Empty())
        assert isinstance(response, EstatisticasResponse)
        assert isinstance(response.total_usuarios, int)
        assert isinstance(response.total_musicas, int)
        assert isinstance(response.total_playlists, int)
        assert isinstance(response.media_musicas_por_playlist, float)
        assert isinstance(response.tecnologia, str)
        assert response.tecnologia == "gRPC"

if __name__ == "__main__":
    print("Starting gRPC service tests...")
    print("Make sure the gRPC service is running on localhost:50051")
    print("Running tests in 5 seconds...")
    time.sleep(5)
    pytest.main([__file__]) 