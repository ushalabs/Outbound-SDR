$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) { python -m venv .venv; if ($LASTEXITCODE) { throw 'Virtual environment creation failed' } }
    & .\.venv\Scripts\python.exe -m pip install -r backend\requirements.lock.txt
    if ($LASTEXITCODE) { throw 'Locked backend dependency installation failed' }
    & .\.venv\Scripts\python.exe -m pip install --no-deps -e './backend[dev]'
    if ($LASTEXITCODE) { throw 'Backend dependency installation failed' }
    Push-Location frontend
    try { npm ci; if ($LASTEXITCODE) { throw 'Frontend dependency installation failed' } } finally { Pop-Location }
} finally { Pop-Location }
