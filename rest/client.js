/**
 * Cliente REST para o serviço de streaming
 * 
 * Este módulo fornece uma interface para interagir com a API REST
 * implementada em Python/FastAPI.
 */

class RestClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }

    // Métodos auxiliares
    async _handleResponse(response) {
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error?.message || 'Erro na requisição');
        }
        return response.json();
    }

    // Usuários
    async listarUsuarios(page = 1, pageSize = 10) {
        const response = await fetch(`${this.baseUrl}/usuarios?page=${page}&page_size=${pageSize}`);
        return this._handleResponse(response);
    }

    async criarUsuario(nome, idade) {
        const response = await fetch(`${this.baseUrl}/usuarios?nome=${encodeURIComponent(nome)}&idade=${idade}`, {
            method: 'POST'
        });
        return this._handleResponse(response);
    }

    async obterUsuario(id) {
        const response = await fetch(`${this.baseUrl}/usuarios/${id}`);
        return this._handleResponse(response);
    }

    // Músicas
    async listarMusicas(page = 1, pageSize = 10) {
        const response = await fetch(`${this.baseUrl}/musicas?page=${page}&page_size=${pageSize}`);
        return this._handleResponse(response);
    }

    async criarMusica(nome, artista, duracaoSegundos) {
        const response = await fetch(
            `${this.baseUrl}/musicas?nome=${encodeURIComponent(nome)}&artista=${encodeURIComponent(artista)}&duracaoSegundos=${duracaoSegundos}`,
            { method: 'POST' }
        );
        return this._handleResponse(response);
    }

    async obterMusica(id) {
        const response = await fetch(`${this.baseUrl}/musicas/${id}`);
        return this._handleResponse(response);
    }

    async atualizarMusica(id, nome, artista, duracaoSegundos) {
        const params = new URLSearchParams();
        if (nome) params.append('nome', nome);
        if (artista) params.append('artista', artista);
        if (duracaoSegundos) params.append('duracaoSegundos', duracaoSegundos);

        const response = await fetch(`${this.baseUrl}/musicas/${id}?${params.toString()}`, {
            method: 'PUT'
        });
        return this._handleResponse(response);
    }

    async deletarMusica(id) {
        const response = await fetch(`${this.baseUrl}/musicas/${id}`, {
            method: 'DELETE'
        });
        return this._handleResponse(response);
    }

    // Playlists
    async listarPlaylists(page = 1, pageSize = 10) {
        const response = await fetch(`${this.baseUrl}/playlists?page=${page}&page_size=${pageSize}`);
        return this._handleResponse(response);
    }

    async criarPlaylist(nome, idUsuario, musicas = []) {
        const params = new URLSearchParams();
        params.append('nome', nome);
        params.append('idUsuario', idUsuario);
        musicas.forEach(id => params.append('musicas', id));

        const response = await fetch(`${this.baseUrl}/playlists?${params.toString()}`, {
            method: 'POST'
        });
        return this._handleResponse(response);
    }

    async obterPlaylist(id) {
        const response = await fetch(`${this.baseUrl}/playlists/${id}`);
        return this._handleResponse(response);
    }

    async atualizarPlaylist(id, nome, musicas) {
        const params = new URLSearchParams();
        if (nome) params.append('nome', nome);
        if (musicas) musicas.forEach(id => params.append('musicas', id));

        const response = await fetch(`${this.baseUrl}/playlists/${id}?${params.toString()}`, {
            method: 'PUT'
        });
        return this._handleResponse(response);
    }

    async deletarPlaylist(id) {
        const response = await fetch(`${this.baseUrl}/playlists/${id}`, {
            method: 'DELETE'
        });
        return this._handleResponse(response);
    }

    // Relacionamentos
    async listarPlaylistsUsuario(idUsuario) {
        const response = await fetch(`${this.baseUrl}/usuarios/${idUsuario}/playlists`);
        return this._handleResponse(response);
    }

    async listarMusicasPlaylist(idPlaylist) {
        const response = await fetch(`${this.baseUrl}/playlists/${idPlaylist}/musicas`);
        return this._handleResponse(response);
    }

    async listarPlaylistsComMusica(idMusica) {
        const response = await fetch(`${this.baseUrl}/musicas/${idMusica}/playlists`);
        return this._handleResponse(response);
    }

    // Estatísticas
    async obterEstatisticas() {
        const response = await fetch(`${this.baseUrl}/stats`);
        return this._handleResponse(response);
    }
}

// Exporta o cliente para uso em outros módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RestClient;
} 