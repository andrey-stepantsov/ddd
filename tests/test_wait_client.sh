#!/bin/bash
# tests/test_wait_client.sh
# Verifies ddd-wait behavior: Success, Timeout, and Config overrides.

REPO_ROOT="$(pwd)"
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

# ==============================================================================
# TEST CASE 1: Normal Success (Wait for ~2s)
# ==============================================================================
echo "--- Test Case 1: Normal Success (2s build) ---"

# Configure a Slow Build (2 seconds)
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

START_TIME=$(date +%s)
OUTPUT=$("$CLIENT_BIN")
RET_CODE=$?
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Verification
if [ $RET_CODE -ne 0 ]; then
    echo "[FAIL] Client exited with error ($RET_CODE)."
    kill $DAEMON_PID; exit 1
fi

if [ "$DURATION" -lt 2 ]; then
    echo "[FAIL] Client returned too fast (${DURATION}s)! It didn't wait for the lock."
    kill $DAEMON_PID; exit 1
fi

if echo "$OUTPUT" | grep -q "CLIENT_TEST_SUCCESS"; then
    echo "[PASS] Client captured correct log output."
else
    echo "[FAIL] Client output missing success message."
    kill $DAEMON_PID; exit 1
fi

# ==============================================================================
# TEST CASE 2: Timeout Enforcement (DDD_TIMEOUT)
# ==============================================================================
echo "--- Test Case 2: Timeout Enforcement ---"

# Configure a Very Slow Build (5 seconds)
cat <<JSON > "$CONFIG_FILE"
{
  "targets": {
    "dev": {
      "build": { 
        "cmd": "sleep 5 && echo 'SHOULD_NOT_SEE_THIS'", 
        "filter": "raw" 
      }
    }
  }
}
JSON

# Run Client with tight timeout (1 second)
# expecting it to fail before the 5s build finishes
START_TIME=$(date +%s)
OUTPUT=$(DDD_TIMEOUT=1 "$CLIENT_BIN")
RET_CODE=$?
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Verification
if [ $RET_CODE -eq 0 ]; then
    echo "[FAIL] Client succeeded but should have timed out!"
    kill $DAEMON_PID; exit 1
fi

if [ "$DURATION" -ge 4 ]; then
    echo "[FAIL] Client waited too long (${DURATION}s). Timeout ignored."
    kill $DAEMON_PID; exit 1
fi

if echo "$OUTPUT" | grep -q "Error: Build timed out"; then
    echo "[PASS] Client correctly reported timeout."
else
    echo "[FAIL] Client output missing timeout error message."
    echo "Output: $OUTPUT"
    kill $DAEMON_PID; exit 1
fi

# Cleanup
kill $DAEMON_PID
rm -rf "$TEST_DIR"
echo "=== All Client Tests Passed ==="