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
