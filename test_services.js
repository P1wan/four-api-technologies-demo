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
        endpoint: 'http://localhost:8004/soap'
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

// REST API Tests
async function testRestAPI() {
    console.log('\n📡 Testing REST API...');
    
    await runTest('List Users', async () => {
        const users = await restClient.listarUsuarios();
        if (!Array.isArray(users)) throw new Error('Expected array of users');
    }, 'rest');

    await runTest('List Songs', async () => {
        const songs = await restClient.listarMusicas();
        if (!Array.isArray(songs)) throw new Error('Expected array of songs');
    }, 'rest');

    await runTest('List Playlists', async () => {
        const playlists = await restClient.listarPlaylists();
        if (!Array.isArray(playlists)) throw new Error('Expected array of playlists');
    }, 'rest');
}

// GraphQL Tests
async function testGraphQL() {
    console.log('\n🔍 Testing GraphQL API...');
    
    await runTest('Query Users', async () => {
        const users = await graphqlClient.queryUsers();
        if (!Array.isArray(users)) throw new Error('Expected array of users');
    }, 'graphql');

    await runTest('Query Songs', async () => {
        const songs = await graphqlClient.querySongs();
        if (!Array.isArray(songs)) throw new Error('Expected array of songs');
    }, 'graphql');

    await runTest('Query Playlists', async () => {
        const playlists = await graphqlClient.queryPlaylists();
        if (!Array.isArray(playlists)) throw new Error('Expected array of playlists');
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

// SOAP Tests
async function testSOAP() {
    console.log('\n📦 Testing SOAP API...');
    
    await runTest('List Users', async () => {
        const result = await soapClient.executeOperation('listar_usuarios');
        if (!result || !Array.isArray(result)) throw new Error('Invalid response format');
    }, 'soap');

    await runTest('List Songs', async () => {
        const result = await soapClient.executeOperation('listar_musicas');
        if (!result || !Array.isArray(result)) throw new Error('Invalid response format');
    }, 'soap');

    await runTest('List Playlists', async () => {
        const result = await soapClient.executeOperation('listar_playlists');
        if (!result || !Array.isArray(result)) throw new Error('Invalid response format');
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
    
    for (const [service, results] of Object.entries(testResults)) {
        console.log(`\n${service.toUpperCase()}:`);
        console.log(`Passed: ${results.passed}`);
        console.log(`Failed: ${results.failed}`);
        
        if (results.errors.length > 0) {
            console.log('\nErrors:');
            results.errors.forEach(({ test, error }) => {
                console.log(`- ${test}: ${error}`);
            });
        }
    }
}

// Run the tests
runTests().catch(error => {
    console.error('Test execution failed:', error);
    process.exit(1);
}); 