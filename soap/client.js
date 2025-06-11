/**
 * SOAP Client for Streaming Service
 * Implements all required operations for the project
 */
// Detect environment and use appropriate DOMParser implementation
let DOMParser;
if (typeof window === 'undefined') {
    ({ DOMParser } = require('xmldom'));
} else {
    DOMParser = window.DOMParser;
}
class SOAPClient {
    constructor(endpoint = 'http://localhost:8004') {
        this.endpoint = endpoint;
        this.wsdlUrl = `${endpoint}?wsdl`;
        this.soapAction = 'http://streaming.soap';
        this.namespace = 'http://streaming.soap';
        
        this.metrics = {
            requestCount: 0,
            totalTime: 0,
            errorCount: 0,
            successCount: 0
        };
        
        // Check server status when in browser
        if (typeof document !== 'undefined') {
            this.checkServerStatus();
        }
    }

    /**
     * List songs in a specific playlist
     */
    async listarMusicasPlaylist(idPlaylist) {
        return await this.executeOperation('listar_musicas_playlist', { 
            id_playlist: idPlaylist 
        });
    }

    /**
     * List playlists containing a specific song
     */
    async listarPlaylistsComMusica(idMusica) {
        return await this.executeOperation('listar_playlists_com_musica', { 
            id_musica: idMusica 
        });
    }

    /**
     * Get service statistics
     */
    async obterEstatisticas() {
        return await this.executeOperation('obter_estatisticas');
    }

    /**
     * Create a new user
     */
    async criarUsuario(id, nome, idade) {
        return await this.executeOperation('criar_usuario', {
            id: id,
            nome: nome,
            idade: parseInt(idade)
        });
    }

    /**
     * Create a new song
     */
    async criarMusica(id, nome, artista, duracao) {
        return await this.executeOperation('criar_musica', {
            id: id,
            nome: nome,
            artista: artista,
            duracao: parseInt(duracao)
        });
    }

    /**
     * Create a new playlist
     */
    async criarPlaylist(id, nome, idUsuario, musicas) {
        return await this.executeOperation('criar_playlist', {
            id: id,
            nome: nome,
            id_usuario: idUsuario,
            musicas: Array.isArray(musicas) ? musicas : []
        });
    }

    /**
     * Execute a SOAP operation
     */
    async executeOperation(operation, params = {}) {
        const startTime = performance.now();
        this.metrics.requestCount++;

        try {
            console.log(`🟡 SOAP: Executando ${operation}`, params);
            
            const soapEnvelope = this.createSoapEnvelope(operation, params);
            console.log('🟡 SOAP Envelope:', soapEnvelope);

            const response = await fetch(this.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'text/xml; charset=utf-8',
                    'SOAPAction': `"${this.soapAction}/${operation}"`,
                    'Accept': 'text/xml'
                },
                body: soapEnvelope
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const xmlText = await response.text();
            console.log('🟡 SOAP Response XML:', xmlText);
            
            const result = this.parseSoapResponse(xmlText, operation);
            
            const endTime = performance.now();
            const duration = endTime - startTime;
            this.metrics.totalTime += duration;
            this.metrics.successCount++;

            console.log(`🟡 SOAP: ${operation} concluído em ${Math.round(duration)}ms`);

            if (typeof document !== 'undefined') {
                this.updateMetrics();
            }

            return result;
        } catch (error) {
            const endTime = performance.now();
            this.metrics.totalTime += (endTime - startTime);
            this.metrics.errorCount++;
            
            console.error(`🟡 SOAP: Erro em ${operation}:`, error);

            if (typeof document !== 'undefined') {
                this.updateMetrics();
            }
            
            throw error;
        }
    }

    /**
     * Create SOAP envelope for the operation
     */
    createSoapEnvelope(operation, params = {}) {
        let paramsXml = '';
        
        // Handle different parameter types
        for (const [key, value] of Object.entries(params)) {
            if (Array.isArray(value)) {
                // Handle arrays (for playlists with multiple songs)
                for (const item of value) {
                    paramsXml += `<${key}>${this.escapeXml(item)}</${key}>`;
                }
            } else {
                paramsXml += `<${key}>${this.escapeXml(value)}</${key}>`;
            }
        }

        return `<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="${this.namespace}">
    <soap:Header/>
    <soap:Body>
        <tns:${operation}>
            ${paramsXml}
        </tns:${operation}>
    </soap:Body>
</soap:Envelope>`;
    }

    /**
     * Parse SOAP response and extract data
     */
    parseSoapResponse(xmlText, operation) {
        try {
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(xmlText, "text/xml");
            
            // Check for SOAP fault
            const faultElement = xmlDoc.getElementsByTagName('soap:Fault')[0] || 
                               xmlDoc.getElementsByTagName('Fault')[0];
            
            if (faultElement) {
                const faultString = faultElement.getElementsByTagName('faultstring')[0]?.textContent || 
                                  'SOAP Fault occurred';
                throw new Error(`SOAP Fault: ${faultString}`);
            }

            // Find the response element
            const responseElementName = `${operation}Response`;
            let responseElement = xmlDoc.getElementsByTagName(responseElementName)[0];
            
            // Try without namespace prefix
            if (!responseElement) {
                const allElements = xmlDoc.getElementsByTagName('*');
                for (let elem of allElements) {
                    if (elem.localName === responseElementName) {
                        responseElement = elem;
                        break;
                    }
                }
            }

            if (!responseElement) {
                // Try to get the body content directly
                const bodyElement = xmlDoc.getElementsByTagName('soap:Body')[0] || 
                                  xmlDoc.getElementsByTagName('Body')[0];
                if (bodyElement && bodyElement.children.length > 0) {
                    responseElement = bodyElement.children[0];
                }
            }

            if (!responseElement) {
                throw new Error(`Response element ${responseElementName} not found in SOAP response`);
            }

            // Convert response to JavaScript object
            const result = this.xmlToJson(responseElement);
            
            // Extract the actual data from the response structure
            return this.extractResponseData(result, operation);
            
        } catch (error) {
            console.error('Error parsing SOAP response:', error);
            console.error('XML Response:', xmlText);
            throw new Error(`Failed to parse SOAP response: ${error.message}`);
        }
    }

    /**
     * Extract meaningful data from parsed response
     */
    extractResponseData(parsed, operation) {
        // Handle different response structures based on operation
        if (typeof parsed === 'object' && parsed !== null) {
            // If it's an array or has array-like properties, return as is
            if (Array.isArray(parsed)) {
                return parsed;
            }
            
            // Look for common response patterns
            const keys = Object.keys(parsed);
            if (keys.length === 1) {
                const firstKey = keys[0];
                const value = parsed[firstKey];
                
                // If the value is an array or object, return it
                if (Array.isArray(value) || (typeof value === 'object' && value !== null)) {
                    return value;
                }
            }
            
            // Return the parsed object as-is
            return parsed;
        }
        
        return parsed;
    }

    /**
     * Convert XML node to JSON object
     */
    xmlToJson(xml) {
        let obj = {};

        if (xml.nodeType === 1) { // Element node
            // Handle attributes
            if (xml.attributes.length > 0) {
                obj["@attributes"] = {};
                for (let j = 0; j < xml.attributes.length; j++) {
                    const attribute = xml.attributes.item(j);
                    obj["@attributes"][attribute.nodeName] = attribute.nodeValue;
                }
            }
        } else if (xml.nodeType === 3) { // Text node
            obj = xml.nodeValue;
        }

        // Handle child nodes
        if (xml.hasChildNodes()) {
            for (let i = 0; i < xml.childNodes.length; i++) {
                const item = xml.childNodes.item(i);
                const nodeName = item.nodeName;
                
                if (typeof(obj[nodeName]) === "undefined") {
                    obj[nodeName] = this.xmlToJson(item);
                } else {
                    if (typeof(obj[nodeName].push) === "undefined") {
                        const old = obj[nodeName];
                        obj[nodeName] = [];
                        obj[nodeName].push(old);
                    }
                    obj[nodeName].push(this.xmlToJson(item));
                }
            }
        }
        
        return obj;
    }

    /**
     * Escape XML special characters
     */
    escapeXml(unsafe) {
        if (unsafe == null) return '';
        return String(unsafe).replace(/[<>&'"]/g, function (c) {
            switch (c) {
                case '<': return '&lt;';
                case '>': return '&gt;';
                case '&': return '&amp;';
                case '\'': return '&apos;';
                case '"': return '&quot;';
                default: return c;
            }
        });
    }

    /**
     * Update metrics display in the UI
     */
    updateMetrics() {
        if (typeof document === 'undefined') return;
        
        const elements = {
            requestCount: document.getElementById('requestCount'),
            errorCount: document.getElementById('errorCount'),
            successCount: document.getElementById('successCount'),
            avgTime: document.getElementById('avgTime')
        };
        
        if (elements.requestCount) {
            elements.requestCount.textContent = this.metrics.requestCount;
        }
        if (elements.errorCount) {
            elements.errorCount.textContent = this.metrics.errorCount;
        }
        if (elements.successCount) {
            elements.successCount.textContent = this.metrics.successCount;
        }
        if (elements.avgTime) {
            const avgTime = this.metrics.requestCount > 0 
                ? Math.round(this.metrics.totalTime / this.metrics.requestCount) 
                : 0;
            elements.avgTime.textContent = `${avgTime}ms`;
        }
    }

    /**
     * Check server status
     */
    async checkServerStatus() {
        if (typeof document === 'undefined') return;

        try {
            const response = await fetch(this.wsdlUrl, {
                method: 'GET',
                headers: { 'Accept': 'text/xml' }
            });
            
            const statusIndicator = document.getElementById('serverStatus');
            const statusText = document.getElementById('statusText');

            if (response.ok) {
                if (statusIndicator) {
                    statusIndicator.className = 'status-indicator status-online';
                }
                if (statusText) {
                    statusText.textContent = 'Servidor SOAP Online';
                }
                console.log('🟡 SOAP: Servidor online e WSDL acessível');
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            const statusIndicator = document.getElementById('serverStatus');
            const statusText = document.getElementById('statusText');
            
            if (statusIndicator) {
                statusIndicator.className = 'status-indicator status-offline';
            }
            if (statusText) {
                statusText.textContent = 'Servidor SOAP Offline';
            }
            console.warn('🟡 SOAP: Servidor offline ou inacessível:', error.message);
        }
    }

    // ========== API METHODS ==========

    /**
     * List all users
     */
    async listarUsuarios() {
        return await this.executeOperation('listar_usuarios');
    }

    /**
     * List all songs
     */
    async listarMusicas() {
        return await this.executeOperation('listar_musicas');
    }

    /**
     * List playlists for a specific user
     */
    async listarPlaylistsUsuario(idUsuario) {
        return await this.executeOperation('listar_playlists_usuario', { 
            id_usuario: idUsuario 
        });
    }
}

// Export for Node.js environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SOAPClient;
}

// Initialize client when in browser
let client;
if (typeof document !== 'undefined') {
    client = new SOAPClient();
}

// ========== UI FUNCTIONS ==========

function displayResponse(data, operation = '') {
    const viewer = document.getElementById('responseViewer');
    if (!viewer) return;

    let displayData = data;
    
    // Format the response for better display
    if (typeof data === 'object') {
        displayData = JSON.stringify(data, null, 2);
    }
    
    const timestamp = new Date().toLocaleTimeString();
    const header = operation ? `=== ${operation.toUpperCase()} (${timestamp}) ===\n` : '';
    
    viewer.textContent = header + displayData;
    viewer.scrollTop = 0;

    console.log(`🟡 SOAP Response for ${operation}:`, data);
}

function displayError(error, operation = '') {
    const viewer = document.getElementById('responseViewer');
    if (!viewer) return;

    const timestamp = new Date().toLocaleTimeString();
    const errorMessage = `=== ERRO em ${operation.toUpperCase()} (${timestamp}) ===\n${error.message}`;
    
    viewer.textContent = errorMessage;
    viewer.style.color = '#dc3545';
    
    // Reset color after 3 seconds
    setTimeout(() => {
        viewer.style.color = '';
    }, 3000);

    console.error(`🟡 SOAP Error in ${operation}:`, error);
}

function clearResponse() {
    const viewer = document.getElementById('responseViewer');
    if (viewer) {
        viewer.textContent = '';
        viewer.style.color = '';
    }
}

// ========== OPERATION FUNCTIONS ==========

async function listarUsuarios() {
    try {
        clearResponse();
        const data = await client.listarUsuarios();
        displayResponse(data, 'listar_usuarios');
    } catch (error) {
        displayError(error, 'listar_usuarios');
    }
}

async function listarMusicas() {
    try {
        clearResponse();
        const data = await client.listarMusicas();
        displayResponse(data, 'listar_musicas');
    } catch (error) {
        displayError(error, 'listar_musicas');
    }
}

async function listarPlaylistsUsuario() {
    const userId = document.getElementById('userId')?.value;
    if (!userId) {
        displayError(new Error('ID do usuário é obrigatório'), 'listar_playlists_usuario');
        return;
    }

    try {
        clearResponse();
        const data = await client.listarPlaylistsUsuario(userId);
        displayResponse(data, 'listar_playlists_usuario');
    } catch (error) {
        displayError(error, 'listar_playlists_usuario');
    }
}

async function listarMusicasPlaylist() {
    const playlistId = document.getElementById('playlistId')?.value;
    if (!playlistId) {
        displayError(new Error('ID da playlist é obrigatório'), 'listar_musicas_playlist');
        return;
    }

    try {
        clearResponse();
        const data = await client.listarMusicasPlaylist(playlistId);
        displayResponse(data, 'listar_musicas_playlist');
    } catch (error) {
        displayError(error, 'listar_musicas_playlist');
    }
}

async function listarPlaylistsComMusica() {
    const musicId = document.getElementById('musicId')?.value;
    if (!musicId) {
        displayError(new Error('ID da música é obrigatório'), 'listar_playlists_com_musica');
        return;
    }

    try {
        clearResponse();
        const data = await client.listarPlaylistsComMusica(musicId);
        displayResponse(data, 'listar_playlists_com_musica');
    } catch (error) {
        displayError(error, 'listar_playlists_com_musica');
    }
}

async function obterEstatisticas() {
    try {
        clearResponse();
        const data = await client.obterEstatisticas();
        displayResponse(data, 'obter_estatisticas');
    } catch (error) {
        displayError(error, 'obter_estatisticas');
    }
}

async function criarUsuario() {
    const id = document.getElementById('novoUsuarioId')?.value;
    const nome = document.getElementById('novoUsuarioNome')?.value;
    const idade = document.getElementById('novoUsuarioIdade')?.value;

    if (!id || !nome || !idade) {
        displayError(new Error('Todos os campos são obrigatórios'), 'criar_usuario');
        return;
    }

    try {
        clearResponse();
        const data = await client.criarUsuario(id, nome, idade);
        displayResponse(data, 'criar_usuario');
        
        // Clear the form
        document.getElementById('novoUsuarioId').value = '';
        document.getElementById('novoUsuarioNome').value = '';
        document.getElementById('novoUsuarioIdade').value = '';
    } catch (error) {
        displayError(error, 'criar_usuario');
    }
}

async function criarMusica() {
    const id = document.getElementById('novaMusicaId')?.value;
    const nome = document.getElementById('novaMusicaNome')?.value;
    const artista = document.getElementById('novaMusicaArtista')?.value;
    const duracao = document.getElementById('novaMusicaDuracao')?.value;

    if (!id || !nome || !artista || !duracao) {
        displayError(new Error('Todos os campos são obrigatórios'), 'criar_musica');
        return;
    }

    try {
        clearResponse();
        const data = await client.criarMusica(id, nome, artista, duracao);
        displayResponse(data, 'criar_musica');
        
        // Clear the form
        document.getElementById('novaMusicaId').value = '';
        document.getElementById('novaMusicaNome').value = '';
        document.getElementById('novaMusicaArtista').value = '';
        document.getElementById('novaMusicaDuracao').value = '';
    } catch (error) {
        displayError(error, 'criar_musica');
    }
}

async function criarPlaylist() {
    const id = document.getElementById('novaPlaylistId')?.value;
    const nome = document.getElementById('novaPlaylistNome')?.value;
    const idUsuario = document.getElementById('novaPlaylistUsuario')?.value;
    const musicasStr = document.getElementById('novaPlaylistMusicas')?.value;

    if (!id || !nome || !idUsuario) {
        displayError(new Error('ID, nome e usuário são obrigatórios'), 'criar_playlist');
        return;
    }

    try {
        clearResponse();
        const musicas = musicasStr ? musicasStr.split(',').map(m => m.trim()).filter(m => m) : [];
        const data = await client.criarPlaylist(id, nome, idUsuario, musicas);
        displayResponse(data, 'criar_playlist');
        
        // Clear the form
        document.getElementById('novaPlaylistId').value = '';
        document.getElementById('novaPlaylistNome').value = '';
        document.getElementById('novaPlaylistUsuario').value = '';
        document.getElementById('novaPlaylistMusicas').value = '';
    } catch (error) {
        displayError(error, 'criar_playlist');
    }
}

// ========== UTILITY FUNCTIONS ==========

function generateRandomId() {
    return 'id_' + Math.random().toString(36).substr(2, 9);
}

function populateTestData() {
    // Fill forms with test data for demonstration
    const testUser = {
        id: generateRandomId(),
        nome: 'Usuário Teste',
        idade: '25'
    };
    
    const testMusic = {
        id: generateRandomId(),
        nome: 'Música Teste',
        artista: 'Artista Teste',
        duracao: '180'
    };
    
    const testPlaylist = {
        id: generateRandomId(),
        nome: 'Playlist Teste',
        usuario: 'user1',
        musicas: 'music1,music2'
    };
    
    // Populate user form
    if (document.getElementById('novoUsuarioId')) {
        document.getElementById('novoUsuarioId').value = testUser.id;
        document.getElementById('novoUsuarioNome').value = testUser.nome;
        document.getElementById('novoUsuarioIdade').value = testUser.idade;
    }
}

// ========== INITIALIZATION ==========

// Check server status periodically
if (typeof document !== 'undefined') {
    // Initial status check
    setTimeout(() => client.checkServerStatus(), 1000);
    
    // Periodic status check every 30 seconds
    setInterval(() => client.checkServerStatus(), 30000);
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(event) {
        if (event.ctrlKey || event.metaKey) {
            switch(event.key) {
                case '1':
                    event.preventDefault();
                    listarUsuarios();
                    break;
                case '2':
                    event.preventDefault();
                    listarMusicas();
                    break;
                case '3':
                    event.preventDefault();
                    obterEstatisticas();
                    break;
                case 'r':
                    event.preventDefault();
                    clearResponse();
                    break;
            }
        }
    });
    
    console.log('🟡 SOAP Client initialized');
    console.log('🟡 Keyboard shortcuts available:');
    console.log('   Ctrl+1: Listar usuários');
    console.log('   Ctrl+2: Listar músicas');
    console.log('   Ctrl+3: Obter estatísticas');
    console.log('   Ctrl+R: Limpar resposta');
}