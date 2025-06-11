"""
Data Loader para Serviços de Streaming
=====================================

Este módulo carrega e organiza os dados JSON gerados para uso pelos serviços backend.
Fornece funções de consulta otimizadas para as operações do serviço de streaming.
"""

import json
import os
from typing import List, Dict, Optional
from collections import defaultdict

class StreamingDataLoader:
    """
    Classe responsável por carregar e gerenciar os dados do serviço de streaming.
    Mantém os dados em memória e fornece métodos de consulta otimizados.
    """

    def __init__(self, data_dir: str = "data"):
        """
        Inicializa o loader com o diretório dos dados.

        Args:
            data_dir: Diretório contendo os arquivos JSON
        """
        self.data_dir = data_dir
        self.usuarios: List[Dict] = []
        self.musicas: List[Dict] = []
        self.playlists: List[Dict] = []

        # Índices para consultas rápidas
        self.usuarios_por_id: Dict[str, Dict] = {}
        self.musicas_por_id: Dict[str, Dict] = {}
        self.playlists_por_id: Dict[str, Dict] = {}
        self.playlists_por_usuario: Dict[str, List[Dict]] = defaultdict(list)
        self.playlists_por_musica: Dict[str, List[Dict]] = defaultdict(list)

        self._carregar_dados()
        self._criar_indices()

    def _carregar_dados(self):
        """Carrega os dados dos arquivos JSON."""
        try:
            # Carregar usuários
            with open(os.path.join(self.data_dir, 'usuarios.json'), 'r', encoding='utf-8') as f:
                self.usuarios = json.load(f)

            # Carregar músicas
            with open(os.path.join(self.data_dir, 'musicas.json'), 'r', encoding='utf-8') as f:
                self.musicas = json.load(f)

            # Carregar playlists
            with open(os.path.join(self.data_dir, 'playlists.json'), 'r', encoding='utf-8') as f:
                self.playlists = json.load(f)

            print(f"✅ Dados carregados com sucesso:")
            print(f"   - {len(self.usuarios)} usuários")
            print(f"   - {len(self.musicas)} músicas")
            print(f"   - {len(self.playlists)} playlists")

        except FileNotFoundError as e:
            print(f"Erro: Arquivo não encontrado - {e}")
            print("Execute primeiro o script gerar_dados.py para criar os dados.")
            raise
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON - {e}")
            raise

    def _criar_indices(self):
        """Cria índices para consultas rápidas."""
        # Índices por ID
        self.usuarios_por_id = {u['id']: u for u in self.usuarios}
        self.musicas_por_id = {m['id']: m for m in self.musicas}
        self.playlists_por_id = {p['id']: p for p in self.playlists}

        # Índice: playlists por usuário
        for playlist in self.playlists:
            id_usuario = playlist['idUsuario']
            self.playlists_por_usuario[id_usuario].append(playlist)

        # Índice: playlists que contêm cada música
        for playlist in self.playlists:
            for id_musica in playlist['musicas']:
                self.playlists_por_musica[id_musica].append(playlist)

        print(f"Índices criados com sucesso")

    # ========== OPERAÇÕES DE CONSULTA PRINCIPAIS ==========

    def listar_todos_usuarios(self) -> List[Dict]:
        """
        Lista todos os usuários do serviço.

        Returns:
            Lista com todos os usuários
        """
        return self.usuarios.copy()

    def listar_todas_musicas(self) -> List[Dict]:
        """
        Lista todas as músicas do serviço.

        Returns:
            Lista com todas as músicas
        """
        return self.musicas.copy()

    def listar_playlists_usuario(self, id_usuario: str) -> List[Dict]:
        """
        Lista todas as playlists de um usuário específico.

        Args:
            id_usuario: ID do usuário

        Returns:
            Lista de playlists do usuário
        """
        return self.playlists_por_usuario.get(id_usuario, []).copy()

    def listar_musicas_playlist(self, id_playlist: str) -> List[Dict]:
        """
        Lista todas as músicas de uma playlist específica.

        Args:
            id_playlist: ID da playlist

        Returns:
            Lista de músicas da playlist
        """
        playlist = self.playlists_por_id.get(id_playlist)
        if not playlist:
            return []

        musicas_da_playlist = []
        for id_musica in playlist['musicas']:
            musica = self.musicas_por_id.get(id_musica)
            if musica:
                musicas_da_playlist.append(musica)

        return musicas_da_playlist

    def listar_playlists_com_musica(self, id_musica: str) -> List[Dict]:
        """
        Lista todas as playlists que contêm uma música específica.

        Args:
            id_musica: ID da música

        Returns:
            Lista de playlists que contêm a música
        """
        return self.playlists_por_musica.get(id_musica, []).copy()

    # ========== OPERAÇÕES AUXILIARES ==========

    def obter_usuario_por_id(self, id_usuario: str) -> Optional[Dict]:
        """Obtém um usuário por ID."""
        return self.usuarios_por_id.get(id_usuario)

    def obter_musica_por_id(self, id_musica: str) -> Optional[Dict]:
        """Obtém uma música por ID."""
        return self.musicas_por_id.get(id_musica)

    def obter_playlist_por_id(self, id_playlist: str) -> Optional[Dict]:
        """Obtém uma playlist por ID."""
        return self.playlists_por_id.get(id_playlist)

    # ========== ESTATÍSTICAS ==========

    def obter_estatisticas(self) -> Dict:
        """
        Retorna estatísticas gerais dos dados.

        Returns:
            Dicionário com estatísticas
        """
        return {
            "total_usuarios": len(self.usuarios),
            "total_musicas": len(self.musicas),
            "total_playlists": len(self.playlists),
            "usuarios_com_playlists": len(self.playlists_por_usuario),
            "media_playlists_por_usuario": len(self.playlists) / len(self.playlists_por_usuario) if self.playlists_por_usuario else 0,
            "media_musicas_por_playlist": sum(len(p['musicas']) for p in self.playlists) / len(self.playlists) if self.playlists else 0
        }

# ========== INSTÂNCIA GLOBAL ==========

# Instância global do data loader (padrão Singleton simplificado)
_data_loader_instance = None

def get_data_loader() -> StreamingDataLoader:
    """
    Retorna a instância singleton do data loader.

    Returns:
        Instância do StreamingDataLoader
    """
    global _data_loader_instance

    if _data_loader_instance is None:
        _data_loader_instance = StreamingDataLoader()

    return _data_loader_instance

# ========== FUNÇÕES DE CONVENIÊNCIA ==========

def listar_todos_usuarios() -> List[Dict]:
    """Função de conveniência para listar todos os usuários."""
    return get_data_loader().listar_todos_usuarios()

def listar_todas_musicas() -> List[Dict]:
    """Função de conveniência para listar todas as músicas."""
    return get_data_loader().listar_todas_musicas()

def listar_playlists_usuario(id_usuario: str) -> List[Dict]:
    """Função de conveniência para listar playlists de um usuário."""
    return get_data_loader().listar_playlists_usuario(id_usuario)

def listar_musicas_playlist(id_playlist: str) -> List[Dict]:
    """Função de conveniência para listar músicas de uma playlist."""
    return get_data_loader().listar_musicas_playlist(id_playlist)

def listar_playlists_com_musica(id_musica: str) -> List[Dict]:
    """Função de conveniência para listar playlists que contêm uma música."""
    return get_data_loader().listar_playlists_com_musica(id_musica)

# ========== TESTE DO MÓDULO ==========

def teste_data_loader():
    """Função de teste para verificar o funcionamento do data loader."""
    print("🧪 TESTE DO DATA LOADER")
    print("=" * 50)

    try:
        loader = get_data_loader()

        # Testar consultas
        print("1. Testando listar_todos_usuarios()...")
        usuarios = loader.listar_todos_usuarios()
        print(f"   ✅ {len(usuarios)} usuários encontrados")

        print("2. Testando listar_todas_musicas()...")
        musicas = loader.listar_todas_musicas()
        print(f"   ✅ {len(musicas)} músicas encontradas")

        print("3. Testando listar_playlists_usuario()...")
        if usuarios:
            primeiro_usuario = usuarios[0]
            playlists = loader.listar_playlists_usuario(primeiro_usuario['id'])
            print(f"   ✅ Usuário '{primeiro_usuario['nome']}' tem {len(playlists)} playlists")

        print("4. Testando listar_musicas_playlist()...")
        if loader.playlists:
            primeira_playlist = loader.playlists[0]
            musicas_playlist = loader.listar_musicas_playlist(primeira_playlist['id'])
            print(f"   ✅ Playlist '{primeira_playlist['nome']}' tem {len(musicas_playlist)} músicas")

        print("5. Testando listar_playlists_com_musica()...")
        if musicas:
            primeira_musica = musicas[0]
            playlists_com_musica = loader.listar_playlists_com_musica(primeira_musica['id'])
            print(f"   ✅ Música '{primeira_musica['nome']}' está em {len(playlists_com_musica)} playlists")

        print("6. Testando estatísticas...")
        stats = loader.obter_estatisticas()
        print(f"   ✅ Estatísticas: {stats}")

        print("\n✅ Todos os testes passaram com sucesso!")

    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        raise

if __name__ == "__main__":
    teste_data_loader()