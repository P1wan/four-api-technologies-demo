// GraphQL Client for Streaming Service
class GraphQLClient {
    constructor(endpoint = 'http://localhost:8001/graphql') {
        this.endpoint = endpoint;
        this.metrics = {
            requestCount: 0,
            totalTime: 0,
            errorCount: 0
        };
        // Only check server status in browser environment
        if (typeof document !== 'undefined') {
            this.checkServerStatus();
        }
    }

    async executeQuery(query, variables = {}) {
        const startTime = performance.now();
        this.metrics.requestCount++;

        try {
            const response = await fetch(this.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify({
                    query,
                    variables
                })
            });

            const result = await response.json();
            const endTime = performance.now();
            this.metrics.totalTime += (endTime - startTime);

            if (result.errors) {
                this.metrics.errorCount++;
                throw new Error(result.errors[0].message);
            }

            if (typeof document !== 'undefined') {
                this.updateMetrics();
            }
            return result.data;
        } catch (error) {
            this.metrics.errorCount++;
            if (typeof document !== 'undefined') {
                this.updateMetrics();
            }
            throw error;
        }
    }

    async executeMutation(mutation, variables = {}) {
        return this.executeQuery(mutation, variables);
    }

    // Add specific query methods - Fixed to use correct Portuguese field names
    async queryUsers() {
        const query = `
            query {
                usuarios {
                    id
                    nome
                    idade
                }
            }
        `;
        const result = await this.executeQuery(query);
        return result.usuarios;
    }

    async querySongs() {
        const query = `
            query {
                musicas {
                    id
                    nome
                    artista
                    duracaoSegundos
                }
            }
        `;
        const result = await this.executeQuery(query);
        return result.musicas;
    }

    async queryPlaylists() {
        const query = `
            query {
                playlistsUsuario(idUsuario: "user1") {
                    id
                    nome
                    idUsuario
                    musicas
                }
            }
        `;
        const result = await this.executeQuery(query);
        return result.playlistsUsuario;
    }

    updateMetrics() {
        if (typeof document === 'undefined') return;
        
        const requestCountEl = document.getElementById('requestCount');
        const errorCountEl = document.getElementById('errorCount');
        const avgTimeEl = document.getElementById('avgTime');
        
        if (requestCountEl) requestCountEl.textContent = this.metrics.requestCount;
        if (errorCountEl) errorCountEl.textContent = this.metrics.errorCount;
        if (avgTimeEl) {
            const avgTime = this.metrics.requestCount > 0 
                ? Math.round(this.metrics.totalTime / this.metrics.requestCount) 
                : 0;
            avgTimeEl.textContent = `${avgTime}ms`;
        }
    }

    async checkServerStatus() {
        if (typeof document === 'undefined') return;

        try {
            const response = await fetch(this.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify({
                    query: '{ __typename }'
                })
            });

            const statusIndicator = document.getElementById('serverStatus');
            const statusText = document.getElementById('statusText');

            if (response.ok && statusIndicator && statusText) {
                statusIndicator.className = 'status-indicator status-online';
                statusText.textContent = 'Servidor Online';
            } else {
                throw new Error('Server not responding');
            }
        } catch (error) {
            const statusIndicator = document.getElementById('serverStatus');
            const statusText = document.getElementById('statusText');
            if (statusIndicator && statusText) {
                statusIndicator.className = 'status-indicator status-offline';
                statusText.textContent = 'Servidor Offline';
            }
        }
    }
}

// Initialize client
const client = new GraphQLClient();

// UI Functions
function displayResponse(data) {
    const viewer = document.getElementById('responseViewer');
    viewer.textContent = JSON.stringify(data, null, 2);
}

function displayError(error) {
    const viewer = document.getElementById('responseViewer');
    viewer.textContent = `Erro: ${error.message}`;
}

async function executeQuery() {
    const query = document.getElementById('queryEditor').value;
    try {
        const data = await client.executeQuery(query);
        displayResponse(data);
    } catch (error) {
        displayError(error);
    }
}

async function executeMutation() {
    const mutation = document.getElementById('mutationEditor').value;
    try {
        const data = await client.executeMutation(mutation);
        displayResponse(data);
    } catch (error) {
        displayError(error);
    }
}

function loadExample(type) {
    const queryEditor = document.getElementById('queryEditor');
    const mutationEditor = document.getElementById('mutationEditor');
    
    const examples = {
        usuarios: `{
  usuarios {
    id
    nome
    idade
  }
}`,
        playlist: `{
  playlistCompleta(idPlaylist: "playlist1") {
    id
    nome
    usuario {
      nome
    }
    musicas {
      nome
      artista
    }
  }
}`,
        estatisticas: `{
  estatisticas {
    totalUsuarios
    totalMusicas
    totalPlaylists
    mediaMusicasPorPlaylist
  }
}`,
        criarUsuario: `mutation {
  criarUsuario(input: {
    nome: "Novo Usuário",
    idade: 25
  }) {
    id
    nome
    idade
  }
}`,
        criarMusica: `mutation {
  criarMusica(input: {
    nome: "Nova Música",
    artista: "Novo Artista",
    duracao: 180
  }) {
    id
    nome
    artista
    duracao
  }
}`,
        criarPlaylist: `mutation {
  criarPlaylist(input: {
    nome: "Nova Playlist",
    idUsuario: "usuario1",
    musicas: ["musica1", "musica2"]
  }) {
    id
    nome
    usuario {
      nome
    }
    musicas {
      nome
    }
  }
}`
    };

    if (type === 'criarUsuario' || type === 'criarMusica' || type === 'criarPlaylist') {
        mutationEditor.value = examples[type];
        document.querySelector('a[href="#mutationTab"]').click();
    } else {
        queryEditor.value = examples[type];
        document.querySelector('a[href="#queryTab"]').click();
    }
}

// Check server status every 30 seconds
setInterval(() => client.checkServerStatus(), 30000);

// Export the client class
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GraphQLClient;
} 