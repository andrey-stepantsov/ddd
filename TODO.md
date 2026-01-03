# Project TODOs

## 🚨 Critical Fixes (Next Release)
- [ ] **Fix `wait` Client Tool Path Resolution**
    - **Issue:** The generated `.ddd/wait` script assumes the `.ddd` directory is in the current working directory (`PWD`). This fails when the script is invoked from a sub-directory (e.g., inside a `weave-view` or deeply nested folder), causing "file not found" errors for the lock/trigger files.
    - **Fix:** Update the `_write_client_tool` function in `dd-daemon.py`. The generated bash script must resolve `DDD_DIR` relative to the script's own location, not the caller's location.
    - **Code Change:**
        ```bash
        # Old
        DDD_DIR=".ddd"
        
        # New
        DDD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        ```
    - **Impact:** Allows the build trigger to work reliably from any directory in the project hierarchy.

- [ ] **Fix Silent Failures in JSON Filter**
    - **Issue:** If the build command fails (exit code != 0) but the regex matches 0 errors, `gcc_json` produces an empty list. This tricks the AI into thinking the build succeeded.
    - **Fix:** `gcc_json` should inject a "Synthetic Error" object containing the raw `stderr` or the `make` exit code message when this state is detected.

## 🛡️ Reliability & Robustness
- [ ] **Implement Stale Lock Cleanup on Startup**
    - **Issue:** If `dd-daemon` crashes or is killed abruptly (SIGKILL), the `run.lock` file may remain. On restart, the daemon might stall or reject new builds.
    - **Fix:** On startup (in `dd-daemon.py`), unconditionally delete `*.lock` files in `.ddd/`.

- [ ] **Add Safety Timeout to Client `wait` Script**
    - **Issue:** The generated `wait` script loops forever (`while [ -f "$LOCK" ]`) if the daemon crashes during a build. This causes the AI agent to hang indefinitely.
    - **Fix:** Add a timeout counter to the bash script generator:
        ```bash
        MAX_RETRIES=300 # 60 seconds at 0.2s sleep
        count=0
        while [ -f "$LOCK" ]; do
            if [ $count -ge $MAX_RETRIES ]; then
                echo "Error: Build timed out or daemon crashed."
                exit 1
            fi
            sleep 0.2
            count=$((count+1))
        done
        ```

## 📊 Observability & Metrics (v0.5.0)
- [ ] **Build Summary Stats**
    - Append a footer to `build.log` with processing metrics:
        - Raw Log Size vs. Filtered Output Size
        - Duration (Seconds)
        - Token Estimate (Approx. 4 chars per token)