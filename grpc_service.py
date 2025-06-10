"""gRPC Backend Stub
===================

Estrutura inicial para o servidor gRPC em Python. As definições de mensagens e
serviços devem ser descritas em ``streaming.proto`` e compiladas com
``grpcio-tools`` para gerar ``streaming_pb2.py`` e ``streaming_pb2_grpc.py``.
Este arquivo demonstra onde integrar o ``StreamingDataLoader`` com o código
proveniente do ``protoc``.
"""

from concurrent import futures
import grpc

from data_loader import get_data_loader

# import streaming_pb2
# import streaming_pb2_grpc


data_loader = get_data_loader()


# class StreamingService(streaming_pb2_grpc.StreamingServiceServicer):
#     """Implementação das operações definidas em streaming.proto."""
#
#     def __init__(self):
#         self.loader = data_loader
#
#     def ListarTodosUsuarios(self, request, context):
#         """Exemplo de método gRPC retornando todos os usuários."""
#         usuarios = self.loader.listar_todos_usuarios()
#         # TODO: montar e retornar ``streaming_pb2.UsuariosResponse``
#         raise NotImplementedError
#
#     # Demais métodos (ListarPlaylistsUsuario, ListarMusicasPlaylist, etc.)
#     # devem seguir a mesma lógica utilizando o ``data_loader``.


def servir(porta: int = 50051) -> None:
    """Inicializa o servidor gRPC.

    Esta função cria ``grpc.server`` e registra ``StreamingService``. Os detalhes
    da resposta são deixados como TODO para implementação futura.
    """
    # server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # streaming_pb2_grpc.add_StreamingServiceServicer_to_server(
    #     StreamingService(), server
    # )
    # server.add_insecure_port(f"[::]:{porta}")
    # server.start()
    # server.wait_for_termination()
    raise NotImplementedError("Implementar servidor gRPC utilizando grpcio")


if __name__ == "__main__":
    servir()
