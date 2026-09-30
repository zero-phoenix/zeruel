# Bootstrap npm/npx only, using the existing Codex Node runtime.
# Official npm 10.9.4 tarball; integrity pinned to registry metadata.
# No administrator access, global installation, or persistent PATH changes.
$ErrorActionPreference = 'Stop'
$zrNode = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
if (!(Test-Path -LiteralPath $zrNode -PathType Leaf)) {
    throw 'No se encontro el Node portable de Codex. Detener.'
}
$zrTar = (Get-Command tar.exe -ErrorAction Stop).Source
$zrRoot = Join-Path $env:USERPROFILE '.zeruel-tools\npm-10.9.4'
New-Item -ItemType Directory -Force -Path $zrRoot | Out-Null
$zrArchive = Join-Path $zrRoot 'npm-10.9.4.tgz'
Invoke-WebRequest -UseBasicParsing -Uri 'https://registry.npmjs.org/npm/-/npm-10.9.4.tgz' -OutFile $zrArchive
$zrHasher = [System.Security.Cryptography.SHA512]::Create()
try {
    $zrDigest = [Convert]::ToBase64String($zrHasher.ComputeHash([IO.File]::ReadAllBytes($zrArchive)))
} finally {
    $zrHasher.Dispose()
}
if ($zrDigest -cne 'OnUG836FwboQIbqtefDNlyR0gTHzIfwRfE3DuiNewBvnMnWEpB0VEXwBlFVgqpNzIgYo/MHh3d2Hel/pszapAA==') {
    throw 'Integridad SHA-512 incorrecta. No extraer ni ejecutar.'
}
& $zrTar -xzf $zrArchive -C $zrRoot
if ($LASTEXITCODE -ne 0) { throw 'Fallo al extraer npm. Detener.' }
Remove-Item -LiteralPath $zrArchive
& $zrNode (Join-Path $zrRoot 'package\bin\npx-cli.js') --version
if ($LASTEXITCODE -ne 0) { throw 'npx no supero la comprobacion. Detener.' }

# Only this PowerShell session. Child processes can locate node.exe.
$env:Path = [IO.Path]::GetDirectoryName($zrNode) + ';' + $env:Path
function global:npx {
    & (Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe') (Join-Path $env:USERPROFILE '.zeruel-tools\npm-10.9.4\package\bin\npx-cli.js') @args
}
Write-Host 'npm/npx portable listo para esta consola. Version esperada: 10.9.4.'
Write-Host 'El agente remoto de Desktop Commander todavia no se ha instalado ni iniciado.'
