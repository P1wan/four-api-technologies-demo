#!/usr/bin/env python3
"""
Servidor SOAP Simples - Sem complicações
========================================
"""

from spyne import Application, rpc, ServiceBase, Unicode, Integer, ComplexModel
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server
import json

# ========== DADOS MOCK SIMPLES ==========
USUARIOS = [
    {"id": "user1", "nome": "João Silva", "idade": 25},
    {"id": "user2", "nome": "Maria Santos", "idade": 30},
    {"id": "user3", "nome": "Pedro Costa", "idade": 28}
]

MUSICAS = [
    {"id": "music1", "nome": "Bohemian Rhapsody", "artista": "Queen", "duracao": 355},
    {"id": "music2", "nome": "Imagine", "artista": "John Lennon", "duracao": 183},
    {"id": "music3", "nome": "Hotel California", "artista": "Eagles", "duracao": 391}
]

PLAYLISTS = [
    {"id": "playlist1", "nome": "Rock Clássico", "usuario": "user1", "musicas": ["music1", "music3"]},
    {"id": "playlist2", "nome": "Chill", "usuario": "user2", "musicas": ["music2"]},
    {"id": "playlist3", "nome": "Favoritas", "usuario": "user1", "musicas": ["music1", "music2"]}
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

# ========== SERVIÇO SOAP ==========
class StreamingService(ServiceBase):
    
    @rpc(_returns=Unicode)
    def listar_usuarios(ctx):
        """Lista usuários em JSON simples"""
        print("🟡 SOAP: listar_usuarios chamado")
        try:
            result = json.dumps(USUARIOS, ensure_ascii=False)
            print(f"🟡 SOAP: Retornando {len(USUARIOS)} usuários")
            return result
        except Exception as e:
            print(f"❌ Erro: {e}")
            raise
    
    @rpc(_returns=Unicode)
    def listar_musicas(ctx):
        """Lista músicas em JSON simples"""
        print("🟡 SOAP: listar_musicas chamado")
        try:
            result = json.dumps(MUSICAS, ensure_ascii=False)
            print(f"🟡 SOAP: Retornando {len(MUSICAS)} músicas")
            return result
        except Exception as e:
            print(f"❌ Erro: {e}")
            raise
    
    @rpc(_returns=Unicode)
    def listar_playlists(ctx):
        """Lista playlists em JSON simples"""
        print("🟡 SOAP: listar_playlists chamado")
        try:
            result = json.dumps(PLAYLISTS, ensure_ascii=False)
            print(f"🟡 SOAP: Retornando {len(PLAYLISTS)} playlists")
            return result
        except Exception as e:
            print(f"❌ Erro: {e}")
            raise
    
    @rpc(Unicode, _returns=Unicode)
    def buscar_usuario(ctx, user_id):
        """Busca usuário por ID"""
        print(f"🟡 SOAP: buscar_usuario chamado com ID: {user_id}")
        try:
            for user in USUARIOS:
                if user["id"] == user_id:
                    result = json.dumps(user, ensure_ascii=False)
                    print(f"🟡 SOAP: Usuário encontrado")
                    return result
            
            result = json.dumps({"erro": "Usuário não encontrado"}, ensure_ascii=False)
            print(f"🟡 SOAP: Usuário não encontrado")
            return result
        except Exception as e:
            print(f"❌ Erro: {e}")
            raise

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
            <p><strong>WSDL:</strong> <a href="?wsdl">Clique aqui</a></p>
            <p><strong>Interface:</strong> <a href="http://localhost:8080/soap/">Teste aqui</a></p>
            <h2>Operações:</h2>
            <ul>
                <li>listar_usuarios()</li>
                <li>listar_musicas()</li>
                <li>listar_playlists()</li>
                <li>buscar_usuario(user_id)</li>
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

def run_server():
    """Executa o servidor"""
    print("🟡 Iniciando servidor SOAP simples...")
    print("🟡 Porta: 8004")
    print("🟡 WSDL: http://localhost:8004/?wsdl")
    print("🟡 Interface: http://localhost:8080/soap/")
    print("=" * 50)
    
    server = make_server('0.0.0.0', 8004, handle_cors)
    
    try:
        print("✅ Servidor rodando! Ctrl+C para parar")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado")

if __name__ == '__main__':
    run_server()