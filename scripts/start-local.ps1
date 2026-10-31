param([switch]$SkipMigrations)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Run .\scripts\setup-local.ps1 first.' }
foreach ($port in @(8000, 5173)) {
    if (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) { throw "Port $port is in use. Stop the existing service first." }
}
$artifactPath = Join-Path $projectRoot 'artifacts'
New-Item -ItemType Directory -Force -Path $artifactPath | Out-Null
if (-not $SkipMigrations -and (Test-Path -LiteralPath (Join-Path $projectRoot 'backend\alembic.ini'))) {
    Push-Location (Join-Path $projectRoot 'backend')
    try { & $pythonPath -m alembic upgrade head; if ($LASTEXITCODE) { throw 'Migration failed' } } finally { Pop-Location }
}
$backendProcess = Start-Process -FilePath $pythonPath -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000') -WorkingDirectory (Join-Path $projectRoot 'backend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $artifactPath 'backend.log') -RedirectStandardError (Join-Path $artifactPath 'backend-error.log')
$nodePath = (Get-Command node).Source
$vitePath = Join-Path $projectRoot 'frontend\node_modules\vite\bin\vite.js'
$frontendProcess = Start-Process -FilePath $nodePath -ArgumentList @(('"' + $vitePath + '"'), '--host', '127.0.0.1', '--port', '5173', '--strictPort') -WorkingDirectory (Join-Path $projectRoot 'frontend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $artifactPath 'frontend.log') -RedirectStandardError (Join-Path $artifactPath 'frontend-error.log')
@{ backend = $backendProcess.Id; frontend = $frontendProcess.Id } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $artifactPath 'local-processes.json')
Write-Host "Backend PID: $($backendProcess.Id); frontend PID: $($frontendProcess.Id)"
Write-Host 'Open http://127.0.0.1:5173 and http://127.0.0.1:8000/docs'
