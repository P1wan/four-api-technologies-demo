#!/usr/bin/env python3
"""
Servidor SOAP Simples - Sem complicações
========================================
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

# Usar dados reais gerados em ``data/``
from data_loader import get_data_loader

# Carrega dados uma única vez
data_loader = get_data_loader()

# Substitui os arrays mock com dados reais
USUARIOS = data_loader.usuarios
MUSICAS = [
    {
        "id": m["id"],
        "nome": m["nome"],
        "artista": m["artista"],
        "duracao": m.get("duracaoSegundos", m.get("duracao", 0)),
    }
    for m in data_loader.musicas
]
PLAYLISTS = [
    {
        "id": p["id"],
        "nome": p["nome"],
        "usuario": p["idUsuario"],
        "musicas": p["musicas"],
    }
    for p in data_loader.playlists
]

# ========== MODELOS SOAP ==========
class Usuario(ComplexModel):
    id = Unicode
    nome = Unicode
    idade = Integer

class Musica(ComplexModel):
    id = Unicode
    nome = Unicode
    artista = Unicode
    duracao = Integer

class Playlist(ComplexModel):
    id = Unicode
    nome = Unicode
    usuario = Unicode

class Estatisticas(ComplexModel):
    total_usuarios = Integer
    total_musicas = Integer
    total_playlists = Integer
    media_musicas_por_playlist = Float
    tecnologia = Unicode
    framework = Unicode

# ========== SERVIÇO SOAP ==========
class StreamingService(ServiceBase):
    
    @rpc(_returns=Array(Usuario))
    def listar_usuarios(ctx):
        """Lista usuários"""
        print("🟡 SOAP: listar_usuarios chamado")
        return [Usuario(**u) for u in USUARIOS]
    
    @rpc(_returns=Array(Musica))
    def listar_musicas(ctx):
        """Lista músicas"""
        print("🟡 SOAP: listar_musicas chamado")
        return [Musica(**m) for m in MUSICAS]
    
    @rpc(_returns=Array(Playlist))
    def listar_playlists(ctx):
        """Lista playlists"""
        print("🟡 SOAP: listar_playlists chamado")
        return [Playlist(id=p["id"], nome=p["nome"], usuario=p["usuario"]) for p in PLAYLISTS]

    @rpc(Unicode, _returns=Array(Playlist))
    def listar_playlists_usuario(ctx, id_usuario):
        """Lista playlists de um usuário"""
        print(f"🟡 SOAP: listar_playlists_usuario chamado para {id_usuario}")
        playlists = [p for p in PLAYLISTS if p["usuario"] == id_usuario]
        return [Playlist(id=p["id"], nome=p["nome"], usuario=p["usuario"]) for p in playlists]

    @rpc(Unicode, _returns=Array(Musica))
    def listar_musicas_playlist(ctx, id_playlist):
        """Lista músicas de uma playlist"""
        print(f"🟡 SOAP: listar_musicas_playlist chamado para {id_playlist}")
        playlist = next((p for p in PLAYLISTS if p["id"] == id_playlist), None)
        if not playlist:
            return []
        musicas = []
        for mid in playlist["musicas"]:
            m = next((mu for mu in MUSICAS if mu["id"] == mid), None)
            if m:
                musicas.append(Musica(**m))
        return musicas

    @rpc(Unicode, _returns=Array(Playlist))
    def listar_playlists_com_musica(ctx, id_musica):
        """Lista playlists que contêm uma música"""
        print(f"🟡 SOAP: listar_playlists_com_musica chamado para {id_musica}")
        playlists = [p for p in PLAYLISTS if id_musica in p["musicas"]]
        return [Playlist(id=p["id"], nome=p["nome"], usuario=p["usuario"]) for p in playlists]
    
    @rpc(Unicode, _returns=Usuario)
    def buscar_usuario(ctx, user_id):
        """Busca usuário por ID"""
        print(f"🟡 SOAP: buscar_usuario chamado com ID: {user_id}")
        for user in USUARIOS:
            if user["id"] == user_id:
                return Usuario(**user)
        return Usuario(id="", nome="", idade=0)

    @rpc(Unicode, Unicode, Integer, _returns=Usuario)
    def criar_usuario(ctx, id, nome, idade):
        """Cria um novo usuário"""
        novo = {"id": id, "nome": nome, "idade": idade}
        USUARIOS.append(novo)
        return Usuario(**novo)

    @rpc(Unicode, _returns=Usuario)
    def GetUser(ctx, id):
        """Obtém usuário por ID"""
        for u in USUARIOS:
            if u["id"] == id:
                return Usuario(**u)
        return Usuario(id="", nome="", idade=0)

    @rpc(Unicode, Unicode, Unicode, Array(Unicode), _returns=Playlist)
    def criar_playlist(ctx, id, nome, id_usuario, musicas):
        """Cria uma nova playlist"""
        nova = {"id": id, "nome": nome, "usuario": id_usuario, "musicas": list(musicas)}
        PLAYLISTS.append(nova)
        return Playlist(id=id, nome=nome, usuario=id_usuario)

    @rpc(Unicode, _returns=Playlist)
    def GetPlaylist(ctx, id):
        """Obtém playlist por ID"""
        for p in PLAYLISTS:
            if p["id"] == id:
                return Playlist(id=p["id"], nome=p["nome"], usuario=p["usuario"])
        return Playlist(id="", nome="", usuario="")

    @rpc(_returns=Estatisticas)
    def obter_estatisticas(ctx):
        """Retorna estatísticas do serviço"""
        total_playlists = len(PLAYLISTS)
        total_musicas = len(MUSICAS)
        total_usuarios = len(USUARIOS)
        media = 0.0
        if total_playlists:
            media = sum(len(p.get("musicas", [])) for p in PLAYLISTS) / total_playlists
        return Estatisticas(
            total_usuarios=total_usuarios,
            total_musicas=total_musicas,
            total_playlists=total_playlists,
            media_musicas_por_playlist=media,
            tecnologia="SOAP",
            framework="Spyne",
        )

# ========== CONFIGURAÇÃO DO SERVIDOR ==========
def create_app():
    """Cria aplicação SOAP"""
    application = Application(
        [StreamingService],
        tns='http://streaming.soap',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11()
    )
    return application

def handle_cors(environ, start_response):
    """Handle CORS e routing simples"""
    method = environ['REQUEST_METHOD']
    path = environ.get('PATH_INFO', '/')
    if path.startswith('/soap'):
        environ['PATH_INFO'] = path[len('/soap'):] or '/'
        path = environ['PATH_INFO']
    query = environ.get('QUERY_STRING', '')
    
    print(f"🌐 Request: {method} {path}?{query}")
    
    # CORS preflight
    if method == 'OPTIONS':
        start_response('200 OK', [
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, SOAPAction')
        ])
        return [b'OK']
    
    # Info page
    if method == 'GET' and 'wsdl' not in query.lower():
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>SOAP Service</title></head>
        <body>
            <h1>🟡 SOAP Service Ativo</h1>
            <p><strong>WSDL:</strong> <a href="/soap?wsdl">Clique aqui</a></p>
            <p><strong>Interface:</strong> <a href="http://localhost:8080/soap/">Teste aqui</a></p>
            <h2>Operações:</h2>
            <ul>
                <li>listar_usuarios()</li>
                <li>listar_musicas()</li>
                <li>listar_playlists()</li>
                <li>buscar_usuario(user_id)</li>
                <li>criar_usuario(id, nome, idade)</li>
                <li>GetUser(id)</li>
                <li>criar_playlist(id, nome, id_usuario, musicas[])</li>
                <li>GetPlaylist(id)</li>
                <li>listar_playlists_usuario(id_usuario)</li>
                <li>listar_musicas_playlist(id_playlist)</li>
                <li>listar_playlists_com_musica(id_musica)</li>
                <li>obter_estatisticas()</li>
            </ul>
        </body>
        </html>
        """
        start_response('200 OK', [
            ('Content-Type', 'text/html'),
            ('Access-Control-Allow-Origin', '*')
        ])
        return [html.encode('utf-8')]
    
    # SOAP requests
    app = create_app()
    wsgi_app = WsgiApplication(app)
    
    def cors_start_response(status, headers):
        headers.append(('Access-Control-Allow-Origin', '*'))
        headers.append(('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'))
        headers.append(('Access-Control-Allow-Headers', 'Content-Type, SOAPAction'))
        return start_response(status, headers)
    
    return wsgi_app(environ, cors_start_response)

def executar_servidor(host="0.0.0.0", port=8004):
    """Executa o servidor"""
    print("🟡 Iniciando servidor SOAP simples...")
    print(f"🟡 Porta: {port}")
    print(f"🟡 WSDL: http://localhost:{port}/soap?wsdl")
    print("🟡 Interface: http://localhost:8080/soap/")
    print("=" * 50)

    server = make_server(host, port, handle_cors)
    
    try:
        print("✅ Servidor rodando! Ctrl+C para parar")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado")

if __name__ == '__main__':
    executar_servidor()
