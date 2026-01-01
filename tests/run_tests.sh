#!/bin/bash
# tests/run_tests.sh
# End-to-End verification of DDD: Lock Protocol & Shadow Logging

REPO_ROOT="$(pwd)"
DAEMON_SCRIPT="$REPO_ROOT/src/dd-daemon.py"
VENV_PYTHON="$REPO_ROOT/.venv/bin/python"

# --- Constants ---
DDD_DIR=".ddd"
TRIGGER_FILE="$DDD_DIR/build.request"
LOG_FILE="$DDD_DIR/build.log"
RAW_LOG_FILE="$DDD_DIR/last_build.raw.log"
LOCK_FILE="$DDD_DIR/run.lock"
CONFIG_FILE="$DDD_DIR/config.json"

TEST_DIR="$(mktemp -d)"
echo "=== Starting DDD Enhanced Test ==="
echo "Workdir: $TEST_DIR"

cd "$TEST_DIR"

# --- Test 1: Daemon Startup ---
echo "--- Test 1: Daemon Startup ---"
"$VENV_PYTHON" "$DAEMON_SCRIPT" > daemon.log 2>&1 &
DAEMON_PID=$!
sleep 2

if [ ! -d "$DDD_DIR" ]; then
    echo "[FAIL] Daemon failed to create $DDD_DIR directory."
    kill $DAEMON_PID; exit 1
fi

# --- Test 2: Lock Protocol & Logging ---
echo "--- Test 2: Lock Protocol & Shadow Logging ---"

# Create a config with a DELAY so we can catch the lock file
cat <<JSON > "$CONFIG_FILE"
{
  "targets": {
    "dev": {
      "build": { 
        "cmd": "sleep 2 && echo 'BUILD_FINISHED'", 
        "filter": "raw" 
      }
    }
  }
}
JSON

# Action: Touch the Trigger
touch "$TRIGGER_FILE"
echo "[*] Triggered. Waiting for Lock..."

# CHECK A: Does Lock appear? (Give it 1s to react)
LOCK_FOUND=0
for i in {1..10}; do
    if [ -f "$LOCK_FILE" ]; then
        LOCK_FOUND=1
        break
    fi
    sleep 0.1
done

if [ $LOCK_FOUND -eq 1 ]; then
    echo "[PASS] Lock file created."
else
    echo "[FAIL] Lock file never appeared!"
    kill $DAEMON_PID; exit 1
fi

# CHECK B: Does Lock vanish? (Wait for build to finish)
echo "[*] Waiting for build to finish..."
while [ -f "$LOCK_FILE" ]; do
    sleep 0.5
done
echo "[PASS] Lock file removed."

# CHECK C: Do logs exist?
if grep -q "BUILD_FINISHED" "$LOG_FILE"; then
    echo "[PASS] Clean log contains output."
else
    echo "[FAIL] Clean log missing output."
    kill $DAEMON_PID; exit 1
fi

if grep -q "BUILD_FINISHED" "$RAW_LOG_FILE"; then
    echo "[PASS] Raw shadow log contains output."
else
    echo "[FAIL] Raw log missing output."
    kill $DAEMON_PID; exit 1
fi

# Cleanup
kill $DAEMON_PID
rm -rf "$TEST_DIR"
echo "=== All Tests Passed ==="
