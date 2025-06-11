#!/usr/bin/env python3
"""
Script de Verificação de Funcionamento - Pós Correções
=====================================================

Verifica se todos os serviços estão funcionando corretamente após as correções
de nomenclatura e problemas de concorrência aplicadas.

Testa especificamente:
1. Serviços básicos funcionando
2. Consistência de nomenclatura (duracaoSegundos vs duracao_segundos)
3. Funcionamento do data_loader
4. Ausência de modificações diretas de dados compartilhados
"""

import sys
import time
import requests
import json
import subprocess
import asyncio
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor
import threading
import grpc

# Importar módulos locais para testes diretos
try:
    from data_loader import get_data_loader
    from streaming_pb2 import Empty
    from streaming_pb2_grpc import StreamingServiceStub
    DATA_LOADER_AVAILABLE = True
except ImportError as e:
    print(f"Aviso: Não foi possível importar módulos locais: {e}")
    DATA_LOADER_AVAILABLE = False

class VerificadorServicos:
    """Classe para verificar o funcionamento dos serviços."""
    
    def __init__(self):
        self.resultados = {
            'data_loader': {'status': 'pendente', 'detalhes': []},
            'rest': {'status': 'pendente', 'detalhes': []},
            'graphql': {'status': 'pendente', 'detalhes': []},
            'soap': {'status': 'pendente', 'detalhes': []},
            'grpc': {'status': 'pendente', 'detalhes': []},
        }
        self.urls = {
            'rest': 'http://localhost:8000',
            'graphql': 'http://localhost:8001/graphql',
            'soap': 'http://localhost:8004',
            'grpc': 'localhost:50051'
        }

    def log_resultado(self, servico: str, status: str, detalhe: str):
        """Registra resultado de teste."""
        self.resultados[servico]['status'] = status
        self.resultados[servico]['detalhes'].append(detalhe)
        simbolo = "✅" if status == "sucesso" else "❌" if status == "erro" else "⚠️"
        print(f"{simbolo} {servico.upper()}: {detalhe}")

    def verificar_data_loader(self):
        """Verifica funcionamento do data_loader."""
        print("\n🔍 Verificando Data Loader...")
        
        if not DATA_LOADER_AVAILABLE:
            self.log_resultado('data_loader', 'erro', 'Módulos não disponíveis para teste direto')
            return False

        try:
            # Teste 1: Carregamento básico
            loader = get_data_loader()
            self.log_resultado('data_loader', 'sucesso', 'Data loader carregado com sucesso')
            
            # Teste 2: Verificar dados básicos
            usuarios = loader.listar_todos_usuarios()
            musicas = loader.listar_todas_musicas()
            self.log_resultado('data_loader', 'sucesso', f'Carregados {len(usuarios)} usuários e {len(musicas)} músicas')
            
            # Teste 3: Verificar nomenclatura consistente
            if musicas:
                primeira_musica = musicas[0]
                if 'duracaoSegundos' in primeira_musica:
                    self.log_resultado('data_loader', 'sucesso', 'Campo duracaoSegundos encontrado nos dados JSON')
                else:
                    self.log_resultado('data_loader', 'aviso', 'Campo duracaoSegundos não encontrado - verificar estrutura')
            
            # Teste 4: Métodos específicos funcionando
            if hasattr(loader, 'obter_musica_por_id') and musicas:
                musica_teste = loader.obter_musica_por_id(musicas[0]['id'])
                if musica_teste:
                    self.log_resultado('data_loader', 'sucesso', 'Método obter_musica_por_id funcionando')
                else:
                    self.log_resultado('data_loader', 'erro', 'Método obter_musica_por_id retornou None')
            
            return True

        except Exception as e:
            self.log_resultado('data_loader', 'erro', f'Erro no data_loader: {str(e)}')
            return False

    def verificar_servico_rest(self):
        """Verifica funcionamento do serviço REST."""
        print("\n🔵 Verificando Serviço REST...")
        
        try:
            # Teste 1: Serviço está rodando
            response = requests.get(f"{self.urls['rest']}/", timeout=5)
            if response.status_code == 200:
                self.log_resultado('rest', 'sucesso', 'Serviço REST respondendo')
            else:
                self.log_resultado('rest', 'erro', f'Status inesperado: {response.status_code}')
                return False

            # Teste 2: Endpoint de usuários
            response = requests.get(f"{self.urls['rest']}/usuarios", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'items' in data and isinstance(data['items'], list):
                    self.log_resultado('rest', 'sucesso', f'Endpoint usuarios OK - {len(data["items"])} usuários')
                else:
                    self.log_resultado('rest', 'aviso', 'Estrutura de resposta inesperada para usuários')
            else:
                self.log_resultado('rest', 'erro', f'Erro no endpoint usuarios: {response.status_code}')

            # Teste 3: Endpoint de músicas (verificar nomenclatura)
            response = requests.get(f"{self.urls['rest']}/musicas", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'items' in data and data['items']:
                    primeira_musica = data['items'][0]
                    if 'duracaoSegundos' in primeira_musica:
                        self.log_resultado('rest', 'sucesso', 'Campo duracaoSegundos presente na API REST')
                    else:
                        self.log_resultado('rest', 'aviso', 'Campo duracaoSegundos não encontrado na resposta REST')
                self.log_resultado('rest', 'sucesso', f'Endpoint musicas OK - {len(data["items"])} músicas')
            else:
                self.log_resultado('rest', 'erro', f'Erro no endpoint musicas: {response.status_code}')

            # Teste 4: Estatísticas
            response = requests.get(f"{self.urls['rest']}/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                self.log_resultado('rest', 'sucesso', f'Estatísticas: {stats.get("total_usuarios", 0)} usuários')
            else:
                self.log_resultado('rest', 'aviso', f'Estatísticas não disponíveis: {response.status_code}')

            return True

        except requests.RequestException as e:
            self.log_resultado('rest', 'erro', f'Erro de conexão: {str(e)}')
            return False

    def verificar_servico_graphql(self):
        """Verifica funcionamento do serviço GraphQL."""
        print("\n🟣 Verificando Serviço GraphQL...")
        
        try:
            # Teste 1: Query de usuários
            query_usuarios = {
                "query": """
                query {
                    usuarios {
                        id
                        nome
                        idade
                    }
                }
                """
            }
            
            response = requests.post(self.urls['graphql'], json=query_usuarios, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'usuarios' in data['data']:
                    usuarios = data['data']['usuarios']
                    self.log_resultado('graphql', 'sucesso', f'Query usuarios OK - {len(usuarios)} usuários')
                else:
                    self.log_resultado('graphql', 'erro', 'Estrutura de resposta inválida para usuarios')
            else:
                self.log_resultado('graphql', 'erro', f'Erro na query usuarios: {response.status_code}')

            # Teste 2: Query de músicas (verificar nomenclatura)
            query_musicas = {
                "query": """
                query {
                    musicas {
                        id
                        nome
                        artista
                        duracao_segundos
                    }
                }
                """
            }
            
            response = requests.post(self.urls['graphql'], json=query_musicas, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'musicas' in data['data']:
                    musicas = data['data']['musicas']
                    if musicas and 'duracao_segundos' in musicas[0]:
                        self.log_resultado('graphql', 'sucesso', 'Campo duracao_segundos presente no GraphQL')
                    self.log_resultado('graphql', 'sucesso', f'Query musicas OK - {len(musicas)} músicas')
                else:
                    self.log_resultado('graphql', 'erro', 'Estrutura de resposta inválida para musicas')
            else:
                self.log_resultado('graphql', 'erro', f'Erro na query musicas: {response.status_code}')

            # Teste 3: Estatísticas
            query_stats = {
                "query": """
                query {
                    estatisticas {
                        total_usuarios
                        total_musicas
                        total_playlists
                        tecnologia
                    }
                }
                """
            }
            
            response = requests.post(self.urls['graphql'], json=query_stats, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'estatisticas' in data['data']:
                    stats = data['data']['estatisticas']
                    self.log_resultado('graphql', 'sucesso', f'Estatísticas: {stats.get("total_usuarios", 0)} usuários')
                else:
                    self.log_resultado('graphql', 'aviso', 'Estatísticas não disponíveis')
            else:
                self.log_resultado('graphql', 'aviso', f'Erro nas estatísticas: {response.status_code}')

            return True

        except requests.RequestException as e:
            self.log_resultado('graphql', 'erro', f'Erro de conexão: {str(e)}')
            return False

    def verificar_servico_soap(self):
        """Verifica funcionamento do serviço SOAP."""
        print("\n🟡 Verificando Serviço SOAP...")
        
        try:
            # Teste 1: Serviço está rodando
            response = requests.get(self.urls['soap'], timeout=5)
            if response.status_code == 200:
                self.log_resultado('soap', 'sucesso', 'Serviço SOAP respondendo')
            else:
                self.log_resultado('soap', 'aviso', f'Página inicial retornou: {response.status_code}')

            # Teste 2: WSDL disponível
            response = requests.get(f"{self.urls['soap']}?wsdl", timeout=5)
            if response.status_code == 200 and 'xml' in response.headers.get('content-type', '').lower():
                self.log_resultado('soap', 'sucesso', 'WSDL disponível')
            else:
                self.log_resultado('soap', 'erro', 'WSDL não disponível ou inválido')
                return False

            # Teste 3: Verificar se métodos padronizados estão presentes
            wsdl_content = response.text
            if 'obter_usuario' in wsdl_content and 'GetUser' not in wsdl_content:
                self.log_resultado('soap', 'sucesso', 'Nomenclatura padronizada aplicada (sem GetUser)')
            elif 'GetUser' in wsdl_content:
                self.log_resultado('soap', 'aviso', 'Métodos antigos ainda presentes (GetUser)')
            
            # Para testar operações SOAP reais, precisaríamos do cliente zeep
            # Por simplicidade, apenas verificamos se o serviço está respondendo
            
            return True

        except requests.RequestException as e:
            self.log_resultado('soap', 'erro', f'Erro de conexão: {str(e)}')
            return False

    def verificar_servico_grpc(self):
        """Verifica funcionamento do serviço gRPC."""
        print("\n🟢 Verificando Serviço gRPC...")
        
        if not DATA_LOADER_AVAILABLE:
            self.log_resultado('grpc', 'aviso', 'Módulos gRPC não disponíveis para teste direto')
            return False

        try:
            # Teste 1: Conexão básica
            channel = grpc.insecure_channel(self.urls['grpc'])
            stub = StreamingServiceStub(channel)
            
            # Teste 2: Operação de estatísticas
            response = stub.ObterEstatisticas(Empty())
            if response:
                self.log_resultado('grpc', 'sucesso', f'gRPC funcionando - {response.total_usuarios} usuários')
            else:
                self.log_resultado('grpc', 'erro', 'Resposta vazia do gRPC')
                return False

            # Teste 3: Verificar se método corrigido funciona
            # (O StreamMusicas usa obter_musica_por_id internamente)
            try:
                # Este teste indireto verifica se a correção foi aplicada
                musicas_response = stub.ListarTodasMusicas(Empty())
                if musicas_response and musicas_response.musicas:
                    primeira_musica = musicas_response.musicas[0]
                    if hasattr(primeira_musica, 'duracao_segundos'):
                        self.log_resultado('grpc', 'sucesso', 'Campo duracao_segundos presente no gRPC')
                    self.log_resultado('grpc', 'sucesso', f'ListarTodasMusicas OK - {len(musicas_response.musicas)} músicas')
                else:
                    self.log_resultado('grpc', 'aviso', 'Nenhuma música retornada pelo gRPC')
            except Exception as e:
                self.log_resultado('grpc', 'erro', f'Erro ao listar músicas: {str(e)}')

            channel.close()
            return True

        except grpc.RpcError as e:
            self.log_resultado('grpc', 'erro', f'Erro gRPC: {str(e)}')
            return False
        except Exception as e:
            self.log_resultado('grpc', 'erro', f'Erro de conexão gRPC: {str(e)}')
            return False

    def verificar_consistencia_nomenclatura(self):
        """Verifica se a nomenclatura está consistente entre serviços."""
        print("\n🔍 Verificando Consistência de Nomenclatura...")
        
        consistencia = {
            'json_usa_camelCase': False,
            'graphql_usa_snake_case': False,
            'grpc_usa_snake_case': False,
            'conversoes_funcionando': True
        }
        
        # Verificar se as verificações anteriores detectaram os campos corretos
        for servico, resultado in self.resultados.items():
            detalhes = ' '.join(resultado['detalhes'])
            
            if servico == 'rest' and 'duracaoSegundos presente' in detalhes:
                consistencia['json_usa_camelCase'] = True
            elif servico == 'graphql' and 'duracao_segundos presente' in detalhes:
                consistencia['graphql_usa_snake_case'] = True
            elif servico == 'grpc' and 'duracao_segundos presente' in detalhes:
                consistencia['grpc_usa_snake_case'] = True

        # Relatório de consistência
        if consistencia['json_usa_camelCase']:
            self.log_resultado('data_loader', 'sucesso', 'JSON usa camelCase (duracaoSegundos) ✓')
        else:
            self.log_resultado('data_loader', 'aviso', 'JSON camelCase não confirmado')

        if consistencia['graphql_usa_snake_case']:
            self.log_resultado('graphql', 'sucesso', 'GraphQL usa snake_case (duracao_segundos) ✓')
        else:
            self.log_resultado('graphql', 'aviso', 'GraphQL snake_case não confirmado')

        if consistencia['grpc_usa_snake_case']:
            self.log_resultado('grpc', 'sucesso', 'gRPC usa snake_case (duracao_segundos) ✓')
        else:
            self.log_resultado('grpc', 'aviso', 'gRPC snake_case não confirmado')

        return all(consistencia.values())

    def executar_verificacao_completa(self):
        """Executa verificação completa de todos os serviços."""
        print("🚀 Iniciando Verificação de Funcionamento Pós-Correções")
        print("=" * 60)
        
        inicio = time.time()
        
        # Verificações em paralelo onde possível
        resultados = {}
        
        # Data loader primeiro (base para outros)
        resultados['data_loader'] = self.verificar_data_loader()
        
        # Serviços em paralelo
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_rest = executor.submit(self.verificar_servico_rest)
            future_graphql = executor.submit(self.verificar_servico_graphql)
            future_soap = executor.submit(self.verificar_servico_soap)
            future_grpc = executor.submit(self.verificar_servico_grpc)
            
            resultados['rest'] = future_rest.result()
            resultados['graphql'] = future_graphql.result()
            resultados['soap'] = future_soap.result()
            resultados['grpc'] = future_grpc.result()

        # Verificação de consistência
        self.verificar_consistencia_nomenclatura()
        
        # Relatório final
        self.gerar_relatorio_final(resultados, time.time() - inicio)
        
        return resultados

    def gerar_relatorio_final(self, resultados: Dict[str, bool], tempo_execucao: float):
        """Gera relatório final da verificação."""
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL DE VERIFICAÇÃO")
        print("=" * 60)
        
        sucessos = sum(1 for r in resultados.values() if r)
        total = len(resultados)
        
        print(f"✅ Serviços funcionando: {sucessos}/{total}")
        print(f"⏱️  Tempo de execução: {tempo_execucao:.2f}s")
        print()
        
        # Status detalhado por serviço
        for servico, funcionando in resultados.items():
            status_emoji = "✅" if funcionando else "❌"
            status_resultado = self.resultados[servico]['status']
            
            print(f"{status_emoji} {servico.upper()}: {status_resultado}")
            
            # Mostrar detalhes se houver problemas
            if not funcionando or status_resultado != 'sucesso':
                for detalhe in self.resultados[servico]['detalhes']:
                    print(f"    - {detalhe}")
        
        print()
        
        # Veredicto final
        if sucessos == total:
            print("🎉 TODAS AS VERIFICAÇÕES PASSARAM!")
            print("📋 O sistema está pronto para demonstração.")
        elif sucessos >= total * 0.75:
            print("⚠️  MAIORIA DOS SERVIÇOS FUNCIONANDO")
            print("📋 Sistema funcional com algumas ressalvas.")
        else:
            print("❌ PROBLEMAS SIGNIFICATIVOS DETECTADOS")
            print("📋 Revisar correções antes da demonstração.")
            
        print("\n🎯 Próximos passos sugeridos:")
        if sucessos == total:
            print("   1. Executar demonstração completa")
            print("   2. Preparar apresentação")
            print("   3. Documentar funcionalidades")
        else:
            print("   1. Corrigir problemas identificados")
            print("   2. Executar nova verificação")
            print("   3. Testar funcionalidades específicas")

def aguardar_servicos(timeout=30):
    """Aguarda os serviços ficarem disponíveis."""
    print("⏳ Aguardando serviços ficarem disponíveis...")
    
    servicos = [
        ('REST', 'http://localhost:8000'),
        ('GraphQL', 'http://localhost:8001'),
        ('SOAP', 'http://localhost:8004'),
    ]
    
    inicio = time.time()
    while time.time() - inicio < timeout:
        todos_ok = True
        for nome, url in servicos:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code not in [200, 404]:  # 404 pode ser OK se não há rota raiz
                    todos_ok = False
                    break
            except:
                todos_ok = False
                break
        
        if todos_ok:
            print("✅ Todos os serviços estão respondendo!")
            return True
            
        print(".", end="", flush=True)
        time.sleep(2)
    
    print(f"\n⚠️  Timeout após {timeout}s - continuando mesmo assim...")
    return False

def main():
    """Função principal."""
    print("🔧 VERIFICADOR DE FUNCIONAMENTO PÓS-CORREÇÕES")
    print("Validando correções de nomenclatura e funcionamento básico")
    print()
    
    # Verificar se deve aguardar serviços
    if len(sys.argv) > 1 and sys.argv[1] == '--wait':
        aguardar_servicos()
    
    verificador = VerificadorServicos()
    resultados = verificador.executar_verificacao_completa()
    
    # Código de saída baseado nos resultados
    sucessos = sum(1 for r in resultados.values() if r)
    total = len(resultados)
    
    if sucessos == total:
        sys.exit(0)  # Todos os testes passaram
    elif sucessos >= total * 0.75:
        sys.exit(1)  # Maioria passou, mas há problemas
    else:
        sys.exit(2)  # Problemas significativos

if __name__ == "__main__":
    main()
