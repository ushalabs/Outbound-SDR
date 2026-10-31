$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location (Join-Path $projectRoot 'backend')
try {
    & ..\.venv\Scripts\python.exe -m pytest -m 'not integration' -q
    if ($LASTEXITCODE) { throw 'Backend tests failed' }
    & ..\.venv\Scripts\python.exe -m ruff check .
    if ($LASTEXITCODE) { throw 'Backend lint failed' }
} finally { Pop-Location }
Push-Location (Join-Path $projectRoot 'frontend')
try {
    npm test; if ($LASTEXITCODE) { throw 'Frontend tests failed' }
    npm run build; if ($LASTEXITCODE) { throw 'Frontend build failed' }
    npm run lint; if ($LASTEXITCODE) { throw 'Frontend lint failed' }
} finally { Pop-Location }
