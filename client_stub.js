/*
 * Basic JavaScript client used as a reference for invoking the four backends.
 * Each function illustrates how a real client could send requests to the
 * respective service. For simplicidade, as implementações reais deverão lidar
 * com tratamento de erros, autenticação e detalhes específicos de cada
 * protocolo.
 */

// URLs padrão dos serviços
const REST_URL = 'http://localhost:8000';
const GRAPHQL_URL = 'http://localhost:8001/graphql';
const SOAP_URL = 'http://localhost:8002/soap';
const GRPC_URL = 'http://localhost:50051'; // gRPC usa porta separada

// -------------------- REST --------------------
export async function listarUsuariosREST() {
  // Exemplo simples de chamada REST utilizando fetch
  const resp = await fetch(`${REST_URL}/usuarios`);
  return resp.json();
}

// -------------------- GraphQL -----------------
export async function listarUsuariosGraphQL() {
  const query = `{ usuarios { id nome idade } }`;
  const resp = await fetch(GRAPHQL_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
  const data = await resp.json();
  return data.data.usuarios;
}

// -------------------- SOAP --------------------
export async function listarUsuariosSOAP() {
  /*
   * Para consumir SOAP via navegador seria necessário utilizar uma biblioteca
   * específica ou enviar manualmente o envelope XML. Abaixo deixamos um
   * esqueleto de requisição que poderá ser completado com a biblioteca de sua
   * preferência (ex. soap-js). O endpoint do serviço deve expor o WSDL em
   * `${SOAP_URL}?wsdl`.
   */
  const envelope = `<?xml version="1.0"?>\n<soap:Envelope>...</soap:Envelope>`;
  const resp = await fetch(SOAP_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'text/xml' },
    body: envelope
  });
  const text = await resp.text();
  return text; // TODO: parsear XML
}

// -------------------- gRPC --------------------
export async function listarUsuariosGRPC() {
  /*
   * Browsers não se conectam diretamente a serviços gRPC; em um cliente Node.js
   * utilize o pacote @grpc/grpc-js. Este stub indica onde conectar e como a
   * chamada pode ser estruturada.
   */
  throw new Error('gRPC client não implementado. Use Node.js para testar.');
}
