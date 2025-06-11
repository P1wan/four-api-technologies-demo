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
    ComplexModel,
    Array,
    Iterable,
)
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server
import json
import uuid
from typing import List, Dict, Optional
import traceback

# Usar dados reais gerados em data/
from data_loader import get_data_loader

# Carrega dados uma única vez
data_loader = get_data_loader()

# Criar cópias locais para evitar modificações dos dados compartilhados
USUARIOS = [usuario.copy() for usuario in data_loader.usuarios]
MUSICAS = [
    {
        "id": musica["id"],
        "nome": musica["nome"],
        "artista": musica["artista"],
        "duracao": musica.get("duracaoSegundos", musica.get("duracao", 0)),
    }
    for musica in data_loader.musicas
]

def obter_playlists_locais() -> List[Dict]:
    """Retorna playlists no formato usado pelo serviço SOAP."""
    return [
        {
            "id": playlist["id"],
            "nome": playlist["nome"],
            "usuario": playlist["idUsuario"],
            "musicas": playlist["musicas"],
        }
        for playlist in data_loader.playlists
    ]

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
        return [Usuario(**usuario) for usuario in USUARIOS]
    
    @rpc(_returns=Array(Musica))
    def listar_musicas(ctx):
        """Lista todas as músicas do sistema."""
        return [Musica(**musica) for musica in MUSICAS]
    
    @rpc(_returns=Array(Playlist))
    def listar_playlists(ctx):
        """Lista todas as playlists do sistema."""
        playlists = obter_playlists_locais()
        return [Playlist(id=p["id"], nome=p["nome"], usuario=p["usuario"]) for p in playlists]

    @rpc(Unicode, _returns=Array(Playlist))
    def listar_playlists_usuario(ctx, id_usuario):
        """Lista playlists de um usuário específico."""
        playlists = [p for p in obter_playlists_locais() if p["usuario"] == id_usuario]
        return [Playlist(id=p["id"], nome=p["nome"], usuario=p["usuario"]) for p in playlists]

    @rpc(Unicode, _returns=Array(Musica))
    def listar_musicas_playlist(ctx, id_playlist):
        """Lista músicas de uma playlist específica."""
        playlist = next((p for p in obter_playlists_locais() if p["id"] == id_playlist), None)
        if not playlist:
            return []
        
        musicas_da_playlist = []
        for id_musica in playlist["musicas"]:
            musica = next((m for m in MUSICAS if m["id"] == id_musica), None)
            if musica:
                musicas_da_playlist.append(Musica(**musica))
        return musicas_da_playlist

    @rpc(Unicode, _returns=Array(Playlist))
    def listar_playlists_com_musica(ctx, id_musica):
        """Lista playlists que contêm uma música específica."""
        playlists = [p for p in obter_playlists_locais() if id_musica in p["musicas"]]
        return [Playlist(id=p["id"], nome=p["nome"], usuario=p["usuario"]) for p in playlists]
    
    @rpc(Unicode, _returns=Usuario)
    def obter_usuario(ctx, id_usuario):
        """Obtém um usuário por ID."""
        usuario = next((u for u in USUARIOS if u["id"] == id_usuario), None)
        if usuario:
            return Usuario(**usuario)
        return Usuario(id="", nome="", idade=0)

    @rpc(Unicode, Integer, _returns=Usuario)
    def criar_usuario(ctx, nome, idade):
        """Cria um novo usuário."""
        novo_id = str(uuid.uuid4())
        novo_usuario = {"id": novo_id, "nome": nome, "idade": idade}
        USUARIOS.append(novo_usuario)
        return Usuario(**novo_usuario)

    @rpc(Unicode, Unicode, Integer, _returns=Musica)
    def criar_musica(ctx, nome, artista, duracao):
        """Cria uma nova música."""
        novo_id = str(uuid.uuid4())
        nova_musica = {
            "id": novo_id,
            "nome": nome,
            "artista": artista,
            "duracao": duracao,
        }
        MUSICAS.append(nova_musica)
        return Musica(**nova_musica)

    @rpc(Unicode, Unicode, Array(Unicode), _returns=Playlist)
    def criar_playlist(ctx, nome, id_usuario, musicas):
        """Cria uma nova playlist."""
        novo_id = str(uuid.uuid4())
        nova_playlist = {
            "id": novo_id,
            "nome": nome,
            "usuario": id_usuario,
            "musicas": list(musicas) if musicas else [],
        }
        # Não modificar dados compartilhados - apenas retornar o resultado
        return Playlist(id=novo_id, nome=nome, usuario=id_usuario)

    @rpc(Unicode, _returns=Playlist)
    def obter_playlist(ctx, id_playlist):
        """Obtém uma playlist por ID."""
        playlist = next((p for p in obter_playlists_locais() if p["id"] == id_playlist), None)
        if playlist:
            return Playlist(id=playlist["id"], nome=playlist["nome"], usuario=playlist["usuario"])
        return Playlist(id="", nome="", usuario="")

    @rpc(_returns=Estatisticas)
    def obter_estatisticas(ctx):
        """Retorna estatísticas do serviço."""
        playlists = obter_playlists_locais()
        total_playlists = len(playlists)
        total_musicas = len(MUSICAS)
        total_usuarios = len(USUARIOS)
        
        media_musicas_por_playlist = 0.0
        if total_playlists > 0:
            total_musicas_em_playlists = sum(len(p.get("musicas", [])) for p in playlists)
            media_musicas_por_playlist = total_musicas_em_playlists / total_playlists
        
        return Estatisticas(
            total_usuarios=total_usuarios,
            total_musicas=total_musicas,
            total_playlists=total_playlists,
            media_musicas_por_playlist=media_musicas_por_playlist,
            tecnologia="SOAP",
            framework="Spyne",
        )

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
            <p>Este é o serviço SOAP da plataforma de streaming.</p>
            <h2>Operações Disponíveis:</h2>
            <ul>
                <li>listar_usuarios</li>
                <li>listar_musicas</li>
                <li>listar_playlists</li>
                <li>listar_playlists_usuario</li>
                <li>listar_musicas_playlist</li>
                <li>listar_playlists_com_musica</li>
                <li>obter_usuario</li>
                <li>criar_usuario</li>
                <li>criar_musica</li>
                <li>criar_playlist</li>
                <li>obter_playlist</li>
                <li>obter_estatisticas</li>
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
