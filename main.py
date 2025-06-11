"""
Script Principal Atualizado - Trabalho de Computação Distribuída
===============================================================

Executa todos os serviços (REST, GraphQL, SOAP/gRPC) simultaneamente
e inclui sistema completo de testes de carga para demonstração.

NOVA FUNCIONALIDADE: Sistema de Testes de Carga Integrado
- Testes comparativos entre as 4 tecnologias
- Métricas detalhadas (latência, RPS, percentis)
- Relatórios automáticos em TXT e CSV
- Interface interativa para demonstração

Autor: Equipe de Computação Distribuída
Data: 2025
"""

import asyncio
import multiprocessing
import time
import sys
import subprocess
import signal
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from threading import Thread
import http.server
import socketserver
import webbrowser
from pathlib import Path

# ========== IMPORTAR SISTEMA DE TESTES DE CARGA ==========
# (Assumindo que o código do sistema de testes está em load_testing.py)
try:
    from load_testing import (
        LoadTestSuite, 
        LoadTestEngine,
        executar_sistema_testes_carga,
        mostrar_ajuda_testes
    )
    LOAD_TESTING_AVAILABLE = True
except ImportError:
    LOAD_TESTING_AVAILABLE = False
    print("⚠️ Sistema de testes de carga não encontrado. Funcionalidade limitada.")


def verificar_dependencias():
    """Verifica e instala dependências necessárias"""
    dependencias = [
        ("fastapi", "fastapi==0.104.1"),
        ("uvicorn", "uvicorn[standard]==0.24.0"),
        ("strawberry", "strawberry-graphql[fastapi]==0.213.0"),
        ("grpcio", "grpcio==1.59.0"),
        ("grpcio-tools", "grpcio-tools==1.59.0"),
        ("grpcio-reflection", "grpcio-reflection==1.59.0"),
        ("spyne", "spyne==2.14.0"),
        ("lxml", "lxml==4.9.3"),
        ("requests", "requests>=2.25.0"),  # Para testes de carga
        ("aiohttp", "aiohttp>=3.8.0")  # Para testes async
    ]

    dependencias_faltando = []

    for nome, pacote in dependencias:
        try:
            __import__(nome)
        except ImportError:
            dependencias_faltando.append(pacote)

    if dependencias_faltando:
        print("📦 Instalando dependências faltando...")
        for pacote in dependencias_faltando:
            print(f"   Instalando {pacote}...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pacote])
        print("✅ Todas as dependências foram instaladas!")

    return True


def executar_servico_rest():
    """Executa o serviço REST"""
    import uvicorn
    from rest_service import app

    print("🔵 REST: Iniciando na porta 8000...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="error",
        access_log=False)


def executar_servico_graphql():
    """Executa o serviço GraphQL"""
    import uvicorn
    from graphql_service import app

    print("🟣 GraphQL: Iniciando na porta 8001...")
    uvicorn.run(app,
                host="0.0.0.0",
                port=8001,
                log_level="error",
                access_log=False)


def executar_servico_soap():
    """Executa o serviço SOAP"""
    from soap_service import executar_servidor

    print("🟡 SOAP: Iniciando na porta 8004...")
    executar_servidor(host="0.0.0.0", port=8004)


def executar_servico_grpc():
    """Executa o serviço gRPC"""
    from grpc_service import servir

    print("🟢 gRPC: Iniciando na porta 50051...")
    servir(porta=50051)


def executar_servico_grpc_web():
    """Executa o proxy gRPC-Web"""
    import uvicorn
    from grpc_web_proxy import app

    print("🟢 gRPC-Web: Iniciando proxy na porta 8003...")
    uvicorn.run(app,
                host="0.0.0.0",
                port=8003,
                log_level="error",
                access_log=False)


def executar_servidor_web():
    """Executa servidor web para interfaces de cliente"""
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(Path.cwd()), **kwargs)

    with socketserver.TCPServer(("", 8080), Handler) as httpd:
        print("🌐 Servidor Web: Iniciando na porta 8080...")
        print("   Acesse: http://localhost:8080")
        httpd.serve_forever()


def mostrar_banner():
    """Mostra o banner inicial com informações"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║               TRABALHO DE COMPUTAÇÃO DISTRIBUÍDA               ║
║        Comparação de Tecnologias de Invocação Remota          ║
╚══════════════════════════════════════════════════════════════╝

🎯 OBJETIVO: Demonstrar 4 tecnologias funcionando simultaneamente

📋 TECNOLOGIAS IMPLEMENTADAS:
├── 🔵 REST      → FastAPI + Swagger UI
├── 🟣 GraphQL   → Strawberry + GraphiQL  
├── 🟡 SOAP      → Spyne + WSDL
└── 🟢 gRPC      → Demonstração com Protocol Buffers

🧪 NOVO: SISTEMA DE TESTES DE CARGA INTEGRADO
├── ⚡ Testes rápidos (2 minutos)
├── 🔄 Testes completos (15 minutos)
├── 📊 Métricas detalhadas (RPS, latência, percentis)
└── 📈 Relatórios comparativos automáticos

🌐 URLS DE ACESSO (aguarde inicialização):
┌─────────────┬──────────────────────────────────┬─────────────────┐
│ Tecnologia  │ URL Principal                    │ Documentação    │
├─────────────┼──────────────────────────────────┼─────────────────┤
│ REST        │ http://localhost:8000            │ /docs           │
│ GraphQL     │ http://localhost:8001            │ /graphql        │
│ SOAP        │ http://localhost:8004            │ /soap?wsdl      │
│ gRPC        │ http://localhost:50051           │ -               │
│ gRPC-Web    │ http://localhost:8003            │ -               │
└─────────────┴──────────────────────────────────┴─────────────────┘

📱 INTERFACES DE CLIENTE:
┌─────────────┬──────────────────────────────────┐
│ Tecnologia  │ URL                              │
├─────────────┼──────────────────────────────────┤
│ REST        │ http://localhost:8080/rest       │
│ GraphQL     │ http://localhost:8080/graphql    │
│ SOAP        │ http://localhost:8080/soap       │
│ gRPC        │ http://localhost:8080/grpc       │
└─────────────┴──────────────────────────────────┘

⚠️  IMPORTANTE: Mantenha este terminal aberto durante a demonstração!
"""
    print(banner)


def mostrar_status_servicos():
    """Mostra o status dos serviços após inicialização"""
    print("\n" + "=" * 65)
    print("✅ TODOS OS SERVIÇOS ESTÃO RODANDO!")
    print("=" * 65)

    servicos = [
        ("🔵 REST API", "http://localhost:8000",
         "Interface principal + Swagger UI"),
        ("🔵 REST Docs", "http://localhost:8000/docs",
         "Documentação interativa"),
        ("🟣 GraphQL", "http://localhost:8001", "Interface principal"),
        ("🟣 GraphiQL", "http://localhost:8001/graphql", "Editor de queries"),
        ("🟢 gRPC", "http://localhost:50051", "Servidor gRPC"),
        ("🟢 gRPC-Web", "http://localhost:8003", "Proxy gRPC-Web"),
        ("🌐 Web", "http://localhost:8080", "Interfaces de cliente")
    ]

    for nome, url, descricao in servicos:
        print(f"{nome:15} → {url:35} ({descricao})")

    print("\n💡 DICAS PARA DEMONSTRAÇÃO:")
    print("1. 🔵 REST: Teste os endpoints em /docs (Swagger UI)")
    print("2. 🟣 GraphQL: Execute queries em /graphql (GraphiQL)")
    print("3. 🟢 gRPC: Use a interface web em /grpc")
    print("4. 🧪 TESTES: Digite 'test' para abrir o sistema de testes de carga")
    print("5. 📊 Compare performance e características de cada tecnologia")

    print("\n🎯 ROTEIRO SUGERIDO (15 min):")
    print("• 5 min: REST - Demonstrar endpoints e JSON responses")
    print("• 5 min: GraphQL - Mostrar queries flexíveis e precisas")
    print("• 3 min: Testes de Carga - Comparar performance das tecnologias")
    print("• 2 min: Conclusões e análise final")

    print("\n" + "=" * 65)


def mostrar_menu_interativo():
    """Mostra menu interativo para controle durante demonstração"""
    menu = """
🎮 MENU INTERATIVO - DEMONSTRAÇÃO AO VIVO
=======================================

OPÇÕES DISPONÍVEIS:

1. 🌐 Abrir Navegador
   • REST API: http://localhost:8000/docs
   • GraphQL: http://localhost:8001/graphql
   • Interfaces Web: http://localhost:8080

2. 🧪 Sistema de Testes de Carga
   • Testes rápidos (2 min)
   • Testes completos (15 min)
   • Análise comparativa das 4 tecnologias

3. 📊 Ver Status dos Serviços
   • Verificar se todos estão funcionando
   • URLs e portas utilizadas

4. 🔧 Testes Manuais Rápidos
   • Verificar conectividade das APIs
   • Teste de smoke test automático

5. 📈 Relatórios de Testes Anteriores
   • Ver resultados de testes de carga
   • Gráficos e métricas comparativas

6. ❓ Ajuda e Documentação
   • Como usar o sistema
   • Explicação das tecnologias

7. 🛑 Parar Serviços e Sair
   • Finalizar demonstração

Digite o número da opção (1-7) ou comando direto:
• 'test' ou 'testes' → Testes de carga
• 'open' ou 'abrir' → Abrir navegador
• 'status' → Status dos serviços
• 'help' ou 'ajuda' → Ajuda
• 'quit' ou 'sair' → Finalizar

Escolha: """
    return menu


def abrir_navegador_demonstracao():
    """Abre navegador com as principais URLs para demonstração"""
    urls = [
        "http://localhost:8000/docs",  # REST Swagger
        "http://localhost:8001/graphql",  # GraphQL
        "http://localhost:8080"  # Interfaces Web
    ]
    
    print("🌐 Abrindo navegador com URLs de demonstração...")
    for url in urls:
        try:
            webbrowser.open(url)
            time.sleep(1)  # Pausa entre aberturas
        except Exception as e:
            print(f"⚠️ Erro ao abrir {url}: {e}")
    
    print("✅ URLs abertas no navegador!")


def executar_teste_smoke():
    """Executa teste rápido de conectividade em todos os serviços"""
    import requests
    
    print("🔥 Executando smoke test nos serviços...")
    
    testes = [
        ("REST", "http://localhost:8000/usuarios", "GET"),
        ("GraphQL", "http://localhost:8001/graphql", "POST"),
        ("Web Server", "http://localhost:8080", "GET")
    ]
    
    resultados = []
    
    for nome, url, metodo in testes:
        try:
            if metodo == "GET":
                response = requests.get(url, timeout=5)
            else:  # POST para GraphQL
                response = requests.post(
                    url, 
                    json={"query": "{ usuarios { id nome } }"}, 
                    timeout=5
                )
            
            if response.status_code in [200, 201]:
                resultados.append(f"✅ {nome}: OK ({response.status_code})")
            else:
                resultados.append(f"⚠️ {nome}: HTTP {response.status_code}")
                
        except Exception as e:
            resultados.append(f"❌ {nome}: Erro - {str(e)[:50]}")
    
    print("\n📋 RESULTADOS DO SMOKE TEST:")
    for resultado in resultados:
        print(f"   {resultado}")
    
    # Verificar se todos passaram
    todos_ok = all("✅" in r for r in resultados)
    if todos_ok:
        print("\n🎉 Todos os serviços estão funcionando corretamente!")
    else:
        print("\n⚠️ Alguns serviços podem estar com problemas.")
    
    return todos_ok


def listar_relatorios_existentes():
    """Lista relatórios de testes de carga existentes"""
    reports_dir = Path("reports")
    
    if not reports_dir.exists():
        print("📊 Nenhum relatório encontrado ainda.")
        print("💡 Execute testes de carga para gerar relatórios.")
        return
    
    # Buscar relatórios
    txt_reports = list(reports_dir.glob("load_test_report_*.txt"))
    csv_reports = list(reports_dir.glob("load_test_data_*.csv"))
    
    if not txt_reports and not csv_reports:
        print("📊 Nenhum relatório encontrado no diretório reports/")
        return
    
    print(f"📊 RELATÓRIOS ENCONTRADOS:")
    print("-" * 30)
    
    if txt_reports:
        print("📄 Relatórios Texto:")
        for report in sorted(txt_reports, reverse=True)[:5]:  # Últimos 5
            timestamp = report.stem.split('_')[-2:]  # data_hora
            print(f"   • {report.name} ({'_'.join(timestamp)})")
    
    if csv_reports:
        print("\n📈 Dados CSV (para gráficos):")
        for csv_file in sorted(csv_reports, reverse=True)[:3]:  # Últimos 3
            timestamp = csv_file.stem.split('_')[-2:]
            print(f"   • {csv_file.name} ({'_'.join(timestamp)})")
    
    print(f"\n💡 Abra os arquivos em {reports_dir.absolute()} para ver detalhes")
    print("💡 Use os CSVs para criar gráficos no Excel/Google Sheets")


def aguardar_comando_interativo():
    """Aguarda comandos interativos durante demonstração"""
    
    print(mostrar_menu_interativo())
    
    while True:
        try:
            comando = input().strip().lower()
            
            if comando in ["1", "open", "abrir"]:
                abrir_navegador_demonstracao()
                
            elif comando in ["2", "test", "testes"]:
                if LOAD_TESTING_AVAILABLE:
                    executar_sistema_testes_carga()
                else:
                    print("❌ Sistema de testes não disponível. Verifique se load_testing_system.py existe.")
                
            elif comando in ["3", "status"]:
                mostrar_status_servicos()
                
            elif comando in ["4", "smoke"]:
                executar_teste_smoke()
                
            elif comando in ["5", "relatorios", "reports"]:
                listar_relatorios_existentes()
                
            elif comando in ["6", "help", "ajuda"]:
                mostrar_ajuda_sistema()
                
            elif comando in ["7", "quit", "sair", "exit"]:
                print("🛑 Finalizando demonstração...")
                break
                
            else:
                print("❌ Comando não reconhecido!")
                print("💡 Digite um número (1-7) ou comando direto (test, open, status, etc.)")
            
            print("\n" + "="*50)
            print("Digite outro comando ou 'sair' para finalizar:")
            
        except KeyboardInterrupt:
            print("\n🛑 Finalizando demonstração...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")


def mostrar_ajuda_sistema():
    """Mostra ajuda completa do sistema"""
    ajuda = """
📖 AJUDA - SISTEMA COMPLETO DE DEMONSTRAÇÃO
==========================================

🎯 OBJETIVO GERAL:
Este sistema demonstra e compara 4 tecnologias de invocação de 
serviços remotos através de implementações práticas e testes de carga.

🔧 COMO USAR:

1. DEMONSTRAÇÃO BÁSICA (5-10 min):
   • Digite 'open' para abrir navegadores
   • Acesse REST em /docs (Swagger UI)
   • Teste GraphQL em /graphql (GraphiQL)
   • Mostre diferenças de sintaxe e funcionalidades

2. TESTES DE CARGA (2-15 min):
   • Digite 'test' para sistema de testes
   • Use "Teste Rápido" para demonstração (2 min)
   • Use "Teste Completo" para análise detalhada (15 min)
   • Compare métricas: latência, RPS, taxa sucesso

3. ANÁLISE DE RESULTADOS:
   • Digite 'relatorios' para ver testes anteriores
   • Arquivos TXT: análise textual completa
   • Arquivos CSV: dados para gráficos Excel/Sheets

🧪 MÉTRICAS DOS TESTES:
• Latência: Tempo de resposta (ms)
• RPS: Requisições por segundo (throughput)
• Taxa Sucesso: Confiabilidade (%)
• Percentis: Consistência (P50, P95, P99)

💡 DICAS PARA APRESENTAÇÃO:
• Mantenha este terminal visível
• Use 'status' para verificar serviços
• Execute 'smoke' antes de demonstrar
• Tenha gráficos prontos dos testes completos

🔍 TROUBLESHOOTING:
• Serviço não responde? Verifique 'status'
• Teste falha? Execute 'smoke' primeiro
• Performance baixa? Feche outros programas
• Erro de porta? Reinicie o sistema

⚠️ LIMITAÇÕES:
• SOAP/gRPC são demonstrações conceituais
• Testes são locais (não refletem rede real)
• Dados em memória (performance otimizada)
"""
    print(ajuda)


def executar_modo_desenvolvimento():
    """Executa em modo desenvolvimento com threads + menu interativo"""
    print("🔧 Modo: Desenvolvimento (threads + menu interativo)")

    # Criar threads para cada serviço
    threads = []

    # Thread REST
    thread_rest = Thread(target=executar_servico_rest, daemon=True)
    threads.append(("REST", thread_rest))

    # Thread GraphQL
    thread_graphql = Thread(target=executar_servico_graphql, daemon=True)
    threads.append(("GraphQL", thread_graphql))

    # Thread SOAP
    thread_soap = Thread(target=executar_servico_soap, daemon=True)
    threads.append(("SOAP", thread_soap))

    # Thread gRPC
    thread_grpc = Thread(target=executar_servico_grpc, daemon=True)
    threads.append(("gRPC", thread_grpc))

    # Thread gRPC-Web
    thread_grpc_web = Thread(target=executar_servico_grpc_web, daemon=True)
    threads.append(("gRPC-Web", thread_grpc_web))

    # Thread Web Server
    thread_web = Thread(target=executar_servidor_web, daemon=True)
    threads.append(("Web", thread_web))

    # Iniciar todas as threads
    for nome, thread in threads:
        print(f"🚀 Iniciando {nome}...")
        thread.start()
        time.sleep(2)

    # Aguardar todos os serviços estarem prontos
    print("\n⏳ Aguardando inicialização completa...")
    time.sleep(8)

    # Mostrar status
    mostrar_status_servicos()

    # Executar smoke test automático
    print("\n🔥 Executando verificação automática...")
    executar_teste_smoke()

    # Abrir navegador automaticamente
    print("\n🌐 Abrindo navegador automaticamente...")
    abrir_navegador_demonstracao()

    # Entrar no modo interativo
    print("\n🎮 SISTEMA PRONTO - MODO INTERATIVO ATIVO")
    print("💡 Digite comandos para controlar a demonstração:")
    aguardar_comando_interativo()


def executar_modo_producao():
    """Executa em modo produção com processos"""
    print("🚀 Modo: Produção (processos)")

    with ProcessPoolExecutor(max_workers=6) as executor:
        print("🔄 Iniciando processos dos serviços...")

        # Submeter processos
        future_rest = executor.submit(executar_servico_rest)
        time.sleep(1)
        future_graphql = executor.submit(executar_servico_graphql)
        time.sleep(1)
        future_soap = executor.submit(executar_servico_soap)
        time.sleep(1)
        future_grpc = executor.submit(executar_servico_grpc)
        time.sleep(1)
        future_grpc_web = executor.submit(executar_servico_grpc_web)
        time.sleep(1)
        future_web = executor.submit(executar_servidor_web)

        print("⏳ Aguardando inicialização...")
        time.sleep(10)

        mostrar_status_servicos()

        try:
            # Aguardar indefinidamente
            future_rest.result()
        except KeyboardInterrupt:
            print("\n🛑 Finalizando processos...")
            executor.shutdown(wait=False)


def executar_modo_demonstracao():
    """Modo específico para demonstração ao professor"""
    print("🎓 Modo: Demonstração Acadêmica")
    print("🎯 Otimizado para apresentação do trabalho")
    
    # Execução similar ao desenvolvimento, mas com foco na demonstração
    executar_modo_desenvolvimento()


def executar_modo_simples():
    """Executa apenas um serviço por vez (para debugging)"""
    servicos = [
        ("REST", executar_servico_rest),
        ("GraphQL", executar_servico_graphql),
        ("gRPC", executar_servico_grpc),
        ("gRPC-Web", executar_servico_grpc_web),
        ("Web", executar_servidor_web),
        ("Sistema de Testes", lambda: executar_sistema_testes_carga() if LOAD_TESTING_AVAILABLE else print("Testes não disponíveis"))
    ]

    print("🔧 Modo Simples: Escolha um serviço para executar")
    for i, (nome, _) in enumerate(servicos, 1):
        print(f"{i}. {nome}")

    try:
        escolha = int(input("\nEscolha (1-6): ")) - 1
        if 0 <= escolha < len(servicos):
            nome, funcao = servicos[escolha]
            print(f"🚀 Executando apenas {nome}...")
            funcao()
        else:
            print("❌ Escolha inválida!")
    except (ValueError, KeyboardInterrupt):
        print("❌ Entrada inválida!")


def main():
    """Função principal"""

    # Mostrar banner
    mostrar_banner()

    # Verificar dependências
    if not verificar_dependencias():
        return

    # Detectar ambiente e modo
    if len(sys.argv) > 1:
        modo = sys.argv[1].lower()
    else:
        # Modo padrão baseado no ambiente
        if "REPL_ID" in os.environ:  # Replit
            modo = "demo"  # Modo demonstração para Replit
        elif "COLAB_GPU" in os.environ:  # Google Colab
            modo = "colab"
        else:
            modo = "demo"  # Modo demonstração como padrão

    print(f"🔧 Ambiente detectado: {modo}")

    try:
        if modo in ["dev", "desenvolvimento"]:
            executar_modo_desenvolvimento()
        elif modo in ["demo", "demonstracao", "replit"]:
            executar_modo_demonstracao()
        elif modo in ["prod", "producao", "production"]:
            executar_modo_producao()
        elif modo in ["simples", "simple", "debug"]:
            executar_modo_simples()
        elif modo == "colab":
            # Para Google Colab, executar apenas REST
            print("📓 Google Colab detectado - executando apenas REST")
            executar_servico_rest()
        elif modo in ["test", "testes"]:
            # Modo apenas para testes de carga
            if LOAD_TESTING_AVAILABLE:
                print("🧪 Modo: Apenas Testes de Carga")
                executar_sistema_testes_carga()
            else:
                print("❌ Sistema de testes não disponível!")
        else:
            print(f"❌ Modo '{modo}' não reconhecido!")
            print("Modos disponíveis: demo, dev, prod, simples, test, colab")

    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        print("💡 Tente executar com: python main.py simples")

    except KeyboardInterrupt:
        print("\n👋 Finalizando aplicação...")


def mostrar_ajuda():
    """Mostra ajuda sobre como usar o script"""
    help_text = """
🆘 AJUDA - Sistema de Demonstração Completo

EXECUÇÃO:
  python main.py [modo]

MODOS DISPONÍVEIS:
  demo        → Modo demonstração (padrão, ideal para apresentação)
  dev         → Modo desenvolvimento (threads)
  prod        → Modo produção (processos separados)  
  simples     → Executa um serviço por vez
  test        → Apenas sistema de testes de carga
  colab       → Otimizado para Google Colab

EXEMPLOS:
  python main.py              # Modo demonstração (padrão)
  python main.py demo         # Modo demonstração  
  python main.py test         # Apenas testes de carga
  python main.py simples      # Escolher serviço individual

NOVIDADES - SISTEMA DE TESTES DE CARGA:
  • Testes comparativos entre REST, GraphQL, SOAP, gRPC
  • Métricas: latência, RPS, percentis, taxa de sucesso
  • Relatórios automáticos em TXT e CSV
  • Interface interativa para demonstração

COMANDOS DURANTE EXECUÇÃO:
  test/testes    → Abrir sistema de testes de carga
  open/abrir     → Abrir navegador com URLs
  status         → Ver status dos serviços
  smoke          → Teste rápido de conectividade
  relatorios     → Ver testes anteriores
  help/ajuda     → Ajuda detalhada
  sair/quit      → Finalizar

PORTAS USADAS:
  8000 → REST API (FastAPI + Swagger)
  8001 → GraphQL (Strawberry + GraphiQL)  
  8004 → SOAP (Spyne + WSDL)
  50051 → gRPC (Protocol Buffers)
  8003 → gRPC-Web (Proxy)
  8080 → Servidor Web (Interfaces)

DEMONSTRAÇÃO RECOMENDADA (15 min):
  1. Execute: python main.py
  2. Digite 'open' para abrir navegadores
  3. Demonstre REST em /docs
  4. Demonstre GraphQL em /graphql
  5. Digite 'test' para testes de carga
  6. Execute teste rápido (2 min)
  7. Analise resultados comparativos
  8. Conclusões sobre cada tecnologia

PARA O TRABALHO ACADÊMICO:
  • Use 'test' para gerar dados dos testes de carga
  • Relatórios ficam em reports/ (TXT + CSV)
  • CSV pode ser usado para gráficos Excel/Sheets
  • Sistema atende requisitos de múltiplos clientes concorrentes
  • Métricas incluem latência, RPS, percentis conforme especificado
"""
    print(help_text)


# ========== CONFIGURAÇÃO PARA DIFERENTES AMBIENTES ==========

if __name__ == "__main__":

    # Verificar argumentos especiais
    if len(sys.argv) > 1:
        if sys.argv[1] in ["help", "-h", "--help"]:
            mostrar_ajuda()
            sys.exit(0)
        elif sys.argv[1] == "smoke":
            # Executar apenas smoke test
            executar_teste_smoke()
            sys.exit(0)

    # Configurar ambiente Replit se detectado
    if "REPL_ID" in os.environ:
        os.environ['PYTHONPATH'] = '.'

    # Executar aplicação principal
    main()