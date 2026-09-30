# Owner sign-in for Antigravity CLI inside a GitHub Codespace: no local Docker, light on the PC.
# Same flow as tools/agy-login.ps1, but docker runs in the codespace (build the image there first:
# `docker build -t zeruel .`). The owner authorizes in Google and pastes the code here.
# The session stays in the codespace (~/agyhome); this script never reads or prints it.
# Run: powershell -ExecutionPolicy Bypass -File tools\agy-login-codespace.ps1 -Codespace <name>
param([Parameter(Mandatory)][string]$Codespace, [switch]$CheckOnly)

function Invoke-Remote([string]$script) {
  # Base64 avoids Windows PowerShell 5.1 quoting and CRLF problems.
  $b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(($script -replace "`r", '')))
  gh codespace ssh -c $Codespace -- "echo $b64 | base64 -d | bash" 2>$null
}

$start = @'
docker rm -f zeruel-agy-login >/dev/null 2>&1 || true
mkdir -p ~/agyhome
docker run -d --name zeruel-agy-login -u root -v ~/agyhome:/root zeruel sleep 900 >/dev/null
docker exec -i zeruel-agy-login sh -c 'cat > /tmp/run.sh' <<'EOS'
#!/bin/sh
cd /root && exec /opt/agy/agy -p 'Return only this JSON object: {"marker":"ZERUEL_OK","sum":42}' --output-format json
EOS
docker exec zeruel-agy-login touch /tmp/code
docker exec -d zeruel-agy-login sh -c "tail -f /tmp/code | script -qfc 'HOME=/root sh /tmp/run.sh' /tmp/out.log"
for i in $(seq 1 90); do
  sleep 1
  log=$(docker exec zeruel-agy-login cat /tmp/out.log 2>/dev/null | tr -d '\r\n')
  url=$(printf '%s' "$log" | grep -oP 'https://accounts\.google\.com/[^\s\x1b]+' | head -1)
  if [ -n "$url" ] && printf '%s' "$log" | grep -qi paste; then echo "URL=$url"; exit 0; fi
done
echo NOURL
'@

$finish = @'
echo __CODE__ | base64 -d | docker exec -i zeruel-agy-login sh -c 'cat >> /tmp/code'
for i in $(seq 1 60); do
  sleep 2
  log=$(docker exec zeruel-agy-login cat /tmp/out.log 2>/dev/null | tr -d '\r')
  printf '%s' "$log" | grep -q '"status"' && break
done
printf '%s' "$log" | grep -o '"status":"[A-Z_]*"' | tail -1
printf '%s' "$log" | grep -q ZERUEL_OK && echo ZERUEL_OK
docker rm -f zeruel-agy-login >/dev/null 2>&1
sudo test -s ~/agyhome/.gemini/antigravity-cli/antigravity-oauth-token && echo SESSION_SAVED || echo NO_SESSION
'@

Write-Host 'Preparando agy en el codespace (hasta 90 s)...'
$out = (Invoke-Remote $start) -join "`n"
$url = [regex]::Match($out, 'URL=(\S+)').Groups[1].Value
if (-not $url) { Write-Host 'No aparecio el enlace de Google (imagen sin construir o sesion ya iniciada?).'; exit 1 }
if ($CheckOnly) {
  Invoke-Remote 'docker rm -f zeruel-agy-login >/dev/null 2>&1' | Out-Null
  Write-Host 'CHECK_OK: agy mostro el enlace de Google; contenedor eliminado.'; exit 0
}
Start-Process msedge $url
$code = Read-Host 'En Edge pulsa Permitir, copia el codigo y pegalo aqui (tienes 60 s)'
$codeB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($code.Trim() + "`n"))
Write-Host 'Enviando el codigo y esperando la respuesta de agy...'
$result = (Invoke-Remote ($finish -replace '__CODE__', $codeB64)) -join ' '
Write-Host "Resultado: $result"
if ($result -match 'SESSION_SAVED') { Write-Host 'Listo: la sesion de agy quedo guardada en el codespace (no se muestra).' }
