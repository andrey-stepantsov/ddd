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
    """Spawns daemon in background mode and waits for startup."""
    daemon_log = ddd_workspace / "daemon_test.log"
    
    # Start Daemon with --daemon
    proc = subprocess.run(
        [sys.executable, str(TOOL_ROOT / "src" / "dd-daemon.py"), "--daemon"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ddd_workspace,
        text=True
    )
    
    if proc.returncode != 0:
        pytest.fail(f"Daemon failed to fork: {proc.stderr}")

    # Wait for .ddd/daemon.pid
    ddd_dir = ddd_workspace / ".ddd"
    pid_file = ddd_dir / "daemon.pid"
    
    start = time.time()
    started = False
    pid = None
    
    while time.time() - start < 5.0:
        if pid_file.exists():
            try:
                content = pid_file.read_text().strip()
                if content:
                    pid = int(content)
                    # verify process exists
                    try:
                        os.kill(pid, 0)
                        started = True
                        break
                    except OSError:
                        pass # PID file exists but process dead?
            except ValueError:
                pass
        time.sleep(0.1)

    if not started or not pid:
        # Check for log
        log_file = ddd_dir / "daemon.log"
        log_content = log_file.read_text() if log_file.exists() else "No log"
        pytest.fail(f"Daemon failed to initialize. Log: {log_content}")

    yield pid

    # Teardown
    if pid:
        try:
            os.kill(pid, 15) # SIGTERM
            # Wait for it to die?
            for _ in range(10):
                try:
                    os.kill(pid, 0)
                    time.sleep(0.1)
                except OSError:
                    break
            else:
                os.kill(pid, 9) # SIGKILL
        except OSError:
            pass # Already dead
