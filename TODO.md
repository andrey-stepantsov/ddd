# Project TODOs & Known Issues

## v0.4.1 - Reliability Improvements
- [ ] **Fix Silent Failures in JSON Filter:** If the build command fails (exit code != 0) but the regex matches 0 errors, `gcc_json` should inject a "Synthetic Error" object containing the raw output or the `make` error message.

## v0.5.0 - Observability & Metrics
- [ ] **Build Summary Stats:** Append a footer to `build.log` with processing metrics.
  *Metrics:*
    - Raw Log Size (KB / Lines)
    - Filtered Output Size (KB / Lines)
    - Duration (Seconds)
    - Compression Ratio (Raw / Filtered)
    - Token Estimate (Approx. 4 chars per token)

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
