"""
Gerador de Dados Fictícios para o Serviço de Streaming de Músicas
================================================================

Este script gera dados em massa para testar as diferentes tecnologias de invocação remota:
- 5000 usuários
- 10000 músicas
- 3000 playlists com relacionamentos realistas

Estrutura dos Dados:
- Usuário: id (UUID), nome, idade
- Música: id (UUID), nome, artista, duracaoSegundos
- Playlist: id (UUID), nome, idUsuario, musicas (lista de IDs)
"""

import json
import uuid
import random
from faker import Faker
import os

# Configurar o Faker para gerar dados em português brasileiro
fake = Faker('pt_BR')


def gerar_usuarios(quantidade=5000):
    """
    Gera uma lista de usuários fictícios
    """
    usuarios = []

    print(f"Gerando {quantidade} usuários...")

    for i in range(quantidade):
        usuario = {
            "id": str(uuid.uuid4()),
            "nome": fake.name(),
            "idade":
            random.randint(13, 80)  # Idade realista para usuários de streaming
        }
        usuarios.append(usuario)

        # Mostrar progresso a cada 1000 usuários
        if (i + 1) % 1000 == 0:
            print(f"  {i + 1} usuários gerados...")

    return usuarios


def gerar_musicas(quantidade=10000):
    """
    Gera uma lista de músicas fictícias com gêneros variados
    """
    musicas = []

    # Listas de nomes e artistas realistas
    nomes_musicas = [
        "Amor Perfeito", "Noite Estrelada", "Coração Selvagem", "Despertar",
        "Liberdade", "Saudade", "Tempestade", "Serenata", "Paixão",
        "Sonho Real", "Vento Norte", "Lua Cheia", "Caminhada", "Esperança",
        "Melodia Doce", "Ritmo Quente", "Alma Livre", "Madrugada", "Energia",
        "Harmonia", "Revolução", "Simplicidade", "Intensidade", "Leveza",
        "Mistério", "Aventura", "Nostalgia", "Euforia", "Tranquilidade",
        "Força Interior"
    ]

    artistas = [
        "Ana Silva", "João Santos", "Maria Oliveira", "Pedro Costa",
        "Lucia Ferreira", "Carlos Rodrigues", "Fernanda Lima", "Ricardo Alves",
        "Juliana Souza", "Bruno Martins", "Camila Pereira", "Diego Barbosa",
        "Isabela Nascimento", "Rafael Carvalho", "Beatriz Gomes",
        "Thiago Ribeiro", "Amanda Torres", "Gabriel Monteiro",
        "Larissa Cardoso", "Leonardo Dias", "Banda Nova Era", "Os Sonhadores",
        "Grupo Harmonia", "Coletivo Musical", "Ensemble Brasil",
        "The Night Walkers", "Urban Sound", "Acoustic Dreams",
        "Electric Souls", "Vintage Vibes"
    ]

    print(f"Gerando {quantidade} músicas...")

    for i in range(quantidade):
        musica = {
            "id": str(uuid.uuid4()),
            "nome":
            random.choice(nomes_musicas) + f" {random.randint(1, 100)}",
            "artista": random.choice(artistas),
            "duracaoSegundos": random.randint(120, 360)  # Entre 2 e 6 minutos
        }
        musicas.append(musica)

        # Mostrar progresso a cada 2000 músicas
        if (i + 1) % 2000 == 0:
            print(f"  {i + 1} músicas geradas...")

    return musicas


def gerar_playlists(usuarios, musicas, quantidade=3000):
    """
    Gera playlists com relacionamentos realistas entre usuários e músicas
    """
    playlists = []

    nomes_playlists = [
        "Meus Favoritos", "Músicas para Relaxar", "Energia Total", "Nostalgia",
        "Workout Mix", "Viagem", "Fim de Semana", "Trabalho", "Festa",
        "Românticas", "Rock Nacional", "MPB Clássica", "Sertanejo Top",
        "Eletrônica", "Jazz Suave", "Bossa Nova", "Forró Animado",
        "Pop Internacional", "Indie Brasileiro", "Clássicos dos Anos 80",
        "Descobertas Recentes", "Para Dormir", "Motivação", "Melancolia",
        "Dança", "Acústico", "Instrumental", "Covers", "Remix", "Top 50",
        "Aleatória", "Especial", "Mix Perfeito"
    ]

    print(f"Gerando {quantidade} playlists...")

    for i in range(quantidade):
        # Selecionar um usuário aleatório como dono da playlist
        usuario_dono = random.choice(usuarios)

        # Número realista de músicas por playlist (5 a 50 músicas)
        num_musicas = random.randint(5, 50)

        # Selecionar músicas aleatórias (sem repetição na mesma playlist)
        musicas_playlist = random.sample(musicas, min(num_musicas,
                                                      len(musicas)))
        ids_musicas = [musica["id"] for musica in musicas_playlist]

        playlist = {
            "id": str(uuid.uuid4()),
            "nome":
            random.choice(nomes_playlists) + f" {random.randint(1, 100)}",
            "idUsuario": usuario_dono["id"],
            "musicas": ids_musicas
        }
        playlists.append(playlist)

        # Mostrar progresso a cada 500 playlists
        if (i + 1) % 500 == 0:
            print(f"  {i + 1} playlists geradas...")

    return playlists


def salvar_dados_json(dados, nome_arquivo):
    """
    Salva os dados em um arquivo JSON formatado
    """
    # Criar diretório data se não existir
    os.makedirs('data', exist_ok=True)

    caminho_arquivo = os.path.join('data', nome_arquivo)

    with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)

    print(f"Dados salvos em: {caminho_arquivo}")


def gerar_relatorio_estatisticas(usuarios, musicas, playlists):
    """
    Gera um relatório com estatísticas dos dados gerados
    """
    print("\n" + "=" * 60)
    print("RELATÓRIO DE ESTATÍSTICAS DOS DADOS GERADOS")
    print("=" * 60)

    print(f"USUÁRIOS: {len(usuarios)}")
    idades = [u['idade'] for u in usuarios]
    print(f"  - Idade média: {sum(idades)/len(idades):.1f} anos")
    print(f"  - Idade mínima: {min(idades)} anos")
    print(f"  - Idade máxima: {max(idades)} anos")

    print(f"\nMÚSICAS: {len(musicas)}")
    duracoes = [m['duracaoSegundos'] for m in musicas]
    print(f"  - Duração média: {sum(duracoes)/len(duracoes):.1f} segundos")
    print(f"  - Duração total: {sum(duracoes)/3600:.1f} horas")

    artistas_unicos = len(set(m['artista'] for m in musicas))
    print(f"  - Artistas únicos: {artistas_unicos}")

    print(f"\nPLAYLISTS: {len(playlists)}")
    tamanhos_playlists = [len(p['musicas']) for p in playlists]
    print(
        f"  - Tamanho médio: {sum(tamanhos_playlists)/len(tamanhos_playlists):.1f} músicas"
    )
    print(f"  - Maior playlist: {max(tamanhos_playlists)} músicas")
    print(f"  - Menor playlist: {min(tamanhos_playlists)} músicas")

    # Calcular distribuição de playlists por usuário
    playlists_por_usuario = {}
    for playlist in playlists:
        id_usuario = playlist['idUsuario']
        playlists_por_usuario[id_usuario] = playlists_por_usuario.get(
            id_usuario, 0) + 1

    usuarios_com_playlists = len(playlists_por_usuario)
    print(f"  - Usuários com playlists: {usuarios_com_playlists}")
    print(
        f"  - Média de playlists por usuário ativo: {len(playlists)/usuarios_com_playlists:.1f}"
    )

    print("\n" + "=" * 60)


def main():
    """
    Função principal que orquestra a geração de todos os dados
    """
    print("GERADOR DE DADOS FICTÍCIOS - SERVIÇO DE STREAMING")
    print("=" * 60)

    # Instalar faker se necessário
    try:
        from faker import Faker
    except ImportError:
        print("ERRO: Biblioteca 'faker' não encontrada!")
        print("Instale com: pip install faker")
        return

    # Gerar os dados
    print("Iniciando geração de dados...\n")

    usuarios = gerar_usuarios(5000)
    musicas = gerar_musicas(10000)
    playlists = gerar_playlists(usuarios, musicas, 3000)

    # Salvar em arquivos JSON
    print("\nSalvando dados em arquivos JSON...")
    salvar_dados_json(usuarios, 'usuarios.json')
    salvar_dados_json(musicas, 'musicas.json')
    salvar_dados_json(playlists, 'playlists.json')

    # Gerar relatório de estatísticas
    gerar_relatorio_estatisticas(usuarios, musicas, playlists)

    print("\n✅ Geração de dados concluída com sucesso!")
    print("\nArquivos gerados:")
    print("  - data/usuarios.json")
    print("  - data/musicas.json")
    print("  - data/playlists.json")

    print("\nPróximos passos:")
    print("1. Instalar dependências: pip install faker")
    print("2. Executar: python gerar_dados.py")
    print("3. Verificar os arquivos JSON na pasta 'data/'")


if __name__ == "__main__":
    main()
