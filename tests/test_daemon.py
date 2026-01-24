import time
import json
import os
import pytest

def test_end_to_end_build_cycle(ddd_workspace, daemon_proc):
    """
    Verifies the split-state protocol:
    1. Trigger -> .ddd/run/build.request
    2. Lock    -> .ddd/run/ipc.lock
    3. Output  -> .ddd/run/build.log
    """
    
    # 1. Configure
    ddd_dir = ddd_workspace / ".ddd"
    run_dir = ddd_dir / "run"
    config_file = ddd_dir / "config.json"
    
    config_data = {
        "targets": {
            "dev": {
                "build": { 
                    "cmd": "sleep 0.5 && echo 'PYTEST_BUILD_SUCCESS'", 
                    "filter": "raw" 
                }
            }
        }
    }
    config_file.write_text(json.dumps(config_data))

    # 2. Trigger
    trigger_file = run_dir / "build.request"
    trigger_file.touch()
    
    # 3. Verify Lock (Busy)
    lock_file = run_dir / "ipc.lock"
    lock_seen = False
    
    for _ in range(20):
        if lock_file.exists():
            lock_seen = True
            break
        time.sleep(0.1)
        
    assert lock_seen, "Daemon did not create .ddd/run/ipc.lock"

    # 4. Verify Lock Release (Idle)
    lock_vanished = False
    for _ in range(30):
        if not lock_file.exists():
            lock_vanished = True
            break
        time.sleep(0.1)
        
    assert lock_vanished, "Daemon did not remove ipc.lock"

    # 5. Verify Logs
    clean_log = run_dir / "build.log"
    assert clean_log.exists()
    assert "PYTEST_BUILD_SUCCESS" in clean_log.read_text()
    
    # 6. Verify Artifacts (New in v0.7.0)
    exit_file = run_dir / "build.exit"
    result_file = run_dir / "job_result.json"
    
    assert exit_file.exists()
    assert exit_file.read_text().strip() == "0"
    
    assert result_file.exists()
    result = json.loads(result_file.read_text())
    assert result["success"] is True
    assert result["exit_code"] == 0
    assert "metrics" in result
    assert result["metrics"]["clean_bytes"] > 0

def test_build_failure_artifacts(ddd_workspace, daemon_proc):
    """Verifies artifacts generated on build failure."""
    ddd_dir = ddd_workspace / ".ddd"
    run_dir = ddd_dir / "run"
    config_file = ddd_dir / "config.json"
    
    config_data = {
        "targets": {
            "dev": {
                "build": { 
                    "cmd": "echo 'FAILING' && exit 1", 
                    "filter": "raw" 
                }
            }
        }
    }
    config_file.write_text(json.dumps(config_data))

    # Trigger
    (run_dir / "build.request").touch()
    
    # Wait for completion (idle)
    time.sleep(1.0) # Simple wait for test speed, robust via lock check loop preferred
    lock_file = run_dir / "ipc.lock"
    for _ in range(30):
        if not lock_file.exists():
            break
        time.sleep(0.1)
        
    # Verify Failure Artifacts
    exit_file = run_dir / "build.exit"
    result_file = run_dir / "job_result.json"
    
    assert exit_file.exists()
    assert exit_file.read_text().strip() != "0"
    
    assert result_file.exists()
    result = json.loads(result_file.read_text())
    assert result["success"] is False
    assert result["exit_code"] != 0
