const UnifiedClient = require('./unified_client');

// Create a new unified client
const client = new UnifiedClient({
    users: 5,           // Number of concurrent users
    spawnRate: 1,       // Users spawned per second
    duration: 30,       // Test duration in seconds
    thinkTime: 1        // Think time between requests in seconds
});

// Define test scenarios
const testScenarios = {
    // REST API test scenario
    rest: [
        { type: 'REST', operation: '/usuarios', params: { method: 'GET' } },
        { type: 'REST', operation: '/musicas', params: { method: 'GET' } },
        { type: 'REST', operation: '/playlists', params: { method: 'GET' } }
    ],

    // GraphQL API test scenario
    graphql: [
        {
            type: 'GraphQL',
            operation: `
                query {
                    usuarios {
                        id
                        nome
                        idade
                    }
                }
            `,
            params: { variables: {} }
        },
        {
            type: 'GraphQL',
            operation: `
                query {
                    musicas {
                        id
                        nome
                        artista
                        duracaoSegundos
                    }
                }
            `,
            params: { variables: {} }
        }
    ],

    // SOAP API test scenario
    soap: [
        { type: 'SOAP', operation: 'listar_usuarios', params: {} },
        { type: 'SOAP', operation: 'listar_musicas', params: {} },
        { type: 'SOAP', operation: 'obter_estatisticas', params: {} }
    ]
};

// Run load tests for each service type
async function runAllTests() {
    console.log('🚀 Starting comprehensive load tests...\n');

    // Test REST API
    console.log('Testing REST API...');
    await client.runLoadTest(testScenarios.rest);

    // Test GraphQL API
    console.log('\nTesting GraphQL API...');
    await client.runLoadTest(testScenarios.graphql);

    // Test SOAP API
    console.log('\nTesting SOAP API...');
    await client.runLoadTest(testScenarios.soap);

    console.log('\n✨ All load tests completed!');
}

// Run the tests
runAllTests().catch(console.error); 