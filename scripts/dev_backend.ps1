$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..
python -m pip install -r backend\requirements.txt
python scripts\seed_demo.py
python scripts\run_backend.py

