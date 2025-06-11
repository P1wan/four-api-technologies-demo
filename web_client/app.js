// Service endpoints
const ENDPOINTS = {
    rest: 'http://localhost:8000',
    graphql: 'http://localhost:8001/graphql',
    soap: 'http://localhost:8004/soap'
};

// Test scenarios for each service
const TEST_SCENARIOS = {
    rest: [
        { name: 'List Users', endpoint: '/usuarios', method: 'GET' },
        { name: 'List Songs', endpoint: '/musicas', method: 'GET' },
        { name: 'List Playlists', endpoint: '/playlists', method: 'GET' }
    ],
    graphql: [
        {
            name: 'Get Users',
            query: `
                query {
                    usuarios {
                        id
                        nome
                        idade
                    }
                }
            `
        },
        {
            name: 'Get Songs',
            query: `
                query {
                    musicas {
                        id
                        nome
                        artista
                        duracaoSegundos
                    }
                }
            `
        }
    ],
    soap: [
        { name: 'List Users', operation: 'listar_usuarios' },
        { name: 'List Songs', operation: 'listar_musicas' },
        { name: 'Get Stats', operation: 'obter_estatisticas' }
    ]
};

// Charts
let responseTimeChart;
let rpsChart;

// Current test state
let currentService = null;
let testRunning = false;
let testResults = {};
let startTime = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    initializeCharts();
    setupEventListeners();
});

function initializeCharts() {
    // Response Time Chart
    const responseTimeCtx = document.getElementById('responseTimeChart').getContext('2d');
    responseTimeChart = new Chart(responseTimeCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Response Time (ms)',
                data: [],
                borderColor: '#0d6efd',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // RPS Chart
    const rpsCtx = document.getElementById('rpsChart').getContext('2d');
    rpsChart = new Chart(rpsCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Requests per Second',
                data: [],
                borderColor: '#198754',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function setupEventListeners() {
    // Service selection
    document.querySelectorAll('.list-group-item').forEach(item => {
        item.addEventListener('click', (e) => {
            document.querySelectorAll('.list-group-item').forEach(i => i.classList.remove('active'));
            e.target.classList.add('active');
            currentService = e.target.dataset.service;
        });
    });

    // Test configuration form
    document.getElementById('testConfig').addEventListener('submit', (e) => {
        e.preventDefault();
        if (!currentService) {
            alert('Please select a service first');
            return;
        }
        startTest();
    });
}

async function startTest() {
    if (testRunning) return;
    
    const config = {
        users: parseInt(document.getElementById('numUsers').value),
        spawnRate: parseInt(document.getElementById('spawnRate').value),
        duration: parseInt(document.getElementById('duration').value),
        thinkTime: parseFloat(document.getElementById('thinkTime').value)
    };

    testRunning = true;
    startTime = Date.now();
    testResults = {};
    resetCharts();
    updateUI();

    // Initialize test results for each scenario
    TEST_SCENARIOS[currentService].forEach(scenario => {
        testResults[scenario.name] = {
            requests: 0,
            fails: 0,
            totalTime: 0,
            minTime: Infinity,
            maxTime: 0,
            times: []
        };
    });

    // Start the test
    const promises = [];
    for (let i = 0; i < config.users; i++) {
        promises.push(runUserScenario(config));
    }

    await Promise.all(promises);
    testRunning = false;
    updateUI();
}

async function runUserScenario(config) {
    const scenarios = TEST_SCENARIOS[currentService];
    const endTime = startTime + (config.duration * 1000);

    while (Date.now() < endTime) {
        for (const scenario of scenarios) {
            try {
                const startTime = performance.now();
                await executeScenario(scenario);
                const endTime = performance.now();
                const duration = endTime - startTime;

                updateTestResults(scenario.name, duration);
                updateCharts();
                updateUI();

                await sleep(config.thinkTime * 1000);
            } catch (error) {
                console.error(`Error in scenario ${scenario.name}:`, error);
                updateTestResults(scenario.name, 0, true);
                updateUI();
            }
        }
    }
}

async function executeScenario(scenario) {
    switch (currentService) {
        case 'rest':
            return await executeRestScenario(scenario);
        case 'graphql':
            return await executeGraphQLScenario(scenario);
        case 'soap':
            return await executeSOAPScenario(scenario);
        default:
            throw new Error(`Unknown service type: ${currentService}`);
    }
}

async function executeRestScenario(scenario) {
    const response = await fetch(`${ENDPOINTS.rest}${scenario.endpoint}`, {
        method: scenario.method,
        headers: {
            'Content-Type': 'application/json'
        }
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
}

async function executeGraphQLScenario(scenario) {
    const response = await fetch(ENDPOINTS.graphql, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            query: scenario.query
        })
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    if (data.errors) throw new Error(data.errors[0].message);
    return data;
}

async function executeSOAPScenario(scenario) {
    const soapEnvelope = createSoapEnvelope(scenario.operation);
    const response = await fetch(ENDPOINTS.soap, {
        method: 'POST',
        headers: {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': `http://streaming.soap.service/${scenario.operation}`
        },
        body: soapEnvelope
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const xmlText = await response.text();
    const result = parseSoapResponse(xmlText, scenario.operation);
    
    if (result.error) {
        throw new Error(`SOAP Fault: ${result.error}`);
    }
    
    return result.data;
}

function createSoapEnvelope(operation) {
    return `<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="http://streaming.soap.service">
    <soap:Header/>
    <soap:Body>
        <tns:${operation} xmlns:tns="http://streaming.soap.service"/>
    </soap:Body>
</soap:Envelope>`;
}

function parseSoapResponse(xmlText, operation) {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(xmlText, "text/xml");
    
    // Check for SOAP Fault
    const faultElement = xmlDoc.getElementsByTagName('soap:Fault')[0] || 
                        xmlDoc.getElementsByTagName('Fault')[0];
    
    if (faultElement) {
        const faultString = faultElement.getElementsByTagName('faultstring')[0]?.textContent || 
                          'SOAP Fault occurred';
        return { error: faultString };
    }

    // Get the response element
    const responseElement = xmlDoc.getElementsByTagName(`${operation}Response`)[0];
    if (!responseElement) {
        return { error: `No response element found for operation ${operation}` };
    }

    // Parse the response data
    const data = xmlToJson(responseElement);
    return { data };
}

function xmlToJson(xml) {
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
                obj[nodeName] = xmlToJson(item);
            } else {
                if (typeof obj[nodeName].push === 'undefined') {
                    const old = obj[nodeName];
                    obj[nodeName] = [];
                    obj[nodeName].push(old);
                }
                obj[nodeName].push(xmlToJson(item));
            }
        }
    }
    return obj;
}

function updateTestResults(scenarioName, duration, failed = false) {
    const result = testResults[scenarioName];
    result.requests++;
    if (failed) {
        result.fails++;
    } else {
        result.totalTime += duration;
        result.minTime = Math.min(result.minTime, duration);
        result.maxTime = Math.max(result.maxTime, duration);
        result.times.push(duration);
    }
}

function updateCharts() {
    const now = new Date();
    const timeLabel = now.toLocaleTimeString();

    // Update Response Time Chart
    responseTimeChart.data.labels.push(timeLabel);
    responseTimeChart.data.datasets[0].data.push(
        Object.values(testResults).reduce((sum, r) => sum + (r.totalTime / r.requests), 0)
    );
    if (responseTimeChart.data.labels.length > 20) {
        responseTimeChart.data.labels.shift();
        responseTimeChart.data.datasets[0].data.shift();
    }
    responseTimeChart.update();

    // Update RPS Chart
    rpsChart.data.labels.push(timeLabel);
    const totalRequests = Object.values(testResults).reduce((sum, r) => sum + r.requests, 0);
    const elapsedSeconds = (Date.now() - startTime) / 1000;
    rpsChart.data.datasets[0].data.push(totalRequests / elapsedSeconds);
    if (rpsChart.data.labels.length > 20) {
        rpsChart.data.labels.shift();
        rpsChart.data.datasets[0].data.shift();
    }
    rpsChart.update();
}

function updateUI() {
    // Update success/failure counts
    const totalRequests = Object.values(testResults).reduce((sum, r) => sum + r.requests, 0);
    const totalFails = Object.values(testResults).reduce((sum, r) => sum + r.fails, 0);
    document.getElementById('successCount').textContent = `${totalRequests - totalFails} Success`;
    document.getElementById('failureCount').textContent = `${totalFails} Failures`;

    // Update results table
    const tbody = document.getElementById('resultsTable');
    tbody.innerHTML = '';
    
    Object.entries(testResults).forEach(([name, result]) => {
        const row = document.createElement('tr');
        const elapsedSeconds = (Date.now() - startTime) / 1000;
        const rps = result.requests / elapsedSeconds;
        const stats = calculateStatistics(result.times);
        
        row.innerHTML = `
            <td>${currentService.toUpperCase()}</td>
            <td>${name}</td>
            <td>${result.requests}</td>
            <td>${result.fails}</td>
            <td>${stats ? stats.p90.toFixed(2) : 0}</td>
            <td>${stats ? stats.p95.toFixed(2) : 0}</td>
            <td>${stats ? stats.p99.toFixed(2) : 0}</td>
            <td>${stats ? stats.mean.toFixed(2) : 0}</td>
            <td>${stats ? stats.stdDev.toFixed(2) : 0}</td>
            <td>${rps.toFixed(2)}</td>
        `;
        tbody.appendChild(row);
    });
}

function resetCharts() {
    responseTimeChart.data.labels = [];
    responseTimeChart.data.datasets[0].data = [];
    responseTimeChart.update();

    rpsChart.data.labels = [];
    rpsChart.data.datasets[0].data = [];
    rpsChart.update();
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Add statistical functions
function calculatePercentile(data, percentile) {
    const sortedData = [...data].sort((a, b) => a - b);
    const index = Math.ceil((percentile / 100) * sortedData.length) - 1;
    return sortedData[index];
}

function calculateStatistics(times) {
    if (!times.length) return null;
    
    const sortedTimes = [...times].sort((a, b) => a - b);
    return {
        min: sortedTimes[0],
        max: sortedTimes[sortedTimes.length - 1],
        p50: calculatePercentile(times, 50),
        p90: calculatePercentile(times, 90),
        p95: calculatePercentile(times, 95),
        p99: calculatePercentile(times, 99),
        mean: times.reduce((a, b) => a + b, 0) / times.length,
        stdDev: Math.sqrt(
            times.reduce((sq, n) => sq + Math.pow(n - (times.reduce((a, b) => a + b, 0) / times.length), 2), 0) / times.length
        )
    };
}

// Add health check function
async function checkServiceHealth(serviceType) {
    const healthElement = document.getElementById(`${serviceType}Health`);
    healthElement.textContent = 'Status: Checking...';
    
    try {
        let response;
        switch (serviceType) {
            case 'rest':
                response = await fetch(`${ENDPOINTS.rest}/usuarios`);
                break;
            case 'graphql':
                response = await fetch(ENDPOINTS.graphql, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: '{ usuarios { id nome } }'
                    })
                });
                break;
            case 'soap':
                const soapEnvelope = createSoapEnvelope('listar_usuarios');
                response = await fetch(ENDPOINTS.soap, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'text/xml; charset=utf-8',
                        'SOAPAction': '"http://streaming.soap.service/listar_usuarios"'
                    },
                    body: soapEnvelope
                });
                break;
        }
        
        if (response.ok) {
            healthElement.textContent = 'Status: Healthy ✅';
            healthElement.style.color = 'green';
        } else {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
    } catch (error) {
        healthElement.textContent = `Status: Unhealthy ❌ (${error.message})`;
        healthElement.style.color = 'red';
    }
}

// Update the table headers in the HTML
document.addEventListener('DOMContentLoaded', () => {
    const tableHeaders = document.querySelector('#resultsTable thead tr');
    tableHeaders.innerHTML = `
        <th>Service</th>
        <th>Scenario</th>
        <th>Requests</th>
        <th>Failures</th>
        <th>P90 (ms)</th>
        <th>P95 (ms)</th>
        <th>P99 (ms)</th>
        <th>Mean (ms)</th>
        <th>Std Dev (ms)</th>
        <th>RPS</th>
    `;
}); 