# Project TODOs

## 🚨 Critical Fixes (Next Release)
- [x] **Fix `wait` Client Tool Path Resolution**
    - **Issue:** The generated `.ddd/wait` script assumed the `.ddd` directory was in `PWD`.
    - **Fix:** Updated `_write_client_tool` in `dd-daemon.py` to use `dirname "${BASH_SOURCE[0]}"`.
    - **Status:** Done. Injected script now resolves paths relative to itself.

- [x] **Fix Silent Failures in JSON Filter**
    - **Issue:** If build failed (exit != 0) but regex matched 0 errors, AI thought it succeeded.
    - **Fix:** `gcc_json` now injects a "Synthetic Error" object if output exists but parses to empty on failure.

## 🛡️ Reliability & Robustness
- [x] **Implement Stale Lock Cleanup on Startup**
    - **Fix:** Daemon now unconditionally deletes `*.lock` files in `.ddd/` on startup.

- [x] **Add Safety Timeout to Client `wait` Script**
    - **Fix:** Added configurable timeout loop to `ddd-wait`.
    - **Feature:** Users can set `DDD_TIMEOUT` (default: 60s).

## 📊 Observability & Metrics (v0.5.0)
- [ ] **Build Summary Stats**
    - Append a footer to `build.log` with processing metrics:
        - Raw Log Size vs. Filtered Output Size
        - Duration (Seconds)
        - Token Estimate (Approx. 4 chars per token)