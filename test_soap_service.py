import pytest
import requests
import time
from typing import Dict, List
from zeep import Client
from zeep.transports import Transport

# Base URL for the SOAP service
BASE_URL = "http://localhost:8004/soap?wsdl"

def get_soap_client():
    """Create and return a SOAP client"""
    transport = Transport(timeout=60)
    return Client(BASE_URL, transport=transport)

def test_service_is_running():
    """Test if the SOAP service is running and accessible"""
    client = get_soap_client()
    # Try to get stats as a simple health check
    response = client.service.obter_estatisticas()
    assert response is not None

def test_list_users():
    """Test listing users"""
    client = get_soap_client()
    response = client.service.listar_usuarios()
    assert response is not None
    assert isinstance(response, list)

def test_list_songs():
    """Test listing songs"""
    client = get_soap_client()
    response = client.service.listar_musicas()
    assert response is not None
    assert isinstance(response, list)

def test_list_playlists():
    """Test listing playlists"""
    client = get_soap_client()
    response = client.service.listar_playlists()
    assert response is not None
    assert isinstance(response, list)

def test_listar_playlists_usuario():
    """Test listing playlists for a specific user"""
    client = get_soap_client()
    usuarios = client.service.listar_usuarios()
    user_id = usuarios[0].id
    playlists = client.service.listar_playlists_usuario(user_id)
    assert isinstance(playlists, list)
    for playlist in playlists:
        assert playlist.usuario == user_id

def test_listar_musicas_playlist():
    """Test listing songs for a playlist"""
    client = get_soap_client()
    playlists = client.service.listar_playlists()
    playlist_id = playlists[0].id
    musicas = client.service.listar_musicas_playlist(playlist_id)
    assert isinstance(musicas, list)
    for musica in musicas:
        assert hasattr(musica, 'id')
        assert hasattr(musica, 'nome')
        assert hasattr(musica, 'artista')
        assert hasattr(musica, 'duracao')

def test_listar_playlists_com_musica():
    """Test listing playlists containing a song"""
    client = get_soap_client()
    playlists = client.service.listar_playlists()
    playlist_id = playlists[0].id
    musicas = client.service.listar_musicas_playlist(playlist_id)
    assert len(musicas) > 0
    musica_id = musicas[0].id
    playlists_with_song = client.service.listar_playlists_com_musica(musica_id)
    assert isinstance(playlists_with_song, list)
    assert any(p.id == playlist_id for p in playlists_with_song)

def test_criar_musica():
    """Test creating a new song"""
    client = get_soap_client()
    nova_musica = client.service.criar_musica('Teste Song', 'Tester', 180)
    assert nova_musica.nome == 'Teste Song'
    musicas = client.service.listar_musicas()
    assert any(m.id == nova_musica.id for m in musicas)

def test_create_and_get_user():
    """Test creating a new user and retrieving it"""
    client = get_soap_client()
    
    # Create a new user
    created_user = client.service.criar_usuario(
        nome="Test User",
        idade=25
    )
    assert created_user is not None
    assert created_user.nome == "Test User"
    assert created_user.idade == 25
    
    # Get the created user
    retrieved_user = client.service.obter_usuario(id_usuario=created_user.id)
    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.nome == "Test User"

def test_create_and_get_playlist():
    """Test creating a playlist and retrieving its songs"""
    client = get_soap_client()
    
    # First create a user
    user = client.service.criar_usuario(
        nome="Playlist Creator",
        idade=30
    )
    
    # Create a playlist
    created_playlist = client.service.criar_playlist(
        nome="Test Playlist",
        id_usuario=user.id,
        musicas=[]  # Empty playlist for testing
    )
    assert created_playlist is not None
    assert created_playlist.nome == "Test Playlist"
    
    # Get the playlist
    retrieved_playlist = client.service.obter_playlist(id_playlist=created_playlist.id)
    assert retrieved_playlist is not None
    assert retrieved_playlist.id == created_playlist.id
    assert retrieved_playlist.nome == "Test Playlist"

def test_service_stats():
    """Test the stats endpoint"""
    client = get_soap_client()
    response = client.service.obter_estatisticas()
    assert response is not None
    assert hasattr(response, 'total_usuarios')
    assert hasattr(response, 'total_musicas')
    assert hasattr(response, 'total_playlists')
    assert hasattr(response, 'media_musicas_por_playlist')
    assert response.tecnologia == "SOAP"
    assert response.framework == "Spyne"

# ========== UPDATE TESTS ==========

def test_update_user():
    """Test updating an existing user"""
    client = get_soap_client()
    
    # Create a user to update
    created_user = client.service.criar_usuario(
        nome="Update Test User",
        idade=25
    )
    
    # Update the user
    updated_user = client.service.atualizar_usuario(
        id_usuario=created_user.id,
        nome="Updated User Name",
        idade=30
    )
    assert updated_user is not None
    assert updated_user.id == created_user.id
    assert updated_user.nome == "Updated User Name"
    assert updated_user.idade == 30

def test_update_song():
    """Test updating an existing song"""
    client = get_soap_client()
    
    # Create a song to update
    created_song = client.service.criar_musica("Update Test Song", "Test Artist", 180)
    
    # Update the song
    updated_song = client.service.atualizar_musica(
        id_musica=created_song.id,
        nome="Updated Song Name",
        artista="Updated Artist",
        duracao=200
    )
    assert updated_song is not None
    assert updated_song.id == created_song.id
    assert updated_song.nome == "Updated Song Name"
    assert updated_song.artista == "Updated Artist"
    assert updated_song.duracao == 200

def test_update_playlist():
    """Test updating an existing playlist"""
    client = get_soap_client()
    
    # Create a user and playlist to update
    user = client.service.criar_usuario(nome="Playlist Update User", idade=30)
    created_playlist = client.service.criar_playlist(
        nome="Update Test Playlist",
        id_usuario=user.id,
        musicas=[]
    )
    
    # Update the playlist
    updated_playlist = client.service.atualizar_playlist(
        id_playlist=created_playlist.id,
        nome="Updated Playlist Name",
        musicas=[]
    )
    assert updated_playlist is not None
    assert updated_playlist.id == created_playlist.id
    assert updated_playlist.nome == "Updated Playlist Name"

# ========== DELETE TESTS ==========

def test_delete_user():
    """Test deleting a user"""
    client = get_soap_client()
    
    # Create a user to delete
    created_user = client.service.criar_usuario(
        nome="Delete Test User",
        idade=40
    )
    
    # Delete the user
    result = client.service.deletar_usuario(id_usuario=created_user.id)
    assert result == True

def test_delete_song():
    """Test deleting a song"""
    client = get_soap_client()
    
    # Create a song to delete
    created_song = client.service.criar_musica("Delete Test Song", "Delete Artist", 120)
    
    # Delete the song
    result = client.service.deletar_musica(id_musica=created_song.id)
    assert result == True

def test_delete_playlist():
    """Test deleting a playlist"""
    client = get_soap_client()
    
    # Create a user and playlist to delete
    user = client.service.criar_usuario(nome="Playlist Delete User", idade=30)
    created_playlist = client.service.criar_playlist(
        nome="Delete Test Playlist",
        id_usuario=user.id,
        musicas=[]
    )
    
    # Delete the playlist
    result = client.service.deletar_playlist(id_playlist=created_playlist.id)
    assert result == True

# ========== ERROR HANDLING TESTS ==========

def test_get_nonexistent_user():
    """Test getting a user that doesn't exist"""
    client = get_soap_client()
    
    # Try to get a user with non-existent ID
    result = client.service.obter_usuario(id_usuario="nonexistent_user_id")
    assert result is not None
    # Em SOAP, retorna objeto com campos None/vazios em vez de erro 404
    assert result.id == "" or result.id is None
    assert result.nome == "" or result.nome is None

def test_get_nonexistent_song():
    """Test getting a song that doesn't exist"""
    client = get_soap_client()
    
    # Note: SOAP service doesn't have obter_musica method, so we'll test with delete
    # Try to delete non-existent song as a way to test non-existent song handling
    result = client.service.deletar_musica(id_musica="nonexistent_song_id")
    assert result == False

def test_get_nonexistent_playlist():
    """Test getting a playlist that doesn't exist"""
    client = get_soap_client()
    
    # Try to get a playlist with non-existent ID
    result = client.service.obter_playlist(id_playlist="nonexistent_playlist_id")
    # O Spyne/Zeep pode retornar None quando todos os campos do objeto são None
    if result is None:
        # Comportamento esperado: retorna None quando playlist não existe
        assert True
    else:
        # Caso retorne objeto com campos None
        assert result.id is None
        assert result.nome is None
        assert result.usuario is None

# ========== VALIDATION TESTS ==========

def test_update_user_invalid_data():
    """Test updating a user with invalid data"""
    client = get_soap_client()
    
    # Create a user first
    created_user = client.service.criar_usuario(nome="Valid User", idade=25)
    
    # Try to update with invalid data (empty name)
    result = client.service.atualizar_usuario(
        id_usuario=created_user.id,
        nome="",  # Empty name is allowed in this implementation
        idade=30
    )
    # The service allows empty names and converts them to None
    assert result.id == created_user.id
    assert result.nome is None or result.nome == ""  # SOAP pode retornar None ou string vazia
    assert result.idade == 30

def test_update_song_invalid_data():
    """Test updating a song with invalid data"""
    client = get_soap_client()
    
    # Create a song first
    created_song = client.service.criar_musica("Valid Song", "Valid Artist", 180)
    
    # Try to update with invalid data (negative duration)
    result = client.service.atualizar_musica(
        id_musica=created_song.id,
        nome="Updated Song",
        artista="Updated Artist",
        duracao=-1  # Negative duration - service aceita mas não é uma boa prática
    )
    # O serviço SOAP aceita duração negativa (sem validação), então a atualização funciona
    assert result.id == created_song.id
    assert result.nome == "Updated Song"
    assert result.artista == "Updated Artist"
    assert result.duracao == -1  # Valor negativo é aceito

def test_update_nonexistent_user():
    """Test updating a user that doesn't exist"""
    client = get_soap_client()
    
    # Try to update non-existent user
    result = client.service.atualizar_usuario(
        id_usuario="nonexistent_id",
        nome="Some Name",
        idade=25
    )
    # Should return empty object
    assert result.id == "" or result.id is None
    assert result.nome == "" or result.nome is None

def test_update_nonexistent_song():
    """Test updating a song that doesn't exist"""
    client = get_soap_client()
    
    # Try to update non-existent song
    result = client.service.atualizar_musica(
        id_musica="nonexistent_id",
        nome="Some Song",
        artista="Some Artist",
        duracao=180
    )
    # Should return empty object
    assert result.id == "" or result.id is None
    assert result.nome == "" or result.nome is None

def test_delete_nonexistent_user():
    """Test deleting a user that doesn't exist"""
    client = get_soap_client()
    
    # Try to delete non-existent user
    result = client.service.deletar_usuario(id_usuario="nonexistent_id")
    assert result == False

def test_delete_nonexistent_song():
    """Test deleting a song that doesn't exist"""
    client = get_soap_client()
    
    # Try to delete non-existent song
    result = client.service.deletar_musica(id_musica="nonexistent_id")
    assert result == False

def test_delete_nonexistent_playlist():
    """Test deleting a playlist that doesn't exist"""
    client = get_soap_client()
    
    # Try to delete non-existent playlist
    result = client.service.deletar_playlist(id_playlist="nonexistent_id")
    assert result == False



if __name__ == "__main__":
    print("Starting SOAP service tests...")
    print("Make sure the SOAP service is running on http://localhost:8004")
    print("Running tests in 5 seconds...")
    time.sleep(5)  # Give time to read the message
    
    # Run all tests
    pytest.main([__file__, "-v"])
