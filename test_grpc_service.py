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
    EstatisticasResponse,
    CriarPlaylistRequest,
    CriarUsuarioRequest,
    CriarMusicaRequest,
    AtualizarUsuarioRequest,
    AtualizarMusicaRequest,
    AtualizarPlaylistRequest,
    BooleanResponse
)
from streaming_pb2_grpc import StreamingServiceStub

# ========== HELPER FUNCTIONS ==========

def create_channel():
    """Create a gRPC channel to the service."""
    return grpc.insecure_channel('localhost:50051')

def create_test_user(stub, nome="Test User gRPC", idade=25):
    """Helper function to create a test user"""
    try:
        user = stub.CriarUsuario(CriarUsuarioRequest(nome=nome, idade=idade))
        return user
    except grpc.RpcError:
        return None

def create_test_song(stub, nome="Test Song", artista="Test Artist", duracao=180):
    """Helper function to create a test song"""
    try:
        song = stub.CriarMusica(CriarMusicaRequest(
            nome=nome,
            artista=artista,
            duracao_segundos=duracao
        ))
        return song
    except grpc.RpcError:
        return None

def create_test_playlist(stub, nome="Test Playlist", user_id=None, musicas=None):
    """Helper function to create a test playlist"""
    if user_id is None:
        # Create a user first
        user = create_test_user(stub)
        user_id = user.id
    
    if musicas is None:
        musicas = []
    
    try:
        playlist = stub.CriarPlaylist(CriarPlaylistRequest(
            nome=nome,
            id_usuario=user_id,
            musicas=musicas
        ))
        return playlist
    except grpc.RpcError:
        return None

# ========== BASIC SERVICE TESTS ==========

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

# ========== USUARIOS CRUD TESTS ==========

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

def test_create_user():
    """Test creating a new user"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        created_user = stub.CriarUsuario(CriarUsuarioRequest(nome="Test User Create", idade=25))
        assert created_user.nome == "Test User Create"
        assert created_user.idade == 25
        assert created_user.id  # Verifica se tem ID

def test_get_user():
    """Test getting a specific user"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        
        # Create a user first
        created_user = create_test_user(stub, "Get User Test", 28)
        assert created_user is not None
        
        # Get the created user
        retrieved_user = stub.ObterUsuario(UsuarioRequest(id_usuario=created_user.id))
        assert retrieved_user.id == created_user.id
        assert retrieved_user.nome == "Get User Test"
        assert retrieved_user.idade == 28

def test_update_user():
    """Test updating an existing user"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        
        # Create a user first
        created_user = create_test_user(stub, "Update User Test", 30)
        assert created_user is not None
        
        # Update the user
        updated_user = stub.AtualizarUsuario(AtualizarUsuarioRequest(
            id_usuario=created_user.id,
            nome="Updated User Name",
            idade=35
        ))
        assert updated_user.id == created_user.id
        assert updated_user.nome == "Updated User Name"
        assert updated_user.idade == 35

def test_delete_user():
    """Test deleting a user"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        
        # Create a user first
        created_user = create_test_user(stub, "Delete User Test", 40)
        assert created_user is not None
        
        # Delete the user
        delete_response = stub.DeletarUsuario(UsuarioRequest(id_usuario=created_user.id))
        assert isinstance(delete_response, BooleanResponse)
        assert hasattr(delete_response, 'success')
        assert delete_response.success == True
        
        # Note: The gRPC service simulates deletion but doesn't actually remove from memory
        # This is by design for demonstration purposes

def test_get_nonexistent_user():
    """Test getting a user that doesn't exist"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        with pytest.raises(grpc.RpcError) as exc_info:
            stub.ObterUsuario(UsuarioRequest(id_usuario="nonexistent_id"))
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND

# ========== MUSICAS CRUD TESTS ==========

def test_list_songs():
    """Test listing songs"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        response = stub.ListarTodasMusicas(Empty())
        assert isinstance(response, MusicasResponse)
        assert hasattr(response, 'musicas')
        assert len(response.musicas) > 0  # Verifica se tem músicas
        for song in response.musicas:
            assert isinstance(song, Musica)
            assert hasattr(song, 'id')
            assert hasattr(song, 'nome')
            assert hasattr(song, 'artista')
            assert hasattr(song, 'duracao_segundos')

def test_create_song():
    """Test creating a new song"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        created_song = stub.CriarMusica(CriarMusicaRequest(
            nome="Test Song Create",
            artista="Test Artist",
            duracao_segundos=200
        ))
        assert created_song.nome == "Test Song Create"
        assert created_song.artista == "Test Artist"
        assert created_song.duracao_segundos == 200
        assert created_song.id  # Verifica se tem ID

def test_get_song():
    """Test getting a specific song"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        
        # Create a song first
        created_song = create_test_song(stub, "Get Song Test", "Get Artist", 150)
        assert created_song is not None
        
        # Get the created song
        retrieved_song = stub.ObterMusica(MusicaRequest(id_musica=created_song.id))
        assert retrieved_song.id == created_song.id
        assert retrieved_song.nome == "Get Song Test"
        assert retrieved_song.artista == "Get Artist"
        assert retrieved_song.duracao_segundos == 150

def test_update_song():
    """Test updating an existing song"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        
        # Create a song first
        created_song = create_test_song(stub, "Update Song Test", "Original Artist", 180)
        assert created_song is not None
        
        # Update the song
        updated_song = stub.AtualizarMusica(AtualizarMusicaRequest(
            id_musica=created_song.id,
            nome="Updated Song Name",
            artista="Updated Artist",
            duracao_segundos=220
        ))
        assert updated_song.id == created_song.id
        assert updated_song.nome == "Updated Song Name"
        assert updated_song.artista == "Updated Artist"
        assert updated_song.duracao_segundos == 220

def test_delete_song():
    """Test deleting a song"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        
        # Create a song first
        created_song = create_test_song(stub, "Delete Song Test", "Delete Artist", 120)
        assert created_song is not None
        
        # Delete the song
        delete_response = stub.DeletarMusica(MusicaRequest(id_musica=created_song.id))
        assert isinstance(delete_response, BooleanResponse)
        assert hasattr(delete_response, 'success')
        assert delete_response.success == True
        
        # Note: The gRPC service simulates deletion but doesn't actually remove from memory
        # This is by design for demonstration purposes

def test_get_nonexistent_song():
    """Test getting a song that doesn't exist"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        with pytest.raises(grpc.RpcError) as exc_info:
            stub.ObterMusica(MusicaRequest(id_musica="nonexistent_id"))
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND

# ========== PLAYLISTS CRUD TESTS ==========

def test_list_playlists():
    """Test listing playlists for a user"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        users_response = stub.ListarTodosUsuarios(Empty())
        user_id = next(iter(users_response.usuarios)).id
        
        response = stub.ListarPlaylistsUsuario(UsuarioRequest(id_usuario=user_id))
        assert isinstance(response, PlaylistsResponse)
        assert hasattr(response, 'playlists')
        # Pode retornar 0 playlists se o usuário não tem nenhuma
        for playlist in response.playlists:
            assert isinstance(playlist, Playlist)
            assert hasattr(playlist, 'id')
            assert hasattr(playlist, 'nome')
            assert hasattr(playlist, 'id_usuario')
            assert hasattr(playlist, 'musicas')

def test_create_playlist():
    """Test creating a playlist"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        
        # Get a user and some songs for the playlist
        users_response = stub.ListarTodosUsuarios(Empty())
        user_id = next(iter(users_response.usuarios)).id
        
        songs_response = stub.ListarTodasMusicas(Empty())
        song_ids = [song.id for song in songs_response.musicas[:2]]  # First 2 songs
        
        # Create playlist
        created_playlist = stub.CriarPlaylist(CriarPlaylistRequest(
            nome="Test Playlist Create",
            id_usuario=user_id,
            musicas=song_ids
        ))
        
        assert created_playlist.nome == "Test Playlist Create"
        assert created_playlist.id_usuario == user_id
        assert len(created_playlist.musicas) == 2
        assert created_playlist.id  # Verifica se tem ID

def test_get_playlist():
    """Test getting a specific playlist"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        
        # Create a playlist first
        created_playlist = create_test_playlist(stub, "Get Playlist Test")
        assert created_playlist is not None
        
        # Get the created playlist
        retrieved_playlist = stub.ObterPlaylist(PlaylistRequest(id_playlist=created_playlist.id))
        assert retrieved_playlist.id == created_playlist.id
        assert retrieved_playlist.nome == "Get Playlist Test"
        assert retrieved_playlist.id_usuario == created_playlist.id_usuario

def test_update_playlist():
    """Test updating an existing playlist"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        
        # Create a playlist first
        created_playlist = create_test_playlist(stub, "Update Playlist Test")
        assert created_playlist is not None
        
        # Get some songs for the update
        songs_response = stub.ListarTodasMusicas(Empty())
        song_ids = [song.id for song in songs_response.musicas[:3]]  # First 3 songs
        
        # Update the playlist
        updated_playlist = stub.AtualizarPlaylist(AtualizarPlaylistRequest(
            id_playlist=created_playlist.id,
            nome="Updated Playlist Name",
            musicas=song_ids
        ))
        assert updated_playlist.id == created_playlist.id
        assert updated_playlist.nome == "Updated Playlist Name"
        assert len(updated_playlist.musicas) == 3

def test_delete_playlist():
    """Test deleting a playlist"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        
        # Create a playlist first
        created_playlist = create_test_playlist(stub, "Delete Playlist Test")
        assert created_playlist is not None
        
        # Delete the playlist
        delete_response = stub.DeletarPlaylist(PlaylistRequest(id_playlist=created_playlist.id))
        assert isinstance(delete_response, BooleanResponse)
        assert hasattr(delete_response, 'success')
        assert delete_response.success == True
        
        # Note: The gRPC service simulates deletion but doesn't actually remove from memory
        # This is by design for demonstration purposes

def test_get_nonexistent_playlist():
    """Test getting a playlist that doesn't exist"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        with pytest.raises(grpc.RpcError) as exc_info:
            stub.ObterPlaylist(PlaylistRequest(id_playlist="nonexistent_id"))
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND

# ========== SPECIFIC GRPC OPERATIONS TESTS ==========

def test_list_playlist_songs():
    """Test listing songs from a specific playlist"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        
        # Get some songs and create a playlist with them
        songs_response = stub.ListarTodasMusicas(Empty())
        song_ids = [song.id for song in songs_response.musicas[:2]]
        
        created_playlist = create_test_playlist(stub, "Songs Test Playlist", musicas=song_ids)
        assert created_playlist is not None
        
        # List songs from the playlist
        playlist_songs = stub.ListarMusicasPlaylist(PlaylistRequest(id_playlist=created_playlist.id))
        assert isinstance(playlist_songs, MusicasResponse)
        assert len(playlist_songs.musicas) == 2
        
        # Verify the songs are the ones we added
        playlist_song_ids = [song.id for song in playlist_songs.musicas]
        for song_id in song_ids:
            assert song_id in playlist_song_ids

def test_list_playlists_with_song():
    """Test listing playlists that contain a specific song"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        
        # Get a song and create playlists with it
        songs_response = stub.ListarTodasMusicas(Empty())
        song_id = songs_response.musicas[0].id
        
        # Create two playlists with the same song
        playlist1 = create_test_playlist(stub, "Playlist With Song 1", musicas=[song_id])
        playlist2 = create_test_playlist(stub, "Playlist With Song 2", musicas=[song_id])
        
        assert playlist1 is not None
        assert playlist2 is not None
        
        # List playlists that contain the song
        playlists_with_song = stub.ListarPlaylistsComMusica(MusicaRequest(id_musica=song_id))
        assert isinstance(playlists_with_song, PlaylistsResponse)
        
        # Verify our created playlists are in the result
        playlist_ids = [p.id for p in playlists_with_song.playlists]
        assert playlist1.id in playlist_ids
        assert playlist2.id in playlist_ids

def test_stream_songs():
    """Test streaming songs functionality"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        
        # Get some song IDs
        songs_response = stub.ListarTodasMusicas(Empty())
        song_ids = [song.id for song in songs_response.musicas[:3]]
        
        # Create stream requests - using generator that yields MusicaRequest
        def generate_requests():
            for song_id in song_ids:
                yield MusicaRequest(id_musica=song_id)
        
        # Stream the songs
        streamed_songs = list(stub.StreamMusicas(generate_requests()))
        assert len(streamed_songs) == 3
        
        # Verify we got the correct songs
        streamed_song_ids = [song.id for song in streamed_songs]
        for song_id in song_ids:
            assert song_id in streamed_song_ids

# ========== COMPLETE WORKFLOW TESTS ==========

def test_create_and_get_user():
    """Test creating a new user and retrieving it"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        
        # Create user
        created_user = stub.CriarUsuario(CriarUsuarioRequest(nome="Test User gRPC", idade=25))
        assert created_user.nome == "Test User gRPC"
        assert created_user.idade == 25
        assert created_user.id  # Verifica se tem ID
        
        # Get user
        retrieved_user = stub.ObterUsuario(UsuarioRequest(id_usuario=created_user.id))
        assert retrieved_user.id == created_user.id
        assert retrieved_user.nome == "Test User gRPC"
        assert retrieved_user.idade == 25

def test_create_and_get_playlist():
    """Test creating a playlist and retrieving its songs"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        
        # Get a user and some songs for the playlist
        users_response = stub.ListarTodosUsuarios(Empty())
        user_id = next(iter(users_response.usuarios)).id
        
        songs_response = stub.ListarTodasMusicas(Empty())
        song_ids = [song.id for song in songs_response.musicas[:2]]  # First 2 songs
        
        # Create playlist
        created_playlist = stub.CriarPlaylist(CriarPlaylistRequest(
            nome="Test Playlist gRPC",
            id_usuario=user_id,
            musicas=song_ids
        ))
        
        assert created_playlist.nome == "Test Playlist gRPC"
        assert created_playlist.id_usuario == user_id
        assert len(created_playlist.musicas) == 2
        assert created_playlist.id  # Verifica se tem ID
        
        # Get playlist
        retrieved_playlist = stub.ObterPlaylist(PlaylistRequest(id_playlist=created_playlist.id))
        assert retrieved_playlist.id == created_playlist.id
        assert retrieved_playlist.nome == "Test Playlist gRPC"
        assert retrieved_playlist.id_usuario == user_id
        assert len(retrieved_playlist.musicas) == 2

# ========== VALIDATION AND ERROR TESTS ==========

def test_create_user_invalid_data():
    """Test creating user with invalid data"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        
        # Test empty name
        with pytest.raises(grpc.RpcError) as exc_info:
            stub.CriarUsuario(CriarUsuarioRequest(nome="", idade=25))
        assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
        
        # Test invalid age
        with pytest.raises(grpc.RpcError) as exc_info:
            stub.CriarUsuario(CriarUsuarioRequest(nome="Test", idade=-1))
        assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT

def test_create_song_invalid_data():
    """Test creating song with invalid data"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        
        # Test empty name
        with pytest.raises(grpc.RpcError) as exc_info:
            stub.CriarMusica(CriarMusicaRequest(nome="", artista="Artist", duracao_segundos=180))
        assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
        
        # Test invalid duration
        with pytest.raises(grpc.RpcError) as exc_info:
            stub.CriarMusica(CriarMusicaRequest(nome="Song", artista="Artist", duracao_segundos=-1))
        assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT

def test_create_playlist_invalid_user():
    """Test creating playlist with invalid user"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        
        with pytest.raises(grpc.RpcError) as exc_info:
            stub.CriarPlaylist(CriarPlaylistRequest(
                nome="Test Playlist",
                id_usuario="nonexistent_user",
                musicas=[]
            ))
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND

def test_update_nonexistent_resources():
    """Test updating resources that don't exist"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        
        # Test update nonexistent user
        with pytest.raises(grpc.RpcError) as exc_info:
            stub.AtualizarUsuario(AtualizarUsuarioRequest(
                id_usuario="nonexistent_id",
                nome="Updated Name",
                idade=30
            ))
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
        
        # Test update nonexistent song
        with pytest.raises(grpc.RpcError) as exc_info:
            stub.AtualizarMusica(AtualizarMusicaRequest(
                id_musica="nonexistent_id",
                nome="Updated Song",
                artista="Updated Artist",
                duracao_segundos=180
            ))
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
        
        # Test update nonexistent playlist
        with pytest.raises(grpc.RpcError) as exc_info:
            stub.AtualizarPlaylist(AtualizarPlaylistRequest(
                id_playlist="nonexistent_id",
                nome="Updated Playlist",
                musicas=[]
            ))
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND

def test_delete_nonexistent_resources():
    """Test deleting resources that don't exist"""
    with create_channel() as channel:
        stub = StreamingServiceStub(channel)
        
        # Test delete nonexistent user
        with pytest.raises(grpc.RpcError) as exc_info:
            stub.DeletarUsuario(UsuarioRequest(id_usuario="nonexistent_id"))
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
        
        # Test delete nonexistent song
        with pytest.raises(grpc.RpcError) as exc_info:
            stub.DeletarMusica(MusicaRequest(id_musica="nonexistent_id"))
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
        
        # Test delete nonexistent playlist
        with pytest.raises(grpc.RpcError) as exc_info:
            stub.DeletarPlaylist(PlaylistRequest(id_playlist="nonexistent_id"))
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND

if __name__ == "__main__":
    print("Starting comprehensive gRPC service tests...")
    print("Make sure the gRPC service is running on localhost:50051")
    print("Running tests in 5 seconds...")
    time.sleep(5)
    pytest.main([__file__, "-v"]) 