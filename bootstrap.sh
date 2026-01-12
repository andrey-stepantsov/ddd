#!/bin/bash
set -e

# Resolve DDD Root (Where this script lives)
DDD_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REQ_FILE="$DDD_ROOT/requirements.txt"

# Venv Location: Inside the component (.venv)
VENV_DIR="$DDD_ROOT/.venv"

# 1. Create Venv if missing
if [ ! -d "$VENV_DIR" ]; then
    echo "[ddd-bootstrap] Creating local environment..."
    python3 -m venv "$VENV_DIR"
    
    # Pip upgrade
    "$VENV_DIR/bin/pip" install --upgrade pip > /dev/null
fi

# 2. Sync Dependencies (Idempotent)
# We use a marker file to avoid running pip install on every execution
HASH_FILE="$VENV_DIR/.req_hash"
CURRENT_HASH=$(shasum "$REQ_FILE" 2>/dev/null || md5sum "$REQ_FILE" | awk '{print $1}')

if [ ! -f "$HASH_FILE" ] || [ "$(cat "$HASH_FILE")" != "$CURRENT_HASH" ]; then
    echo "[ddd-bootstrap] Syncing dependencies..."
    "$VENV_DIR/bin/pip" install -r "$REQ_FILE" > /dev/null
    echo "$CURRENT_HASH" > "$HASH_FILE"
fi

# 3. Execution
# Add DDD root to PYTHONPATH so 'src' imports work
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$DDD_ROOT"

exec "$VENV_DIR/bin/python3" "$@"
