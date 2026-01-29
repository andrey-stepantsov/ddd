# DDD - Distributed Developer Daemon (v0.7.0)

**Repository:** [github.com/andrey-stepantsov/ddd](https://github.com/andrey-stepantsov/ddd)

## Overview
DDD ("Dead Drop Daemon") is a physical-to-virtual bridge that allows modern AI agents and host tools to control a persistent, isolated build container. It separates **Source Code** from **Build State** using a robust file-watching protocol.

## 🚀 New in v0.7.0: Project-Local Architecture
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
│   ├── config.json           <-- [User] Build Configuration (see CONFIG_REFERENCE.md)
│   ├── filters/              <-- [User] Custom Filters (optional)
│   ├── daemon.log            <-- [System] Daemon stdout/stderr (--daemon mode)
│   ├── daemon.pid            <-- [System] Daemon Process ID (--daemon mode)
│   └── run/                  <-- [System] Ephemeral State (GitIgnored)
│       ├── ipc.lock          <-- Daemon Busy Signal
│       ├── build.request     <-- Trigger File
│       ├── build.log         <-- Filtered Build Output
│       ├── build.exit        <-- Exit Code (0=success, 1=failure)
│       ├── job_result.json   <-- Rich Build Metrics
│       └── last_build.raw.log <-- Unfiltered Original Output
└── src/
```

## 🚦 Usage

### Basic Usage

1.  **Configure Your Build:**
    Create `.ddd/config.json` (see `CONFIG_REFERENCE.md` for details):
    ```json
    {
      "targets": {
        "dev": {
          "build": {
            "cmd": "make -j4",
            "filter": "gcc_json"
          }
        }
      }
    }
    ```

2.  **Start the Daemon:**
    Run `dd-daemon` in your project root. It will create `.ddd/run/` automatically.
    ```bash
    dd-daemon
    ```

3.  **Trigger a Build:**
    Run the client tool (or have your AI Agent run it):
    ```bash
    ./.ddd/wait
    ```

4.  **The Protocol:**
    * **Trigger:** Client touches `.ddd/run/build.request`.
    * **Lock:** Daemon creates `.ddd/run/ipc.lock`.
    * **Build:** Daemon runs the command defined in `config.json`.
    * **Response:** Daemon writes output to `.ddd/run/build.log` and removes the lock.

### Advanced Usage

#### Background Daemon Mode

Run the daemon detached from your terminal:

```bash
dd-daemon --daemon
```

**Management:**
```bash
# Check daemon status
cat .ddd/daemon.pid      # Process ID
tail -f .ddd/daemon.log  # Watch daemon logs

# Stop daemon
kill $(cat .ddd/daemon.pid)
```

#### Custom Client Timeout

Override the default 60-second timeout:

```bash
DDD_TIMEOUT=120 ./.ddd/wait  # Wait up to 2 minutes
```

Useful for long-running builds or slow systems.

#### Build Artifacts & Observability

After each build, the daemon generates several artifacts:

```bash
.ddd/run/
├── build.log            # Filtered, AI-friendly output
├── build.exit           # Exit code: 0=success, 1=failure
├── job_result.json      # Rich metrics (duration, compression, tokens)
└── last_build.raw.log   # Unfiltered original output
```

**CI/CD Integration:**
```bash
./.ddd/wait
exit_code=$(cat .ddd/run/build.exit)
exit $exit_code
```

**Metrics Example** (`job_result.json`):
```json
{
  "success": true,
  "exit_code": 0,
  "duration": 2.34,
  "metrics": {
    "raw_bytes": 50000,
    "clean_bytes": 12000
  },
  "timestamp": 1706400000.0,
  "pid": 12345
}
```

#### Filter Configuration

Control output processing with filters (see `FILTERS.md` for details):

**Single filter:**
```json
"filter": "gcc_json"
```

**Chained filters:**
```json
"filter": ["gcc_make", "gcc_json"]
```

**No filtering (raw output):**
```json
"filter": "raw"
```

## 🧪 Testing
Run the self-contained test suite:
```bash
./bin/ddd-test
```

## 📚 Documentation

- **[CONFIG_REFERENCE.md](CONFIG_REFERENCE.md)** - Complete configuration guide with examples
- **[FILTERS.md](FILTERS.md)** - Available filters and custom filter development
- **[PARASITIC_MODE.md](PARASITIC_MODE.md)** - Host build + containerized AI setup
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development setup and testing
- **[ROADMAP.md](ROADMAP.md)** - Feature roadmap and version history
