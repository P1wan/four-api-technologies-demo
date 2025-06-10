// gRPC-Web client implementation
class GrpcClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
        this.metrics = {
            requests: 0,
            totalTime: 0,
            errors: 0
        };
    }

    async makeRequest(endpoint, request, description) {
        this.metrics.requests++;
        const startTime = performance.now();

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/grpc-web-text',
                    'X-User-Agent': 'grpc-web-javascript/0.1'
                },
                body: JSON.stringify(request)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            const endTime = performance.now();
            const duration = Math.round(endTime - startTime);
            this.metrics.totalTime += duration;

            return {
                data,
                duration,
                error: null
            };
        } catch (error) {
            const endTime = performance.now();
            const duration = Math.round(endTime - startTime);
            this.metrics.errors++;

            return {
                data: null,
                duration,
                error: error.message
            };
        }
    }

    async listarUsuarios() {
        return this.makeRequest('/streaming.StreamingService/ListarTodosUsuarios', 
            {}, 'Listar todos os usuários');
    }

    async listarMusicas() {
        return this.makeRequest('/streaming.StreamingService/ListarTodasMusicas', 
            {}, 'Listar todas as músicas');
    }

    async listarPlaylistsUsuario(userId) {
        return this.makeRequest('/streaming.StreamingService/ListarPlaylistsUsuario', 
            { id_usuario: userId }, `Playlists do usuário ${userId}`);
    }

    async listarMusicasPlaylist(playlistId) {
        return this.makeRequest('/streaming.StreamingService/ListarMusicasPlaylist', 
            { id_playlist: playlistId }, `Músicas da playlist ${playlistId}`);
    }

    async listarPlaylistsComMusica(musicId) {
        return this.makeRequest('/streaming.StreamingService/ListarPlaylistsComMusica', 
            { id_musica: musicId }, `Playlists contendo música ${musicId}`);
    }

    async obterEstatisticas() {
        return this.makeRequest('/streaming.StreamingService/ObterEstatisticas', 
            {}, 'Obter estatísticas do serviço');
    }

    async streamMusicas(musicIds) {
        const stream = new EventSource(`${this.baseURL}/streaming.StreamingService/StreamMusicas`);
        const results = [];

        return new Promise((resolve, reject) => {
            stream.onmessage = (event) => {
                const data = JSON.parse(event.data);
                results.push(data);

                if (results.length === musicIds.length) {
                    stream.close();
                    resolve({
                        data: results,
                        duration: 0,
                        error: null
                    });
                }
            };

            stream.onerror = (error) => {
                stream.close();
                reject({
                    data: null,
                    duration: 0,
                    error: error.message
                });
            };

            // Send music IDs
            musicIds.forEach(id => {
                stream.send(JSON.stringify({ id_musica: id }));
            });
        });
    }

    getMetrics() {
        const avgTime = this.metrics.totalTime / (this.metrics.requests - this.metrics.errors);
        return {
            requests: this.metrics.requests,
            avgTime: isNaN(avgTime) ? 0 : Math.round(avgTime),
            errors: this.metrics.errors
        };
    }
}

// Export the client class
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GrpcClient;
} 