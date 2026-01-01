#!/bin/bash
# tests/test_wait_client.sh
# Verifies the ddd-wait client blocks and returns output

REPO_ROOT="$(pwd)"
# Use the installed binary to verify the shim/path works
CLIENT_BIN="$HOME/.local/bin/ddd-wait"
DAEMON_BIN="$HOME/.local/bin/dd-daemon"

# --- Constants ---
DDD_DIR=".ddd"
CONFIG_FILE="$DDD_DIR/config.json"

TEST_DIR="$(mktemp -d)"
echo "=== Testing ddd-wait Client ==="
echo "Workdir: $TEST_DIR"

cd "$TEST_DIR"

# 1. Start Daemon
echo "[*] Starting Daemon..."
"$DAEMON_BIN" > daemon.log 2>&1 &
DAEMON_PID=$!
sleep 2

if [ ! -d "$DDD_DIR" ]; then
    echo "[FAIL] Daemon failed to start."
    cat daemon.log
    exit 1
fi

# 2. Configure a Slow Build (2 seconds)
cat <<JSON > "$CONFIG_FILE"
{
  "targets": {
    "dev": {
      "build": { 
        "cmd": "sleep 2 && echo 'CLIENT_TEST_SUCCESS'", 
        "filter": "raw" 
      }
    }
  }
}
JSON

# 3. Run ddd-wait and capture output
echo "[*] Running ddd-wait (expect ~2s delay)..."
START_TIME=$(date +%s)
OUTPUT=$("$CLIENT_BIN")
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# 4. Verify Duration (Should be at least 2s)
echo "[*] Duration: ${DURATION}s"
if [ "$DURATION" -lt 2 ]; then
    echo "[FAIL] Client returned too fast! It didn't wait for the lock."
    kill $DAEMON_PID; exit 1
fi

# 5. Verify Output
if echo "$OUTPUT" | grep -q "CLIENT_TEST_SUCCESS"; then
    echo "[PASS] Client captured correct log output."
else
    echo "[FAIL] Client output missing success message."
    echo "--- OUTPUT START ---"
    echo "$OUTPUT"
    echo "--- OUTPUT END ---"
    kill $DAEMON_PID; exit 1
fi

# Cleanup
kill $DAEMON_PID
rm -rf "$TEST_DIR"
echo "=== Client Test Passed ==="
