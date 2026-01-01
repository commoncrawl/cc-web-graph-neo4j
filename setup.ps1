python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name cc-hypergraph --display-name "cc-hypergraph"
if (-not (Get-Command java -ErrorAction SilentlyContinue)) { Write-Host "Java unfounded. Please install OpenJDK 11+."; exit 1 }
Write-Host "venv OK"
