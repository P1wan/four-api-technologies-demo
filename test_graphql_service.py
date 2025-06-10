import pytest
import requests
import json
import time

# Base URL for the GraphQL service
BASE_URL = "http://localhost:8001/graphql"

def test_service_is_running():
    """Test if the GraphQL service is running and accessible"""
    response = requests.post(
        BASE_URL,
        json={
            "query": """
            query {
                estatisticas {
                    totalUsuarios
                    totalMusicas
                    totalPlaylists
                    usuariosComPlaylists
                    mediaMusicasPorPlaylist
                    tecnologia
                }
            }
            """
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "estatisticas" in data["data"]
    stats = data["data"]["estatisticas"]
    assert "totalUsuarios" in stats
    assert "totalMusicas" in stats
    assert "totalPlaylists" in stats
    assert "usuariosComPlaylists" in stats
    assert "mediaMusicasPorPlaylist" in stats
    assert "tecnologia" in stats

def test_list_users():
    """Test listing users"""
    response = requests.post(
        BASE_URL,
        json={
            "query": """
            query {
                usuarios {
                    id
                    nome
                    idade
                }
            }
            """
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "usuarios" in data["data"]
    users = data["data"]["usuarios"]
    assert isinstance(users, list)
    assert len(users) > 0
    assert all("id" in user and "nome" in user and "idade" in user for user in users)

def test_list_songs():
    """Test listing songs"""
    response = requests.post(
        BASE_URL,
        json={
            "query": """
            query {
                musicas {
                    id
                    nome
                    artista
                    duracaoSegundos
                }
            }
            """
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "musicas" in data["data"]
    songs = data["data"]["musicas"]
    assert isinstance(songs, list)
    assert len(songs) > 0
    assert all("id" in song and "nome" in song and "artista" in song and "duracaoSegundos" in song for song in songs)

def test_list_playlists():
    """Test listing playlists for a user"""
    # First get a user ID
    response = requests.post(
        BASE_URL,
        json={
            "query": """
            query {
                usuarios {
                    id
                }
            }
            """
        }
    )
    assert response.status_code == 200
    data = response.json()
    user_id = data["data"]["usuarios"][0]["id"]

    # Then get their playlists
    response = requests.post(
        BASE_URL,
        json={
            "query": """
            query($idUsuario: String!) {
                playlistsUsuario(idUsuario: $idUsuario) {
                    id
                    nome
                    idUsuario
                    musicas
                }
            }
            """,
            "variables": {
                "idUsuario": user_id
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "playlistsUsuario" in data["data"]
    playlists = data["data"]["playlistsUsuario"]
    assert isinstance(playlists, list)
    assert all("id" in p and "nome" in p and "idUsuario" in p and "musicas" in p for p in playlists)

def test_create_and_get_user():
    """Test creating a new user and retrieving it"""
    # Create a new user
    response = requests.post(
        BASE_URL,
        json={
            "query": """
            mutation($input: UsuarioInput!) {
                criarUsuario(input: $input) {
                    id
                    nome
                    idade
                }
            }
            """,
            "variables": {
                "input": {
                    "nome": "Test User",
                    "idade": 25
                }
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "criarUsuario" in data["data"]
    created_user = data["data"]["criarUsuario"]
    assert created_user["nome"] == "Test User"
    assert created_user["idade"] == 25

    # Get the created user
    response = requests.post(
        BASE_URL,
        json={
            "query": """
            query($id: String!) {
                usuario(id: $id) {
                    id
                    nome
                    idade
                }
            }
            """,
            "variables": {
                "id": created_user["id"]
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "usuario" in data["data"]
    retrieved_user = data["data"]["usuario"]
    assert retrieved_user["id"] == created_user["id"]
    assert retrieved_user["nome"] == created_user["nome"]
    assert retrieved_user["idade"] == created_user["idade"]

def test_create_and_get_playlist():
    """Test creating a playlist and retrieving its songs"""
    # First create a user
    response = requests.post(
        BASE_URL,
        json={
            "query": """
            mutation($input: UsuarioInput!) {
                criarUsuario(input: $input) {
                    id
                }
            }
            """,
            "variables": {
                "input": {
                    "nome": "Playlist Creator",
                    "idade": 30
                }
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    user_id = data["data"]["criarUsuario"]["id"]

    # Get some songs
    response = requests.post(
        BASE_URL,
        json={
            "query": """
            query {
                musicas {
                    id
                }
            }
            """
        }
    )
    assert response.status_code == 200
    data = response.json()
    song_ids = [song["id"] for song in data["data"]["musicas"][:3]]

    # Create a playlist
    response = requests.post(
        BASE_URL,
        json={
            "query": """
            mutation($input: PlaylistInput!) {
                criarPlaylist(input: $input) {
                    id
                    nome
                    idUsuario
                    musicas
                }
            }
            """,
            "variables": {
                "input": {
                    "nome": "My Test Playlist",
                    "idUsuario": user_id,
                    "musicas": song_ids
                }
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "criarPlaylist" in data["data"]
    created_playlist = data["data"]["criarPlaylist"]
    assert created_playlist["nome"] == "My Test Playlist"
    assert created_playlist["idUsuario"] == user_id
    assert set(created_playlist["musicas"]) == set(song_ids)

    # Get the playlist's songs
    response = requests.post(
        BASE_URL,
        json={
            "query": """
            query($idPlaylist: String!) {
                musicasPlaylist(idPlaylist: $idPlaylist) {
                    id
                    nome
                    artista
                    duracaoSegundos
                }
            }
            """,
            "variables": {
                "idPlaylist": created_playlist["id"]
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "musicasPlaylist" in data["data"]
    songs = data["data"]["musicasPlaylist"]
    assert isinstance(songs, list)
    assert len(songs) == len(song_ids)
    assert all("id" in song and "nome" in song and "artista" in song and "duracaoSegundos" in song for song in songs)

def test_service_stats():
    """Test the stats endpoint"""
    response = requests.post(
        BASE_URL,
        json={
            "query": """
            query {
                estatisticas {
                    totalUsuarios
                    totalMusicas
                    totalPlaylists
                    usuariosComPlaylists
                    mediaMusicasPorPlaylist
                    tecnologia
                }
            }
            """
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "estatisticas" in data["data"]
    stats = data["data"]["estatisticas"]
    assert isinstance(stats["totalUsuarios"], int)
    assert isinstance(stats["totalMusicas"], int)
    assert isinstance(stats["totalPlaylists"], int)
    assert isinstance(stats["usuariosComPlaylists"], int)
    assert isinstance(stats["mediaMusicasPorPlaylist"], float)
    assert isinstance(stats["tecnologia"], str)

if __name__ == "__main__":
    print("Starting GraphQL service tests...")
    print("Make sure the GraphQL service is running on http://localhost:8001")
    print("Running tests in 5 seconds...")
    time.sleep(5)
    pytest.main([__file__]) 