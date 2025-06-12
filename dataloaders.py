"""DataLoader implementation for GraphQL
====================================

This module provides DataLoader implementations to optimize GraphQL queries
by batching and caching database requests, and also provides the main data loader
for the streaming service that loads data from JSON files.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from functools import partial
import asyncio
from collections import defaultdict
import json
import os

@dataclass
class Batch:
    """Represents a batch of keys to be loaded"""
    keys: List[str]
    future: asyncio.Future

class DataLoader:
    """Generic DataLoader implementation for batching and caching requests"""
    
    def __init__(self, batch_load_fn):
        self.batch_load_fn = batch_load_fn
        self.cache = {}
        self.queue = []
        self.batch_size = 100
        self.batch_timeout = 0.1  # seconds
        
    async def load(self, key: str) -> Any:
        """Load a single value by key"""
        if key in self.cache:
            return self.cache[key]
            
        future = asyncio.Future()
        self.queue.append((key, future))
        
        if len(self.queue) >= self.batch_size:
            await self.dispatch()
            
        return await future
        
    async def load_many(self, keys: List[str]) -> List[Any]:
        """Load multiple values by keys"""
        return await asyncio.gather(*[self.load(key) for key in keys])
        
    async def dispatch(self):
        """Process the current batch of requests"""
        if not self.queue:
            return
            
        # Get current batch
        current_queue = self.queue
        self.queue = []
        
        # Group keys by their futures
        key_groups = defaultdict(list)
        for key, future in current_queue:
            key_groups[future].append(key)
            
        # Load data for each group
        for future, keys in key_groups.items():
            try:
                values = await self.batch_load_fn(keys)
                for key, value in zip(keys, values):
                    self.cache[key] = value
                future.set_result(values[0] if len(values) == 1 else values)
            except Exception as e:
                future.set_exception(e)
                
    async def clear(self):
        """Clear the cache"""
        self.cache.clear()
        
    async def clear_all(self):
        """Clear the cache and process any pending requests"""
        await self.clear()
        if self.queue:
            await self.dispatch()

class GraphQLDataLoaders:
    """Collection of DataLoaders for the GraphQL service"""
    
    def __init__(self, data_loader):
        self.data_loader = data_loader
        
        # Create DataLoaders for each entity type
        self.usuario_loader = DataLoader(self._load_usuarios)
        self.musica_loader = DataLoader(self._load_musicas)
        self.playlist_loader = DataLoader(self._load_playlists)
        
    async def _load_usuarios(self, keys: List[str]) -> List[Dict[str, Any]]:
        """Load multiple users by ID"""
        return [self.data_loader.get_usuario(key) for key in keys]
        
    async def _load_musicas(self, keys: List[str]) -> List[Dict[str, Any]]:
        """Load multiple songs by ID"""
        return [self.data_loader.get_musica(key) for key in keys]
        
    async def _load_playlists(self, keys: List[str]) -> List[Dict[str, Any]]:
        """Load multiple playlists by ID"""
        return [self.data_loader.get_playlist(key) for key in keys]
        
    async def get_usuario(self, id: str) -> Dict[str, Any]:
        """Get a user by ID using the DataLoader"""
        return await self.usuario_loader.load(id)
        
    async def get_musica(self, id: str) -> Dict[str, Any]:
        """Get a song by ID using the DataLoader"""
        return await self.musica_loader.load(id)
        
    async def get_playlist(self, id: str) -> Dict[str, Any]:
        """Get a playlist by ID using the DataLoader"""
        return await self.playlist_loader.load(id)
        
    async def get_usuarios(self, ids: List[str]) -> List[Dict[str, Any]]:
        """Get multiple users by ID using the DataLoader"""
        return await self.usuario_loader.load_many(ids)
        
    async def get_musicas(self, ids: List[str]) -> List[Dict[str, Any]]:
        """Get multiple songs by ID using the DataLoader"""
        return await self.musica_loader.load_many(ids)
        
    async def get_playlists(self, ids: List[str]) -> List[Dict[str, Any]]:
        """Get multiple playlists by ID using the DataLoader"""
        return await self.playlist_loader.load_many(ids)
        
    async def clear_all(self):
        """Clear all DataLoader caches"""
        await asyncio.gather(
            self.usuario_loader.clear_all(),
            self.musica_loader.clear_all(),
            self.playlist_loader.clear_all()
        )

class StreamingDataLoader:
    """Carregador de dados principal para o serviço de streaming."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Inicializa o carregador de dados.
        
        Args:
            data_dir: Diretório onde estão os arquivos JSON
        """
        self.data_dir = data_dir
        self.usuarios = []
        self.musicas = []
        self.playlists = []
        self._carregar_dados()
    
    def _carregar_dados(self):
        """Carrega todos os dados dos arquivos JSON."""
        try:
            self._carregar_usuarios()
            self._carregar_musicas()
            self._carregar_playlists()
            print(f"✅ Dados carregados: {len(self.usuarios)} usuários, {len(self.musicas)} músicas, {len(self.playlists)} playlists")
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            raise
    
    def _carregar_usuarios(self):
        """Carrega usuários do arquivo JSON."""
        arquivo_usuarios = os.path.join(self.data_dir, "usuarios.json")
        if os.path.exists(arquivo_usuarios):
            with open(arquivo_usuarios, 'r', encoding='utf-8') as f:
                self.usuarios = json.load(f)
        else:
            print(f"⚠️  Arquivo {arquivo_usuarios} não encontrado")
            self.usuarios = []
    
    def _carregar_musicas(self):
        """Carrega músicas do arquivo JSON."""
        arquivo_musicas = os.path.join(self.data_dir, "musicas.json")
        if os.path.exists(arquivo_musicas):
            with open(arquivo_musicas, 'r', encoding='utf-8') as f:
                musicas_raw = json.load(f)
                # Padronizar para snake_case: duracao_segundos -> duracaoSegundos para compatibilidade
                self.musicas = []
                for musica in musicas_raw:
                    musica_padronizada = {
                        "id": musica["id"],
                        "nome": musica["nome"],
                        "artista": musica["artista"],
                        "duracaoSegundos": musica.get("duracao_segundos", musica.get("duracaoSegundos", 0))
                    }
                    self.musicas.append(musica_padronizada)
        else:
            print(f"⚠️  Arquivo {arquivo_musicas} não encontrado")
            self.musicas = []
    
    def _carregar_playlists(self):
        """Carrega playlists do arquivo JSON."""
        arquivo_playlists = os.path.join(self.data_dir, "playlists.json")
        if os.path.exists(arquivo_playlists):
            with open(arquivo_playlists, 'r', encoding='utf-8') as f:
                playlists_raw = json.load(f)
                # Padronizar para snake_case: id_usuario -> idUsuario para compatibilidade
                self.playlists = []
                for playlist in playlists_raw:
                    playlist_padronizada = {
                        "id": playlist["id"],
                        "nome": playlist["nome"],
                        "idUsuario": playlist.get("id_usuario", playlist.get("idUsuario", "")),
                        "musicas": playlist.get("musicas", [])
                    }
                    self.playlists.append(playlist_padronizada)
        else:
            print(f"⚠️  Arquivo {arquivo_playlists} não encontrado")
            self.playlists = []
    
    def get_usuario(self, id_usuario: str) -> Optional[Dict[str, Any]]:
        """Obtém um usuário por ID."""
        return next((u for u in self.usuarios if u["id"] == id_usuario), None)
    
    def get_musica(self, id_musica: str) -> Optional[Dict[str, Any]]:
        """Obtém uma música por ID."""
        return next((m for m in self.musicas if m["id"] == id_musica), None)
    
    def get_playlist(self, id_playlist: str) -> Optional[Dict[str, Any]]:
        """Obtém uma playlist por ID."""
        return next((p for p in self.playlists if p["id"] == id_playlist), None)
    
    def listar_playlists_usuario(self, id_usuario: str) -> List[Dict[str, Any]]:
        """Lista todas as playlists de um usuário."""
        return [p for p in self.playlists if p["idUsuario"] == id_usuario]
    
    def listar_musicas_playlist(self, id_playlist: str) -> List[Dict[str, Any]]:
        """Lista todas as músicas de uma playlist."""
        playlist = self.get_playlist(id_playlist)
        if not playlist:
            return []
        
        musicas_da_playlist = []
        for id_musica in playlist["musicas"]:
            musica = self.get_musica(id_musica)
            if musica:
                musicas_da_playlist.append(musica)
        
        return musicas_da_playlist
    
    def listar_playlists_com_musica(self, id_musica: str) -> List[Dict[str, Any]]:
        """Lista todas as playlists que contêm uma música específica."""
        return [p for p in self.playlists if id_musica in p["musicas"]]


# Instância global do carregador de dados
_data_loader_instance = None

def get_data_loader() -> StreamingDataLoader:
    """
    Obtém a instância singleton do carregador de dados.
    
    Returns:
        StreamingDataLoader: Instância do carregador de dados
    """
    global _data_loader_instance
    if _data_loader_instance is None:
        _data_loader_instance = StreamingDataLoader()
    return _data_loader_instance