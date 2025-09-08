#!/bin/bash
set -euxo pipefail

# Create virtual environment if not present
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
