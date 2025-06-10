// SOAP Client for Streaming Service
class SOAPClient {
    constructor(endpoint = 'http://localhost:8004/soap') {
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

    async executeOperation(operation, params = {}) {
        const startTime = performance.now();
        this.metrics.requestCount++;

        try {
            const soapEnvelope = this.createSoapEnvelope(operation, params);
            const response = await fetch(this.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'text/xml;charset=UTF-8',
                    'SOAPAction': `http://streaming.service/${operation}`
                },
                body: soapEnvelope
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const xmlText = await response.text();
            const result = this.parseSoapResponse(xmlText, operation);
            const endTime = performance.now();
            this.metrics.totalTime += (endTime - startTime);

            if (typeof document !== 'undefined') {
                this.updateMetrics();
            }
            return result;
        } catch (error) {
            this.metrics.errorCount++;
            if (typeof document !== 'undefined') {
                this.updateMetrics();
            }
            throw error;
        }
    }

    createSoapEnvelope(operation, params) {
        let paramsXml = '';
        for (const [key, value] of Object.entries(params)) {
            paramsXml += `<${key}>${value}</${key}>`;
        }

        return `<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <soap:Body>
        <${operation} xmlns="http://streaming.service">
            ${paramsXml}
        </${operation}>
    </soap:Body>
</soap:Envelope>`;
    }

    parseSoapResponse(xmlText, operation) {
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(xmlText, "text/xml");
        
        // Remove namespaces for easier parsing
        const response = xmlDoc.getElementsByTagName(`${operation}Response`)[0];
        if (!response) {
            throw new Error('Invalid SOAP response');
        }

        // Convert XML to JSON
        return this.xmlToJson(response);
    }

    xmlToJson(xml) {
        // Create the return object
        let obj = {};

        if (xml.nodeType === 1) { // element
            // do attributes
            if (xml.attributes.length > 0) {
                obj["@attributes"] = {};
                for (let j = 0; j < xml.attributes.length; j++) {
                    const attribute = xml.attributes.item(j);
                    obj["@attributes"][attribute.nodeName] = attribute.nodeValue;
                }
            }
        } else if (xml.nodeType === 3) { // text
            obj = xml.nodeValue;
        }

        // do children
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
            const response = await fetch(this.endpoint + '?wsdl');
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
const client = new SOAPClient();

// UI Functions
function displayResponse(data) {
    const viewer = document.getElementById('responseViewer');
    viewer.textContent = JSON.stringify(data, null, 2);
}

function displayError(error) {
    const viewer = document.getElementById('responseViewer');
    viewer.textContent = `Erro: ${error.message}`;
}

// Operation Functions
async function listarUsuarios() {
    try {
        const data = await client.executeOperation('listarUsuarios');
        displayResponse(data);
    } catch (error) {
        displayError(error);
    }
}

async function listarMusicas() {
    try {
        const data = await client.executeOperation('listarMusicas');
        displayResponse(data);
    } catch (error) {
        displayError(error);
    }
}

async function listarPlaylistsUsuario() {
    const userId = document.getElementById('userId').value;
    if (!userId) {
        displayError(new Error('ID do usuário é obrigatório'));
        return;
    }

    try {
        const data = await client.executeOperation('listarPlaylistsUsuario', { id_usuario: userId });
        displayResponse(data);
    } catch (error) {
        displayError(error);
    }
}

async function listarMusicasPlaylist() {
    const playlistId = document.getElementById('playlistId').value;
    if (!playlistId) {
        displayError(new Error('ID da playlist é obrigatório'));
        return;
    }

    try {
        const data = await client.executeOperation('listarMusicasPlaylist', { id_playlist: playlistId });
        displayResponse(data);
    } catch (error) {
        displayError(error);
    }
}

async function listarPlaylistsComMusica() {
    const musicId = document.getElementById('musicId').value;
    if (!musicId) {
        displayError(new Error('ID da música é obrigatório'));
        return;
    }

    try {
        const data = await client.executeOperation('listarPlaylistsComMusica', { id_musica: musicId });
        displayResponse(data);
    } catch (error) {
        displayError(error);
    }
}

async function obterEstatisticas() {
    try {
        const data = await client.executeOperation('obterEstatisticas');
        displayResponse(data);
    } catch (error) {
        displayError(error);
    }
}

async function criarUsuario() {
    const id = document.getElementById('novoUsuarioId').value;
    const nome = document.getElementById('novoUsuarioNome').value;
    const idade = document.getElementById('novoUsuarioIdade').value;

    if (!id || !nome || !idade) {
        displayError(new Error('Todos os campos são obrigatórios'));
        return;
    }

    try {
        const data = await client.executeOperation('criarUsuario', {
            id: id,
            nome: nome,
            idade: idade
        });
        displayResponse(data);
    } catch (error) {
        displayError(error);
    }
}

async function criarMusica() {
    const id = document.getElementById('novaMusicaId').value;
    const nome = document.getElementById('novaMusicaNome').value;
    const artista = document.getElementById('novaMusicaArtista').value;
    const duracao = document.getElementById('novaMusicaDuracao').value;

    if (!id || !nome || !artista || !duracao) {
        displayError(new Error('Todos os campos são obrigatórios'));
        return;
    }

    try {
        const data = await client.executeOperation('criarMusica', {
            id: id,
            nome: nome,
            artista: artista,
            duracao: duracao
        });
        displayResponse(data);
    } catch (error) {
        displayError(error);
    }
}

async function criarPlaylist() {
    const id = document.getElementById('novaPlaylistId').value;
    const nome = document.getElementById('novaPlaylistNome').value;
    const idUsuario = document.getElementById('novaPlaylistUsuario').value;
    const musicas = document.getElementById('novaPlaylistMusicas').value;

    if (!id || !nome || !idUsuario || !musicas) {
        displayError(new Error('Todos os campos são obrigatórios'));
        return;
    }

    try {
        const data = await client.executeOperation('criarPlaylist', {
            id: id,
            nome: nome,
            id_usuario: idUsuario,
            musicas: musicas.split(',').map(m => m.trim())
        });
        displayResponse(data);
    } catch (error) {
        displayError(error);
    }
}

// Check server status every 30 seconds
setInterval(() => client.checkServerStatus(), 30000);

// Export the client class
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SOAPClient;
} 