/**
 * QuickAdd User Script Bridge for Obsidian Production OS.
 * Triggers the Python pipeline directly on the active Markdown script.
 */

const { exec } = require('child_process');
const path = require('path');

module.exports = async (params) => {
    const { app, quickAddApi } = params;
    const activeFile = app.workspace.getActiveFile();

    if (!activeFile) {
        new Notice("Production OS: No active note selected!");
        return;
    }

    const adapter = app.vault.adapter;
    const vaultBasePath = adapter.basePath || adapter.path;
    const targetScriptPath = path.join(vaultBasePath, activeFile.path);
    const pythonExe = path.join(vaultBasePath, '.venv', 'Scripts', 'python.exe');
    const cliScript = path.join(vaultBasePath, '08_AUTOMATION', 'Scripts', 'cli.py');

    new Notice(`🎬 Running Production OS Pipeline on: ${activeFile.name}...`, 5000);

    const command = `"${pythonExe}" "${cliScript}" pipeline "${targetScriptPath}"`;

    exec(command, (error, stdout, stderr) => {
        if (error) {
            console.error(`Production OS Error: ${stderr || error.message}`);
            new Notice(`❌ Pipeline failed: ${error.message}`, 8000);
            return;
        }
        console.log(`Production OS Output:\n${stdout}`);
        new Notice(`✔ Production OS Pipeline complete for ${activeFile.name}!`, 6000);
    });
};
