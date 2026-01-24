#!/bin/bash
# tools/lib/bootstrap.sh
# Hermetic Python Bootstrapper for Mission Pack

set -e

# get_script_dir: Resolves the directory of the sourcing script
get_script_dir() {
    cd "$(dirname "${BASH_SOURCE[1]}")" && pwd
}

# ensure_environment: Main entry point
# Usage: ensure_environment <path_to_deps_file> [python_version]
ensure_environment() {
    local DEPS_FILE="$1"
    # Default to python3 if not specified. In real usage we might download a specific python binary.
    # For now, we assume implicit 'python3' availability on host as the base.
    local BASE_PYTHON="python3" 

    if [ ! -f "$DEPS_FILE" ]; then
        echo "❌ Requirements file not found: $DEPS_FILE"
        exit 1
    fi

    # 1. Detect Host
    local OS
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    local ARCH
    ARCH=$(uname -m | tr '[:upper:]' '[:lower:]')

    # 2. Calculate Hash of Dependency File
    # Use sha256sum or shasum depending on OS
    local HASH
    if command -v sha256sum >/dev/null 2>&1; then
        HASH=$(sha256sum "$DEPS_FILE" | awk '{print $1}')
    else 
        # macOS usually has shasum
        HASH=$(shasum -a 256 "$DEPS_FILE" | awk '{print $1}')
    fi
    # Shorten hash for readability
    HASH=${HASH:0:12}

    # 3. Determine Env Path
    local MISSION_HOME="${HOME}/.mission"
    local ENV_NAME="${OS}_${ARCH}_${HASH}"
    local ENV_DIR="${MISSION_HOME}/envs/${ENV_NAME}"
    
    # Export for caller
    export PYTHON_EXE="${ENV_DIR}/bin/python"
    export BOOTSTRAP_ENV_DIR="${ENV_DIR}"
    
    # 3.5 Isolate Pip Cache
    export XDG_CACHE_HOME="${MISSION_HOME}/cache"
    export PIP_CACHE_DIR="${MISSION_HOME}/pip_cache"
    export PIP_NO_WARN_SCRIPT_LOCATION=0

    # 4. Check & Provision
    if [ -f "$PYTHON_EXE" ]; then
        # Check if we should re-validate? For speed, we trust existence = valid.
        return 0
    fi

    echo "📦 Bootstrapping Isolated Environment..."
    echo "   Target: $ENV_DIR"
    echo "   Deps:   $DEPS_FILE"
    
    rm -rf "$ENV_DIR"
    mkdir -p "$(dirname "$ENV_DIR")"
    
    # Create Venv
    echo "   Creating Virtual Environment..."
    "$BASE_PYTHON" -m venv "$ENV_DIR"
    
    # Install Dependencies
    echo "   Installing Dependencies..."
    # If pyproject.toml, we need to install the project itself or use poetry?
    # For simplicity, if it's pyproject.toml, we assume 'pip install .' works or 'pip install -e .'
    # If it's requirements.txt, 'pip install -r'
    
    if [[ "$DEPS_FILE" == *"pyproject.toml" ]]; then
       # We need to be in the project root for 'pip install .' to work correctly usually
       # or pass the directory.
       local PROJECT_DIR
       PROJECT_DIR=$(dirname "$DEPS_FILE")
       
       # Install build deps usually needed?
       # We simply pip install the project directory.
       # Using -e (editable) is better for dev tools? Or regular install?
       # For tools/bin/chaos, we probably want the tool dependencies.
       # Let's assume 'pip install .'
       "$ENV_DIR/bin/pip" install --upgrade pip >/dev/null 2>&1
       "$ENV_DIR/bin/pip" install "$PROJECT_DIR"
       
    else
       "$ENV_DIR/bin/pip" install --upgrade pip >/dev/null 2>&1
       "$ENV_DIR/bin/pip" install -r "$DEPS_FILE"
    fi
    
    echo "✅ Environment Ready."
}

# --- Main Execution ---

# 1. Setup Paths
DDD_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REQ_FILE="$DDD_ROOT/requirements.txt"

# 2. Bootstrap
ensure_environment "$REQ_FILE"

# 3. Launch
# Add DDD_ROOT to PYTHONPATH
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$DDD_ROOT"

# Execute arguments using the bootstrapped Python
exec "$PYTHON_EXE" "$@"
