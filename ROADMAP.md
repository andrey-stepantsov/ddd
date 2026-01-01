# DDD Roadmap & Architecture

## Strategic Goals
1.  **Reliability:** The daemon must never hang or crash silently.
2.  **Extensibility:** Users can add build parsers (plugins) without modifying core source.
3.  **Observability:** AI agents must receive structured, machine-readable errors.

---

## 🏗 Phase 1: The Test Harness (Immediate Priority)
**Goal:** Replace fragile shell scripts with a robust Python testing framework to enable safe refactoring.

* [ ] **Switch to Pytest:**
    * Create `requirements-dev.txt` (keep `requirements.txt` lean).
    * Add `pytest` and `coverage`.
* [ ] **Port Core Tests:**
    * Convert `tests/run_tests.sh` logic into `tests/test_daemon.py`.
    * Use `subprocess` to spawn the daemon and verify Lock/Log protocols.
* [ ] **Unit Tests:**
    * Ensure `src/filters.py` has native unit tests using `pytest` fixtures.

## 🔌 Phase 2: The Plugin Bus
**Goal:** Decouple filter logic from the daemon core. Support a "Cascade" of plugin sources.

* [ ] **Refactor Filter Registry:**
    * Deprecate hardcoded imports in `src/filters.py`.
    * Implement dynamic `importlib` loader.
* [ ] **Implement "The Cascade" (Load Order):**
    1.  Project Local: `.ddd/filters/*.py` (High Priority)
    2.  User Global: `~/.config/ddd/filters/*.py`
    3.  Built-in: `src/filters/*.py` (Defaults)

## 🧪 Phase 3: Plugin Reliability
**Goal:** Ensure plugins are robust "Micro-Libraries" with their own tests.

* [ ] **"Test Where You Live" Standard:**
    * Enforce rule: Every `my_filter.py` must have a sibling `test_my_filter.py`.
* [ ] **Test Discovery:**
    * Configure `pytest` to scan `.ddd/filters/` and `~/.config/ddd/filters/` for tests.
    * Create a helper `ddd-test` command that runs core tests + active plugin tests.

## 🧠 Phase 4: Structured Logging
**Goal:** Provide AI with JSON-formatted error logs for high-precision fixing.

* [ ] **Create `gcc_json` Plugin:**
    * Implement regex parsers for GCC/Clang output.
    * Return JSON: `[{"file": "main.c", "line": 10, "error": "missing ;"}]`.
* [ ] **Integration:**
    * Verify Aider can consume and act on this JSON data.

---

## 🛡 Future Ideas (Backlog)
* **Native Daemonization:** Support `--start/--stop` arguments to detach from terminal.
* **Process Management:** Add timeouts to `config.json` to prevent zombie builds.