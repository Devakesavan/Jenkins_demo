#!/bin/bash
set -euxo pipefail

. .venv/bin/activate

echo ">>> Running basic sanity test..."
python -c "import app; print('Flask app object exists:', hasattr(app, 'app'))"
