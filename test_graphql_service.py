"""
Test suite for GraphQL service - Expanded CRUD Tests
"""

import requests
import json
import time
import pytest

# Base URL for the GraphQL service
BASE_URL = "http://localhost:8001/graphql"

# ===== HELPER FUNCTIONS =====

def make_graphql_request(query, variables=None):
    """Make a GraphQL request and return the response"""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    response = requests.post(BASE_URL, json=payload, timeout=10)
    return response

def assert_graphql_response(response, expected_data_key=None, allow_null=False):
    """Assert basic GraphQL response structure"""
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    if expected_data_key:
        assert expected_data_key in data["data"]
        if not allow_null:
            assert data["data"][expected_data_key] is not None
    return data

def create_test_user():
    """Helper function to create a test user and return its ID"""
    response = make_graphql_request("""
        mutation($input: UsuarioInput!) {
            criar_usuario(input: $input) {
                id
                nome
                idade
            }
        }
    """, {
        "input": {
            "nome": "Test User GraphQL",
            "idade": 28
        }
    })
    data = assert_graphql_response(response, "criar_usuario")
    created_user = data["data"]["criar_usuario"]
    return created_user["id"]

def create_test_music():
    """Helper function to create a test music and return its ID"""
    response = make_graphql_request("""
        mutation($input: MusicaInput!) {
            criar_musica(input: $input) {
                id
                nome
                artista
                duracao_segundos
            }
        }
    """, {
        "input": {
            "nome": "Test Song GraphQL",
            "artista": "Test Artist",
            "duracao_segundos": 240
        }
    })
    data = assert_graphql_response(response, "criar_musica")
    created_music = data["data"]["criar_musica"]
    return created_music["id"]

def create_test_playlist():
    """Helper function to create a test playlist and return its ID"""
    user_id = create_test_user()
    music_id = create_test_music()
    
    response = make_graphql_request("""
        mutation($input: PlaylistInput!) {
            criar_playlist(input: $input) {
                id
                nome
                id_usuario
                musicas
            }
        }
    """, {
        "input": {
            "nome": "Test Playlist GraphQL",
            "id_usuario": user_id,
            "musicas": [music_id]
        }
    })
    data = assert_graphql_response(response, "criar_playlist")
    created_playlist = data["data"]["criar_playlist"]
    return created_playlist["id"]

# ===== BASIC CONNECTIVITY TESTS =====

def test_service_is_running():
    """Test if the GraphQL service is accessible"""
    try:
        response = make_graphql_request("""
            query {
                __schema {
                    types {
                        name
                    }
                }
            }
        """)
        data = assert_graphql_response(response)
        assert "__schema" in data["data"]
        print("✅ GraphQL service is running and accessible")
    except requests.exceptions.RequestException as e:
        pytest.fail(f"GraphQL service is not accessible: {e}")

# ===== USER TESTS =====

def test_list_users():
    """Test listing all users"""
    response = make_graphql_request("""
        query {
            usuarios {
                id
                nome
                idade
            }
        }
    """)
    data = assert_graphql_response(response, "usuarios")
    users = data["data"]["usuarios"]
    assert isinstance(users, list)
    assert len(users) > 0
    assert all("id" in u and "nome" in u and "idade" in u for u in users)
    print(f"✅ Listed {len(users)} users")

def test_create_user():
    """Test creating a new user"""
    response = make_graphql_request("""
        mutation($input: UsuarioInput!) {
            criar_usuario(input: $input) {
                id
                nome
                idade
            }
        }
    """, {
        "input": {
            "nome": "Test User GraphQL",
            "idade": 28
        }
    })
    data = assert_graphql_response(response, "criar_usuario")
    created_user = data["data"]["criar_usuario"]
    assert created_user["nome"] == "Test User GraphQL"
    assert created_user["idade"] == 28
    assert "id" in created_user
    print(f"✅ Created user: {created_user['id']}")

def test_get_user():
    """Test getting a single user by ID"""
    # First create a user
    user_id = create_test_user()
    
    # Then get it
    response = make_graphql_request("""
        query($id: String!) {
            usuario(id: $id) {
                id
                nome
                idade
            }
        }
    """, {"id": user_id})
    data = assert_graphql_response(response, "usuario")
    user = data["data"]["usuario"]
    assert user["id"] == user_id
    assert user["nome"] == "Test User GraphQL"
    assert user["idade"] == 28
    print(f"✅ Retrieved user: {user_id}")

def test_update_user():
    """Test updating a user"""
    # First create a user
    user_id = create_test_user()
    
    # Then update it
    response = make_graphql_request("""
        mutation($id: String!, $input: UsuarioInput!) {
            atualizar_usuario(id: $id, input: $input) {
                id
                nome
                idade
            }
        }
    """, {
        "id": user_id,
        "input": {
            "nome": "Updated Test User",
            "idade": 35
        }
    })
    data = assert_graphql_response(response, "atualizar_usuario")
    updated_user = data["data"]["atualizar_usuario"]
    assert updated_user["id"] == user_id
    assert updated_user["nome"] == "Updated Test User"
    assert updated_user["idade"] == 35
    print(f"✅ Updated user: {user_id}")

def test_delete_user():
    """Test deleting a user"""
    # First create a user
    user_id = create_test_user()
    
    # Then delete it
    response = make_graphql_request("""
        mutation($id: String!) {
            deletar_usuario(id: $id)
        }
    """, {"id": user_id})
    data = assert_graphql_response(response, "deletar_usuario")
    assert data["data"]["deletar_usuario"] == True
    print(f"✅ Deleted user: {user_id}")

# ===== MUSIC TESTS =====

def test_list_songs():
    """Test listing all songs"""
    response = make_graphql_request("""
        query {
            musicas {
                id
                nome
                artista
                duracao_segundos
            }
        }
    """)
    data = assert_graphql_response(response, "musicas")
    songs = data["data"]["musicas"]
    assert isinstance(songs, list)
    assert len(songs) > 0
    assert all("id" in s and "nome" in s and "artista" in s and "duracao_segundos" in s for s in songs)
    print(f"✅ Listed {len(songs)} songs")

def test_create_music():
    """Test creating a new music"""
    response = make_graphql_request("""
        mutation($input: MusicaInput!) {
            criar_musica(input: $input) {
                id
                nome
                artista
                duracao_segundos
            }
        }
    """, {
        "input": {
            "nome": "Test Song GraphQL",
            "artista": "Test Artist",
            "duracao_segundos": 240
        }
    })
    data = assert_graphql_response(response, "criar_musica")
    created_music = data["data"]["criar_musica"]
    assert created_music["nome"] == "Test Song GraphQL"
    assert created_music["artista"] == "Test Artist"
    assert created_music["duracao_segundos"] == 240
    assert "id" in created_music
    print(f"✅ Created music: {created_music['id']}")

def test_update_music():
    """Test updating a music"""
    # First create a music
    music_id = create_test_music()
    
    # Then update it
    response = make_graphql_request("""
        mutation($id: String!, $input: MusicaInput!) {
            atualizar_musica(id: $id, input: $input) {
                id
                nome
                artista
                duracao_segundos
            }
        }
    """, {
        "id": music_id,
        "input": {
            "nome": "Updated Test Song",
            "artista": "Updated Artist",
            "duracao_segundos": 300
        }
    })
    data = assert_graphql_response(response, "atualizar_musica")
    updated_music = data["data"]["atualizar_musica"]
    assert updated_music["id"] == music_id
    assert updated_music["nome"] == "Updated Test Song"
    assert updated_music["artista"] == "Updated Artist"
    assert updated_music["duracao_segundos"] == 300
    print(f"✅ Updated music: {music_id}")

def test_delete_music():
    """Test deleting a music"""
    # First create a music
    music_id = create_test_music()
    
    # Then delete it
    response = make_graphql_request("""
        mutation($id: String!) {
            deletar_musica(id: $id)
        }
    """, {"id": music_id})
    data = assert_graphql_response(response, "deletar_musica")
    assert data["data"]["deletar_musica"] == True
    print(f"✅ Deleted music: {music_id}")

# ===== PLAYLIST TESTS =====

def test_list_playlists():
    """Test listing playlists for a user"""
    # First, get a user ID
    response = make_graphql_request("""
        query {
            usuarios {
                id
            }
        }
    """)
    data = assert_graphql_response(response, "usuarios")
    users = data["data"]["usuarios"]
    assert len(users) > 0
    user_id = users[0]["id"]

    # Now test playlists for this user
    response = make_graphql_request("""
        query($userId: String!) {
            playlists_usuario(id_usuario: $userId) {
                id
                nome
                id_usuario
                musicas
            }
        }
    """, {"userId": user_id})
    data = assert_graphql_response(response, "playlists_usuario")
    playlists = data["data"]["playlists_usuario"]
    assert isinstance(playlists, list)
    print(f"✅ Listed {len(playlists)} playlists for user {user_id}")

def test_create_playlist():
    """Test creating a new playlist"""
    # First create a user and get some music IDs
    user_id = create_test_user()
    music_id = create_test_music()
    
    response = make_graphql_request("""
        mutation($input: PlaylistInput!) {
            criar_playlist(input: $input) {
                id
                nome
                id_usuario
                musicas
            }
        }
    """, {
        "input": {
            "nome": "Test Playlist GraphQL",
            "id_usuario": user_id,
            "musicas": [music_id]
        }
    })
    data = assert_graphql_response(response, "criar_playlist")
    created_playlist = data["data"]["criar_playlist"]
    assert created_playlist["nome"] == "Test Playlist GraphQL"
    assert created_playlist["id_usuario"] == user_id
    assert music_id in created_playlist["musicas"]
    assert "id" in created_playlist
    print(f"✅ Created playlist: {created_playlist['id']}")

def test_create_and_get_playlist():
    """Test creating a playlist and retrieving its songs"""
    # Create dependencies
    user_id = create_test_user()
    music_id1 = create_test_music()
    music_id2 = create_test_music()
    
    # Create playlist
    response = make_graphql_request("""
        mutation($input: PlaylistInput!) {
            criar_playlist(input: $input) {
                id
                nome
                id_usuario
                musicas
            }
        }
    """, {
        "input": {
            "nome": "Test Multi-Song Playlist",
            "id_usuario": user_id,
            "musicas": [music_id1, music_id2]
        }
    })
    data = assert_graphql_response(response, "criar_playlist")
    playlist_id = data["data"]["criar_playlist"]["id"]
    
    # Get playlist songs
    response = make_graphql_request("""
        query($playlistId: String!) {
            musicas_playlist(id_playlist: $playlistId) {
                id
                nome
                artista
                duracao_segundos
            }
        }
    """, {"playlistId": playlist_id})
    data = assert_graphql_response(response, "musicas_playlist")
    songs = data["data"]["musicas_playlist"]
    assert len(songs) == 2
    song_ids = [s["id"] for s in songs]
    assert music_id1 in song_ids
    assert music_id2 in song_ids
    print(f"✅ Retrieved {len(songs)} songs from playlist: {playlist_id}")

def test_update_playlist():
    """Test updating a playlist"""
    # Create dependencies
    user_id = create_test_user()
    music_id1 = create_test_music()
    music_id2 = create_test_music()
    playlist_id = create_test_playlist()
    
    # Update playlist
    response = make_graphql_request("""
        mutation($id: String!, $input: PlaylistInput!) {
            atualizar_playlist(id: $id, input: $input) {
                id
                nome
                id_usuario
                musicas
            }
        }
    """, {
        "id": playlist_id,
        "input": {
            "nome": "Updated Test Playlist",
            "id_usuario": user_id,
            "musicas": [music_id1, music_id2]
        }
    })
    data = assert_graphql_response(response, "atualizar_playlist")
    updated_playlist = data["data"]["atualizar_playlist"]
    assert updated_playlist["id"] == playlist_id
    assert updated_playlist["nome"] == "Updated Test Playlist"
    assert len(updated_playlist["musicas"]) == 2
    print(f"✅ Updated playlist: {playlist_id}")

def test_delete_playlist():
    """Test deleting a playlist"""
    # First create a playlist
    playlist_id = create_test_playlist()
    
    # Then delete it
    response = make_graphql_request("""
        mutation($id: String!) {
            deletar_playlist(id: $id)
        }
    """, {"id": playlist_id})
    data = assert_graphql_response(response, "deletar_playlist")
    assert data["data"]["deletar_playlist"] == True
    print(f"✅ Deleted playlist: {playlist_id}")

# ===== ADVANCED QUERY TESTS =====

def test_playlist_complete():
    """Test getting complete playlist data"""
    # Create dependencies
    user_id = create_test_user()
    music_id = create_test_music()
    
    # Create playlist
    response = make_graphql_request("""
        mutation($input: PlaylistInput!) {
            criar_playlist(input: $input) {
                id
            }
        }
    """, {
        "input": {
            "nome": "Complete Test Playlist",
            "id_usuario": user_id,
            "musicas": [music_id]
        }
    })
    data = assert_graphql_response(response, "criar_playlist")
    playlist_id = data["data"]["criar_playlist"]["id"]
    
    # Get complete playlist
    response = make_graphql_request("""
        query($playlistId: String!) {
            playlist_completa(id_playlist: $playlistId) {
                id
                nome
                usuario {
                    id
                    nome
                    idade
                }
                musicas {
                    id
                    nome
                    artista
                    duracao_segundos
                }
            }
        }
    """, {"playlistId": playlist_id})
    data = assert_graphql_response(response, "playlist_completa")
    complete_playlist = data["data"]["playlist_completa"]
    assert complete_playlist["id"] == playlist_id
    assert complete_playlist["nome"] == "Complete Test Playlist"
    assert complete_playlist["usuario"]["id"] == user_id
    assert len(complete_playlist["musicas"]) == 1
    assert complete_playlist["musicas"][0]["id"] == music_id
    print(f"✅ Retrieved complete playlist data: {playlist_id}")

def test_playlists_with_music():
    """Test finding playlists that contain a specific music"""
    # Create dependencies
    user_id = create_test_user()
    music_id = create_test_music()
    
    # Create playlist with the music
    response = make_graphql_request("""
        mutation($input: PlaylistInput!) {
            criar_playlist(input: $input) {
                id
            }
        }
    """, {
        "input": {
            "nome": "Playlist With Specific Music",
            "id_usuario": user_id,
            "musicas": [music_id]
        }
    })
    playlist_id = response.json()["data"]["criar_playlist"]["id"]
    
    # Find playlists with this music
    response = make_graphql_request("""
        query($musicId: String!) {
            playlists_com_musica(id_musica: $musicId) {
                id
                nome
                id_usuario
                musicas
            }
        }
    """, {"musicId": music_id})
    data = assert_graphql_response(response, "playlists_com_musica")
    playlists = data["data"]["playlists_com_musica"]
    assert len(playlists) >= 1
    found_playlist = next((p for p in playlists if p["id"] == playlist_id), None)
    assert found_playlist is not None
    assert music_id in found_playlist["musicas"]
    print(f"✅ Found {len(playlists)} playlists containing music: {music_id}")

# ===== STATISTICS TESTS =====

def test_service_stats():
    """Test getting service statistics"""
    response = make_graphql_request("""
        query {
            estatisticas {
                total_usuarios
                total_musicas
                total_playlists
                usuarios_com_playlists
                media_musicas_por_playlist
                tecnologia
            }
        }
    """)
    data = assert_graphql_response(response, "estatisticas")
    stats = data["data"]["estatisticas"]
    assert isinstance(stats["total_usuarios"], int)
    assert isinstance(stats["total_musicas"], int)
    assert isinstance(stats["total_playlists"], int)
    assert isinstance(stats["usuarios_com_playlists"], int)
    assert isinstance(stats["media_musicas_por_playlist"], float)
    assert stats["tecnologia"] == "GraphQL"
    assert stats["total_usuarios"] >= 0
    assert stats["total_musicas"] >= 0
    assert stats["total_playlists"] >= 0
    print(f"✅ Service stats: {stats['total_usuarios']} users, {stats['total_musicas']} songs, {stats['total_playlists']} playlists")

# ===== ERROR HANDLING TESTS =====

def test_user_validation_errors():
    """Test user validation errors"""
    # Test empty name
    response = make_graphql_request("""
        mutation($input: UsuarioInput!) {
            criar_usuario(input: $input) {
                id
                nome
                idade
            }
        }
    """, {
        "input": {
            "nome": "",
            "idade": 25
        }
    })
    data = response.json()
    assert "errors" in data
    print("✅ Empty name validation working")
    
    # Test invalid age
    response = make_graphql_request("""
        mutation($input: UsuarioInput!) {
            criar_usuario(input: $input) {
                id
                nome
                idade
            }
        }
    """, {
        "input": {
            "nome": "Valid Name",
            "idade": -5
        }
    })
    data = response.json()
    assert "errors" in data
    print("✅ Invalid age validation working")

def test_music_validation_errors():
    """Test music validation errors"""
    # Test invalid duration
    response = make_graphql_request("""
        mutation($input: MusicaInput!) {
            criar_musica(input: $input) {
                id
                nome
                artista
                duracao_segundos
            }
        }
    """, {
        "input": {
            "nome": "Test Song",
            "artista": "Test Artist",
            "duracao_segundos": -10
        }
    })
    data = response.json()
    assert "errors" in data
    print("✅ Invalid duration validation working")

def test_nonexistent_resource_errors():
    """Test errors when accessing non-existent resources"""
    # Test non-existent user
    response = make_graphql_request("""
        query {
            usuario(id: "nonexistent-user-id") {
                id
                nome
                idade
            }
        }
    """)
    data = assert_graphql_response(response, "usuario", allow_null=True)
    assert data["data"]["usuario"] is None
    print("✅ Non-existent user handling working")
    
    # Test non-existent playlist
    response = make_graphql_request("""
        query {
            musicas_playlist(id_playlist: "nonexistent-playlist-id") {
                id
                nome
                artista
                duracao_segundos
            }
        }
    """)
    data = assert_graphql_response(response, "musicas_playlist")
    assert data["data"]["musicas_playlist"] == []
    print("✅ Non-existent playlist handling working")

if __name__ == "__main__":
    print("Starting GraphQL service tests...")
    print("Make sure the GraphQL service is running on http://localhost:8001")
    print("Running tests in 5 seconds...")
    time.sleep(5)
    pytest.main([__file__]) 