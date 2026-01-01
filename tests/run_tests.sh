#!/bin/bash
# tests/run_tests.sh
# End-to-End test of the DDD infrastructure (Dot-Folder Mode)

REPO_ROOT="$(pwd)"
DAEMON_SCRIPT="$REPO_ROOT/src/dd-daemon.py"
VENV_PYTHON="$REPO_ROOT/.venv/bin/python"

# --- Constants ---
DDD_DIR=".ddd"
TRIGGER_FILE="$DDD_DIR/build.request"
LOG_FILE="$DDD_DIR/build.log"
CONFIG_FILE="$DDD_DIR/config.json"

# Create a sandbox for testing
TEST_DIR="$(mktemp -d)"
echo "=== Starting DDD Dot-Folder Test ==="
echo "Workdir: $TEST_DIR"

cd "$TEST_DIR"

# --- Test 1: Daemon Startup & Directory Creation ---
echo "--- Test 1: Daemon Startup ---"

# Start Daemon in background
"$VENV_PYTHON" "$DAEMON_SCRIPT" > daemon.log 2>&1 &
DAEMON_PID=$!

# Give it a moment to initialize
sleep 2

# Check if .ddd directory was auto-created
if [ ! -d "$DDD_DIR" ]; then
    echo "[FAIL] Daemon failed to create $DDD_DIR directory."
    kill $DAEMON_PID
    exit 1
fi
echo "[PASS] .ddd directory created."

# --- Test 2: Configuration Loading ---
echo "--- Test 2: Trigger Logic ---"

# Create a mock config inside the hidden folder
cat <<JSON > "$CONFIG_FILE"
{
  "targets": {
    "dev": {
      "build": { 
        "cmd": "echo 'BUILD_RUN_SUCCESS'", 
        "filter": "raw" 
      },
      "verify": { 
        "cmd": "echo 'VERIFY_RUN_SUCCESS'", 
        "filter": "raw" 
      }
    }
  }
}
JSON

# Action: Touch the Trigger
touch "$TRIGGER_FILE"
sleep 2

# Check results
if grep -q "BUILD_RUN_SUCCESS" "$LOG_FILE" && grep -q "VERIFY_RUN_SUCCESS" "$LOG_FILE"; then
    echo "[PASS] Daemon triggered and executed pipeline."
else
    echo "[FAIL] Pipeline failed or logs missing."
    echo "--- Daemon Log ---"
    cat daemon.log
    if [ -f "$LOG_FILE" ]; then
        echo "--- Build Log ---"
        cat "$LOG_FILE"
    fi
    kill $DAEMON_PID
    exit 1
fi

# Cleanup
kill $DAEMON_PID
rm -rf "$TEST_DIR"
echo "=== All Tests Passed ==="
