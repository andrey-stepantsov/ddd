#!/bin/bash
# install.sh - Complete setup for DDD (Venv + Shim + Link)

set -e  # Exit on error

REPO_ROOT="$(pwd)"
VENV_DIR="$REPO_ROOT/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"
BIN_DIR="$HOME/.local/bin"

echo "=== Installing DDD ==="

# 1. Ensure Requirements File Exists
if [ ! -f "requirements.txt" ]; then
    echo "[*] Creating default requirements.txt..."
    echo "watchdog" > requirements.txt
fi

# 2. Setup/Update Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    echo "[*] Creating virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "[*] Virtual environment found."
fi

# 3. Install Dependencies
echo "[*] Installing dependencies..."
"$VENV_PYTHON" -m pip install -q -r requirements.txt

# 4. Create Bin Directory
mkdir -p "$BIN_DIR"

# 5. Install Daemon (The Shim)
echo "[*] Installing dd-daemon to $BIN_DIR..."

# CRITICAL FIX: Remove existing link/file to prevent overwriting source
rm -f "$BIN_DIR/dd-daemon"

cat <<SHIM > "$BIN_DIR/dd-daemon"
#!/bin/bash
exec "$VENV_PYTHON" "$REPO_ROOT/src/dd-daemon.py" "\$@"
SHIM
chmod +x "$BIN_DIR/dd-daemon"

# 6. Install Client (Symlink)
echo "[*] Installing ddd-wait to $BIN_DIR..."
rm -f "$BIN_DIR/ddd-wait"
ln -sf "$REPO_ROOT/bin/ddd-wait" "$BIN_DIR/ddd-wait"

echo "=== Success! ==="
echo "You can now run 'dd-daemon' and 'ddd-wait' from anywhere."
