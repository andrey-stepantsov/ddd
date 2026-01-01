#!/bin/bash
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR="$REPO_ROOT/test_workspace"
DAEMON_SCRIPT="$REPO_ROOT/src/dd-daemon.py"
MOUNT_TOOL="$REPO_ROOT/tools/dd-print-mount"
PAYLOAD_FILE="$REPO_ROOT/payload/dd-verify"

PASS='\033[0;32m[PASS]\033[0m'
FAIL='\033[0;31m[FAIL]\033[0m'
function fail { echo -e "$FAIL $1"; exit 1; }
function pass { echo -e "$PASS $1"; }

echo "=== Starting dd-daemon Infrastructure Test ==="

rm -rf "$TEST_DIR" && mkdir -p "$TEST_DIR"
mkdir -p "$(dirname "$PAYLOAD_FILE")"
if [ ! -f "$PAYLOAD_FILE" ]; then
    echo "#!/bin/bash" > "$PAYLOAD_FILE" && echo "echo 'Payload OK'" >> "$PAYLOAD_FILE"
    chmod +x "$PAYLOAD_FILE"
fi

echo "--- Test 1: Mount Tool ---"
MOUNT_OUTPUT=$("$MOUNT_TOOL")
if [[ "$MOUNT_OUTPUT" == *"-v"* && "$MOUNT_OUTPUT" == *":/mission/bin:ro"* ]]; then
    pass "Mount string valid."
else
    fail "Mount string invalid: $MOUNT_OUTPUT"
fi

echo "--- Test 2: Daemon Logic (Mocked) ---"
cd "$TEST_DIR"
cat <<JSON > .dd-config
{ "build_cmd": "echo 'Build' > build.log", "verify_cmd": "echo 'Verify' > verify.log", "watch_dir": "." }
JSON

python3 "$DAEMON_SCRIPT" > daemon.out 2>&1 &
DAEMON_PID=$!
sleep 2
touch changed_file.c
sleep 2

if grep -q "Build" build.log 2>/dev/null; then pass "Build triggered."; else cat daemon.out; fail "Build failed."; fi
if grep -q "Verify" verify.log 2>/dev/null; then pass "Verify triggered."; else fail "Verify failed."; fi

kill "$DAEMON_PID" && wait "$DAEMON_PID" 2>/dev/null

echo "--- Test 3: Docker Injection ---"
if command -v docker &> /dev/null; then
    docker run --rm $("$MOUNT_TOOL") alpine ls -l /mission/bin/dd-verify > docker.log 2>&1
    if grep -q "dd-verify" docker.log; then pass "Injection successful."; else cat docker.log; fail "Injection failed."; fi
else
    echo "Docker not found, skipping."
fi

rm -rf "$TEST_DIR"
echo "=== All Tests Passed ==="
