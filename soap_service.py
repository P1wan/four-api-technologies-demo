"""SOAP Backend Stub
====================

Este arquivo contém a estrutura inicial de um serviço SOAP em Python. A
implementação real pode utilizar bibliotecas como ``spyne`` ou ``zeep`` para
expor o contrato WSDL e responder às operações SOAP. O objetivo deste stub é
servir de guia de implementação para o projeto do Trabalho 6.
"""

# Dependências sugeridas:
#   pip install spyne lxml
#
# O arquivo ``streaming.wsdl`` deve descrever as operações abaixo. As classes e
# métodos aqui definidos mostram como integrar o ``StreamingDataLoader`` para
# fornecer dados reais ao serviço.

from typing import List

# from spyne import Application, rpc, ServiceBase, Integer, Unicode, Array
# from spyne.protocol.soap import Soap11
# from spyne.server.wsgi import WsgiApplication

from data_loader import get_data_loader

# Instância única de dados usada por todas as operações
data_loader = get_data_loader()


# class StreamingService(ServiceBase):
#     """Serviço SOAP com operações do streaming de músicas."""
#
#     @rpc(_returns=Array(Usuario))
#     def listar_todos_usuarios(ctx):
#         """Retorna todos os usuários cadastrados."""
#         return data_loader.listar_todos_usuarios()
#
#     @rpc(Unicode, _returns=Array(Playlist))
#     def listar_playlists_usuario(ctx, id_usuario):
#         """Listar playlists de um usuário específico."""
#         return data_loader.listar_playlists_usuario(id_usuario)
#
#     # Demais operações seguem a mesma ideia: utilizar ``data_loader`` para
#     # recuperar músicas ou playlists e retornar os objetos SOAP correspondentes.


def executar_servidor(porta: int = 8002) -> None:
    """Executa o servidor SOAP.

    Esta função deve criar a aplicação ``spyne.Application`` e disponibilizar o
    WSDL em ``/soap?wsdl``. Ela é deixada como TODO para que os alunos completem
    conforme a biblioteca escolhida.
    """
    # TODO: configurar Application e WsgiApplication
    # app = Application([...])
    # wsgi_app = WsgiApplication(app)
    # from wsgiref.simple_server import make_server
    # server = make_server("0.0.0.0", porta, wsgi_app)
    # server.serve_forever()
    raise NotImplementedError("Implementar servidor SOAP utilizando spyne")


if __name__ == "__main__":
    executar_servidor()
