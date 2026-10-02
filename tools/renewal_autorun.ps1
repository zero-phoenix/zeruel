<#
.SYNOPSIS
    Real OAuth Permission Renewal Autorun Tool for Zeruel Synthetic Probe.
    Opens the default browser (with David's active Google session) using the deployed web/app.js autorun:
    https://zeruel-synthetic-probe.onrender.com/#autorun=<32 hex nuevo>
    Observes execution via screen OCR, verifies synthetic_success or error, and records to log.
    Never touches, reads, or exposes secrets or credentials.
#>

param(
    [string]$TaskId = "",
    [string]$LogPath = "D:\SystemHope\renewal\log.txt",
    [string]$BaseUrl = "https://zeruel-synthetic-probe.onrender.com",
    [int]$TimeoutSeconds = 180,
    [string]$HintFile = (Join-Path $HOME ".zeruel-private\renewal_hint.txt")
)

$ErrorActionPreference = "Stop"

# 1. Generate new 32-character hexadecimal TaskId if not specified
if (-not $TaskId -or $TaskId.Length -ne 32) {
    $bytes = New-Object byte[] 16
    [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $TaskId = ($bytes | ForEach-Object { $_.ToString("x2") }) -join ""
}

$LogDir = Split-Path -Path $LogPath -Parent
if ($LogDir -and -not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$autorunUrl = "$BaseUrl/#autorun=$TaskId"
# El hint (cuenta de Google) vive solo en un archivo privado local y solo viaja en el fragmento.
if (Test-Path $HintFile) {
    $hint = (Get-Content $HintFile -Raw).Trim()
    if ($hint) { $autorunUrl += "&hint=" + [uri]::EscapeDataString($hint) }
}
Write-Host "Iniciando autorun en navegador Brave (TaskId $TaskId)"
Write-Host "TaskId generado: $TaskId"

# 2. Launch in Brave browser (with David's active Google session)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$launchScript = Join-Path $scriptDir "launch_brave.py"
python $launchScript $autorunUrl

# 3. Observe execution via screen/window OCR helper without secrets
$observeScript = Join-Path $scriptDir "observe_probe.py"

Write-Host "Esperando ejecucion y observando estado de la sonda..."
$resultJson = python $observeScript $TaskId $TimeoutSeconds $LogPath
$jsonLine = if ($resultJson -is [array]) {
    ($resultJson | Where-Object { $_ -match '^\s*\{.*\}\s*$' } | Select-Object -Last 1)
} else {
    $resultJson
}

try {
    $result = $jsonLine | ConvertFrom-Json
    Write-Host "Resultado: $($result.state) - $($result.detail)"
    if ($result.state -eq "synthetic_success") {
        Write-Host "PRUEBA EXITOSA: $TaskId -> synthetic_success"
        exit 0
    } elseif ($result.state -eq "account_picker") {
        Write-Error "DETENCION: Google solicito elegir cuenta interactiva."
        exit 2
    } elseif ($result.state -eq "paused") {
        Write-Error "DETENCION: El servidor reporto estado 'paused' (reinicio detectado)."
        exit 3
    } else {
        Write-Error "DETENCION: Estado inesperado: $($result.state)"
        exit 1
    }
} catch {
    Write-Host "Salida cruda del observador: $resultJson"
    exit 1
}
