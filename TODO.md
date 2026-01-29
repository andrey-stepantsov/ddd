# Project TODOs

## 🚧 Active Sprint
*(No active tasks. Ready for next version)*

## 🐛 Bugs Discovered (Documentation Analysis - Jan 2026)

### Target Name Hardcoded
- **Issue:** Daemon hardcodes target name "dev" (src/dd-daemon.py:117)
- **Impact:** Users cannot use different target names despite "targets" being a map
- **Expected:** CLI argument to select target: `dd-daemon --target production`
- **Workaround:** Always name your target "dev"
- **Priority:** Medium

### Parasitic Template Was Broken
- **Issue:** templates/parasitic.json used old config format (removed in v0.7.0)
- **Status:** FIXED - Updated to new targets format
- **File:** templates/parasitic.json still exists with old format
- **Action:** Should delete or update templates/parasitic.json to match new format

### Stdbuf Wrapper Complexity
- **Issue:** Auto-buffering logic wraps commands in nested shell quotes (src/dd-daemon.py:195-198)
- **Observation:** `shlex.quote(cmd)` then wrapping in `sh -c` may cause issues with complex shell commands
- **Potential Problem:** Commands with heredocs, subshells, or complex quoting might break
- **Priority:** Low (works for common cases)

### No Multi-Target Test Coverage
- **Issue:** Tests only verify "dev" target
- **Gap:** No tests for:
  - Multiple targets in config
  - Target selection (when implemented)
  - Invalid target handling
- **Priority:** Low (blocked by target selection feature)

## 🔮 Backlog & Future Improvements

### v0.8.0: Service Integration
- [ ] **Target Selection via CLI**
    - Allow selecting target: `dd-daemon --target production`
    - Currently hardcoded to "dev" (see Bugs section)
- [ ] **Native Daemonization (Enhanced)**
    - Status: `--daemon` flag exists (v0.7.0)
    - Remaining: systemd/launchd integration files
    - Add `--start`, `--stop`, `--status` convenience commands
- [ ] **Daemon-Side Process Management**
    - Currently, the client (`ddd-wait`) handles timeouts
    - **Task:** Add `timeout_sec` to `config.json` so the Daemon can kill zombie build processes (`make` hangs) even if the client disconnects
    - Prevents resource leaks when client crashes

### v0.9.0: Advanced Features
- [ ] **Dependency Graphing (Integration)**
    - Investigate integrating `cscope` or `clang-query` to feed better context to the AI
- [ ] **Remote Build Support**
    - Dispatch builds to remote Docker hosts
    - Use case: Cloud build agents, distributed CI/CD

### Documentation Improvements
- [ ] **TROUBLESHOOTING.md** - Common issues and solutions
- [ ] **EXAMPLES.md** - Real-world configuration examples
- [ ] **Update templates/parasitic.json** - Currently uses old config format

## ✅ Recently Completed (v0.6.0)

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