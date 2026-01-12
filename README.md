# DDD - Distributed Developer Daemon (v0.6.0)

**Repository:** [github.com/andrey-stepantsov/ddd](https://github.com/andrey-stepantsov/ddd)

## Overview
DDD ("Dead Drop Daemon") is a physical-to-virtual bridge that allows modern AI agents and host tools to control a persistent, isolated build container. It separates **Source Code** from **Build State** using a robust file-watching protocol.

## 🚀 New in v0.6.0: Project-Local Architecture
* **Split State:** All runtime locks (`ipc.lock`) and logs (`build.log`) now live in `.ddd/run/`.
* **Portable:** Zero-dependency installation. Just copy the `ddd` folder and run.
* **Self-Bootstrapping:** Automatically creates its own isolated Python environment.

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
│       └── build.log      <-- Build Output
└── src/
```

## 🚦 Usage

1.  **Start the Daemon:**
    Run `dd-daemon` in your project root. It will create `.ddd/run/` automatically.

2.  **Trigger a Build:**
    Run the client tool (or have your AI Agent run it):
    ```bash
    ./.ddd/wait
    ```

3.  **The Protocol:**
    * **Trigger:** Client touches `.ddd/run/build.request`.
    * **Lock:** Daemon creates `.ddd/run/ipc.lock`.
    * **Build:** Daemon runs the command defined in `config.json`.
    * **Response:** Daemon writes output to `.ddd/run/build.log` and removes the lock.

## 🧪 Testing
Run the self-contained test suite:
```bash
./bin/ddd-test
```
