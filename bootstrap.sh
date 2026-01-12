#!/bin/bash
set -e

# Resolve DDD Root (Where this script lives)
DDD_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REQ_FILE="$DDD_ROOT/requirements.txt"

# Venv Location: Inside the component (.venv)
VENV_DIR="$DDD_ROOT/.venv"

# 1. Create Venv if missing or broken
#    We explicitly check for 'pip' to detect broken Debian/Ubuntu venvs
if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_DIR/bin/pip" ]; then
    echo "[ddd-bootstrap] Creating local environment..."
    
    # Clear partial state to avoid conflicts
    rm -rf "$VENV_DIR"
    
    # Try standard creation (might fail to install pip on some distros)
    python3 -m venv "$VENV_DIR" || true

    # CHECK: Did pip actually get installed?
    if [ ! -f "$VENV_DIR/bin/pip" ]; then
        # Detect Python Version inside the new venv
        PY_VER=$("$VENV_DIR/bin/python3" -c "import sys; print('%d.%d' % (sys.version_info.major, sys.version_info.minor))")
        
        # Determine correct URL based on version
        PIP_URL="https://bootstrap.pypa.io/get-pip.py"
        if [[ "$PY_VER" == "3.6" ]]; then PIP_URL="https://bootstrap.pypa.io/pip/3.6/get-pip.py"; fi
        
        echo "⚠️  System Python ($PY_VER) is missing ensurepip. Fetching pip from $PIP_URL..."
        
        # Download and install
        curl -sSL "$PIP_URL" -o /tmp/get-pip.py
        "$VENV_DIR/bin/python3" /tmp/get-pip.py
        rm /tmp/get-pip.py
    fi

    # Upgrade pip to be safe
    "$VENV_DIR/bin/pip" install --upgrade pip > /dev/null
fi

# 2. Sync Dependencies (Idempotent)
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
