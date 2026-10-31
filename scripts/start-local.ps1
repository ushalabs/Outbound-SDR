param([switch]$SkipMigrations)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Run .\scripts\setup-local.ps1 first.' }
$nodePath = (Get-Command node).Source
$vitePath = Join-Path $projectRoot 'frontend\node_modules\vite\bin\vite.js'
if (-not (Test-Path -LiteralPath $vitePath)) { throw 'Run setup-local.ps1 to install frontend dependencies.' }
foreach ($port in @(8000, 5173)) {
    if (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) { throw "Port $port is in use. Stop the existing service first." }
}
$artifactPath = Join-Path $projectRoot 'artifacts'
New-Item -ItemType Directory -Force -Path $artifactPath | Out-Null
if (-not $SkipMigrations -and (Test-Path -LiteralPath (Join-Path $projectRoot 'backend\alembic.ini'))) {
    Push-Location (Join-Path $projectRoot 'backend')
    try { & $pythonPath -m alembic upgrade head; if ($LASTEXITCODE) { throw 'Migration failed' } } finally { Pop-Location }
}
$startedProcesses = @()
try {
$backendProcess = Start-Process -FilePath $pythonPath -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000') -WorkingDirectory (Join-Path $projectRoot 'backend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $artifactPath 'backend.log') -RedirectStandardError (Join-Path $artifactPath 'backend-error.log')
$startedProcesses += $backendProcess
$workerProcess = Start-Process -FilePath $pythonPath -ArgumentList @('-m', 'app.worker') -WorkingDirectory (Join-Path $projectRoot 'backend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $artifactPath 'worker.log') -RedirectStandardError (Join-Path $artifactPath 'worker-error.log')
$startedProcesses += $workerProcess
$frontendProcess = Start-Process -FilePath $nodePath -ArgumentList @(('"' + $vitePath + '"'), '--host', '127.0.0.1', '--port', '5173', '--strictPort') -WorkingDirectory (Join-Path $projectRoot 'frontend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $artifactPath 'frontend.log') -RedirectStandardError (Join-Path $artifactPath 'frontend-error.log')
$startedProcesses += $frontendProcess
$ready = $false
for ($attempt = 0; $attempt -lt 25; $attempt++) {
    foreach ($service in $startedProcesses) {
        $service.Refresh()
        if ($service.HasExited) { throw 'A local service exited. Inspect artifacts logs.' }
    }
    try {
        $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/health' -TimeoutSec 1
        $front = Invoke-WebRequest -Uri 'http://127.0.0.1:5173' -TimeoutSec 1 -UseBasicParsing
        if ($health.status -eq 'ok' -and $front.StatusCode -eq 200) { $ready = $true; break }
    } catch { }
    Start-Sleep -Milliseconds 400
}
if (-not $ready) { throw 'Services did not become ready. Inspect artifacts logs.' }
} catch {
    foreach ($service in $startedProcesses) { Stop-Process -Id $service.Id -ErrorAction SilentlyContinue }
    throw
}
@{ backend = $backendProcess.Id; frontend = $frontendProcess.Id; worker = $workerProcess.Id } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $artifactPath 'local-processes.json')
Write-Host "Backend PID: $($backendProcess.Id); frontend PID: $($frontendProcess.Id); worker PID: $($workerProcess.Id)"
Write-Host 'Open http://127.0.0.1:5173 and http://127.0.0.1:8000/docs'
