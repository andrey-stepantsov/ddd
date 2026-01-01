#!/bin/bash
set -e

# --- Configuration ---
REPO_ROOT="$(pwd)"
INSTALL_DIR="$HOME/.local/bin"
VENV_DIR="$REPO_ROOT/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"

# Daemon Config
DAEMON_NAME="dd-daemon"
DAEMON_SOURCE="$REPO_ROOT/src/dd-daemon.py"
DAEMON_TARGET="$INSTALL_DIR/$DAEMON_NAME"

# Mount Tool Config
MOUNT_NAME="dd-print-mount"
MOUNT_SOURCE="$REPO_ROOT/tools/dd-print-mount"
MOUNT_TARGET="$INSTALL_DIR/$MOUNT_NAME"

echo "=== Installing ddd Toolkit ==="

# 1. Setup Virtual Environment (Auto-Healing)
if [ ! -d "$VENV_DIR" ]; then
    echo "[+] Creating isolated virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# 2. Install Dependencies
echo "[+] Checking Python dependencies..."
"$VENV_PYTHON" -m pip install watchdog > /dev/null

mkdir -p "$INSTALL_DIR"

# 3. Install Daemon (Wrapper Method)
if [ -L "$DAEMON_TARGET" ] || [ -f "$DAEMON_TARGET" ]; then
    rm "$DAEMON_TARGET"
fi

echo "[+] Installing $DAEMON_NAME..."
cat <<WRAPPER > "$DAEMON_TARGET"
#!/bin/bash
exec "$VENV_PYTHON" "$DAEMON_SOURCE" "\$@"
WRAPPER
chmod +x "$DAEMON_TARGET"

# 4. Install Mount Tool (Symlink Method)
# Since this is a standalone bash script, a symlink is perfect.
if [ -L "$MOUNT_TARGET" ] || [ -f "$MOUNT_TARGET" ]; then
    rm "$MOUNT_TARGET"
fi

echo "[+] Installing $MOUNT_NAME..."
ln -s "$MOUNT_SOURCE" "$MOUNT_TARGET"

# 5. Final Path Check
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo "WARNING: $INSTALL_DIR is not in your PATH."
else
    echo "SUCCESS: Toolkit installed ($DAEMON_NAME, $MOUNT_NAME)."
fi
