param(
    [string]$venvDir = '.venv'
)

Write-Host "Creating virtual environment in $venvDir"
python -m venv $venvDir
Write-Host "Activating and installing dev dependencies"
& "$venvDir\Scripts\Activate.ps1"
# Install editable package and dev extras
pip install -e .[dev]
Write-Host "Done. Activate with: .\\$venvDir\\Scripts\\Activate.ps1"
