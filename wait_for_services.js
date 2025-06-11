const http = require('http');

const services = [
    { name: 'REST API', port: 8000, path: '/docs' },
    { name: 'GraphQL API', port: 8001, path: '/graphql' },
    { name: 'SOAP API', port: 8004, path: '?wsdl' }
];

function checkService(service) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'localhost',
            port: service.port,
            path: service.path,
            method: 'GET',
            timeout: 5000  // Increased timeout to 5 seconds
        };

        const req = http.request(options, (res) => {
            if (res.statusCode >= 200 && res.statusCode < 500) {
                console.log(`✅ ${service.name} is ready (Status: ${res.statusCode})`);
                resolve(true);
            } else {
                console.log(`❌ ${service.name} returned unexpected status ${res.statusCode}`);
                resolve(false);
            }
        });

        req.on('error', (error) => {
            if (error.code === 'ECONNREFUSED') {
                console.log(`⏳ ${service.name} is not ready yet (Connection refused)`);
            } else if (error.code === 'ETIMEDOUT') {
                console.log(`⏳ ${service.name} request timed out`);
            } else {
                console.log(`⏳ ${service.name} error: ${error.message}`);
            }
            resolve(false);
        });

        req.on('timeout', () => {
            req.destroy();
            console.log(`⏳ ${service.name} request timed out after ${options.timeout}ms`);
            resolve(false);
        });

        req.end();
    });
}

async function waitForServices(maxAttempts = 30) {  // Added max attempts (30 * 2s = 60s max wait)
    console.log('Waiting for services to be ready...');
    let attempts = 0;
    
    while (attempts < maxAttempts) {
        console.log(`\nAttempt ${attempts + 1}/${maxAttempts}`);
        const results = await Promise.all(services.map(checkService));
        if (results.every(result => result)) {
            console.log('\nAll services are ready! 🎉');
            return true;
        }
        attempts++;
        if (attempts < maxAttempts) {
            console.log(`Waiting 2 seconds before next attempt...`);
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    }
    
    console.error('\n❌ Failed to connect to all services after maximum attempts');
    return false;
}

// If this script is run directly
if (require.main === module) {
    waitForServices().then((success) => {
        if (success) {
            console.log('You can now run the tests!');
            process.exit(0);
        } else {
            console.error('Service check failed. Please ensure all services are running.');
            process.exit(1);
        }
    });
}

module.exports = { waitForServices }; 