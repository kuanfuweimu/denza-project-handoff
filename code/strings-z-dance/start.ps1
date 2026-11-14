$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$port = 8789
$existing = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if (-not $existing) {
  Start-Process -FilePath "node" -ArgumentList "server.js" -WorkingDirectory $root -WindowStyle Minimized
  Start-Sleep -Milliseconds 600
}

$chrome = @(
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
  "$env:ProgramFiles(x86)\Microsoft\Edge\Application\msedge.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

$profile = Join-Path $root "browser-profile"
if ($chrome) {
  Start-Process $chrome "--user-data-dir=`"$profile`" --new-window http://localhost:$port/?view=split"
  Start-Process $chrome "--user-data-dir=`"$profile`" --new-window http://localhost:$port/control.html"
} else {
  Start-Process "http://localhost:$port/?view=split"
  Start-Process "http://localhost:$port/control.html"
}
