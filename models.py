"""
Model classes for the streaming service
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Usuario:
    id: str
    nome: str
    idade: int
    playlists: List[str] = None

    def __post_init__(self):
        if self.playlists is None:
            self.playlists = []

@dataclass
class Musica:
    id: str
    nome: str
    artista: str
    duracao_segundos: int
    playlists: List[str] = None

    def __post_init__(self):
        if self.playlists is None:
            self.playlists = []

@dataclass
class Playlist:
    id: str
    nome: str
    id_usuario: str
    musicas: List[str]

@dataclass
class StreamingService:
    usuarios: List[Usuario]
    musicas: List[Musica]
    playlists: List[Playlist]

    def get_usuario(self, id: str) -> Optional[Usuario]:
        return next((u for u in self.usuarios if u.id == id), None)

    def get_musica(self, id: str) -> Optional[Musica]:
        return next((m for m in self.musicas if m.id == id), None)

    def get_playlist(self, id: str) -> Optional[Playlist]:
        return next((p for p in self.playlists if p.id == id), None)