$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$processFile = Join-Path $projectRoot 'artifacts\local-processes.json'
if (-not (Test-Path -LiteralPath $processFile)) { Write-Host 'No recorded local services.'; return }
$recorded = Get-Content -LiteralPath $processFile -Raw | ConvertFrom-Json
foreach ($entry in $recorded.PSObject.Properties) {
    $serviceId = [int]$entry.Value
    $service = Get-CimInstance Win32_Process -Filter "ProcessId = $serviceId" -ErrorAction SilentlyContinue
    if ($service -and $service.CommandLine -and $service.CommandLine.IndexOf($projectRoot, [StringComparison]::OrdinalIgnoreCase) -ge 0) {
        Stop-Process -Id $serviceId -ErrorAction SilentlyContinue
        Write-Host "Stopped $($entry.Name) ($serviceId)"
    } elseif ($service) {
        Write-Host "Skipped $serviceId because it no longer belongs to this project."
    }
}
