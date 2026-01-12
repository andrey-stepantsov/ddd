#!/bin/bash
set -e

DDD_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REQ_FILE="$DDD_ROOT/requirements.txt"
VENV_DIR="$DDD_ROOT/.venv"

# 1. Create Venv
if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_DIR/bin/pip" ]; then
    echo "[ddd-bootstrap] Creating local environment..."
    rm -rf "$VENV_DIR"
    
    python3 -m venv "$VENV_DIR" || true

    if [ ! -f "$VENV_DIR/bin/pip" ]; then
        # Detect Major.Minor version (e.g., "3.8")
        PY_VER=$("$VENV_DIR/bin/python3" -c "import sys; print('%d.%d' % (sys.version_info.major, sys.version_info.minor))")
        
        # Default to modern URL
        PIP_URL="https://bootstrap.pypa.io/get-pip.py"
        
        # Legacy overrides
        if [[ "$PY_VER" == "3.6" ]]; then PIP_URL="https://bootstrap.pypa.io/pip/3.6/get-pip.py"; fi
        if [[ "$PY_VER" == "3.7" ]]; then PIP_URL="https://bootstrap.pypa.io/pip/3.7/get-pip.py"; fi
        if [[ "$PY_VER" == "3.8" ]]; then PIP_URL="https://bootstrap.pypa.io/pip/3.8/get-pip.py"; fi
        
        echo "⚠️  System Python ($PY_VER) missing pip. Fetching from $PIP_URL..."
        
        curl -sSL "$PIP_URL" -o /tmp/get-pip.py
        "$VENV_DIR/bin/python3" /tmp/get-pip.py
        rm /tmp/get-pip.py
    fi

    "$VENV_DIR/bin/pip" install --upgrade pip > /dev/null
fi

# 2. Sync Dependencies
HASH_FILE="$VENV_DIR/.req_hash"
CURRENT_HASH=$(shasum "$REQ_FILE" 2>/dev/null || md5sum "$REQ_FILE" | awk '{print $1}')

if [ ! -f "$HASH_FILE" ] || [ "$(cat "$HASH_FILE")" != "$CURRENT_HASH" ]; then
    echo "[ddd-bootstrap] Syncing dependencies..."
    "$VENV_DIR/bin/pip" install -r "$REQ_FILE" > /dev/null
    echo "$CURRENT_HASH" > "$HASH_FILE"
fi

export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$DDD_ROOT"
exec "$VENV_DIR/bin/python3" "$@"
