# Contributing to DDD

Thank you for your interest in the Distributed Developer Daemon.

## 🛠 Development Environment

We support two ways to set up your development environment: **Devbox** (recommended) or **Standard Python Venv**.

### Option A: Devbox (Automated)
If you have [Devbox](https://www.jetpack.io/devbox/docs/installing_devbox/) installed:

1. Enter the shell:

    devbox shell

   *This automatically installs Python 3.x and creates the virtual environment.*

2. Install dependencies:

    pip install -r requirements.txt
    # pip install -r requirements-dev.txt  # (Coming soon in Phase 1)

### Option B: Manual Setup
1. Create a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

2. Install dependencies:

    pip install -r requirements.txt

---

## 🧪 Running Tests

### End-to-End Verification
We currently use a shell-based integration test suite.

    ./tests/run_tests.sh

This script will:
1. Spin up the daemon in the background.
2. Trigger a mock build.
3. Verify the lock file protocol and log capture.

### Client Verification
To test the `ddd-wait` client specifically:

    ./tests/test_wait_client.sh

---

## 🚀 Releasing

1. **Bump Version:** Update the version number in `VERSION`.
2. **Tag:** Create a git tag (e.g., `v0.1.0`).
3. **Push:** Push the tag to origin.
