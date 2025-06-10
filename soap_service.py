"""
SOAP Service for Streaming Platform
===================================

Implements a SOAP service using Spyne for the streaming platform.
"""

from spyne import Application, rpc, ServiceBase, Unicode, Integer, Array, ComplexModel
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server
from typing import List, Optional

from models import Usuario, Musica, Playlist, StreamingService
from data_loader import get_data_loader

# Data loader instance
data_loader = get_data_loader()

class UsuarioModel(ComplexModel):
    id = Unicode
    nome = Unicode
    idade = Integer

class MusicaModel(ComplexModel):
    id = Unicode
    nome = Unicode
    artista = Unicode
    duracao_segundos = Integer

class PlaylistModel(ComplexModel):
    id = Unicode
    nome = Unicode
    id_usuario = Unicode
    musicas = Array(Unicode)

class EstatisticasModel(ComplexModel):
    total_usuarios = Integer
    total_musicas = Integer
    total_playlists = Integer
    media_musicas_por_playlist = Integer

class StreamingService(ServiceBase):
    def __init__(self):
        self.service = StreamingService()

    @rpc(_returns=Array(UsuarioModel))
    def listar_usuarios(self):
        """List all users"""
        usuarios = data_loader.usuarios
        return [
            UsuarioModel(
                id=u["id"],
                nome=u["nome"],
                idade=u["idade"]
            )
            for u in usuarios
        ]

    @rpc(_returns=Array(MusicaModel))
    def listar_musicas(self):
        """List all songs"""
        musicas = data_loader.musicas
        return [
            MusicaModel(
                id=m["id"],
                nome=m["nome"],
                artista=m["artista"],
                duracao_segundos=m["duracaoSegundos"]
            )
            for m in musicas
        ]

    @rpc(_returns=Array(PlaylistModel))
    def listar_playlists(self):
        """List all playlists"""
        playlists = data_loader.playlists
        return [
            PlaylistModel(
                id=p["id"],
                nome=p["nome"],
                id_usuario=p["idUsuario"],
                musicas=p["musicas"]
            )
            for p in playlists
        ]

    @rpc(_returns=EstatisticasModel)
    def obter_estatisticas(self):
        """Obtém estatísticas do serviço"""
        try:
            stats = self.service.obter_estatisticas()
            return EstatisticasModel(
                total_usuarios=stats.total_usuarios,
                total_musicas=stats.total_musicas,
                total_playlists=stats.total_playlists,
                media_musicas_por_playlist=stats.media_musicas_por_playlist
            )
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            raise

    @rpc(Unicode, Unicode, Integer, _returns=UsuarioModel)
    def criar_usuario(self, id, nome, idade):
        """Cria um novo usuário"""
        try:
            usuario = self.service.criar_usuario(id, nome, idade)
            return UsuarioModel(id=usuario.id, nome=usuario.nome, idade=usuario.idade)
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {str(e)}")
            raise

    @rpc(Unicode, Unicode, Unicode, Integer, _returns=MusicaModel)
    def criar_musica(self, id, nome, artista, duracao):
        """Cria uma nova música"""
        try:
            musica = self.service.criar_musica(id, nome, artista, duracao)
            return MusicaModel(id=musica.id, nome=musica.nome, artista=musica.artista, 
                             duracao_segundos=musica.duracaoSegundos)
        except Exception as e:
            logger.error(f"Erro ao criar música: {str(e)}")
            raise

    @rpc(Unicode, Unicode, Unicode, Array(Unicode), _returns=PlaylistModel)
    def criar_playlist(self, id, nome, id_usuario, musicas):
        """Cria uma nova playlist"""
        try:
            playlist = self.service.criar_playlist(id, nome, id_usuario, musicas)
            return PlaylistModel(id=playlist.id, nome=playlist.nome, 
                               id_usuario=playlist.id_usuario, musicas=playlist.musicas)
        except Exception as e:
            logger.error(f"Erro ao criar playlist: {str(e)}")
            raise

def executar_servidor(host="0.0.0.0", port=8004):
    """Start the SOAP server"""
    application = Application(
        [StreamingService],
        tns='streaming.soap',
        name='StreamingService',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11()
    )

    wsgi_app = WsgiApplication(application)
    server = make_server(host, port, wsgi_app)
    print(f"🟡 SOAP: Servidor rodando em http://{host}:{port}/soap")
    server.serve_forever()

if __name__ == '__main__':
    executar_servidor()
