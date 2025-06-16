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
import shutil
import tempfile
import atexit
import uuid

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
    """Carregador de dados principal para o serviço de streaming com persistência temporária."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Inicializa o carregador de dados.
        
        Args:
            data_dir: Diretório onde estão os arquivos JSON originais
        """
        self.data_dir = data_dir
        self.temp_dir = None
        self.usuarios = []
        self.musicas = []
        self.playlists = []
        self._setup_temp_persistence()
        self._carregar_dados()
        
        # Registrar limpeza ao sair
        atexit.register(self._cleanup_temp_files)
    
    def _setup_temp_persistence(self):
        """Configura o sistema de persistência temporária."""
        # Criar diretório temporário
        self.temp_dir = tempfile.mkdtemp(prefix="streaming_temp_")
        print(f"📁 Diretório temporário criado: {self.temp_dir}")
        
        # Copiar arquivos originais para o diretório temporário
        for filename in ["usuarios.json", "musicas.json", "playlists.json"]:
            src = os.path.join(self.data_dir, filename)
            dst = os.path.join(self.temp_dir, filename)
            
            if os.path.exists(src):
                shutil.copy2(src, dst)
                print(f"📋 Copiado: {filename} -> temp")
            else:
                # Criar arquivo vazio se não existir
                with open(dst, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                print(f"📄 Criado arquivo vazio: {filename}")
    
    def _cleanup_temp_files(self):
        """Remove arquivos temporários."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"🗑️  Arquivos temporários removidos: {self.temp_dir}")
    
    def _carregar_dados(self):
        """Carrega todos os dados dos arquivos temporários."""
        try:
            self._carregar_usuarios()
            self._carregar_musicas()
            self._carregar_playlists()
            print(f"✅ Dados carregados: {len(self.usuarios)} usuários, {len(self.musicas)} músicas, {len(self.playlists)} playlists")
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            raise
    
    def _carregar_usuarios(self):
        """Carrega usuários do arquivo temporário."""
        arquivo_usuarios = os.path.join(self.temp_dir, "usuarios.json")
        with open(arquivo_usuarios, 'r', encoding='utf-8') as f:
            self.usuarios = json.load(f)
    
    def _carregar_musicas(self):
        """Carrega músicas do arquivo temporário."""
        arquivo_musicas = os.path.join(self.temp_dir, "musicas.json")
        with open(arquivo_musicas, 'r', encoding='utf-8') as f:
            self.musicas = json.load(f)
    
    def _carregar_playlists(self):
        """Carrega playlists do arquivo temporário."""
        arquivo_playlists = os.path.join(self.temp_dir, "playlists.json")
        with open(arquivo_playlists, 'r', encoding='utf-8') as f:
            self.playlists = json.load(f)
    
    def _salvar_usuarios(self):
        """Salva usuários no arquivo temporário."""
        arquivo_usuarios = os.path.join(self.temp_dir, "usuarios.json")
        with open(arquivo_usuarios, 'w', encoding='utf-8') as f:
            json.dump(self.usuarios, f, ensure_ascii=False, indent=2)
    
    def _salvar_musicas(self):
        """Salva músicas no arquivo temporário."""
        arquivo_musicas = os.path.join(self.temp_dir, "musicas.json")
        with open(arquivo_musicas, 'w', encoding='utf-8') as f:
            json.dump(self.musicas, f, ensure_ascii=False, indent=2)
    
    def _salvar_playlists(self):
        """Salva playlists no arquivo temporário."""
        arquivo_playlists = os.path.join(self.temp_dir, "playlists.json")
        with open(arquivo_playlists, 'w', encoding='utf-8') as f:
            json.dump(self.playlists, f, ensure_ascii=False, indent=2)

    # ========== MÉTODOS DE LEITURA ==========
    
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
        return [p for p in self.playlists if p["id_usuario"] == id_usuario]
    
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

    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas do sistema."""
        usuarios_com_playlists = len(set(p["id_usuario"] for p in self.playlists))
        total_musicas_playlists = sum(len(p["musicas"]) for p in self.playlists)
        
        return {
            "total_usuarios": len(self.usuarios),
            "total_musicas": len(self.musicas),
            "total_playlists": len(self.playlists),
            "usuarios_com_playlists": usuarios_com_playlists,
            "media_musicas_por_playlist": (
                total_musicas_playlists / len(self.playlists) if self.playlists else 0.0
            )
        }

    # ========== MÉTODOS CRUD - USUÁRIOS ==========
    
    def criar_usuario(self, nome: str, idade: int) -> Dict[str, Any]:
        """Cria um novo usuário."""
        novo_usuario = {
            "id": str(uuid.uuid4()),
            "nome": nome,
            "idade": idade
        }
        
        self.usuarios.append(novo_usuario)
        self._salvar_usuarios()
        
        return novo_usuario
    
    def atualizar_usuario(self, id_usuario: str, nome: str = None, idade: int = None) -> Optional[Dict[str, Any]]:
        """Atualiza um usuário existente."""
        usuario = self.get_usuario(id_usuario)
        if not usuario:
            return None
        
        if nome is not None:
            usuario["nome"] = nome
        if idade is not None:
            usuario["idade"] = idade
        
        self._salvar_usuarios()
        return usuario
    
    def deletar_usuario(self, id_usuario: str) -> bool:
        """Remove um usuário."""
        usuario_index = next((i for i, u in enumerate(self.usuarios) if u["id"] == id_usuario), None)
        if usuario_index is None:
            return False
        
        # Remover usuário
        del self.usuarios[usuario_index]
        
        # Remover playlists do usuário
        self.playlists = [p for p in self.playlists if p["id_usuario"] != id_usuario]
        
        self._salvar_usuarios()
        self._salvar_playlists()
        
        return True

    # ========== MÉTODOS CRUD - MÚSICAS ==========
    
    def criar_musica(self, nome: str, artista: str, duracao_segundos: int) -> Dict[str, Any]:
        """Cria uma nova música."""
        nova_musica = {
            "id": str(uuid.uuid4()),
            "nome": nome,
            "artista": artista,
            "duracao_segundos": duracao_segundos
        }
        
        self.musicas.append(nova_musica)
        self._salvar_musicas()
        
        return nova_musica
    
    def atualizar_musica(self, id_musica: str, nome: str = None, artista: str = None, duracao_segundos: int = None) -> Optional[Dict[str, Any]]:
        """Atualiza uma música existente."""
        musica = self.get_musica(id_musica)
        if not musica:
            return None
        
        if nome is not None:
            musica["nome"] = nome
        if artista is not None:
            musica["artista"] = artista
        if duracao_segundos is not None:
            musica["duracao_segundos"] = duracao_segundos
        
        self._salvar_musicas()
        return musica
    
    def deletar_musica(self, id_musica: str) -> bool:
        """Remove uma música."""
        musica_index = next((i for i, m in enumerate(self.musicas) if m["id"] == id_musica), None)
        if musica_index is None:
            return False
        
        # Remover música
        del self.musicas[musica_index]
        
        # Remover música das playlists
        for playlist in self.playlists:
            if id_musica in playlist["musicas"]:
                playlist["musicas"].remove(id_musica)
        
        self._salvar_musicas()
        self._salvar_playlists()
        
        return True

    # ========== MÉTODOS CRUD - PLAYLISTS ==========
    
    def criar_playlist(self, nome: str, id_usuario: str, musicas: List[str] = None) -> Dict[str, Any]:
        """Cria uma nova playlist."""
        if musicas is None:
            musicas = []
        
        nova_playlist = {
            "id": str(uuid.uuid4()),
            "nome": nome,
            "id_usuario": id_usuario,
            "musicas": musicas
        }
        
        self.playlists.append(nova_playlist)
        self._salvar_playlists()
        
        return nova_playlist
    
    def atualizar_playlist(self, id_playlist: str, nome: str = None, musicas: List[str] = None) -> Optional[Dict[str, Any]]:
        """Atualiza uma playlist existente."""
        playlist = self.get_playlist(id_playlist)
        if not playlist:
            return None
        
        if nome is not None:
            playlist["nome"] = nome
        if musicas is not None:
            playlist["musicas"] = musicas
        
        self._salvar_playlists()
        return playlist
    
    def deletar_playlist(self, id_playlist: str) -> bool:
        """Remove uma playlist."""
        playlist_index = next((i for i, p in enumerate(self.playlists) if p["id"] == id_playlist), None)
        if playlist_index is None:
            return False
        
        del self.playlists[playlist_index]
        self._salvar_playlists()
        
        return True


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