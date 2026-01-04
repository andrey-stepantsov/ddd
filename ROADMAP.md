# DDD Roadmap & Architecture

## Strategic Goals
1.  **Reliability:** The daemon must never hang or crash silently.
2.  **Extensibility:** Users can add build parsers (plugins) without modifying core source.
3.  **Observability:** AI agents must receive structured, machine-readable errors and metrics.

---

## 🚀 Upcoming: The "Service" Era (v0.6.0)
**Goal:** Transition DDD from a foreground tool to a proper background service.

* [ ] **Native Daemonization:**
    * Support `--start` (launch in background) and `--stop` (kill via PID file).
    * Integration with systemd (Linux) and launchd (macOS).
* [ ] **Process Management:**
    * Daemon should enforce timeouts on child processes (`make`), not just the client.
    * Prevent zombie builds if the client disconnects.

## 🔮 Future Backlog
* [ ] **Dependency Graphing:**
    * Integrate `cscope` or `clang-query` to help agents understand "Callers" and "Callees".
* [ ] **Remote Builders:**
    * Allow the Daemon to dispatch builds to a remote docker host (e.g., rigid cloud build agents).

---

## ✅ Completed History

### v0.5.0: Observability (Jan 2026)
* [x] **Build Metrics:** Footer in `build.log` with Duration, Compression Ratio, and Token Usage.
* [x] **Noise Reduction:** Refined metrics to clearly indicate "Noise Reduction" vs "Compression".

### v0.4.0: The Plugin Architecture (Dec 2025)
* [x] **Phase 4: Structured Logging:** `gcc_json` filter for machine-readable errors.
* [x] **Phase 3: Plugin Reliability:** `ddd-test` runner for user plugins.
* [x] **Phase 2: The Plugin Bus:** "Cascade" loading (Built-in -> User -> Project).

### v0.3.0: The Test Harness (Nov 2025)
* [x] **Phase 1: Pytest Migration:** Replaced shell scripts with `pytest` suite.