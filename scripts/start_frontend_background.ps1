$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..\frontend

$stdout = "dev.stdout.log"
$stderr = "dev.stderr.log"

if (Test-Path $stdout) { Remove-Item -LiteralPath $stdout -Force }
if (Test-Path $stderr) { Remove-Item -LiteralPath $stderr -Force }

& "C:\Program Files\nodejs\npm.cmd" "run" "dev" "--" "--host" "0.0.0.0" "--port" "5173" 1>> $stdout 2>> $stderr

