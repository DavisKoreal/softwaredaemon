#!/usr/bin/env pwsh
# PowerShell script to start both frontend and backend

Write-Host "Starting Task Tree Visualizer Demo" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Change to the task-tree-visualizer directory
Set-Location "C:\Users\Administrator\Desktop\softwaredaemon\task-tree-visualizer"

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

# Start the frontend in the background
Write-Host "Starting frontend on http://localhost:3000..." -ForegroundColor Cyan
Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WindowStyle Minimized

# Wait a moment for the frontend to start
Start-Sleep -Seconds 3

# Change to the backend directory
Set-Location "C:\Users\Administrator\Desktop\softwaredaemon\v0x1"

# Start the WebSocket server
Write-Host "Starting WebSocket server on ws://localhost:8000..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "WebSocket: ws://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "The frontend should automatically connect to the WebSocket server." -ForegroundColor Yellow
Write-Host "You can also run the full daemon with: python 0x1daemon.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the servers" -ForegroundColor Red

# Run the test WebSocket server
python test_websocket.py