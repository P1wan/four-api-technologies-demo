"""DataLoader implementation for GraphQL
====================================

This module provides DataLoader implementations to optimize GraphQL queries
by batching and caching database requests.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from functools import partial
import asyncio
from collections import defaultdict

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