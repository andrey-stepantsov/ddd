# Project TODOs

## 🚧 Active Sprint
*(No active tasks. Ready for v0.5.0 Release Candidate)*

## 🔮 Backlog & Future Improvements
- [ ] **Native Daemonization**
    - Support `--start` / `--stop` arguments to run the daemon as a detached background service (systemd/launchd).
- [ ] **Daemon-Side Process Management**
    - Currently, the client (`ddd-wait`) handles timeouts.
    - **Task:** Add `timeout_sec` to `config.json` so the Daemon can kill zombie build processes (`make` hangs) even if the client disconnects.
- [ ] **Dependency Graphing (Integration)**
    - Investigate integrating `cscope` or `clang-query` to feed better context to the AI (Planned for `aider-vertex`).

## ✅ Recently Completed (v0.5.0)

### Observability
- [x] **Build Summary Stats**
    - Appended footer to `build.log` with Duration, Noise Reduction %, and Token Estimates.

### Reliability & Fixes (v0.4.x)
- [x] **Fix `wait` Client Tool Path Resolution**
    - Injected script now correctly resolves `DDD_DIR` relative to itself using `dirname "${BASH_SOURCE[0]}"`.
- [x] **Fix Silent Failures in JSON Filter**
    - `gcc_json` filter now detects empty regex matches on non-empty input and injects a "Synthetic Error" to alert the AI.
- [x] **Stale Lock Cleanup**
    - Daemon unconditionally deletes `*.lock` files in `.ddd/` on startup to recover from crashes.
- [x] **Client Safety Timeout**
    - `ddd-wait` now accepts `DDD_TIMEOUT` (default: 60s) to prevent hanging on stalled builds.