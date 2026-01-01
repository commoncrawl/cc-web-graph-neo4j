#!/usr/bin/env bash
set -e
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name cc-hypergraph --display-name "cc-hypergraph"
command -v java >/dev/null 2>&1 || { echo "Java unfounded. Please install OpenJDK 11+."; exit 1; }
echo "venv OK"
