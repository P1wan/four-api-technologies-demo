import pytest
import requests
import time
from typing import Dict, List

# Base URL for the REST service
BASE_URL = "http://localhost:8000"

# ========== BASIC SERVICE TESTS ==========

def test_service_is_running():
    """Test if the service is running and accessible"""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "Serviço de Streaming - REST API" in response.text

def test_service_stats():
    """Test the stats endpoint"""
    response = requests.get(f"{BASE_URL}/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "total_usuarios" in stats
    assert "total_musicas" in stats
    assert "total_playlists" in stats
    assert stats["tecnologia"] == "REST"
    assert stats["framework"] == "FastAPI"

# ========== HELPER FUNCTIONS ==========

def create_test_user(nome="Test User Helper", idade=25):
    """Helper function to create a user for testing"""
    new_user = {
        "nome": nome,
        "idade": idade
    }
    response = requests.post(f"{BASE_URL}/usuarios", json=new_user)
    if response.status_code == 200:
        return response.json()
    return None

def create_test_song(nome="Test Song", artista="Test Artist", duracao=180):
    """Helper function to create a song for testing"""
    new_song = {
        "nome": nome,
        "artista": artista,
        "duracao_segundos": duracao
    }
    response = requests.post(f"{BASE_URL}/musicas", json=new_song)
    if response.status_code == 200:
        return response.json()
    return None

# ========== USUARIOS CRUD TESTS ==========

def test_list_users():
    """Test listing users endpoint"""
    response = requests.get(f"{BASE_URL}/usuarios")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)

def test_create_user():
    """Test creating a new user"""
    new_user = {
        "nome": "Test User Create",
        "idade": 25
    }
    response = requests.post(f"{BASE_URL}/usuarios", json=new_user)
    assert response.status_code == 200
    created_user = response.json()
    assert created_user["nome"] == new_user["nome"]
    assert created_user["idade"] == new_user["idade"]
    assert "id" in created_user

def test_get_user():
    """Test getting a specific user"""
    # First create a user
    created_user = create_test_user("Get User Test", 28)
    assert created_user is not None
    user_id = created_user["id"]
    
    # Get the created user
    response = requests.get(f"{BASE_URL}/usuarios/{user_id}")
    assert response.status_code == 200
    retrieved_user = response.json()
    assert retrieved_user["id"] == user_id
    assert retrieved_user["nome"] == created_user["nome"]
    assert retrieved_user["idade"] == created_user["idade"]

def test_update_user():
    """Test updating an existing user"""
    # First create a user
    created_user = create_test_user("Update User Test", 35)
    assert created_user is not None
    user_id = created_user["id"]
    
    # Update the user
    update_data = {
        "nome": "Updated User Name",
        "idade": 30
    }
    response = requests.put(f"{BASE_URL}/usuarios/{user_id}", json=update_data)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["id"] == user_id
    assert updated_user["nome"] == update_data["nome"]
    assert updated_user["idade"] == update_data["idade"]

def test_delete_user():
    """Test deleting a user"""
    # First create a user
    created_user = create_test_user("Delete User Test", 40)
    assert created_user is not None
    user_id = created_user["id"]
    
    # Delete the user
    response = requests.delete(f"{BASE_URL}/usuarios/{user_id}")
    assert response.status_code == 200
    delete_response = response.json()
    assert "message" in delete_response
    assert "removido com sucesso" in delete_response["message"]
    
    # Verify user is deleted (should return 404)
    response = requests.get(f"{BASE_URL}/usuarios/{user_id}")
    assert response.status_code == 404

def test_get_nonexistent_user():
    """Test getting a user that doesn't exist"""
    response = requests.get(f"{BASE_URL}/usuarios/nonexistent_id")
    assert response.status_code == 404

# ========== MUSICAS CRUD TESTS ==========

def test_list_songs():
    """Test listing songs endpoint"""
    response = requests.get(f"{BASE_URL}/musicas")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)

def test_create_song():
    """Test creating a new song"""
    new_song = {
        "nome": "Test Song",
        "artista": "Test Artist",
        "duracao_segundos": 180
    }
    response = requests.post(f"{BASE_URL}/musicas", json=new_song)
    assert response.status_code == 200
    created_song = response.json()
    assert created_song["nome"] == new_song["nome"]
    assert created_song["artista"] == new_song["artista"]
    assert created_song["duracao_segundos"] == new_song["duracao_segundos"]
    assert "id" in created_song

def test_get_song():
    """Test getting a specific song"""
    # Use an existing song from the data
    songs_response = requests.get(f"{BASE_URL}/musicas")
    songs_data = songs_response.json()
    if songs_data["items"]:
        song_id = songs_data["items"][0]["id"]
        
        response = requests.get(f"{BASE_URL}/musicas/{song_id}")
        assert response.status_code == 200
        retrieved_song = response.json()
        assert retrieved_song["id"] == song_id
        assert "nome" in retrieved_song
        assert "artista" in retrieved_song

def test_update_song():
    """Test updating an existing song"""
    # Use an existing song from the data
    songs_response = requests.get(f"{BASE_URL}/musicas")
    songs_data = songs_response.json()
    if songs_data["items"]:
        song_id = songs_data["items"][0]["id"]
        
        # Update the song
        update_data = {
            "nome": "Updated Song Name",
            "artista": "Updated Artist"
        }
        response = requests.put(f"{BASE_URL}/musicas/{song_id}", json=update_data)
        assert response.status_code == 200
        updated_song = response.json()
        assert updated_song["id"] == song_id
        assert updated_song["nome"] == update_data["nome"]
        assert updated_song["artista"] == update_data["artista"]

def test_delete_song():
    """Test deleting a song"""
    # Create a new song for deletion test
    created_song = create_test_song("Delete Song Test", "Delete Artist", 120)
    assert created_song is not None
    song_id = created_song["id"]
    
    # Delete the song
    response = requests.delete(f"{BASE_URL}/musicas/{song_id}")
    assert response.status_code == 200
    delete_response = response.json()
    assert "message" in delete_response
    assert "removida com sucesso" in delete_response["message"]

def test_get_nonexistent_song():
    """Test getting a song that doesn't exist"""
    response = requests.get(f"{BASE_URL}/musicas/nonexistent_id")
    assert response.status_code == 404

# ========== PLAYLISTS CRUD TESTS ==========

def test_list_playlists():
    """Test listing playlists endpoint"""
    response = requests.get(f"{BASE_URL}/playlists")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)

def test_create_playlist():
    """Test creating a new playlist"""
    # First create a user
    user_response = requests.post(f"{BASE_URL}/usuarios", json={"nome": "Playlist Creator", "idade": 30})
    assert user_response.status_code == 200
    user_id = user_response.json()["id"]
    
    # Create a playlist without songs
    new_playlist = {
        "nome": "Test Playlist",
        "id_usuario": user_id
    }
    response = requests.post(f"{BASE_URL}/playlists", json=new_playlist)
    assert response.status_code == 200
    created_playlist = response.json()
    assert created_playlist["nome"] == new_playlist["nome"]
    assert created_playlist["id_usuario"] == user_id
    assert "id" in created_playlist
    assert isinstance(created_playlist["musicas"], list)

def test_get_playlist():
    """Test getting a specific playlist"""
    # Use an existing playlist from the data
    playlists_response = requests.get(f"{BASE_URL}/playlists")
    playlists_data = playlists_response.json()
    if playlists_data["items"]:
        playlist_id = playlists_data["items"][0]["id"]
        
        response = requests.get(f"{BASE_URL}/playlists/{playlist_id}")
        assert response.status_code == 200
        retrieved_playlist = response.json()
        assert retrieved_playlist["id"] == playlist_id
        assert "nome" in retrieved_playlist
        assert "id_usuario" in retrieved_playlist
        assert "musicas" in retrieved_playlist

def test_update_playlist():
    """Test updating an existing playlist"""
    # Create a playlist for testing  
    user = create_test_user("Playlist Update User", 30)
    assert user is not None
    
    new_playlist = {
        "nome": "Update Test Playlist",
        "id_usuario": user["id"]
    }
    response = requests.post(f"{BASE_URL}/playlists", json=new_playlist)
    assert response.status_code == 200
    created_playlist = response.json()
    playlist_id = created_playlist["id"]
    
    # Update the playlist
    update_data = {
        "nome": "Updated Playlist Name"
    }
    response = requests.put(f"{BASE_URL}/playlists/{playlist_id}", json=update_data)
    assert response.status_code == 200
    updated_playlist = response.json()
    assert updated_playlist["id"] == playlist_id
    assert updated_playlist["nome"] == update_data["nome"]

def test_delete_playlist():
    """Test deleting a playlist"""
    # Create a playlist for deletion test
    user = create_test_user("Playlist Delete User", 30)
    assert user is not None
    
    new_playlist = {
        "nome": "Delete Test Playlist",
        "id_usuario": user["id"]
    }
    response = requests.post(f"{BASE_URL}/playlists", json=new_playlist)
    assert response.status_code == 200
    created_playlist = response.json()
    playlist_id = created_playlist["id"]
    
    # Delete the playlist
    response = requests.delete(f"{BASE_URL}/playlists/{playlist_id}")
    assert response.status_code == 200
    delete_response = response.json()
    assert "message" in delete_response
    assert "removida com sucesso" in delete_response["message"]

def test_get_nonexistent_playlist():
    """Test getting a playlist that doesn't exist"""
    response = requests.get(f"{BASE_URL}/playlists/nonexistent_id")
    assert response.status_code == 404

# ========== RELACIONAMENTO TESTS ==========

def test_get_playlist_songs():
    """Test getting songs from a playlist"""
    # Use an existing playlist from the data
    playlists_response = requests.get(f"{BASE_URL}/playlists")
    playlists_data = playlists_response.json()
    if playlists_data["items"]:
        playlist_id = playlists_data["items"][0]["id"]
        
        response = requests.get(f"{BASE_URL}/playlists/{playlist_id}/musicas")
        assert response.status_code == 200
        songs = response.json()
        assert isinstance(songs, list)

def test_get_user_playlists():
    """Test getting playlists from a user"""
    # Use an existing user from the data
    users_response = requests.get(f"{BASE_URL}/usuarios")
    users_data = users_response.json()
    if users_data["items"]:
        user_id = users_data["items"][0]["id"]
        
        response = requests.get(f"{BASE_URL}/usuarios/{user_id}/playlists")
        assert response.status_code == 200
        playlists = response.json()
        assert isinstance(playlists, list)

# ========== VALIDATION TESTS ==========

def test_create_user_invalid_data():
    """Test creating a user with invalid data"""
    # Missing required field
    invalid_user = {
        "nome": "Test User"
        # missing 'idade'
    }
    response = requests.post(f"{BASE_URL}/usuarios", json=invalid_user)
    assert response.status_code == 422  # FastAPI validation error

def test_create_playlist_invalid_user():
    """Test creating a playlist with non-existent user"""
    invalid_playlist = {
        "nome": "Test Playlist",
        "id_usuario": "nonexistent_user_id"
    }
    response = requests.post(f"{BASE_URL}/playlists", json=invalid_playlist)
    assert response.status_code == 400  # Should return 400 for business logic error

if __name__ == "__main__":
    print("Starting comprehensive REST service tests...")
    print("Make sure the REST service is running on http://localhost:8000")
    print("Running tests in 5 seconds...")
    time.sleep(5)  # Give time to read the message
    
    # Run all tests
    pytest.main([__file__, "-v"]) 