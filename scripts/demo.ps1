$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
$python = Join-Path (Get-Location) '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Ejecuta primero: uv venv --python 3.12; uv pip install -r requirements.txt'
}
& $python -m brujula demo @args
exit $LASTEXITCODE
