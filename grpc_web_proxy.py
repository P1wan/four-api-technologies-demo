"""
gRPC-Web Proxy Server
====================

Este servidor atua como um proxy entre clientes web e o servidor gRPC,
permitindo que navegadores se comuniquem com serviços gRPC através de HTTP/1.1.

Autor: Equipe de Computação Distribuída
Data: 2025
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import grpc
import json
from typing import Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="gRPC-Web Proxy",
    description="Proxy para comunicação entre navegadores e serviços gRPC",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar executor para chamadas gRPC
executor = ThreadPoolExecutor(max_workers=10)

# Configuração do servidor gRPC
GRPC_SERVER = "localhost:50051"

async def call_grpc_method(method_name: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Chama um método gRPC e retorna a resposta"""
    try:
        # Criar canal gRPC
        channel = grpc.aio.insecure_channel(GRPC_SERVER)
        
        # Importar stubs gerados
        from streaming_pb2 import (
            ListarUsuariosRequest,
            ListarMusicasRequest,
            ListarPlaylistsUsuarioRequest,
            ListarMusicasPlaylistRequest,
            ListarPlaylistsComMusicaRequest,
            EstatisticasRequest
        )
        from streaming_pb2_grpc import StreamingServiceStub

        # Criar stub
        stub = StreamingServiceStub(channel)

        # Mapear métodos
        method_map = {
            "ListarUsuarios": (stub.ListarUsuarios, ListarUsuariosRequest),
            "ListarMusicas": (stub.ListarMusicas, ListarMusicasRequest),
            "ListarPlaylistsUsuario": (stub.ListarPlaylistsUsuario, ListarPlaylistsUsuarioRequest),
            "ListarMusicasPlaylist": (stub.ListarMusicasPlaylist, ListarMusicasPlaylistRequest),
            "ListarPlaylistsComMusica": (stub.ListarPlaylistsComMusica, ListarPlaylistsComMusicaRequest),
            "ObterEstatisticas": (stub.ObterEstatisticas, EstatisticasRequest)
        }

        if method_name not in method_map:
            raise ValueError(f"Método {method_name} não encontrado")

        # Obter método e classe de request
        method, request_class = method_map[method_name]

        # Criar request
        request = request_class(**request_data)

        # Chamar método
        response = await method(request)

        # Converter resposta para dict
        return json.loads(response.SerializeToJson())

    except Exception as e:
        logger.error(f"Erro ao chamar método gRPC: {str(e)}")
        raise

@app.post("/grpc/{method_name}")
async def handle_grpc_request(method_name: str, request: Request):
    """Endpoint para chamadas gRPC via HTTP"""
    try:
        # Ler dados da requisição
        request_data = await request.json()

        # Chamar método gRPC
        response = await call_grpc_method(method_name, request_data)

        return response

    except Exception as e:
        logger.error(f"Erro ao processar requisição: {str(e)}")
        return {"error": str(e)}, 500

@app.get("/health")
async def health_check():
    """Endpoint para verificar saúde do proxy"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003) 