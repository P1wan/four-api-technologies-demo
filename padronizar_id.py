# padronizar_ids.py
import json
import os
import re

def to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()

def convert_keys_to_snake_case(obj):
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            new_key = to_snake_case(k)
            new_obj[new_key] = convert_keys_to_snake_case(v)
        return new_obj
    elif isinstance(obj, list):
        return [convert_keys_to_snake_case(item) for item in obj]
    else:
        return obj

def padronizar_chaves_json():
    """
    Este script padroniza as chaves dos arquivos usuarios.json e playlists.json para snake_case.
    """
    data_dir = 'data'
    usuarios_path = os.path.join(data_dir, 'usuarios.json')
    playlists_path = os.path.join(data_dir, 'playlists.json')
    musicas_path = os.path.join(data_dir, 'musicas.json')
    if not os.path.exists(data_dir):
        print(f"Erro: O diretório '{data_dir}' não existe. Por favor, crie o diretório e coloque os arquivos JSON nele.")
        return

    print("Iniciando a padronização das chaves para snake_case...")

    try:
        with open(usuarios_path, 'r', encoding='utf-8') as f:
            usuarios = json.load(f)
        with open(playlists_path, 'r', encoding='utf-8') as f:
            playlists = json.load(f)
        with open(musicas_path, 'r', encoding='utf-8') as f:
            musicas = json.load(f)
    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado. Verifique se o diretório 'data' existe. Detalhes: {e}")
        return

    usuarios_snake = convert_keys_to_snake_case(usuarios)
    playlists_snake = convert_keys_to_snake_case(playlists)
    musicas_snake = convert_keys_to_snake_case(musicas)
    print("Chaves convertidas para snake_case com sucesso!")

    try:
        with open(usuarios_path, 'w', encoding='utf-8') as f:
            json.dump(usuarios_snake, f, indent=4, ensure_ascii=False)
        with open(playlists_path, 'w', encoding='utf-8') as f:
            json.dump(playlists_snake, f, indent=4, ensure_ascii=False)
        with open(musicas_path, 'w', encoding='utf-8') as f:
            json.dump(musicas_snake, f, indent=4, ensure_ascii=False)
        print("Chaves dos arquivos 'usuarios.json' e 'playlists.json' foram padronizadas para snake_case com sucesso!")
    except Exception as e:
        print(f"Ocorreu um erro ao salvar os arquivos: {e}")

if __name__ == '__main__':
    padronizar_chaves_json()
