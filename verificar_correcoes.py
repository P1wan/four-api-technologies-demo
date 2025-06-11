#!/usr/bin/env python3
"""
Verificação Rápida das Correções Aplicadas
==========================================

Verifica se as correções de nomenclatura e código foram aplicadas corretamente
através de análise estática dos arquivos.
"""

import os
import re
import json
from pathlib import Path

class VerificadorCorrecoes:
    """Verifica se as correções foram aplicadas corretamente."""
    
    def __init__(self):
        self.resultados = []
        self.base_path = Path('.')

    def log(self, status: str, descricao: str, detalhes: str = ""):
        """Registra resultado de verificação."""
        simbolo = "✅" if status == "ok" else "❌" if status == "erro" else "⚠️"
        self.resultados.append((status, descricao, detalhes))
        print(f"{simbolo} {descricao}")
        if detalhes:
            print(f"    {detalhes}")

    def verificar_grpc_service(self):
        """Verifica se o erro do gRPC foi corrigido."""
        print("\n🔍 Verificando correção do gRPC Service...")
        
        arquivo = self.base_path / 'grpc_service.py'
        if not arquivo.exists():
            self.log("erro", "Arquivo grpc_service.py não encontrado")
            return False

        conteudo = arquivo.read_text(encoding='utf-8')
        
        # Verificar se o método correto está sendo usado
        if 'self.loader.obter_musica_por_id(' in conteudo:
            self.log("ok", "Método obter_musica_por_id está sendo usado corretamente")
        elif 'self.loader.obter_musica(' in conteudo:
            self.log("erro", "Método incorreto obter_musica ainda está sendo usado")
            return False
        else:
            self.log("aviso", "Não foi possível verificar o método no gRPC")

        # Verificar se não há emojis
        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000027BF]')
        if not emoji_pattern.search(conteudo):
            self.log("ok", "Emojis removidos do grpc_service.py")
        else:
            self.log("aviso", "Emojis ainda encontrados no grpc_service.py")

        return True

    def verificar_soap_service(self):
        """Verifica se as correções do SOAP foram aplicadas."""
        print("\n🔍 Verificando correções do SOAP Service...")
        
        arquivo = self.base_path / 'soap_service.py'
        if not arquivo.exists():
            self.log("erro", "Arquivo soap_service.py não encontrado")
            return False

        conteudo = arquivo.read_text(encoding='utf-8')
        
        # Verificar se métodos inconsistentes foram removidos/padronizados
        if 'def GetUser(' in conteudo or 'def GetPlaylist(' in conteudo:
            self.log("aviso", "Métodos com nomenclatura inconsistente ainda presentes (GetUser, GetPlaylist)")
        else:
            self.log("ok", "Nomenclatura de métodos padronizada")

        # Verificar se não há modificação direta de data_loader
        if 'data_loader.musicas.append(' in conteudo:
            self.log("erro", "Modificação direta de dados compartilhados ainda presente")
            return False
        else:
            self.log("ok", "Modificações diretas de dados compartilhados removidas")

        # Verificar se emojis foram removidos
        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000027BF]')
        if not emoji_pattern.search(conteudo):
            self.log("ok", "Emojis removidos do soap_service.py")
        else:
            self.log("aviso", "Emojis ainda encontrados no soap_service.py")

        return True

    def verificar_graphql_service(self):
        """Verifica se as correções do GraphQL foram aplicadas."""
        print("\n🔍 Verificando correções do GraphQL Service...")
        
        arquivo = self.base_path / 'graphql_service.py'
        if not arquivo.exists():
            self.log("erro", "Arquivo graphql_service.py não encontrado")
            return False

        conteudo = arquivo.read_text(encoding='utf-8')
        
        # Verificar uso de duracao_segundos no GraphQL
        if 'duracao_segundos: int' in conteudo:
            self.log("ok", "Campo duracao_segundos definido no schema GraphQL")
        else:
            self.log("aviso", "Campo duracao_segundos não encontrado no schema")

        # Verificar conversão de nomenclatura
        if 'duracao_segundos=m["duracaoSegundos"]' in conteudo:
            self.log("ok", "Conversão de nomenclatura implementada (duracaoSegundos -> duracao_segundos)")
        else:
            self.log("aviso", "Conversão de nomenclatura não encontrada")

        # Verificar se emojis foram removidos
        emoji_pattern = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000027BF]')
        if not emoji_pattern.search(conteudo):
            self.log("ok", "Emojis removidos do graphql_service.py")
        else:
            self.log("aviso", "Emojis ainda encontrados no graphql_service.py")

        return True

    def verificar_dados_json(self):
        """Verifica se os dados JSON usam nomenclatura consistente."""
        print("\n🔍 Verificando nomenclatura nos dados JSON...")
        
        arquivo_musicas = self.base_path / 'data' / 'musicas.json'
        if not arquivo_musicas.exists():
            self.log("aviso", "Arquivo data/musicas.json não encontrado")
            return False

        try:
            with open(arquivo_musicas, 'r', encoding='utf-8') as f:
                musicas = json.load(f)
            
            if musicas and isinstance(musicas, list):
                primeira_musica = musicas[0]
                if 'duracaoSegundos' in primeira_musica:
                    self.log("ok", "Dados JSON usam camelCase (duracaoSegundos)")
                elif 'duracao_segundos' in primeira_musica:
                    self.log("aviso", "Dados JSON usam snake_case - pode ser inconsistente")
                else:
                    self.log("erro", "Campo de duração não encontrado nos dados")
                    return False
            else:
                self.log("erro", "Formato inválido no arquivo de músicas")
                return False

        except Exception as e:
            self.log("erro", f"Erro ao ler dados JSON: {str(e)}")
            return False

        return True

    def verificar_proto_file(self):
        """Verifica se o arquivo proto usa nomenclatura correta."""
        print("\n🔍 Verificando arquivo Protocol Buffers...")
        
        arquivo = self.base_path / 'streaming.proto'
        if not arquivo.exists():
            self.log("aviso", "Arquivo streaming.proto não encontrado")
            return False

        conteudo = arquivo.read_text(encoding='utf-8')
        
        if 'int32 duracao_segundos' in conteudo:
            self.log("ok", "Proto file usa snake_case (duracao_segundos)")
        else:
            self.log("aviso", "Campo duracao_segundos não encontrado no proto")

        return True

    def verificar_estrutura_projeto(self):
        """Verifica se a estrutura do projeto está íntegra."""
        print("\n🔍 Verificando estrutura do projeto...")
        
        arquivos_criticos = [
            'data_loader.py',
            'rest_service.py',
            'graphql_service.py',
            'soap_service.py',
            'grpc_service.py',
            'main.py'
        ]
        
        todos_presentes = True
        for arquivo in arquivos_criticos:
            caminho = self.base_path / arquivo
            if caminho.exists():
                self.log("ok", f"Arquivo {arquivo} presente")
            else:
                self.log("erro", f"Arquivo {arquivo} não encontrado")
                todos_presentes = False

        return todos_presentes

    def executar_verificacao(self):
        """Executa todas as verificações."""
        print("🔧 VERIFICAÇÃO DAS CORREÇÕES APLICADAS")
        print("=" * 50)
        
        resultados = []
        
        # Executar verificações
        resultados.append(self.verificar_estrutura_projeto())
        resultados.append(self.verificar_dados_json())
        resultados.append(self.verificar_proto_file())
        resultados.append(self.verificar_grpc_service())
        resultados.append(self.verificar_soap_service())
        resultados.append(self.verificar_graphql_service())
        
        # Relatório final
        print("\n" + "=" * 50)
        print("📊 RELATÓRIO DE VERIFICAÇÃO")
        print("=" * 50)
        
        sucessos = sum(1 for r in resultados if r)
        total = len(resultados)
        
        print(f"✅ Verificações bem-sucedidas: {sucessos}/{total}")
        
        # Estatísticas por status
        status_count = {"ok": 0, "aviso": 0, "erro": 0}
        for status, _, _ in self.resultados:
            status_count[status] += 1
        
        print(f"✅ Sucessos: {status_count['ok']}")
        print(f"⚠️  Avisos: {status_count['aviso']}")
        print(f"❌ Erros: {status_count['erro']}")
        
        print("\n🎯 AVALIAÇÃO GERAL:")
        if status_count['erro'] == 0:
            if status_count['aviso'] <= 2:
                print("🎉 CORREÇÕES APLICADAS COM SUCESSO!")
                print("   O código está pronto para a próxima fase.")
            else:
                print("✅ CORREÇÕES APLICADAS (com ressalvas)")
                print("   Algumas melhorias podem ser feitas.")
        else:
            print("❌ CORREÇÕES INCOMPLETAS")
            print("   Há problemas que precisam ser corrigidos.")
        
        return sucessos == total and status_count['erro'] == 0

def main():
    """Função principal."""
    verificador = VerificadorCorrecoes()
    sucesso = verificador.executar_verificacao()
    
    if sucesso:
        print("\n🚀 Pronto para prosseguir com a verificação de funcionamento!")
        print("   Execute os serviços e teste as funcionalidades.")
    else:
        print("\n🔧 Revise as correções antes de prosseguir.")
    
    return 0 if sucesso else 1

if __name__ == "__main__":
    exit(main())