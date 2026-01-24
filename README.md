# DDD - Distributed Developer Daemon (v0.7.0)

**Repository:** [github.com/andrey-stepantsov/ddd](https://github.com/andrey-stepantsov/ddd)

## Overview
DDD ("Dead Drop Daemon") is a physical-to-virtual bridge that allows modern AI agents and host tools to control a persistent, isolated build container. It separates **Source Code** from **Build State** using a robust file-watching protocol.

## 🚀 New in v0.7.0: Robust Architecture
* **Daemon Mode:** Native background support via `dd-daemon --daemon` (Double-Fork).
* **Structured Artifacts:** Machine-readable `job_result.json` and `build.exit` for reliable automation.
* **Hermetic Bootstrap:** Uses hash-based caching for fully isolated Python environments.

## 🛠 Installation

### Option A: Standalone (Manual)
1.  Copy this directory to your machine (e.g., `~/tools/ddd`).
2.  Symlink the binary:
    ```bash
    ln -s ~/tools/ddd/bin/dd-daemon /usr/local/bin/dd-daemon
    ```

### Option B: Mission Pack (Integrated)
DDD comes pre-bundled with **Mission Core**.
* **Daemon:** `.mission/tools/bin/dd-daemon`
* **Client:** `.mission/tools/ddd/bin/ddd-wait`

## 🏗 Directory Structure

```text
YourProject/
├── .ddd/
│   ├── config.json        <-- [User] Build Targets
│   ├── filters/           <-- [User] Custom Parsers
│   └── run/               <-- [System] Ephemeral State (GitIgnored)
│       ├── ipc.lock       <-- Daemon Busy Signal
│       ├── build.request  <-- Trigger File
│       ├── build.log      <-- Build Output
│       ├── build.exit     <-- [New] Atomic Exit Code
│       └── job_result.json <-- [New] Full Job Metadata
└── src/
```

## 🚦 Usage

1.  **Start the Daemon:**
    ```bash
    dd-daemon --daemon
    ```
    This will fork into the background and create `.ddd/daemon.pid`.

2.  **Trigger a Build:**
    Run the client tool (or have your AI Agent run it):
    ```bash
    ./.ddd/wait
    ```

3.  **The Protocol:**
    * **Trigger:** Client touches `.ddd/run/build.request`.
    * **Lock:** Daemon creates `.ddd/run/ipc.lock`.
    * **Timeouts:** Daemon respects `stdbuf` for real-time streaming.
    * **Result:** 
        * `build.log`: Human-readable output.
        * `build.exit`: "0" or "1".
        * `job_result.json`: Detailed metrics (clean bytes, duration).

## 🧪 Testing
Run the self-contained test suite (requires `devbox` or `pytest`):
```bash
devbox run test
```
