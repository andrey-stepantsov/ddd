# Contributing to DDD

Thank you for your interest in the Distributed Developer Daemon.

## 🛠 Development Environment

We support two ways to set up your development environment: **Devbox** (Core Devs) or **Standard Python Venv** (Plugin Devs).

### Option A: Devbox (Automated)
If you have [Devbox](https://www.jetpack.io/devbox/docs/installing_devbox/) installed:

1. Enter the shell:

    devbox shell

   *This automatically installs Python 3.x, creates the virtual environment, and syncs all dependencies.*

### Option B: Manual Setup
Use this if you installed via `install.sh` and now want to run tests.

1. Activate the virtual environment:

    # If you ran install.sh, the venv is already here:
    source .venv/bin/activate

2. Install dependencies:

    pip install -r requirements.txt
    pip install -r requirements-dev.txt

---

## 🧪 Running Tests

### End-to-End & Unit Verification
We use `pytest` for the complete test suite (Daemon behavior + Filter logic).

    pytest

### Testing Plugins (New in v0.3.0)
If you write custom filters (in `.ddd/filters` or `~/.config/ddd/filters`), you can verify them using the `ddd-test` runner.

**The "Test Where You Live" Rule:**
If you create `my_filter.py`, create a sibling `test_my_filter.py` next to it.

**Running the Tests:**
Run the test runner from your project root:

    ddd-test

This command automatically:
1.  Discovers core tests (`tests/`).
2.  Discovers your global plugins (`~/.config/ddd/filters`).
3.  Discovers your project plugins (`.ddd/filters`).
4.  Sets up `PYTHONPATH` so imports work correctly.
5.  Runs `pytest` on everything.

### Client Verification
To test the `ddd-wait` client binary specifically:

    ./tests/test_wait_client.sh

---

## 🚀 Releasing

1. **Bump Version:** Update the version number in `VERSION`.
2. **Tag:** Create a git tag (e.g., `v0.1.0`).
3. **Push:** Push the tag to origin.