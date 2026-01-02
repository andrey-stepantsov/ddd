import time
import json
import os
import pytest

def test_end_to_end_build_cycle(ddd_workspace, daemon_proc):
    """
    Verifies the core 'Triple-Head' protocol:
    1. User touches build.request
    2. Daemon sees it and creates run.lock (Busy)
    3. Daemon runs command and writes logs
    4. Daemon removes run.lock (Idle)
    """
    
    # --- 1. Configure the Daemon ---
    ddd_dir = ddd_workspace / ".ddd"
    config_file = ddd_dir / "config.json"
    
    # We use 'sleep 1' so we have time to assert the lock file exists
    config_data = {
        "targets": {
            "dev": {
                "build": { 
                    "cmd": "sleep 1 && echo 'PYTEST_BUILD_SUCCESS'", 
                    "filter": "raw" 
                }
            }
        }
    }
    config_file.write_text(json.dumps(config_data))

    # --- 2. Trigger the Build ---
    trigger_file = ddd_dir / "build.request"
    trigger_file.touch()
    
    # --- 3. Verify Lock Acquisition (Busy State) ---
    # The shell script waited 1s; we poll for up to 2s
    lock_file = ddd_dir / "run.lock"
    lock_seen = False
    
    for _ in range(20):
        if lock_file.exists():
            lock_seen = True
            break
        time.sleep(0.1)
        
    assert lock_seen, "Daemon did not create run.lock after trigger."

    # --- 4. Verify Lock Release (Idle State) ---
    # Wait for the 'sleep 1' to finish and lock to be removed
    lock_vanished = False
    for _ in range(30):
        if not lock_file.exists():
            lock_vanished = True
            break
        time.sleep(0.1)
        
    assert lock_vanished, "Daemon did not remove run.lock after build completed."

    # --- 5. Verify Log Capture ---
    clean_log = ddd_dir / "build.log"
    raw_log = ddd_dir / "last_build.raw.log"
    
    assert clean_log.exists(), "Clean log file was not created."
    assert "PYTEST_BUILD_SUCCESS" in clean_log.read_text(), "Clean log missing expected output."
    
    assert raw_log.exists(), "Raw log file was not created."
    assert "PYTEST_BUILD_SUCCESS" in raw_log.read_text(), "Raw log missing expected output."