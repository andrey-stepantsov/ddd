import pytest
import subprocess
import sys
import os
import time
import signal
from pathlib import Path

# Identify project root relative to this file
REPO_ROOT = Path(__file__).parent.parent.resolve()

# --- CRITICAL FIX: Add project root to sys.path ---
# This allows tests to run 'from src.filters import ...'
sys.path.insert(0, str(REPO_ROOT))

@pytest.fixture
def ddd_workspace(tmp_path, monkeypatch):
    """
    Sets up an isolated workspace for a test run.
    1. Creates a temp directory (tmp_path).
    2. Switches the CWD to that directory (monkeypatch).
    """
    monkeypatch.chdir(tmp_path)
    return tmp_path

@pytest.fixture
def daemon_proc(ddd_workspace):
    """
    Spawns the dd-daemon in the background of the workspace.
    Mimics the logic of 'tests/run_tests.sh':
    1. Starts daemon.
    2. Waits for startup.
    3. Yields process.
    4. Kills on teardown.
    """
    # Define logs within the temp workspace
    daemon_log = ddd_workspace / "daemon_test.log"
    
    # Start the daemon using the same Python interpreter running pytest
    with open(daemon_log, "w") as log_file:
        proc = subprocess.Popen(
            [sys.executable, str(REPO_ROOT / "src" / "dd-daemon.py")],
            stdout=log_file,
            stderr=subprocess.STDOUT,
            cwd=ddd_workspace,
            text=True
        )

    # Startup Check: Wait for .ddd directory to appear (Timeout: 2s)
    ddd_dir = ddd_workspace / ".ddd"
    start = time.time()
    started = False
    while time.time() - start < 2.0:
        if ddd_dir.exists() and proc.poll() is None:
            started = True
            break
        time.sleep(0.1)

    if not started:
        if daemon_log.exists():
            print(f"\n[!] Daemon Log:\n{daemon_log.read_text()}")
        proc.terminate()
        pytest.fail("Daemon failed to initialize .ddd directory.")

    yield proc

    # Teardown: Kill the daemon
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            proc.kill()