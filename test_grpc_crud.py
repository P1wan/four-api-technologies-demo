#!/usr/bin/env python3
"""
Teste abrangente das operações CRUD implementadas no gRPC
"""

import grpc
import streaming_pb2
import streaming_pb2_grpc
import sys
import time

def test_grpc_crud_operations():
    """Testa todas as operações CRUD implementadas"""
    
    print("🧪 Iniciando testes das operações CRUD gRPC...")
    
    try:
        # Conectar ao servidor gRPC
        channel = grpc.insecure_channel('localhost:50051')
        stub = streaming_pb2_grpc.StreamingServiceStub(channel)
        
        # Testar se o servidor está rodando
        try:
            request = streaming_pb2.google_dot_protobuf_dot_empty__pb2.Empty()
            stub.ListarUsuarios(request)
            print("✅ Conexão com servidor gRPC estabelecida")
        except grpc.RpcError as e:
            print(f"❌ Erro ao conectar com servidor gRPC: {e}")
            print("💡 Certifique-se de que o servidor gRPC está rodando na porta 50051")
            return False
        
        # === TESTES DE USUÁRIOS ===
        print("\n📁 Testando operações de Usuários:")
        
        # 1. Criar usuário
        print("  🔸 Testando criação de usuário...")
        try:
            criar_request = streaming_pb2.CriarUsuarioRequest(
                nome="João Teste",
                idade=30
            )
            novo_usuario = stub.CriarUsuario(criar_request)
            print(f"    ✅ Usuário criado: {novo_usuario.nome} (ID: {novo_usuario.id_usuario})")
        except grpc.RpcError as e:
            print(f"    ❌ Erro ao criar usuário: {e.details()}")
            return False
        
        # 2. Obter usuário
        print("  🔸 Testando obtenção de usuário...")
        try:
            obter_request = streaming_pb2.IdRequest(id="user_1")
            usuario = stub.ObterUsuario(obter_request)
            print(f"    ✅ Usuário obtido: {usuario.nome}")
        except grpc.RpcError as e:
            print(f"    ❌ Erro ao obter usuário: {e.details()}")
        
        # 3. Atualizar usuário
        print("  🔸 Testando atualização de usuário...")
        try:
            atualizar_request = streaming_pb2.AtualizarUsuarioRequest(
                id_usuario="user_1",
                nome="João Silva Atualizado",
                idade=31
            )
            usuario_atualizado = stub.AtualizarUsuario(atualizar_request)
            print(f"    ✅ Usuário atualizado: {usuario_atualizado.nome}")
        except grpc.RpcError as e:
            print(f"    ❌ Erro ao atualizar usuário: {e.details()}")
        
        # 4. Deletar usuário
        print("  🔸 Testando deleção de usuário...")
        try:
            deletar_request = streaming_pb2.IdRequest(id="user_1")
            resultado = stub.DeletarUsuario(deletar_request)
            print(f"    ✅ Usuário deletado: {resultado.success} - {resultado.message}")
        except grpc.RpcError as e:
            print(f"    ❌ Erro ao deletar usuário: {e.details()}")
        
        # === TESTES DE MÚSICAS ===
        print("\n🎵 Testando operações de Músicas:")
        
        # 1. Criar música
        print("  🔸 Testando criação de música...")
        try:
            criar_musica_request = streaming_pb2.CriarMusicaRequest(
                nome="Música Teste",
                artista="Artista Teste",
                duracao_segundos=180
            )
            nova_musica = stub.CriarMusica(criar_musica_request)
            print(f"    ✅ Música criada: {nova_musica.nome} - {nova_musica.artista}")
        except grpc.RpcError as e:
            print(f"    ❌ Erro ao criar música: {e.details()}")
        
        # 2. Obter música
        print("  🔸 Testando obtenção de música...")
        try:
            obter_musica_request = streaming_pb2.IdRequest(id="musica_1")
            musica = stub.ObterMusica(obter_musica_request)
            print(f"    ✅ Música obtida: {musica.nome}")
        except grpc.RpcError as e:
            print(f"    ❌ Erro ao obter música: {e.details()}")
        
        # 3. Atualizar música
        print("  🔸 Testando atualização de música...")
        try:
            atualizar_musica_request = streaming_pb2.AtualizarMusicaRequest(
                id_musica="musica_1",
                nome="Música Atualizada",
                artista="Artista Atualizado",
                duracao_segundos=200
            )
            musica_atualizada = stub.AtualizarMusica(atualizar_musica_request)
            print(f"    ✅ Música atualizada: {musica_atualizada.nome}")
        except grpc.RpcError as e:
            print(f"    ❌ Erro ao atualizar música: {e.details()}")
        
        # 4. Deletar música
        print("  🔸 Testando deleção de música...")
        try:
            deletar_musica_request = streaming_pb2.IdRequest(id="musica_1")
            resultado = stub.DeletarMusica(deletar_musica_request)
            print(f"    ✅ Música deletada: {resultado.success} - {resultado.message}")
        except grpc.RpcError as e:
            print(f"    ❌ Erro ao deletar música: {e.details()}")
        
        # === TESTES DE PLAYLISTS ===
        print("\n📋 Testando operações de Playlists:")
        
        # 1. Criar playlist
        print("  🔸 Testando criação de playlist...")
        try:
            criar_playlist_request = streaming_pb2.CriarPlaylistRequest(
                nome="Playlist Teste",
                id_usuario="user_1",
                musicas=["musica_1", "musica_2"]
            )
            nova_playlist = stub.CriarPlaylist(criar_playlist_request)
            print(f"    ✅ Playlist criada: {nova_playlist.nome}")
        except grpc.RpcError as e:
            print(f"    ❌ Erro ao criar playlist: {e.details()}")
        
        # 2. Obter playlist
        print("  🔸 Testando obtenção de playlist...")
        try:
            obter_playlist_request = streaming_pb2.IdRequest(id="playlist_1")
            playlist = stub.ObterPlaylist(obter_playlist_request)
            print(f"    ✅ Playlist obtida: {playlist.nome}")
        except grpc.RpcError as e:
            print(f"    ❌ Erro ao obter playlist: {e.details()}")
        
        # 3. Atualizar playlist
        print("  🔸 Testando atualização de playlist...")
        try:
            atualizar_playlist_request = streaming_pb2.AtualizarPlaylistRequest(
                id_playlist="playlist_1",
                nome="Playlist Atualizada",
                musicas=["musica_1", "musica_2", "musica_3"]
            )
            playlist_atualizada = stub.AtualizarPlaylist(atualizar_playlist_request)
            print(f"    ✅ Playlist atualizada: {playlist_atualizada.nome}")
        except grpc.RpcError as e:
            print(f"    ❌ Erro ao atualizar playlist: {e.details()}")
        
        # 4. Deletar playlist
        print("  🔸 Testando deleção de playlist...")
        try:
            deletar_playlist_request = streaming_pb2.IdRequest(id="playlist_1")
            resultado = stub.DeletarPlaylist(deletar_playlist_request)
            print(f"    ✅ Playlist deletada: {resultado.success} - {resultado.message}")
        except grpc.RpcError as e:
            print(f"    ❌ Erro ao deletar playlist: {e.details()}")
        
        print("\n✅ Todos os testes das operações CRUD foram executados!")
        print("📝 Nota: Este é um teste de demonstração - os dados não são persistidos.")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro geral durante os testes: {e}")
        return False
    
    finally:
        try:
            channel.close()
        except:
            pass

def test_validation_errors():
    """Testa validações de erro"""
    
    print("\n🔍 Testando validações de erro...")
    
    try:
        channel = grpc.insecure_channel('localhost:50051')
        stub = streaming_pb2_grpc.StreamingServiceStub(channel)
        
        # Teste 1: Criar usuário com nome vazio
        print("  🔸 Testando criação de usuário com nome vazio...")
        try:
            criar_request = streaming_pb2.CriarUsuarioRequest(
                nome="",  # Nome vazio
                idade=25
            )
            stub.CriarUsuario(criar_request)
            print("    ❌ Deveria ter falhado com nome vazio")
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                print(f"    ✅ Validação funcionou: {e.details()}")
            else:
                print(f"    ⚠️  Código de erro inesperado: {e.code()}")
        
        # Teste 2: Criar usuário com idade inválida
        print("  🔸 Testando criação de usuário com idade inválida...")
        try:
            criar_request = streaming_pb2.CriarUsuarioRequest(
                nome="João",
                idade=0  # Idade inválida
            )
            stub.CriarUsuario(criar_request)
            print("    ❌ Deveria ter falhado com idade inválida")
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                print(f"    ✅ Validação funcionou: {e.details()}")
            else:
                print(f"    ⚠️  Código de erro inesperado: {e.code()}")
        
        # Teste 3: Buscar usuário inexistente
        print("  🔸 Testando busca de usuário inexistente...")
        try:
            obter_request = streaming_pb2.IdRequest(id="usuario_inexistente")
            stub.ObterUsuario(obter_request)
            print("    ❌ Deveria ter falhado para usuário inexistente")
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                print(f"    ✅ Validação funcionou: {e.details()}")
            else:
                print(f"    ⚠️  Código de erro inesperado: {e.code()}")
        
        print("✅ Testes de validação concluídos!")
        
    except Exception as e:
        print(f"❌ Erro durante testes de validação: {e}")
    
    finally:
        try:
            channel.close()
        except:
            pass
    server_thread.start()
    
    # Aguardar servidor iniciar
    time.sleep(2)
    
    # Conectar ao servidor
    try:
        channel = grpc.insecure_channel('localhost:50051')
        stub = streaming_pb2_grpc.StreamingServiceStub(channel)
        
        print("🧪 Testando operações CRUD do gRPC...")
        
        # Teste 1: Listar usuários
        print("\n1. Testando ListarTodosUsuarios...")
        response = stub.ListarTodosUsuarios(streaming_pb2.Empty())
        print(f"   ✅ Encontrados {len(response.usuarios)} usuários")
        
        # Teste 2: Obter usuário específico
        if response.usuarios:
            primeiro_usuario = response.usuarios[0]
            print(f"\n2. Testando ObterUsuario para {primeiro_usuario.id}...")
            user_request = streaming_pb2.UsuarioRequest(id_usuario=primeiro_usuario.id)
            user_response = stub.ObterUsuario(user_request)
            print(f"   ✅ Usuário obtido: {user_response.nome}, {user_response.idade} anos")
        
        # Teste 3: Criar usuário
        print(f"\n3. Testando CriarUsuario...")
        create_request = streaming_pb2.CriarUsuarioRequest(
            nome="Teste Usuario",
            idade=25
        )
        created_user = stub.CriarUsuario(create_request)
        print(f"   ✅ Usuário criado: {created_user.nome} (ID: {created_user.id})")
        
        # Teste 4: Atualizar usuário
        print(f"\n4. Testando AtualizarUsuario...")
        update_request = streaming_pb2.AtualizarUsuarioRequest(
            id_usuario=created_user.id,
            nome="Teste Usuario Atualizado",
            idade=26
        )
        updated_user = stub.AtualizarUsuario(update_request)
        print(f"   ✅ Usuário atualizado: {updated_user.nome}, {updated_user.idade} anos")
        
        # Teste 5: Deletar usuário
        print(f"\n5. Testando DeletarUsuario...")
        delete_request = streaming_pb2.UsuarioRequest(id_usuario=created_user.id)
        delete_response = stub.DeletarUsuario(delete_request)
        print(f"   ✅ Usuário deletado: {delete_response.success} - {delete_response.message}")
        
        # Teste 6: Listar músicas
        print(f"\n6. Testando ListarTodasMusicas...")
        music_response = stub.ListarTodasMusicas(streaming_pb2.Empty())
        print(f"   ✅ Encontradas {len(music_response.musicas)} músicas")
        
        # Teste 7: Obter estatísticas
        print(f"\n7. Testando ObterEstatisticas...")
        stats = stub.ObterEstatisticas(streaming_pb2.Empty())
        print(f"   ✅ Estatísticas: {stats.total_usuarios} usuários, {stats.total_musicas} músicas, {stats.total_playlists} playlists")
        print(f"   📊 Média de músicas por playlist: {stats.media_musicas_por_playlist:.2f}")
        print(f"   🏷️  Tecnologia: {stats.tecnologia}")
        
        print(f"\n🎉 Todos os testes CRUD do gRPC passaram com sucesso!")
        
    except grpc.RpcError as e:
        print(f"❌ Erro gRPC: {e}")
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    finally:
        channel.close()

if __name__ == "__main__":
    test_grpc_crud()
