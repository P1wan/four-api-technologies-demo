const { DOMParser } = require('@xmldom/xmldom');
const fetch = require('node-fetch');

class UnifiedClient {
    constructor(config = {}) {
        // Service endpoints
        this.endpoints = {
            rest: config.restEndpoint || 'http://localhost:8000',
            graphql: config.graphqlEndpoint || 'http://localhost:8001/graphql',
            soap: config.soapEndpoint || 'http://localhost:8004/soap',
            grpc: config.grpcEndpoint || 'http://localhost:8003'
        };

        // Load testing configuration
        this.loadTestConfig = {
            users: config.users || 10,
            spawnRate: config.spawnRate || 1,
            duration: config.duration || 60, // seconds
            thinkTime: config.thinkTime || 1 // seconds
        };

        // Metrics collection
        this.metrics = {
            requests: [],
            startTime: null,
            endTime: null,
            totalRequests: 0,
            successfulRequests: 0,
            failedRequests: 0,
            totalResponseTime: 0
        };

        // SOAP specific configuration
        this.soapConfig = {
            namespace: 'http://streaming.soap.service',
            soapAction: 'http://streaming.soap.service'
        };
    }

    // REST API Methods
    async restRequest(endpoint, method = 'GET', body = null) {
        const startTime = Date.now();
        try {
            const response = await fetch(`${this.endpoints.rest}${endpoint}`, {
                method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: body ? JSON.stringify(body) : null
            });

            const data = await response.json();
            const endTime = Date.now();
            this.recordMetrics('REST', endpoint, startTime, endTime, response.ok);
            return data;
        } catch (error) {
            const endTime = Date.now();
            this.recordMetrics('REST', endpoint, startTime, endTime, false, error);
            throw error;
        }
    }

    // GraphQL Methods
    async graphqlRequest(query, variables = {}) {
        const startTime = Date.now();
        try {
            const response = await fetch(this.endpoints.graphql, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query,
                    variables
                })
            });

            const data = await response.json();
            const endTime = Date.now();
            this.recordMetrics('GraphQL', query, startTime, endTime, !data.errors);
            return data;
        } catch (error) {
            const endTime = Date.now();
            this.recordMetrics('GraphQL', query, startTime, endTime, false, error);
            throw error;
        }
    }

    // SOAP Methods
    async soapRequest(operation, params = {}) {
        const startTime = Date.now();
        try {
            const soapEnvelope = this.createSoapEnvelope(operation, params);
            console.log(`SOAP Request for ${operation}:`, soapEnvelope);
            
            const response = await fetch(this.endpoints.soap, {
                method: 'POST',
                headers: {
                    'Content-Type': 'text/xml; charset=utf-8',
                    'SOAPAction': `"${this.soapConfig.soapAction}/${operation}"`,
                    'Accept': 'text/xml'
                },
                body: soapEnvelope
            });

            const xmlText = await response.text();
            console.log(`SOAP Response for ${operation}:`, xmlText);
            
            if (!response.ok) {
                throw new Error(`HTTP Error: ${response.status} ${response.statusText}\nResponse: ${xmlText}`);
            }

            const result = this.parseSoapResponse(xmlText, operation);
            const endTime = Date.now();
            this.recordMetrics('SOAP', operation, startTime, endTime, true);
            return result;
        } catch (error) {
            const endTime = Date.now();
            this.recordMetrics('SOAP', operation, startTime, endTime, false, error);
            console.error(`SOAP Error for ${operation}:`, error);
            throw error;
        }
    }

    // Load Testing Methods
    async runLoadTest(testScenario) {
        console.log('Starting load test...');
        this.metrics.startTime = Date.now();
        
        const promises = [];
        for (let i = 0; i < this.loadTestConfig.users; i++) {
            promises.push(this.runUserScenario(testScenario, i));
        }

        await Promise.all(promises);
        this.metrics.endTime = Date.now();
        this.printMetrics();
    }

    async runUserScenario(scenario, userIndex) {
        for (const step of scenario) {
            await this.executeStep(step, userIndex);
            await this.sleep(this.loadTestConfig.thinkTime * 1000);
        }
    }

    async executeStep(step, userIndex) {
        const { type, operation, params } = step;
        try {
            switch (type) {
                case 'REST':
                    return await this.restRequest(operation, params.method, params.body);
                case 'GraphQL':
                    return await this.graphqlRequest(operation, params.variables);
                case 'SOAP':
                    return await this.soapRequest(operation, params);
                default:
                    throw new Error(`Unknown operation type: ${type}`);
            }
        } catch (error) {
            console.error(`Error executing ${type} operation ${operation}:`, error);
            throw error;
        }
    }

    // Helper Methods
    createSoapEnvelope(operation, params = {}) {
        let paramsXml = '';
        for (const [key, value] of Object.entries(params)) {
            paramsXml += `<${key}>${this.escapeXml(value)}</${key}>`;
        }

        return `<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="${this.soapConfig.namespace}">
    <soap:Header/>
    <soap:Body>
        <tns:${operation}>
            ${paramsXml}
        </tns:${operation}>
    </soap:Body>
</soap:Envelope>`;
    }

    parseSoapResponse(xmlText, operation) {
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(xmlText, "text/xml");
        
        // Check for XML parsing errors
        const parserError = xmlDoc.getElementsByTagName('parsererror')[0];
        if (parserError) {
            throw new Error(`XML Parsing Error: ${parserError.textContent}`);
        }
        
        const faultElement = xmlDoc.getElementsByTagName('soap:Fault')[0] || 
                           xmlDoc.getElementsByTagName('Fault')[0];
        
        if (faultElement) {
            const faultString = faultElement.getElementsByTagName('faultstring')[0]?.textContent || 
                              'SOAP Fault occurred';
            const faultCode = faultElement.getElementsByTagName('faultcode')[0]?.textContent || 
                            'Unknown fault code';
            const faultDetail = faultElement.getElementsByTagName('detail')[0]?.textContent || 
                              'No additional details';
            throw new Error(`SOAP Fault:\nCode: ${faultCode}\nMessage: ${faultString}\nDetails: ${faultDetail}`);
        }

        const responseElement = xmlDoc.getElementsByTagName(`${operation}Response`)[0];
        if (!responseElement) {
            // Try to find any response element as fallback
            const anyResponse = xmlDoc.getElementsByTagName('Response')[0];
            if (anyResponse) {
                console.warn(`Using fallback response element for operation ${operation}`);
                return this.xmlToJson(anyResponse);
            }
            throw new Error(`No response element found for operation ${operation}. Full response: ${xmlText}`);
        }

        return this.xmlToJson(responseElement);
    }

    xmlToJson(xml) {
        const obj = {};
        if (xml.nodeType === 1) {
            if (xml.attributes.length > 0) {
                obj['@attributes'] = {};
                for (let j = 0; j < xml.attributes.length; j++) {
                    const attribute = xml.attributes.item(j);
                    obj['@attributes'][attribute.nodeName] = attribute.nodeValue;
                }
            }
        } else if (xml.nodeType === 3) {
            obj.text = xml.nodeValue;
        }

        if (xml.hasChildNodes()) {
            for (let i = 0; i < xml.childNodes.length; i++) {
                const item = xml.childNodes.item(i);
                const nodeName = item.nodeName;
                if (typeof obj[nodeName] === 'undefined') {
                    obj[nodeName] = this.xmlToJson(item);
                } else {
                    if (typeof obj[nodeName].push === 'undefined') {
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

    escapeXml(unsafe) {
        return unsafe
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&apos;');
    }

    recordMetrics(type, operation, startTime, endTime, success, error = null) {
        const duration = endTime - startTime;
        this.metrics.requests.push({
            type,
            operation,
            startTime,
            endTime,
            duration,
            success,
            error: error?.message
        });

        this.metrics.totalRequests++;
        this.metrics.totalResponseTime += duration;
        if (success) {
            this.metrics.successfulRequests++;
        } else {
            this.metrics.failedRequests++;
        }
    }

    printMetrics() {
        const totalDuration = (this.metrics.endTime - this.metrics.startTime) / 1000;
        const avgResponseTime = this.metrics.totalResponseTime / this.metrics.totalRequests;

        console.log('\n📊 Load Test Results:');
        console.log('=====================');
        console.log(`Total Duration: ${totalDuration.toFixed(2)}s`);
        console.log(`Total Requests: ${this.metrics.totalRequests}`);
        console.log(`Successful Requests: ${this.metrics.successfulRequests}`);
        console.log(`Failed Requests: ${this.metrics.failedRequests}`);
        console.log(`Average Response Time: ${avgResponseTime.toFixed(2)}ms`);
        console.log(`Requests per Second: ${(this.metrics.totalRequests / totalDuration).toFixed(2)}`);
        
        // Print errors if any
        const errors = this.metrics.requests.filter(r => !r.success);
        if (errors.length > 0) {
            console.log('\n❌ Errors:');
            errors.forEach(error => {
                console.log(`- ${error.type} ${error.operation}: ${error.error}`);
            });
        }
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

module.exports = UnifiedClient; 