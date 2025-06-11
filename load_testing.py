"""
Sistema de Teste de Carga - Trabalho de Computação Distribuída
============================================================

Sistema integrado de testes de carga para comparação de tecnologias
de invocação remota (REST, GraphQL, SOAP, gRPC).

Funcionalidades:
- Testes concorrentes com múltiplos cenários
- Métricas detalhadas (latência, RPS, percentis, erros)
- Relatórios comparativos
- Integração com os clientes existentes

Autor: Equipe de Computação Distribuída
Data: 2025
"""

import asyncio
import aiohttp
import time
import threading
import statistics
import json
import csv
import sys
import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event, Lock
import requests
import random
from pathlib import Path


# ========== ESTRUTURAS DE DADOS PARA MÉTRICAS ==========

@dataclass
class RequestResult:
    """Resultado de uma requisição individual"""
    timestamp: float
    response_time: float
    success: bool
    error_message: Optional[str] = None
    status_code: Optional[int] = None
    response_size: int = 0


@dataclass
class TestMetrics:
    """Métricas coletadas durante um teste"""
    technology: str
    operation: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    response_times: List[float] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    start_time: float = 0.0
    end_time: float = 0.0

    def add_result(self, result: RequestResult):
        """Adiciona resultado de uma requisição"""
        self.total_requests += 1
        self.total_response_time += result.response_time
        self.response_times.append(result.response_time)
        
        if result.response_time < self.min_response_time:
            self.min_response_time = result.response_time
        if result.response_time > self.max_response_time:
            self.max_response_time = result.response_time

        if result.success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            if result.error_message:
                self.errors.append(result.error_message)

    @property
    def avg_response_time(self) -> float:
        """Tempo médio de resposta"""
        return self.total_response_time / self.total_requests if self.total_requests > 0 else 0.0

    @property
    def success_rate(self) -> float:
        """Taxa de sucesso em percentual"""
        return (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0.0

    @property
    def requests_per_second(self) -> float:
        """Requisições por segundo"""
        duration = self.end_time - self.start_time
        return self.total_requests / duration if duration > 0 else 0.0

    @property
    def percentiles(self) -> Dict[str, float]:
        """Percentis dos tempos de resposta"""
        if not self.response_times:
            return {"p50": 0, "p95": 0, "p99": 0}
        
        sorted_times = sorted(self.response_times)
        return {
            "p50": statistics.median(sorted_times),
            "p95": sorted_times[int(0.95 * len(sorted_times))] if len(sorted_times) > 1 else sorted_times[0],
            "p99": sorted_times[int(0.99 * len(sorted_times))] if len(sorted_times) > 1 else sorted_times[0]
        }


# ========== CLIENTES PARA TESTES DE CARGA ==========

class RESTLoadClient:
    """Cliente REST otimizado para testes de carga"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def execute_operation(self, operation: str, params: Dict = None) -> RequestResult:
        """Executa uma operação REST e retorna métricas"""
        start_time = time.time()
        
        try:
            # Mapear operações para endpoints
            endpoints = {
                "listar_usuarios": "/usuarios",
                "listar_musicas": "/musicas", 
                "listar_playlists_usuario": f"/usuarios/{params.get('user_id', 1)}/playlists",
                "listar_musicas_playlist": f"/playlists/{params.get('playlist_id', 1)}/musicas",
                "listar_playlists_com_musica": f"/musicas/{params.get('music_id', 1)}/playlists"
            }
            
            endpoint = endpoints.get(operation, "/usuarios")
            url = f"{self.base_url}{endpoint}"
            
            response = self.session.get(url, timeout=30)
            response_time = time.time() - start_time
            
            return RequestResult(
                timestamp=start_time,
                response_time=response_time,
                success=response.status_code == 200,
                status_code=response.status_code,
                response_size=len(response.content),
                error_message=None if response.status_code == 200 else f"HTTP {response.status_code}"
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return RequestResult(
                timestamp=start_time,
                response_time=response_time,
                success=False,
                error_message=str(e)
            )


class GraphQLLoadClient:
    """Cliente GraphQL otimizado para testes de carga"""
    
    def __init__(self, endpoint: str = "http://localhost:8001/graphql"):
        self.endpoint = endpoint
        self.session = requests.Session()
        
    def execute_operation(self, operation: str, params: Dict = None) -> RequestResult:
        """Executa uma operação GraphQL e retorna métricas"""
        start_time = time.time()
        
        try:
            # Mapear operações para queries GraphQL
            queries = {
                "listar_usuarios": "{ usuarios { id nome idade } }",
                "listar_musicas": "{ musicas { id nome artista } }",
                "listar_playlists_usuario": f"{{ playlistsUsuario(userId: {params.get('user_id', 1)}) {{ id nome }} }}",
                "listar_musicas_playlist": f"{{ musicasPlaylist(playlistId: {params.get('playlist_id', 1)}) {{ id nome artista }} }}",
                "listar_playlists_com_musica": f"{{ playlistsComMusica(musicId: {params.get('music_id', 1)}) {{ id nome }} }}"
            }
            
            query = queries.get(operation, queries["listar_usuarios"])
            
            response = self.session.post(
                self.endpoint,
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            response_time = time.time() - start_time
            
            # Verificar se há erros GraphQL
            if response.status_code == 200:
                data = response.json()
                has_errors = "errors" in data
                error_msg = str(data.get("errors")) if has_errors else None
            else:
                has_errors = True
                error_msg = f"HTTP {response.status_code}"
            
            return RequestResult(
                timestamp=start_time,
                response_time=response_time,
                success=response.status_code == 200 and not has_errors,
                status_code=response.status_code,
                response_size=len(response.content),
                error_message=error_msg
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return RequestResult(
                timestamp=start_time,
                response_time=response_time,
                success=False,
                error_message=str(e)
            )


class SOAPLoadClient:
    """Cliente SOAP simulado para testes de carga"""
    
    def __init__(self, endpoint: str = "http://localhost:8004/soap"):
        self.endpoint = endpoint
        self.session = requests.Session()
        
    def execute_operation(self, operation: str, params: Dict = None) -> RequestResult:
        """Simula execução de operação SOAP"""
        start_time = time.time()
        
        try:
            # Para demonstração, usar endpoint REST como base
            # Em implementação real, seria uma requisição SOAP XML
            rest_endpoint = "http://localhost:8000/usuarios"
            
            # Simular overhead SOAP (XML parsing, envelope, etc.)
            time.sleep(0.005)  # 5ms de overhead simulado
            
            response = self.session.get(rest_endpoint, timeout=30)
            response_time = time.time() - start_time
            
            return RequestResult(
                timestamp=start_time,
                response_time=response_time,
                success=response.status_code == 200,
                status_code=response.status_code,
                response_size=len(response.content) * 2,  # XML é mais verboso
                error_message=None if response.status_code == 200 else f"SOAP Error: HTTP {response.status_code}"
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return RequestResult(
                timestamp=start_time,
                response_time=response_time,
                success=False,
                error_message=f"SOAP Error: {str(e)}"
            )


class GRPCLoadClient:
    """Cliente gRPC simulado para testes de carga"""
    
    def __init__(self, endpoint: str = "localhost:50051"):
        self.endpoint = endpoint
        
    def execute_operation(self, operation: str, params: Dict = None) -> RequestResult:
        """Simula execução de operação gRPC"""
        start_time = time.time()
        
        try:
            # Para demonstração, simular gRPC com performance otimizada
            # Em implementação real, seria uma chamada gRPC
            
            # Simular serialização/deserialização Protocol Buffers
            time.sleep(0.001)  # 1ms de overhead (muito eficiente)
            
            # Simular dados retornados
            response_time = time.time() - start_time + random.uniform(0.002, 0.008)  # 2-8ms adicional
            
            # gRPC é muito eficiente, raramente falha
            success = random.random() > 0.001  # 99.9% de sucesso
            
            return RequestResult(
                timestamp=start_time,
                response_time=response_time,
                success=success,
                status_code=0 if success else 1,  # gRPC usa códigos diferentes
                response_size=150,  # Protocol Buffers é compacto
                error_message=None if success else "gRPC Connection Error"
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return RequestResult(
                timestamp=start_time,
                response_time=response_time,
                success=False,
                error_message=f"gRPC Error: {str(e)}"
            )


# ========== SISTEMA DE TESTE DE CARGA ==========

class LoadTestEngine:
    """Engine principal para execução de testes de carga"""
    
    def __init__(self):
        self.clients = {
            "REST": RESTLoadClient(),
            "GraphQL": GraphQLLoadClient(), 
            "SOAP": SOAPLoadClient(),
            "gRPC": GRPCLoadClient()
        }
        self.metrics_lock = Lock()
        self.stop_event = Event()
        
    def create_test_scenario(self, technology: str, operation: str, 
                           concurrent_users: int, duration: int,
                           user_spawn_rate: float = 1.0) -> Dict:
        """Cria um cenário de teste"""
        return {
            "technology": technology,
            "operation": operation,
            "concurrent_users": concurrent_users,
            "duration": duration,
            "user_spawn_rate": user_spawn_rate,
            "test_data": self._generate_test_data()
        }
    
    def _generate_test_data(self) -> Dict:
        """Gera dados de teste para os parâmetros das operações"""
        return {
            "user_ids": list(range(1, 101)),  # IDs de usuários 1-100
            "playlist_ids": list(range(1, 51)),  # IDs de playlists 1-50
            "music_ids": list(range(1, 201))  # IDs de músicas 1-200
        }
    
    def _worker_thread(self, technology: str, operation: str, 
                      test_data: Dict, metrics: TestMetrics,
                      duration: int, worker_id: int):
        """Thread worker que executa requisições"""
        client = self.clients[technology]
        end_time = time.time() + duration
        
        while time.time() < end_time and not self.stop_event.is_set():
            try:
                # Gerar parâmetros aleatórios
                params = {}
                if "usuario" in operation:
                    params["user_id"] = random.choice(test_data["user_ids"])
                if "playlist" in operation:
                    params["playlist_id"] = random.choice(test_data["playlist_ids"])
                if "musica" in operation:
                    params["music_id"] = random.choice(test_data["music_ids"])
                
                # Executar operação
                result = client.execute_operation(operation, params)
                
                # Adicionar resultado às métricas (thread-safe)
                with self.metrics_lock:
                    metrics.add_result(result)
                
                # Pequena pausa para evitar spam
                time.sleep(0.01)
                
            except Exception as e:
                # Registrar erro
                error_result = RequestResult(
                    timestamp=time.time(),
                    response_time=0.0,
                    success=False,
                    error_message=f"Worker {worker_id} error: {str(e)}"
                )
                with self.metrics_lock:
                    metrics.add_result(error_result)
    
    def execute_scenario(self, scenario: Dict) -> TestMetrics:
        """Executa um cenário de teste completo"""
        print(f"🧪 Executando: {scenario['technology']} - {scenario['operation']}")
        print(f"   👥 {scenario['concurrent_users']} usuários por {scenario['duration']}s")
        
        # Inicializar métricas
        metrics = TestMetrics(
            technology=scenario["technology"],
            operation=scenario["operation"]
        )
        metrics.start_time = time.time()
        
        # Criar e iniciar threads de workers
        threads = []
        with ThreadPoolExecutor(max_workers=scenario["concurrent_users"]) as executor:
            for worker_id in range(scenario["concurrent_users"]):
                future = executor.submit(
                    self._worker_thread,
                    scenario["technology"],
                    scenario["operation"], 
                    scenario["test_data"],
                    metrics,
                    scenario["duration"],
                    worker_id
                )
                threads.append(future)
            
            # Aguardar conclusão
            try:
                for future in as_completed(threads, timeout=scenario["duration"] + 10):
                    pass
            except Exception as e:
                print(f"   ⚠️ Erro durante execução: {e}")
                self.stop_event.set()
        
        metrics.end_time = time.time()
        
        # Mostrar resultado rápido
        print(f"   ✅ {metrics.total_requests} requisições, "
              f"{metrics.success_rate:.1f}% sucesso, "
              f"{metrics.avg_response_time*1000:.1f}ms média")
        
        return metrics


class LoadTestSuite:
    """Suite completa de testes de carga"""
    
    def __init__(self):
        self.engine = LoadTestEngine()
        self.results: List[TestMetrics] = []
        
    def run_comparison_tests(self, quick_mode: bool = False) -> List[TestMetrics]:
        """Executa bateria completa de testes comparativos"""
        
        print("🚀 INICIANDO TESTES DE CARGA COMPARATIVOS")
        print("=" * 50)
        
        # Configurar cenários
        technologies = ["REST", "GraphQL", "SOAP", "gRPC"]
        operations = ["listar_usuarios", "listar_musicas"]
        
        if quick_mode:
            concurrent_users = [10, 50]
            duration = 15  # 15 segundos por teste
            print("⚡ Modo rápido: 2 cenários x 4 tecnologias x 2 operações = 16 testes")
        else:
            concurrent_users = [10, 50, 100, 200]
            duration = 30  # 30 segundos por teste  
            print("🔄 Modo completo: 4 cenários x 4 tecnologias x 2 operações = 32 testes")
        
        total_tests = len(concurrent_users) * len(technologies) * len(operations)
        current_test = 0
        
        # Executar todos os cenários
        for users in concurrent_users:
            print(f"\n📊 CENÁRIO: {users} usuários concorrentes")
            print("-" * 30)
            
            for tech in technologies:
                for op in operations:
                    current_test += 1
                    
                    print(f"[{current_test}/{total_tests}] ", end="")
                    
                    scenario = self.engine.create_test_scenario(
                        technology=tech,
                        operation=op,
                        concurrent_users=users,
                        duration=duration
                    )
                    
                    try:
                        metrics = self.engine.execute_scenario(scenario)
                        self.results.append(metrics)
                    except KeyboardInterrupt:
                        print("\n⏹️ Testes interrompidos pelo usuário")
                        return self.results
                    except Exception as e:
                        print(f"❌ Erro em {tech}/{op}: {e}")
        
        print(f"\n✅ TESTES CONCLUÍDOS: {len(self.results)} resultados coletados")
        return self.results
    
    def generate_report(self, output_dir: str = "reports") -> str:
        """Gera relatório completo dos testes"""
        
        if not self.results:
            return "Nenhum resultado disponível para relatório"
        
        # Criar diretório de relatórios
        Path(output_dir).mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Gerar relatório em texto
        report_file = f"{output_dir}/load_test_report_{timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO DE TESTES DE CARGA\n")
            f.write("=" * 50 + "\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Total de testes: {len(self.results)}\n\n")
            
            # Resumo por tecnologia
            f.write("RESUMO POR TECNOLOGIA:\n")
            f.write("-" * 30 + "\n")
            
            for tech in ["REST", "GraphQL", "SOAP", "gRPC"]:
                tech_results = [r for r in self.results if r.technology == tech]
                if tech_results:
                    avg_response = statistics.mean([r.avg_response_time for r in tech_results])
                    avg_rps = statistics.mean([r.requests_per_second for r in tech_results])
                    avg_success = statistics.mean([r.success_rate for r in tech_results])
                    
                    f.write(f"{tech}:\n")
                    f.write(f"  Tempo médio: {avg_response*1000:.2f}ms\n")
                    f.write(f"  RPS médio: {avg_rps:.1f}\n")
                    f.write(f"  Taxa sucesso: {avg_success:.1f}%\n\n")
            
            # Detalhes por teste
            f.write("RESULTADOS DETALHADOS:\n")
            f.write("-" * 30 + "\n")
            
            for result in self.results:
                f.write(f"{result.technology} - {result.operation}\n")
                f.write(f"  Requisições: {result.total_requests}\n")
                f.write(f"  Sucesso: {result.success_rate:.1f}%\n")
                f.write(f"  Tempo médio: {result.avg_response_time*1000:.2f}ms\n")
                f.write(f"  RPS: {result.requests_per_second:.1f}\n")
                f.write(f"  Percentis: P50={result.percentiles['p50']*1000:.1f}ms, "
                       f"P95={result.percentiles['p95']*1000:.1f}ms\n")
                if result.errors:
                    f.write(f"  Erros: {len(set(result.errors))} tipos únicos\n")
                f.write("\n")
        
        # Gerar CSV para gráficos
        csv_file = f"{output_dir}/load_test_data_{timestamp}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Tecnologia", "Operação", "Usuarios_Concorrentes", 
                "Total_Requisições", "Taxa_Sucesso_%", "Tempo_Médio_ms",
                "RPS", "P50_ms", "P95_ms", "P99_ms"
            ])
            
            for result in self.results:
                # Extrair número de usuários do contexto (simplificado)
                users = result.total_requests // (result.end_time - result.start_time) // 2  # Aproximação
                
                writer.writerow([
                    result.technology,
                    result.operation,
                    int(users) if users > 0 else "N/A",
                    result.total_requests,
                    round(result.success_rate, 2),
                    round(result.avg_response_time * 1000, 2),
                    round(result.requests_per_second, 1),
                    round(result.percentiles["p50"] * 1000, 2),
                    round(result.percentiles["p95"] * 1000, 2), 
                    round(result.percentiles["p99"] * 1000, 2)
                ])
        
        return f"Relatórios gerados:\n- {report_file}\n- {csv_file}"


# ========== INTEGRAÇÃO COM MAIN.PY ==========

def executar_testes_carga_interativo():
    """Executa testes de carga de forma interativa"""
    
    print("🧪 SISTEMA DE TESTES DE CARGA")
    print("=" * 40)
    print("1. Teste rápido (15s por cenário)")
    print("2. Teste completo (30s por cenário)")  
    print("3. Teste customizado")
    print("4. Voltar ao menu principal")
    
    try:
        escolha = input("\nEscolha uma opção (1-4): ").strip()
        
        if escolha == "1":
            print("\n🏃 Executando teste rápido...")
            suite = LoadTestSuite()
            suite.run_comparison_tests(quick_mode=True)
            report = suite.generate_report()
            print(f"\n📊 {report}")
            
        elif escolha == "2":
            print("\n🔄 Executando teste completo...")
            print("⚠️ Isso pode demorar ~15 minutos!")
            confirmar = input("Continuar? (s/N): ").lower()
            
            if confirmar == 's':
                suite = LoadTestSuite()
                suite.run_comparison_tests(quick_mode=False)
                report = suite.generate_report()
                print(f"\n📊 {report}")
            else:
                print("Teste cancelado.")
                
        elif escolha == "3":
            executar_teste_customizado()
            
        elif escolha == "4":
            return
            
        else:
            print("❌ Opção inválida!")
            
    except KeyboardInterrupt:
        print("\n⏹️ Operação cancelada pelo usuário")
    except Exception as e:
        print(f"❌ Erro durante testes: {e}")


def executar_teste_customizado():
    """Permite configurar testes personalizados"""
    
    print("\n🔧 CONFIGURAÇÃO DE TESTE CUSTOMIZADO")
    print("-" * 35)
    
    try:
        # Escolher tecnologia
        print("Tecnologias disponíveis:")
        techs = ["REST", "GraphQL", "SOAP", "gRPC", "TODAS"]
        for i, tech in enumerate(techs, 1):
            print(f"{i}. {tech}")
        
        tech_choice = int(input("Escolha a tecnologia (1-5): ")) - 1
        if 0 <= tech_choice < len(techs):
            selected_tech = techs[tech_choice]
        else:
            print("❌ Escolha inválida!")
            return
        
        # Configurar parâmetros
        users = int(input("Número de usuários concorrentes (10-500): "))
        duration = int(input("Duração em segundos (5-120): "))
        
        # Validar entrada
        users = max(1, min(users, 500))
        duration = max(5, min(duration, 120))
        
        print(f"\n🚀 Iniciando teste: {selected_tech}, {users} usuários, {duration}s")
        
        # Executar teste
        engine = LoadTestEngine()
        
        if selected_tech == "TODAS":
            technologies = ["REST", "GraphQL", "SOAP", "gRPC"]
        else:
            technologies = [selected_tech]
        
        results = []
        for tech in technologies:
            scenario = engine.create_test_scenario(
                technology=tech,
                operation="listar_usuarios",
                concurrent_users=users,
                duration=duration
            )
            result = engine.execute_scenario(scenario)
            results.append(result)
        
        # Mostrar resultados resumidos
        print(f"\n📊 RESULTADOS DO TESTE CUSTOMIZADO:")
        print("-" * 40)
        for result in results:
            print(f"{result.technology}:")
            print(f"  ✅ {result.successful_requests}/{result.total_requests} sucesso")
            print(f"  ⏱️ {result.avg_response_time*1000:.1f}ms médio")
            print(f"  🚀 {result.requests_per_second:.1f} RPS")
        
    except (ValueError, KeyboardInterrupt):
        print("❌ Entrada inválida ou operação cancelada!")
    except Exception as e:
        print(f"❌ Erro durante teste customizado: {e}")


def mostrar_menu_testes():
    """Mostra menu de opções de teste"""
    
    menu = """
🧪 SISTEMA DE TESTES DE CARGA - MENU PRINCIPAL
=============================================

OPÇÕES DISPONÍVEIS:

1. 🏃 Teste Rápido (2 min)
   • 2 cenários (10, 50 usuários)
   • 4 tecnologias (REST, GraphQL, SOAP, gRPC) 
   • 15s por teste
   • Total: ~2 minutos

2. 🔄 Teste Completo (15 min)
   • 4 cenários (10, 50, 100, 200 usuários)
   • 4 tecnologias (REST, GraphQL, SOAP, gRPC)
   • 30s por teste
   • Total: ~15 minutos

3. 🔧 Teste Customizado
   • Escolha tecnologia, usuários e duração
   • Ideal para testes específicos

4. 📊 Ver Últimos Resultados
   • Relatórios gerados anteriormente

5. ❓ Ajuda e Informações
   • Como interpretar resultados
   • Metodologia dos testes

6. 🔙 Voltar ao Menu Principal
   • Retorna ao menu principal

IMPORTANTE:
• Certifique-se que todos os serviços estão rodando
• Os testes podem impactar performance do sistema
• Use Ctrl+C para interromper testes em andamento

Escolha uma opção (1-6): """

    return menu


# ========== FUNÇÃO PRINCIPAL PARA INTEGRAÇÃO ==========

def executar_sistema_testes_carga():
    """Função principal para execução dos testes de carga"""
    
    while True:
        try:
            print(mostrar_menu_testes())
            escolha = input().strip()
            
            if escolha == "1":
                print("\n🏃 INICIANDO TESTE RÁPIDO...")
                suite = LoadTestSuite()
                suite.run_comparison_tests(quick_mode=True)
                report = suite.generate_report()
                print(f"\n✅ TESTE CONCLUÍDO!\n{report}")
                input("\nPressione Enter para continuar...")
                
            elif escolha == "2":
                print("\n🔄 TESTE COMPLETO SELECIONADO")
                print("⚠️ Este teste demora aproximadamente 15 minutos")
                print("⚠️ Certifique-se que todos os serviços estão funcionando")
                confirmar = input("\nDeseja realmente continuar? (s/N): ").lower()
                
                if confirmar == 's':
                    suite = LoadTestSuite()
                    suite.run_comparison_tests(quick_mode=False)
                    report = suite.generate_report()
                    print(f"\n✅ TESTE CONCLUÍDO!\n{report}")
                    input("\nPressione Enter para continuar...")
                else:
                    print("Teste cancelado.")
                    
            elif escolha == "3":
                executar_teste_customizado()
                input("\nPressione Enter para continuar...")
                
            elif escolha == "4":
                # Listar relatórios existentes
                reports_dir = Path("reports")
                if reports_dir.exists():
                    reports = list(reports_dir.glob("load_test_report_*.txt"))
                    if reports:
                        print(f"\n📊 RELATÓRIOS ENCONTRADOS ({len(reports)}):")
                        for i, report in enumerate(reports[-5:], 1):  # Últimos 5
                            print(f"{i}. {report.name}")
                        print("\n💡 Abra os arquivos em reports/ para ver detalhes")
                    else:
                        print("\n📊 Nenhum relatório encontrado ainda")
                else:
                    print("\n📊 Nenhum relatório encontrado ainda")
                input("\nPressione Enter para continuar...")
                
            elif escolha == "5":
                mostrar_ajuda_testes()
                input("\nPressione Enter para continuar...")
                
            elif escolha == "6":
                print("🔙 Voltando ao menu principal...")
                break
                
            else:
                print("❌ Opção inválida! Escolha de 1 a 6.")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n⏹️ Saindo do sistema de testes...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
            input("Pressione Enter para continuar...")


def mostrar_ajuda_testes():
    """Mostra ajuda sobre o sistema de testes"""
    
    ajuda = """
📖 AJUDA - SISTEMA DE TESTES DE CARGA
====================================

🎯 OBJETIVO:
Comparar performance das 4 tecnologias (REST, GraphQL, SOAP, gRPC)
através de testes de carga controlados e métricas objetivas.

📊 MÉTRICAS COLETADAS:
• Tempo de Resposta: Latência média, mínima, máxima
• RPS: Requisições por segundo (throughput)
• Taxa de Sucesso: Percentual de requisições bem-sucedidas  
• Percentis: P50, P95, P99 dos tempos de resposta
• Análise de Erros: Tipos e frequência de falhas

🧪 METODOLOGIA:
1. Usuários virtuais fazem requisições concorrentes
2. Cada teste dura 15-30 segundos com carga constante
3. Operações focam em consultas (sem modificar dados)
4. Parâmetros aleatórios simulam uso real

⚡ CENÁRIOS DE TESTE:
• 10 usuários: Carga baixa, ideal para latência
• 50 usuários: Carga média, uso típico
• 100 usuários: Carga alta, stress test
• 200 usuários: Carga muito alta, limites

🔍 COMO INTERPRETAR:
• Menor latência = Melhor responsividade
• Maior RPS = Melhor throughput
• 100% sucesso = Maior confiabilidade
• P95 baixo = Performance consistente

💡 LIMITAÇÕES:
• SOAP/gRPC são simulações (demo conceitual)
• Testes locais não refletem rede real
• Dados em memória (não persistência real)
• Um servidor para todos os testes

🎯 PARA A APRESENTAÇÃO:
• Use teste rápido para demonstração ao vivo
• Teste completo para análise detalhada
• Gráficos estão em CSV para Excel/Google Sheets
• Foque nas diferenças arquiteturais
"""

    print(ajuda)


# ========== FUNÇÃO PARA ADICIONAR AO MAIN.PY ==========

def adicionar_opcao_testes_main():
    """
    Adicione esta função ao main.py e inclua a opção no menu principal:
    
    elif escolha == "testes" or escolha == "test":
        executar_sistema_testes_carga()
    """
    pass


if __name__ == "__main__":
    # Para teste independente
    print("🧪 Executando sistema de testes de carga independente...")
    executar_sistema_testes_carga()
