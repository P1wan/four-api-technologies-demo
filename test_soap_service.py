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
    transport = Transport(timeout=10)
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

def test_create_and_get_user():
    """Test creating a new user and retrieving it"""
    client = get_soap_client()
    
    # Create a new user
    created_user = client.service.criar_usuario(
        id="test123",
        nome="Test User",
        idade=25
    )
    assert created_user is not None
    assert created_user.nome == "Test User"
    assert created_user.idade == 25
    
    # Get the created user
    retrieved_user = client.service.GetUser(id=created_user.id)
    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.nome == "Test User"

def test_create_and_get_playlist():
    """Test creating a playlist and retrieving its songs"""
    client = get_soap_client()
    
    # First create a user
    user = client.service.criar_usuario(
        id="creator123",
        nome="Playlist Creator",
        idade=30
    )
    
    # Create a playlist
    created_playlist = client.service.criar_playlist(
        id="playlist123",
        nome="Test Playlist",
        id_usuario=user.id,
        musicas=[]  # Empty playlist for testing
    )
    assert created_playlist is not None
    assert created_playlist.nome == "Test Playlist"
    
    # Get the playlist
    retrieved_playlist = client.service.GetPlaylist(id=created_playlist.id)
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

if __name__ == "__main__":
    print("Starting SOAP service tests...")
    print("Make sure the SOAP service is running on http://localhost:8004")
    print("Running tests in 5 seconds...")
    time.sleep(5)  # Give time to read the message
    
    # Run all tests
    pytest.main([__file__, "-v"]) 