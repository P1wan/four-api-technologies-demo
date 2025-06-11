// Test script for all services and clients
const RestClient = require('./rest/client');
const GraphQLClient = require('./graphql/client');
const GrpcClient = require('./grpc/client');
const SOAPClient = require('./soap/client');
const { waitForServices } = require('./wait_for_services');

// Test configuration
const config = {
    rest: {
        endpoint: 'http://localhost:8000'
    },
    graphql: {
        endpoint: 'http://localhost:8001/graphql'
    },
    grpc: {
        endpoint: 'http://localhost:8003'  // Using gRPC-Web proxy
    },
    soap: {
        endpoint: 'http://localhost:8004/soap'  // Fixed: added /soap suffix
    }
};

// Initialize clients
const restClient = new RestClient(config.rest.endpoint);
const graphqlClient = new GraphQLClient(config.graphql.endpoint);
const grpcClient = new GrpcClient(config.grpc.endpoint);
const soapClient = new SOAPClient(config.soap.endpoint);

// Test results storage
const testResults = {
    rest: { passed: 0, failed: 0, errors: [] },
    graphql: { passed: 0, failed: 0, errors: [] },
    grpc: { passed: 0, failed: 0, errors: [] },
    soap: { passed: 0, failed: 0, errors: [] }
};

// Helper function to run tests
async function runTest(name, testFn, service) {
    console.log(`\n🧪 Running test: ${name}`);
    try {
        await testFn();
        testResults[service].passed++;
        console.log(`✅ ${name}: PASSED`);
    } catch (error) {
        testResults[service].failed++;
        testResults[service].errors.push({ test: name, error: error.message });
        console.error(`❌ ${name}: FAILED - ${error.message}`);
    }
}

// REST API Tests - Fixed to handle paginated responses
async function testRestAPI() {
    console.log('\n📡 Testing REST API...');
    
    await runTest('List Users', async () => {
        const response = await restClient.listarUsuarios();
        // Fixed: REST returns paginated response with 'items' property
        if (!response.items || !Array.isArray(response.items)) {
            throw new Error('Expected paginated response with items array');
        }
        console.log(`   Found ${response.items.length} users (total: ${response.total})`);
    }, 'rest');

    await runTest('List Songs', async () => {
        const response = await restClient.listarMusicas();
        // Fixed: REST returns paginated response with 'items' property
        if (!response.items || !Array.isArray(response.items)) {
            throw new Error('Expected paginated response with items array');
        }
        console.log(`   Found ${response.items.length} songs (total: ${response.total})`);
    }, 'rest');

    await runTest('List Playlists', async () => {
        const response = await restClient.listarPlaylists();
        // Fixed: REST returns paginated response with 'items' property
        if (!response.items || !Array.isArray(response.items)) {
            throw new Error('Expected paginated response with items array');
        }
        console.log(`   Found ${response.items.length} playlists (total: ${response.total})`);
    }, 'rest');
}

// GraphQL Tests - Fixed to use correct field names
async function testGraphQL() {
    console.log('\n🔍 Testing GraphQL API...');
    
    await runTest('Query Users', async () => {
        // Fixed: Use correct field name 'usuarios' instead of 'users'
        const query = `
            query {
                usuarios {
                    id
                    nome
                    idade
                }
            }
        `;
        const result = await graphqlClient.executeQuery(query);
        if (!result.usuarios || !Array.isArray(result.usuarios)) {
            throw new Error('Expected usuarios array');
        }
        console.log(`   Found ${result.usuarios.length} users`);
    }, 'graphql');

    await runTest('Query Songs', async () => {
        // Fixed: Use correct field name 'musicas' instead of 'songs'
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
        const result = await graphqlClient.executeQuery(query);
        if (!result.musicas || !Array.isArray(result.musicas)) {
            throw new Error('Expected musicas array');
        }
        console.log(`   Found ${result.musicas.length} songs`);
    }, 'graphql');

    await runTest('Query User Playlists', async () => {
        // Fixed: Use correct GraphQL query structure
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
        const result = await graphqlClient.executeQuery(query);
        if (!result.playlistsUsuario || !Array.isArray(result.playlistsUsuario)) {
            throw new Error('Expected playlistsUsuario array');
        }
        console.log(`   Found ${result.playlistsUsuario.length} playlists for user1`);
    }, 'graphql');
}

// gRPC Tests
async function testGrpc() {
    console.log('\n🔄 Testing gRPC API...');
    
    await runTest('List Users', async () => {
        const result = await grpcClient.listarUsuarios();
        if (result.error) throw new Error(result.error);
    }, 'grpc');

    await runTest('List Songs', async () => {
        const result = await grpcClient.listarMusicas();
        if (result.error) throw new Error(result.error);
    }, 'grpc');

    await runTest('List Playlists', async () => {
        const result = await grpcClient.listarPlaylistsComMusica(1);
        if (result.error) throw new Error(result.error);
    }, 'grpc');
}

// SOAP Tests - Fixed endpoint and improved validation
async function testSOAP() {
    console.log('\n📦 Testing SOAP API...');
    
    await runTest('List Users', async () => {
        const result = await soapClient.listarUsuarios();
        if (!result || !Array.isArray(result)) {
            throw new Error('Expected array of users in response');
        }
        console.log(`   Found ${result.length} users`);
    }, 'soap');

    await runTest('List Songs', async () => {
        const result = await soapClient.listarMusicas();
        if (!result || !Array.isArray(result)) {
            throw new Error('Expected array of songs in response');
        }
        console.log(`   Found ${result.length} songs`);
    }, 'soap');

    await runTest('List Playlists', async () => {
        const result = await soapClient.listarPlaylistsUsuario('user1');
        if (!result || !Array.isArray(result)) {
            throw new Error('Expected array of playlists in response');
        }
        console.log(`   Found ${result.length} playlists for user1`);
    }, 'soap');

    await runTest('Get Statistics', async () => {
        const result = await soapClient.obterEstatisticas();
        if (!result || typeof result !== 'object') {
            throw new Error('Expected statistics object in response');
        }
        console.log('   Statistics retrieved successfully');
    }, 'soap');
}

// Main test runner
async function runTests() {
    console.log('Starting comprehensive service tests...\n');

    // Wait for all services to be ready
    await waitForServices();
    console.log('\nAll services are ready, starting tests...\n');

    // Test REST API
    console.log('Testing REST API...');
    await testRestAPI();

    // Test GraphQL API
    console.log('\n🔍 Testing GraphQL API...');
    await testGraphQL();

    // Test gRPC API
    console.log('\n🔄 Testing gRPC API...');
    await testGrpc();

    // Test SOAP API
    console.log('\n📦 Testing SOAP API...');
    await testSOAP();

    // Print summary
    console.log('\n📊 Test Summary:');
    console.log('================');
    
    let totalPassed = 0;
    let totalFailed = 0;
    
    for (const [service, results] of Object.entries(testResults)) {
        console.log(`\n${service.toUpperCase()}:`);
        console.log(`✅ Passed: ${results.passed}`);
        console.log(`❌ Failed: ${results.failed}`);
        
        totalPassed += results.passed;
        totalFailed += results.failed;
        
        if (results.errors.length > 0) {
            console.log('\nErrors:');
            results.errors.forEach(({ test, error }) => {
                console.log(`- ${test}: ${error}`);
            });
        }
    }
    
    console.log('\n🎯 OVERALL RESULTS:');
    console.log(`✅ Total Passed: ${totalPassed}`);
    console.log(`❌ Total Failed: ${totalFailed}`);
    console.log(`📊 Success Rate: ${totalPassed > 0 ? Math.round((totalPassed / (totalPassed + totalFailed)) * 100) : 0}%`);
    
    if (totalFailed === 0) {
        console.log('\n🎉 ALL TESTS PASSED! All services are working correctly.');
    } else {
        console.log('\n⚠️  Some tests failed. Check individual service implementations.');
    }
}

// Run the tests
runTests().catch(error => {
    console.error('Test execution failed:', error);
    process.exit(1);
}); 