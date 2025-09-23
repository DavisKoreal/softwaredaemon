# PowerShell script to fix the UI setup for the Task Agent project and ensure the interface runs
# Logs all actions to task-agent-project/setup_fix.log

# Define project directory and log file
$projectDir = Join-Path $PSScriptRoot "task-agent-project"
$logFile = Join-Path $projectDir "setup_fix.log"

# Function to log messages
function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "$timestamp : $Message"
    # Ensure the project directory exists before writing to log
    if (-not (Test-Path $projectDir)) {
        New-Item -ItemType Directory -Path $projectDir -Force | Out-Null
    }
    $logMessage | Out-File -FilePath $logFile -Append -Encoding UTF8 -Force
    Write-Host $logMessage
}

# Start logging
Write-Log "Starting UI setup fix..."

# Change to project directory
if (-not (Test-Path $projectDir)) {
    Write-Log "ERROR: Project directory not found: $projectDir"
    exit 1
}
Set-Location $projectDir
Write-Log "Changed to project directory: $projectDir"

# Check for Node.js and npm
Write-Log "Checking for Node.js and npm installation..."
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Log "ERROR: Node.js not found. Please install Node.js 18+ and ensure it's in PATH."
    exit 1
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Log "ERROR: npm not found. Please install Node.js 18+ and ensure npm is in PATH."
    exit 1
}
Write-Log "Node.js found: $(node --version)"
Write-Log "npm found: $(npm --version)"

# Clear npm cache to resolve registry issues
Write-Log "Clearing npm cache..."
try {
    $npmCacheOutput = npm cache clean --force *>&1
    Write-Log "Successfully cleared npm cache"
    $npmCacheOutput | Out-File -FilePath $logFile -Append -Encoding UTF8
} catch {
    Write-Log "ERROR: Failed to clear npm cache. Error: $_"
    exit 1
}

# Update package.json with corrected dependency versions
Write-Log "Updating package.json with corrected dependency versions..."
$packageJsonContent = @"
{
  "name": "task-agent-ui",
  "version": "1.0.0",
  "scripts": {
    "start": "vite",
    "build": "tsc && vite build"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "lucide-react": "^0.441.0",
    "@radix-ui/react-slot": "^1.1.0",
    "@radix-ui/react-scroll-area": "^1.1.0",
    "@radix-ui/react-button": "^1.1.0",
    "class-variance-authority": "^0.7.0",
    "tailwindcss": "^3.4.10",
    "vite": "^5.4.8",
    "@vitejs/plugin-react": "^4.3.1"
  },
  "devDependencies": {
    "typescript": "^5.5.4",
    "@types/react": "^18.3.5",
    "@types/react-dom": "^18.3.0"
  }
}
"@
Set-Content -Path (Join-Path $projectDir "package.json") -Value $packageJsonContent -Encoding UTF8
Write-Log "Updated package.json"

# Install Node.js dependencies
Write-Log "Installing Node.js dependencies..."
try {
    $npmOutput = npm install *>&1
    Write-Log "Successfully installed Node.js dependencies"
    $npmOutput | Out-File -FilePath $logFile -Append -Encoding UTF8
} catch {
    Write-Log "ERROR: Failed to install Node.js dependencies. Error: $_"
    Write-Log "Check the npm error log at: C:\Users\Administrator\AppData\Local\npm-cache\_logs\"
    exit 1
}

# Install Vite globally as a fallback
Write-Log "Installing Vite globally..."
try {
    $viteInstallOutput = npm install -g vite@5.4.8 *>&1
    Write-Log "Successfully installed Vite globally"
    $viteInstallOutput | Out-File -FilePath $logFile -Append -Encoding UTF8
} catch {
    Write-Log "WARNING: Failed to install Vite globally. Error: $_"
    Write-Log "Continuing, as local Vite installation may still work."
}

# Initialize ShadCN
Write-Log "Initializing ShadCN UI..."
try {
    $shadcnOutput = npx shadcn@latest init --yes *>&1
    Write-Log "Successfully initialized ShadCN UI"
    $shadcnOutput | Out-File -FilePath $logFile -Append -Encoding UTF8
} catch {
    Write-Log "ERROR: Failed to initialize ShadCN UI. Error: $_"
    exit 1
}

# Add ShadCN components
$components = @("card", "button", "scroll-area", "badge")
foreach ($component in $components) {
    Write-Log "Adding ShadCN component: $component"
    try {
        $componentOutput = npx shadcn@latest add $component --yes *>&1
        Write-Log "Successfully added ShadCN component: $component"
        $componentOutput | Out-File -FilePath $logFile -Append -Encoding UTF8
    } catch {
        Write-Log "ERROR: Failed to add ShadCN component: $component. Error: $_"
        exit 1
    }
}

# Verify Vite installation
Write-Log "Verifying Vite installation..."
if (-not (Get-Command vite -ErrorAction SilentlyContinue)) {
    Write-Log "WARNING: Vite command not found in PATH. Ensure node_modules/.bin is in PATH or Vite is installed globally."
    Write-Log "Attempting to run Vite from node_modules..."
    $vitePath = Join-Path $projectDir "node_modules/.bin/vite"
    if (-not (Test-Path $vitePath)) {
        Write-Log "ERROR: Vite not found in node_modules. Installation may have failed."
        exit 1
    }
} else {
    Write-Log "Vite command found"
}

# Provide instructions to run the UI
Write-Log "Setup fix completed successfully!"
Write-Log "To run the user interface:"
Write-Log "1. Ensure the Python server is running in a separate terminal:"
Write-Log "   cd $projectDir"
Write-Log "   python taskagent.py"
Write-Log "2. Start the React UI in this terminal:"
Write-Log "   cd $projectDir"
Write-Log "   npm run start"
Write-Log "3. Open http://localhost:5173 in your browser to view the dashboard."
Write-Log "Note: If 'vite' is still not recognized, run 'npx vite' instead of 'npm run start'."
Write-Log "Note: Ensure your DEEPSEEK_API_KEY is set in .env before running the Python server."

# End of script
Write-Log "PowerShell UI setup fix script execution completed."