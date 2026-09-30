param([switch]$AllowAdditionalProcesses)

# Optional Remote Desktop Commander startup. Requires an explicit exception to
# the owner's one-background-process limit: remote agent + local MCP child,
# in addition to any existing ADB server. This has not been tested on Windows.
$ErrorActionPreference = 'Stop'
if (!$AllowAdditionalProcesses) {
    throw 'Se requiere permiso explicito para procesos adicionales antes de arrancar el agente remoto.'
}
$zrNode = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
$zrNpx = Join-Path $env:USERPROFILE '.zeruel-tools\npm-10.9.4\package\bin\npx-cli.js'
foreach ($zrFile in @($zrNode, $zrNpx)) {
    if (!(Test-Path -LiteralPath $zrFile -PathType Leaf)) {
        throw 'Falta Node o npm portable. Detener.'
    }
}

$zrOldPath = $env:Path
$zrOldSkipDownload = $env:PUPPETEER_SKIP_DOWNLOAD
try {
    $env:Path = [IO.Path]::GetDirectoryName($zrNode) + ';' + $env:Path
    # Avoid downloading Chromium. Other package dependencies still install.
    $env:PUPPETEER_SKIP_DOWNLOAD = 'true'
    Write-Host 'Version fijada: Desktop Commander 0.2.52. Puede descargar otras dependencias.'
    Write-Host 'Completa la autorizacion en tu navegador. No compartas codigos ni tokens.'
    Write-Host 'Conserva esta consola abierta; Ctrl+C detiene este agente. No apaga la PC.'
    & $zrNode $zrNpx --yes '@wonderwhy-er/desktop-commander@0.2.52' remote --no-persist-session --disable-no-sleep
    if ($LASTEXITCODE -ne 0) { throw 'El agente termino con error. No repetir automaticamente.' }
} finally {
    $env:Path = $zrOldPath
    if ($null -eq $zrOldSkipDownload) {
        Remove-Item Env:PUPPETEER_SKIP_DOWNLOAD -ErrorAction SilentlyContinue
    } else {
        $env:PUPPETEER_SKIP_DOWNLOAD = $zrOldSkipDownload
    }
}
