@echo off
cd /d "%~dp0"
set "VAULT_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if not exist "%VAULT_PYTHON%" set "VAULT_PYTHON=python"
powershell -NoProfile -Command "try { $r = Invoke-WebRequest 'http://127.0.0.1:8765/api/state' -UseBasicParsing -TimeoutSec 2; if ($r.StatusCode -eq 200) { Start-Process 'http://127.0.0.1:8765'; exit 0 } } catch {}; Start-Process -FilePath $env:VAULT_PYTHON -ArgumentList 'server.py' -WorkingDirectory (Get-Location).Path -WindowStyle Hidden -RedirectStandardOutput 'server.log' -RedirectStandardError 'server-error.log'; Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8765'"
