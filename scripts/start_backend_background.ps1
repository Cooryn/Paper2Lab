$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$stdout = "backend\data\logs\backend.stdout.log"
$stderr = "backend\data\logs\backend.stderr.log"

if (Test-Path $stdout) { Remove-Item -LiteralPath $stdout -Force }
if (Test-Path $stderr) { Remove-Item -LiteralPath $stderr -Force }

& "C:\Users\Coryn\miniconda3\python.exe" "scripts\run_backend.py" 1>> $stdout 2>> $stderr

