"""
Script Principal - Trabalho de Computação Distribuída
====================================================

Executa todos os serviços (REST, GraphQL, SOAP/gRPC) simultaneamente
para demonstração em ambiente web.

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


def verificar_dependencias():
    """Verifica e instala dependências necessárias"""
    dependencias = [("fastapi", "fastapi==0.104.1"),
                    ("uvicorn", "uvicorn[standard]==0.24.0"),
                    ("strawberry", "strawberry-graphql[fastapi]==0.213.0")]

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
        log_level="error",  # Reduzir logs para demonstração
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


def executar_demonstracoes():
    """Executa as demonstrações SOAP/gRPC"""
    import uvicorn
    from soap_grpc_demo import app

    print("🟡 SOAP/gRPC: Iniciando demonstrações na porta 8002...")
    uvicorn.run(app,
                host="0.0.0.0",
                port=8002,
                log_level="error",
                access_log=False)


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
├── 🟡 SOAP      → Demonstração com WSDL
└── 🟢 gRPC      → Demonstração com Protocol Buffers

🌐 URLS DE ACESSO (aguarde inicialização):
┌─────────────┬──────────────────────────────────┬─────────────────┐
│ Tecnologia  │ URL Principal                    │ Documentação    │
├─────────────┼──────────────────────────────────┼─────────────────┤
│ REST        │ http://localhost:8000            │ /docs           │
│ GraphQL     │ http://localhost:8001            │ /graphql        │
│ SOAP+gRPC   │ http://localhost:8002            │ /               │
└─────────────┴──────────────────────────────────┴─────────────────┘

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
        ("🟡 SOAP+gRPC", "http://localhost:8002", "Demonstrações e exemplos")
    ]

    for nome, url, descricao in servicos:
        print(f"{nome:15} → {url:35} ({descricao})")

    print("\n💡 DICAS PARA DEMONSTRAÇÃO:")
    print("1. 🔵 REST: Teste os endpoints em /docs (Swagger UI)")
    print("2. 🟣 GraphQL: Execute queries em /graphql (GraphiQL)")
    print("3. 🟡 SOAP+gRPC: Veja códigos e exemplos na página principal")
    print("4. 📊 Compare performance e características de cada tecnologia")

    print("\n🎯 ROTEIRO SUGERIDO (15 min):")
    print("• 5 min: REST - Demonstrar endpoints e JSON responses")
    print("• 5 min: GraphQL - Mostrar queries flexíveis e precisas")
    print("• 3 min: SOAP/gRPC - Explicar código e características")
    print("• 2 min: Comparação final e conclusões")

    print("\n" + "=" * 65)


def aguardar_ctrl_c():
    """Aguarda Ctrl+C para finalizar"""
    try:
        print("\n⌨️  Pressione Ctrl+C para parar todos os serviços...\n")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Parando todos os serviços...")
        return


def executar_modo_desenvolvimento():
    """Executa em modo desenvolvimento com threads"""
    print("🔧 Modo: Desenvolvimento (threads)")

    # Criar threads para cada serviço
    threads = []

    # Thread REST
    thread_rest = Thread(target=executar_servico_rest, daemon=True)
    threads.append(("REST", thread_rest))

    # Thread GraphQL
    thread_graphql = Thread(target=executar_servico_graphql, daemon=True)
    threads.append(("GraphQL", thread_graphql))

    # Thread Demonstrações
    thread_demo = Thread(target=executar_demonstracoes, daemon=True)
    threads.append(("SOAP+gRPC", thread_demo))

    # Iniciar todas as threads
    for nome, thread in threads:
        print(f"🚀 Iniciando {nome}...")
        thread.start()
        time.sleep(2)  # Aguardar um pouco entre inicializações

    # Aguardar todos os serviços estarem prontos
    print("\n⏳ Aguardando inicialização completa...")
    time.sleep(8)

    # Mostrar status
    mostrar_status_servicos()

    # Aguardar finalização
    aguardar_ctrl_c()


def executar_modo_producao():
    """Executa em modo produção com processos"""
    print("🚀 Modo: Produção (processos)")

    with ProcessPoolExecutor(max_workers=3) as executor:
        print("🔄 Iniciando processos dos serviços...")

        # Submeter processos
        future_rest = executor.submit(executar_servico_rest)
        time.sleep(1)
        future_graphql = executor.submit(executar_servico_graphql)
        time.sleep(1)
        future_demo = executor.submit(executar_demonstracoes)

        print("⏳ Aguardando inicialização...")
        time.sleep(10)

        mostrar_status_servicos()

        try:
            # Aguardar indefinidamente
            future_rest.result()
        except KeyboardInterrupt:
            print("\n🛑 Finalizando processos...")
            executor.shutdown(wait=False)


def executar_modo_simples():
    """Executa apenas um serviço por vez (para debugging)"""
    servicos = [("REST", executar_servico_rest),
                ("GraphQL", executar_servico_graphql),
                ("SOAP+gRPC", executar_demonstracoes)]

    print("🔧 Modo Simples: Escolha um serviço para executar")
    for i, (nome, _) in enumerate(servicos, 1):
        print(f"{i}. {nome}")

    try:
        escolha = int(input("\nEscolha (1-3): ")) - 1
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

    # Detectar ambiente
    if len(sys.argv) > 1:
        modo = sys.argv[1].lower()
    else:
        # Modo padrão baseado no ambiente
        if "REPL_ID" in os.environ:  # Replit
            modo = "replit"
        elif "COLAB_GPU" in os.environ:  # Google Colab
            modo = "colab"
        else:
            modo = "dev"

    print(f"🔧 Ambiente detectado: {modo}")

    try:
        if modo in ["dev", "desenvolvimento", "replit"]:
            executar_modo_desenvolvimento()
        elif modo in ["prod", "producao", "production"]:
            executar_modo_producao()
        elif modo in ["simples", "simple", "debug"]:
            executar_modo_simples()
        elif modo == "colab":
            # Para Google Colab, executar apenas REST
            print("📓 Google Colab detectado - executando apenas REST")
            executar_servico_rest()
        else:
            print(f"❌ Modo '{modo}' não reconhecido!")
            print("Modos disponíveis: dev, prod, simples, colab")

    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        print("💡 Tente executar com: python main.py simples")

    except KeyboardInterrupt:
        print("\n👋 Finalizando aplicação...")


def verificar_portas():
    """Verifica se as portas estão disponíveis"""
    import socket

    portas = [8000, 8001, 8002]
    portas_ocupadas = []

    for porta in portas:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', porta)) == 0:
                portas_ocupadas.append(porta)

    if portas_ocupadas:
        print(f"⚠️  Portas ocupadas: {portas_ocupadas}")
        print("💡 Pare outros serviços ou use portas diferentes")
        return False

    return True


def executar_testes_rapidos():
    """Executa testes rápidos nos serviços"""
    import requests
    import time

    print("🧪 Executando testes rápidos...")

    servicos = [("REST", "http://localhost:8000/usuarios"),
                ("GraphQL", "http://localhost:8001"),
                ("SOAP+gRPC", "http://localhost:8002")]

    for nome, url in servicos:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {nome}: OK")
            else:
                print(f"⚠️  {nome}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {nome}: Erro - {e}")


def executar_com_ngrok():
    """Executa com ngrok para URL pública (útil para demonstrações)"""
    try:
        from pyngrok import ngrok

        print("🌐 Configurando URLs públicas com ngrok...")

        # Executar serviços em background
        thread_rest = Thread(target=executar_servico_rest, daemon=True)
        thread_rest.start()
        time.sleep(5)

        # Criar túneis ngrok
        public_url_rest = ngrok.connect(8000)

        print(f"🔗 URL Pública REST: {public_url_rest}")
        print(f"🔗 Documentação: {public_url_rest}/docs")

        # Aguardar
        aguardar_ctrl_c()

    except ImportError:
        print("❌ pyngrok não instalado. Instale com: pip install pyngrok")
        print("💡 Executando normalmente...")
        executar_modo_desenvolvimento()


# ========== FUNÇÕES AUXILIARES PARA REPLIT ==========


def configurar_replit():
    """Configurações específicas para Replit"""

    # Definir variáveis de ambiente
    os.environ['PYTHONPATH'] = '.'

    # Criar arquivo .replit se não existir
    replit_config = """
run = "python main.py"
language = "python3"

[nix]
channel = "stable-21_11"

[deps]
fastapi = "*"
uvicorn = "*"
strawberry-graphql = "*"

[[ports]]
localPort = 8000
externalPort = 80

[[ports]]  
localPort = 8001
externalPort = 8001

[[ports]]
localPort = 8002  
externalPort = 8002
"""

    if not os.path.exists('.replit'):
        with open('.replit', 'w') as f:
            f.write(replit_config)
        print("✅ Arquivo .replit criado")


def mostrar_ajuda():
    """Mostra ajuda sobre como usar o script"""
    help_text = """
🆘 AJUDA - Como usar o script principal

EXECUÇÃO:
  python main.py [modo]

MODOS DISPONÍVEIS:
  dev         → Modo desenvolvimento (padrão, threads)
  prod        → Modo produção (processos separados)  
  simples     → Executa um serviço por vez
  colab       → Otimizado para Google Colab
  ngrok       → Cria URLs públicas com ngrok
  help        → Mostra esta ajuda

EXEMPLOS:
  python main.py              # Modo padrão (dev)
  python main.py prod         # Modo produção
  python main.py simples      # Escolher serviço individual
  python main.py ngrok        # URLs públicas

PORTAS USADAS:
  8000 → REST API (FastAPI + Swagger)
  8001 → GraphQL (Strawberry + GraphiQL)  
  8002 → Demonstrações SOAP/gRPC

RESOLUÇÃO DE PROBLEMAS:
  • Porta ocupada? Pare outros serviços ou mude as portas
  • Dependência faltando? O script instala automaticamente
  • Erro de import? Verifique se os arquivos .py estão na pasta
  • No Replit? Use o modo padrão (dev)

DEMONSTRAÇÃO AO PROFESSOR:
  1. Execute: python main.py
  2. Aguarde "TODOS OS SERVIÇOS ESTÃO RODANDO"
  3. Acesse as URLs mostradas
  4. Demonstre REST → GraphQL → SOAP/gRPC
  5. Compare características e performance
"""
    print(help_text)


# ========== CONFIGURAÇÃO PARA DIFERENTES AMBIENTES ==========

if __name__ == "__main__":

    # Verificar argumentos especiais
    if len(sys.argv) > 1:
        if sys.argv[1] in ["help", "-h", "--help"]:
            mostrar_ajuda()
            sys.exit(0)
        elif sys.argv[1] == "test":
            executar_testes_rapidos()
            sys.exit(0)
        elif sys.argv[1] == "ngrok":
            executar_com_ngrok()
            sys.exit(0)

    # Configurar ambiente Replit se detectado
    if "REPL_ID" in os.environ:
        configurar_replit()

    # Verificar portas disponíveis
    # verificar_portas()  # Comentado para evitar problemas em alguns ambientes

    # Executar aplicação principal
    main()
