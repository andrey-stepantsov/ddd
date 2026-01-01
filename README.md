# DDD Infrastructure Documentation

### 1. The Manifesto (`README.md`)

```markdown
# DDD: The Triple-Head Development Architecture

DDD is a physical-to-virtual bridge that allows modern AI agents and host tools to control a persistent, isolated build container.

## The Architecture

The system runs as three distinct "Heads" in three terminals:

1.  **The Builder (`*-dev` container)**
    * **Role:** Passive persistence.
    * **Job:** Holds the compiler state, object files, and dependencies. Never exits.
    * **Mechanism:** Docker container running `sleep infinity`.

2.  **The Watcher (`dd-daemon`)**
    * **Role:** The Nervous System.
    * **Job:** Watches for the specific signal (`.build_request`), triggers the build inside the container, and runs verification.
    * **Mechanism:** Python script on Host using `watchdog`.

3.  **The Coder (AI Agent / You)**
    * **Role:** The Brain.
    * **Job:** Edits source code and signals when ready.
    * **Mechanism:** Aider (inside a container) or Neovim (on host).

## The Protocol (Explicit Mode)

To prevent infinite loops and broken builds, the Daemon **ignores all file changes** except one.

1.  **Edit:** Modify as many files as needed.
2.  **Signal:** Run `touch .build_request`.
3.  **React:** Daemon sees signal -> Runs Build -> Runs Verify.

## Setup

1.  **Install:** `./install.sh` (Puts tools in `~/.local/bin`)
2.  **Configure:** Create `.dd-config` in your project root:
    ```json
    {
      "build_cmd": "docker exec -t nethack-dev make -j4",
      "verify_cmd": "docker exec -t nethack-dev /mission/bin/dd-verify",
      "watch_dir": "."
    }
    ```
3.  **Run:** `dd-daemon`
```

---

### 2. The Watcher (`src/dd-daemon.py`)

```python
#!/usr/bin/env python3
import json
import os
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CONFIG_FILE = ".dd-config"
TRIGGER_FILE = ".build_request"

class RequestHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_run = 0
        self.cooldown = 2.0  # Debounce to prevent double-taps

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            print(f"[!] {CONFIG_FILE} not found")
            return None
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Error reading config: {e}")
            return None

    def run_pipeline(self):
        # Debounce
        if time.time() - self.last_run < self.cooldown:
            return
        self.last_run = time.time()

        print(f"\n[>>>] Signal received: {TRIGGER_FILE}")
        
        config = self.load_config()
        if not config: return

        build_cmd = config.get('build_cmd')
        if not build_cmd: return

        print(f"[+] Executing Build: {build_cmd}")
        # We run shell=True so complex commands (pipes, etc) work
        build_res = subprocess.run(build_cmd, shell=True)
        
        if build_res.returncode != 0:
            print("[-] Build Failed.")
            return

        verify_cmd = config.get('verify_cmd')
        if verify_cmd:
            print(f"[+] Verifying: {verify_cmd}")
            subprocess.run(verify_cmd, shell=True)
        else:
            print("[.] No 'verify_cmd' defined.")

    def on_modified(self, event):
        if os.path.basename(event.src_path) == TRIGGER_FILE:
            self.run_pipeline()
            
    def on_created(self, event):
        if os.path.basename(event.src_path) == TRIGGER_FILE:
            self.run_pipeline()

if __name__ == "__main__":
    if not os.path.exists(CONFIG_FILE):
        print(f"WARNING: No {CONFIG_FILE} found.")
        
    print(f"[*] dd-daemon ACTIVE (Explicit Mode).")
    print(f"[*] Waiting for signal: 'touch {TRIGGER_FILE}'")
    
    event_handler = RequestHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[*] Daemon stopping.")
    observer.join()
```

---

### 3. The Smart Mount Tool (`tools/dd-print-mount`)

```bash
#!/bin/bash

# Use Python to resolve the true location of this script (handles symlinks on Mac/Linux)
REAL_SCRIPT_PATH=$(python3 -c "import os; print(os.path.realpath('$0'))")
SCRIPT_DIR="$(dirname "$REAL_SCRIPT_PATH")"

# Resolve payload directory relative to the REAL script location
PAYLOAD_DIR="$(cd "$SCRIPT_DIR/../payload" && pwd)"

# Output the Docker mount string
echo "-v $PAYLOAD_DIR:/mission/bin:ro"
```

---

### 4. The Installer (`install.sh`)

```bash
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
```

---

### 5. The Payload (`payload/dd-verify`)

```bash
#!/bin/bash
echo "--- [dd-verify] Starting Verification ---"
echo "User: $(whoami)"
echo "Workdir: $(pwd)"

# TARGET: Adjusted for NetHack source structure
TARGET="src/nethack"

if [ -f "$TARGET" ]; then
    echo "[PASS] Binary found at $TARGET"
else
    echo "[FAIL] Binary not found at $TARGET"
    exit 1
fi
```

---

### 6. The Test Suite (`tests/run_tests.sh`)

```bash
#!/bin/bash
# tests/run_tests.sh
# End-to-End test of the ddd infrastructure

REPO_ROOT="$(pwd)"
DAEMON_SCRIPT="$REPO_ROOT/src/dd-daemon.py"
MOUNT_TOOL="$REPO_ROOT/tools/dd-print-mount"
VENV_PYTHON="$REPO_ROOT/.venv/bin/python"

# Create a sandbox for testing
TEST_DIR="$(mktemp -d)"
echo "=== Starting dd-daemon Infrastructure Test ==="
echo "Workdir: $TEST_DIR"

# --- Test 1: Mount Tool ---
echo "--- Test 1: Mount Tool ---"
MOUNT_OUT=$($MOUNT_TOOL)
if [[ "$MOUNT_OUT" == "-v "*":/mission/bin:ro" ]]; then
    echo "[PASS] Mount string valid: $MOUNT_OUT"
else
    echo "[FAIL] Invalid mount string: $MOUNT_OUT"
    exit 1
fi

# --- Test 2: Daemon Trigger Logic ---
echo "--- Test 2: Daemon Explicit Protocol ---"

cd "$TEST_DIR"

# Create a mock config that writes to a 'success' file
cat <<JSON > .dd-config
{
  "build_cmd": "echo 'BUILD_RUN' > build.log",
  "verify_cmd": "echo 'VERIFY_RUN' > verify.log",
  "watch_dir": "."
}
JSON

# Start Daemon in background
"$VENV_PYTHON" "$DAEMON_SCRIPT" > daemon.log 2>&1 &
DAEMON_PID=$!

# Give it a second to spin up
sleep 2

# Action: Touch a random file (Should be IGNORED)
touch random_file.txt
sleep 1
if [ -f build.log ]; then
    echo "[FAIL] Daemon triggered on random file (Should be strict!)"
    kill $DAEMON_PID
    exit 1
fi

# Action: Touch the Trigger (Should be DETECTED)
touch .build_request
sleep 2

# Check results
if grep -q "BUILD_RUN" build.log && grep -q "VERIFY_RUN" verify.log; then
    echo "[PASS] Daemon correctly triggered on .build_request"
else
    echo "[FAIL] Daemon did not trigger or commands failed."
    echo "--- Daemon Log ---"
    cat daemon.log
    kill $DAEMON_PID
    exit 1
fi

# Cleanup
kill $DAEMON_PID
rm -rf "$TEST_DIR"
echo "=== All Tests Passed ==="
```

### 7. Commit Command

```bash
chmod +x tests/run_tests.sh tools/dd-print-mount install.sh payload/dd-verify
git add .
git commit -m "feat: Implement Explicit Trigger Protocol (.build_request) and fix path resolution"
```
