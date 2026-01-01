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
