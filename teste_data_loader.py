# Criar arquivo: teste_data_loader.py
from data_loader import get_data_loader

def testar_data_loader():
    print("🔍 Testando Data Loader...")
    
    loader = get_data_loader()
    
    # Teste básico
    usuarios = loader.listar_todos_usuarios()
    musicas = loader.listar_todas_musicas()
    
    print(f"✅ Carregados: {len(usuarios)} usuários, {len(musicas)} músicas")
    
    # Teste de nomenclatura
    if musicas and 'duracaoSegundos' in musicas[0]:
        print("✅ JSON usa camelCase (duracaoSegundos)")
    
    # Teste de método específico
    if musicas:
        primeira_musica = loader.obter_musica_por_id(musicas[0]['id'])
        if primeira_musica:
            print("✅ Método obter_musica_por_id funcionando")
    
    return True

if __name__ == "__main__":
    testar_data_loader()