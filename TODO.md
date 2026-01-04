# Project TODOs

## 🚧 Active Sprint: Observability (v0.5.0)
- [ ] **Build Summary Stats**
    - **Goal:** Provide the AI with feedback on the "cost" and speed of the build.
    - **Task:** Append a footer to `build.log` with processing metrics:
        - Raw Log Size vs. Filtered Output Size (Compression ratio).
        - Duration (Seconds).
        - Token Estimate (Approx. 4 chars per token).

## 🔮 Backlog & Future Improvements
- [ ] **Native Daemonization**
    - Support `--start` / `--stop` arguments to run the daemon as a detached background service (systemd/launchd).
- [ ] **Daemon-Side Process Management**
    - Currently, the client (`ddd-wait`) handles timeouts.
    - **Task:** Add `timeout_sec` to `config.json` so the Daemon can kill zombie build processes (`make` hangs) even if the client disconnects.
- [ ] **Dependency Graphing (Integration)**
    - Investigate integrating `cscope` or `clang-query` to feed better context to the AI (Planned for `aider-vertex`).

## ✅ Recently Completed (v0.4.x)

### Reliability & Fixes
- [x] **Fix `wait` Client Tool Path Resolution**
    - Injected script now correctly resolves `DDD_DIR` relative to itself using `dirname "${BASH_SOURCE[0]}"`.
- [x] **Fix Silent Failures in JSON Filter**
    - `gcc_json` filter now detects empty regex matches on non-empty input and injects a "Synthetic Error" to alert the AI.
- [x] **Stale Lock Cleanup**
    - Daemon unconditionally deletes `*.lock` files in `.ddd/` on startup to recover from crashes.
- [x] **Client Safety Timeout**
    - `ddd-wait` now accepts `DDD_TIMEOUT` (default: 60s) to prevent hanging on stalled builds.

### Architecture (Completed Roadmap Items)
- [x] **Phase 1: Test Harness**
    - Ported legacy shell scripts to `pytest` (`tests/test_daemon.py`).
    - Added unit tests for filters (`tests/test_filters.py`).
- [x] **Phase 2: Plugin Bus**
    - Implemented dynamic "Cascade" loading (Built-in -> User Global -> Project Local) in `src/filters/__init__.py`.
- [x] **Phase 3: Plugin Reliability**
    - Created `ddd-test` runner to discover and test custom user plugins.
- [x] **Phase 4: Structured Logging**
    - Implemented `gcc_json` filter to parse GCC/Clang output into machine-readable JSON arrays.