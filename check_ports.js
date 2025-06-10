const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

const ports = [8000, 8001, 8003, 8004, 50051, 8080];

async function checkAndKillPorts() {
    console.log('Checking for processes using our service ports...');
    
    for (const port of ports) {
        try {
            // For Windows
            const { stdout } = await execPromise(`netstat -ano | findstr :${port}`);
            if (stdout) {
                const lines = stdout.split('\n');
                for (const line of lines) {
                    if (line.includes('LISTENING')) {
                        const pid = line.trim().split(/\s+/).pop();
                        console.log(`Found process ${pid} using port ${port}`);
                        try {
                            await execPromise(`taskkill /F /PID ${pid}`);
                            console.log(`✅ Killed process ${pid} using port ${port}`);
                        } catch (killError) {
                            console.error(`❌ Failed to kill process ${pid}: ${killError.message}`);
                        }
                    }
                }
            }
        } catch (error) {
            if (!error.message.includes('no connections')) {
                console.error(`Error checking port ${port}: ${error.message}`);
            }
        }
    }
    
    console.log('\nPort check complete!');
}

// Run if called directly
if (require.main === module) {
    checkAndKillPorts().then(() => {
        console.log('You can now start your services!');
    });
}

module.exports = { checkAndKillPorts }; 