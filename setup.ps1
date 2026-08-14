$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python 3.12 is required and must be available as 'python'."
}
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    throw "Node.js 22 LTS is required and must be available as 'node'."
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "npm is required and must be available as 'npm'."
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
}
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm install
Push-Location frontend
npm install
Pop-Location
npx playwright install chromium
Write-Host "Setup complete. Use .\dev.ps1 all to start both services."
