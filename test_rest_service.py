import pytest
import requests
import time
from typing import Dict, List

# Base URL for the REST service
BASE_URL = "http://localhost:8000"

def test_service_is_running():
    """Test if the service is running and accessible"""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "Serviço de Streaming - REST API" in response.text

def test_list_users():
    """Test listing users endpoint"""
    response = requests.get(f"{BASE_URL}/usuarios")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)

def test_list_songs():
    """Test listing songs endpoint"""
    response = requests.get(f"{BASE_URL}/musicas")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)

def test_list_playlists():
    """Test listing playlists endpoint"""
    response = requests.get(f"{BASE_URL}/playlists")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)

def test_create_and_get_user():
    """Test creating a new user and retrieving it"""
    # Create a new user
    new_user = {
        "nome": "Test User",
        "idade": 25
    }
    response = requests.post(f"{BASE_URL}/usuarios", params=new_user)
    assert response.status_code == 200
    created_user = response.json()
    assert created_user["nome"] == new_user["nome"]
    assert created_user["idade"] == new_user["idade"]
    
    # Get the created user
    user_id = created_user["id"]
    response = requests.get(f"{BASE_URL}/usuarios/{user_id}")
    assert response.status_code == 200
    retrieved_user = response.json()
    assert retrieved_user["id"] == user_id
    assert retrieved_user["nome"] == new_user["nome"]

def test_create_and_get_playlist():
    """Test creating a playlist and retrieving its songs"""
    # First create a user
    user_response = requests.post(f"{BASE_URL}/usuarios", params={"nome": "Playlist Creator", "idade": 30})
    user_id = user_response.json()["id"]
    
    # Create a playlist
    new_playlist = {
        "nome": "Test Playlist",
        "idUsuario": user_id,
        "musicas": []  # Empty playlist for testing
    }
    response = requests.post(f"{BASE_URL}/playlists", params=new_playlist)
    assert response.status_code == 200
    created_playlist = response.json()
    assert created_playlist["nome"] == new_playlist["nome"]
    
    # Get the playlist's songs
    playlist_id = created_playlist["id"]
    response = requests.get(f"{BASE_URL}/playlists/{playlist_id}/musicas")
    assert response.status_code == 200
    songs = response.json()
    assert isinstance(songs, list)

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

if __name__ == "__main__":
    print("Starting REST service tests...")
    print("Make sure the REST service is running on http://localhost:8000")
    print("Running tests in 5 seconds...")
    time.sleep(5)  # Give time to read the message
    
    # Run all tests
    pytest.main([__file__, "-v"]) 