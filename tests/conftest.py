import pytest
import subprocess
import sys
import os
import time
from pathlib import Path

# Identify tool root (where src/ is)
TOOL_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(TOOL_ROOT))

@pytest.fixture
def ddd_workspace(tmp_path, monkeypatch):
    """Isolated workspace."""
    monkeypatch.chdir(tmp_path)
    return tmp_path

@pytest.fixture
def daemon_proc(ddd_workspace):
    """Spawns daemon and waits for startup."""
    daemon_log = ddd_workspace / "daemon_test.log"
    
    # Start Daemon
    with open(daemon_log, "w") as log_file:
        proc = subprocess.Popen(
            [sys.executable, str(TOOL_ROOT / "src" / "dd-daemon.py")],
            stdout=log_file,
            stderr=subprocess.STDOUT,
            cwd=ddd_workspace,
            text=True
        )

    # Wait for .ddd and .ddd/run to appear
    ddd_dir = ddd_workspace / ".ddd"
    run_dir = ddd_dir / "run"
    
    start = time.time()
    started = False
    while time.time() - start < 3.0:
        if run_dir.exists() and proc.poll() is None:
            started = True
            break
        time.sleep(0.1)

    if not started:
        if daemon_log.exists():
            print(f"\n[!] Daemon Log:\n{daemon_log.read_text()}")
        proc.terminate()
        pytest.fail("Daemon failed to initialize .ddd/run directory.")

    yield proc

    # Teardown
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            proc.kill()
