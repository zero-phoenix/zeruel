# Owner sign-in for Antigravity CLI inside a local test container (Windows, Docker Desktop).
# Opens the FULL official URL in the browser (terminals split long URLs) and forwards the
# code typed here. agy waits only 60 s and requires a TTY: `script` provides one.
# The session ends in <home>\.gemini\antigravity-cli\antigravity-oauth-token (private; never commit it).
param([string]$HomeDir = "$env:USERPROFILE\.zeruel-private\agy-home")
$ErrorActionPreference = 'Stop'
$env:MSYS_NO_PATHCONV = '1'
New-Item -ItemType Directory -Force $HomeDir | Out-Null
docker rm -f zeruel-agy-login 2>$null | Out-Null
docker run -d --name zeruel-agy-login -v "${HomeDir}:/root" zeruel sleep 900 | Out-Null
docker exec -u root zeruel-agy-login sh -c "touch /tmp/code; printf '#!/bin/sh\ncd /root && exec /opt/agy/agy -p ''Return only this JSON object: {\""marker\"":\""ZERUEL_OK\"",\""sum\"":42}'' --output-format json\n' > /tmp/run.sh"
docker exec -d -u root zeruel-agy-login sh -c "tail -f /tmp/code | script -qfc 'HOME=/root sh /tmp/run.sh' /tmp/out.log"
$url = $null
for ($i = 0; $i -lt 90 -and -not $url; $i++) {
  Start-Sleep -Milliseconds 500
  $log = (docker exec zeruel-agy-login sh -c "cat /tmp/out.log 2>/dev/null") -join ''
  $m = [regex]::Match($log, 'https://accounts\.google\.com/[^\s\x1b]+')
  if ($m.Success -and $log -match 'paste') { $url = $m.Value }
}
if (-not $url) { Write-Host 'No sign-in URL (already signed in, or build the image first: docker build -t zeruel .)'; exit 1 }
Start-Process $url
$code = Read-Host 'Pulsa Permitir en Google, pega aqui el codigo (60 s)'
$code.Trim() | docker exec -i zeruel-agy-login sh -c "cat >> /tmp/code"
for ($i = 0; $i -lt 60; $i++) {
  Start-Sleep -Seconds 2
  $log = (docker exec zeruel-agy-login sh -c "cat /tmp/out.log") -join ''
  if ($log -match '"status"') { break }
}
Write-Host ([regex]::Match($log, '"status":"[A-Z]+"').Value)
docker rm -f zeruel-agy-login | Out-Null  # removes the log that echoed the (single-use) code
Write-Host "Session stored under $HomeDir (private)."
