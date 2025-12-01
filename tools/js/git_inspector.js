const { execSync } = require('child_process');

function getGitStatus() {
    try {
        // Check if git exists
        execSync("git --version", { stdio: 'ignore' });
        
        // Get status
        const statusOutput = execSync("git status --porcelain", { encoding: 'utf8' });
        
        const changes = [];
        statusOutput.split('\n').forEach(line => {
            if (line.length > 3) {
                const status = line.substring(0, 2);
                const file = line.substring(3);
                changes.push({ status, file });
            }
        });
        
        // Get branch
        const branch = execSync("git branch --show-current", { encoding: 'utf8' }).trim();
        
        return {
            branch: branch,
            changes: changes,
            clean: changes.length === 0
        };
    } catch (e) {
        if (e.message.includes("not a git repository")) {
             return { error: "Not a git repository" };
        }
        return { error: e.message };
    }
}

function main() {
    const args = process.argv.slice(2);
    const mode = args[1] || "status"; // args[0] is --mode usually
    
    // Simple arg parsing
    let currentMode = "status";
    for (let i = 0; i < args.length; i++) {
        if (args[i] === "--mode") {
            currentMode = args[i+1];
        }
    }
    
    if (currentMode === "status") {
        console.log(JSON.stringify(getGitStatus(), null, 2));
    } else {
        console.log(JSON.stringify({ error: `Unknown mode: ${currentMode}` }));
    }
}

main();
