#!/usr/bin/env python3
"""
Servidor SOAP para Plataforma de Streaming
==========================================

Implementacao completa do servico SOAP usando Spyne.
Padronizado seguindo convenções Python e boas práticas de desenvolvimento.
"""

from spyne import (
    Application,
    rpc,
    ServiceBase,
    Unicode,
    Integer,
    Float,
    Boolean,
    ComplexModel,
    Array,
    Iterable,
)
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server
import json
from typing import List, Dict, Optional
import traceback

# Usar dados reais gerados em data/
from dataloaders import get_data_loader

# Função para obter data_loader dinamicamente
def get_loader():
    return get_data_loader()

# Criar cópias locais para evitar modificações dos dados compartilhados
# SOAP agora usa delegação total para o data_loader
# Não precisa mais de cópias locais ou listas temporárias

# Modelos SOAP padronizados
class Usuario(ComplexModel):
    """Modelo de usuário para SOAP."""
    id = Unicode
    nome = Unicode
    idade = Integer

class Musica(ComplexModel):
    """Modelo de música para SOAP."""
    id = Unicode
    nome = Unicode
    artista = Unicode
    duracao = Integer

class Playlist(ComplexModel):
    """Modelo de playlist para SOAP."""
    id = Unicode
    nome = Unicode
    usuario = Unicode

class Estatisticas(ComplexModel):
    """Modelo de estatísticas para SOAP."""
    total_usuarios = Integer
    total_musicas = Integer
    total_playlists = Integer
    media_musicas_por_playlist = Float
    tecnologia = Unicode
    framework = Unicode

class StreamingService(ServiceBase):
    """Serviço SOAP para plataforma de streaming."""
    
    @rpc(_returns=Array(Usuario))
    def listar_usuarios(ctx):
        """Lista todos os usuários do sistema."""
        return [Usuario(**usuario) for usuario in get_loader().usuarios]
    
    @rpc(_returns=Array(Musica))
    def listar_musicas(ctx):
        """Lista todas as músicas do sistema."""
        return [Musica(id=m["id"], nome=m["nome"], artista=m["artista"], 
                      duracao=m["duracao_segundos"]) 
                for m in get_loader().musicas]
    
    @rpc(_returns=Array(Playlist))
    def listar_playlists(ctx):
        """Lista todas as playlists do sistema."""
        playlists = []
        for p in get_loader().playlists:
            playlists.append(Playlist(id=p["id"], nome=p["nome"], usuario=p["id_usuario"]))
        return playlists

    @rpc(Unicode, _returns=Array(Playlist))
    def listar_playlists_usuario(ctx, id_usuario):
        """Lista playlists de um usuário específico."""
        result_playlists = []
        for p in get_loader().playlists:
            if p["id_usuario"] == id_usuario:
                result_playlists.append(Playlist(id=p["id"], nome=p["nome"], usuario=p["id_usuario"]))
        return result_playlists

    @rpc(Unicode, _returns=Array(Musica))
    def listar_musicas_playlist(ctx, id_playlist):
        """Lista músicas de uma playlist específica."""
        playlist = next((p for p in get_loader().playlists if p["id"] == id_playlist), None)
        if not playlist:
            return []
        
        musicas_da_playlist = []
        for id_musica in playlist["musicas"]:
            musica = next((m for m in get_loader().musicas if m["id"] == id_musica), None)
            if musica:
                musicas_da_playlist.append(Musica(
                    id=musica["id"], nome=musica["nome"], artista=musica["artista"],
                    duracao=musica["duracao_segundos"]
                ))
        return musicas_da_playlist

    @rpc(Unicode, _returns=Array(Playlist))
    def listar_playlists_com_musica(ctx, id_musica):
        """Lista playlists que contêm uma música específica."""
        result_playlists = []
        for p in get_loader().playlists:
            if id_musica in p["musicas"]:
                result_playlists.append(Playlist(id=p["id"], nome=p["nome"], usuario=p["id_usuario"]))
        return result_playlists
    
    @rpc(Unicode, _returns=Usuario)
    def obter_usuario(ctx, id_usuario):
        """Obtém um usuário por ID."""
        usuario = get_loader().get_usuario(id_usuario)
        if usuario:
            return Usuario(**usuario)
        return Usuario(id=None, nome=None, idade=0)

    @rpc(Unicode, Integer, _returns=Usuario)
    def criar_usuario(ctx, nome, idade):
        """Cria um novo usuário."""
        novo_usuario = get_loader().criar_usuario(nome, idade)
        return Usuario(**novo_usuario)

    @rpc(Unicode, Unicode, Integer, _returns=Musica)
    def criar_musica(ctx, nome, artista, duracao):
        """Cria uma nova música."""
        nova_musica = get_loader().criar_musica(nome, artista, duracao_segundos=duracao)
        return Musica(id=nova_musica["id"], nome=nova_musica["nome"], 
                     artista=nova_musica["artista"], 
                     duracao=nova_musica["duracao_segundos"])

    @rpc(Unicode, Unicode, Array(Unicode), _returns=Playlist)
    def criar_playlist(ctx, nome, id_usuario, musicas):
        """Cria uma nova playlist."""
        nova_playlist = get_loader().criar_playlist(nome, id_usuario, list(musicas) if musicas else [])
        return Playlist(id=nova_playlist["id"], nome=nova_playlist["nome"], usuario=nova_playlist["id_usuario"])

    @rpc(Unicode, _returns=Playlist)
    def obter_playlist(ctx, id_playlist):
        """Obtém uma playlist por ID."""
        playlist = get_loader().get_playlist(id_playlist)
        if playlist:
            return Playlist(id=playlist["id"], nome=playlist["nome"], usuario=playlist["id_usuario"])
        return Playlist(id=None, nome=None, usuario=None)

    @rpc(_returns=Estatisticas)
    def obter_estatisticas(ctx):
        """Retorna estatísticas do serviço."""
        total_playlists = len(get_loader().playlists)
        total_musicas = len(get_loader().musicas)
        total_usuarios = len(get_loader().usuarios)
        
        media_musicas_por_playlist = 0.0
        if total_playlists > 0:
            total_musicas_em_playlists = sum(len(p.get("musicas", [])) for p in get_loader().playlists)
            media_musicas_por_playlist = total_musicas_em_playlists / total_playlists
        
        return Estatisticas(
            total_usuarios=total_usuarios,
            total_musicas=total_musicas,
            total_playlists=total_playlists,
            media_musicas_por_playlist=media_musicas_por_playlist,
            tecnologia="SOAP",
            framework="Spyne"
        )

    # ========== UPDATE AND DELETE OPERATIONS ==========

    @rpc(Unicode, Unicode, Integer, _returns=Usuario)
    def atualizar_usuario(ctx, id_usuario, nome, idade):
        """Atualiza um usuário existente."""
        usuario_atualizado = get_loader().atualizar_usuario(id_usuario, nome, idade)
        if usuario_atualizado:
            return Usuario(**usuario_atualizado)
        return Usuario(id=None, nome=None, idade=0)

    @rpc(Unicode, _returns=Boolean)
    def deletar_usuario(ctx, id_usuario):
        """Remove um usuário do sistema."""
        return get_loader().deletar_usuario(id_usuario)

    @rpc(Unicode, Unicode, Unicode, Integer, _returns=Musica)
    def atualizar_musica(ctx, id_musica, nome, artista, duracao):
        """Atualiza uma música existente."""
        musica_atualizada = get_loader().atualizar_musica(id_musica, nome, artista, duracao_segundos=duracao)
        if musica_atualizada:
            return Musica(id=musica_atualizada["id"], nome=musica_atualizada["nome"], 
                         artista=musica_atualizada["artista"], 
                         duracao=musica_atualizada["duracao_segundos"])
        return Musica(id=None, nome=None, artista=None, duracao=0)

    @rpc(Unicode, _returns=Boolean)
    def deletar_musica(ctx, id_musica):
        """Remove uma música do sistema."""
        return get_loader().deletar_musica(id_musica)

    @rpc(Unicode, Unicode, Array(Unicode), _returns=Playlist)
    def atualizar_playlist(ctx, id_playlist, nome, musicas):
        """Atualiza uma playlist existente."""
        playlist_atualizada = get_loader().atualizar_playlist(id_playlist, nome, list(musicas) if musicas else None)
        if playlist_atualizada:
            return Playlist(id=playlist_atualizada["id"], nome=playlist_atualizada["nome"], 
                           usuario=playlist_atualizada["id_usuario"])
        return Playlist(id=None, nome=None, usuario=None)

    @rpc(Unicode, _returns=Boolean)
    def deletar_playlist(ctx, id_playlist):
        """Remove uma playlist do sistema."""
        return get_loader().deletar_playlist(id_playlist)

    @rpc(_returns=Array(Playlist))
    def listar_playlists_simples(ctx):
        """Lista playlists sem o campo musicas para teste."""
        playlists = []
        for p in get_loader().playlists[:5]:  # Apenas 5 para teste
            playlists.append(Playlist(id=p["id"], nome=p["nome"], usuario=p["id_usuario"]))
        return playlists

def criar_aplicacao_soap():
    """Cria a aplicação SOAP."""
    application = Application(
        [StreamingService],
        tns='http://streaming.soap.service',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11(),
        name='StreamingService'
    )
    return application

def manipular_cors_e_roteamento(environ, start_response):
    """Manipula CORS e roteamento de requisições."""
    method = environ['REQUEST_METHOD']
    path = environ.get('PATH_INFO', '/')
    
    # Log request details
    print(f"\nSOAP Request:")
    print(f"Method: {method}")
    print(f"Path: {path}")
    print(f"Headers: {dict(environ)}")
    
    # Normalizar path para SOAP
    if path.startswith('/soap'):
        environ['PATH_INFO'] = path[len('/soap'):] or '/'
        path = environ['PATH_INFO']
    
    query = environ.get('QUERY_STRING', '')
    
    # Preflight CORS
    if method == 'OPTIONS':
        start_response('200 OK', [
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, SOAPAction')
        ])
        return [b'OK']
    
    # Página informativa
    if method == 'GET' and 'wsdl' not in query.lower():
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Serviço SOAP - Plataforma de Streaming</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #2c3e50; }
                ul { margin: 20px 0; }
                li { margin: 5px 0; }
                a { color: #3498db; }
                .error { color: #e74c3c; }
                .success { color: #2ecc71; }
            </style>
        </head>
        <body>
            <h1>Serviço SOAP - Plataforma de Streaming</h1>
            <p>Este é o serviço SOAP da plataforma de streaming.</p>            <h2>Operações Disponíveis:</h2>
            <ul>
                <li><strong>Consultas:</strong></li>
                <li>listar_usuarios</li>
                <li>listar_musicas</li>
                <li>listar_playlists</li>
                <li>listar_playlists_usuario</li>
                <li>listar_musicas_playlist</li>
                <li>listar_playlists_com_musica</li>
                <li>obter_usuario</li>
                <li>obter_playlist</li>
                <li>obter_estatisticas</li>
                <li><strong>Operações CRUD:</strong></li>
                <li>criar_usuario</li>
                <li>atualizar_usuario</li>
                <li>deletar_usuario</li>
                <li>criar_musica</li>
                <li>atualizar_musica</li>
                <li>deletar_musica</li>
                <li>criar_playlist</li>
                <li>atualizar_playlist</li>
                <li>deletar_playlist</li>
            </ul>
            <p>Para ver o WSDL, acesse: <a href="?wsdl">?wsdl</a></p>
        </body>
        </html>
        """
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [html.encode('utf-8')]

    def start_response_com_cors(status, headers):
        """Adiciona headers CORS à resposta."""
        headers.extend([
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, SOAPAction')
        ])
        return start_response(status, headers)

    try:
        # Process SOAP request
        application = criar_aplicacao_soap()
        wsgi_app = WsgiApplication(application)
        return wsgi_app(environ, start_response_com_cors)
    except Exception as e:
        print(f"SOAP Error: {str(e)}")
        error_response = f"""
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                <soap:Fault>
                    <faultcode>soap:Server</faultcode>
                    <faultstring>Internal Server Error</faultstring>
                    <detail>
                        <error>{str(e)}</error>
                        <traceback>{traceback.format_exc()}</traceback>
                    </detail>
                </soap:Fault>
            </soap:Body>
        </soap:Envelope>
        """
        start_response_com_cors('500 Internal Server Error', [('Content-Type', 'text/xml')])
        return [error_response.encode('utf-8')]

def executar_servidor(host="0.0.0.0", port=8004):
    """Executa o servidor SOAP."""
    print(f"Iniciando servidor SOAP em http://{host}:{port}")
    print("Pressione Ctrl+C para encerrar")
    
    application = criar_aplicacao_soap()
    wsgi_app = WsgiApplication(application)
    server = make_server(host, port, manipular_cors_e_roteamento)
    server.serve_forever()

if __name__ == '__main__':
    executar_servidor()
