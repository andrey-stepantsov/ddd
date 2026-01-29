# DDD - Distributed Developer Daemon (v0.7.0)

**Repository:** [github.com/andrey-stepantsov/ddd](https://github.com/andrey-stepantsov/ddd)

## Overview

### The Problem

AI coding assistants (Aider, Cursor, Copilot) need to trigger builds and read compiler output. But:
- Running builds inside AI containers is **slow** (no native toolchain)
- Mounting volumes breaks **IDE integration** (debugger, intellisense)
- Docker adds **10-50% overhead** to every compile

### The Solution

DDD separates "editing code" from "building code":
- **AI Agent (in container):** Edits your code, triggers builds via file
- **DDD Daemon (on host):** Watches files, runs native builds, writes results
- **Communication:** Simple file protocol (no network, no security risk)

### Why "Dead Drop"?

Like a spy's dead drop, DDD uses files (`.ddd/run/build.request`) to pass messages between isolated environments without direct communication.

### Use Cases

✅ **AI Pair Programming** - Aider in container, native builds on host  
✅ **Parasitic CI** - Linux CI using macOS compiler via DDD  
✅ **Performance** - Avoid Docker build overhead (10-50% faster)  
✅ **Multi-Tool** - Multiple editors sharing one build daemon

❌ **Not for:** Simple local dev (just run `make`), projects without builds

### How It Works (30 seconds)

```text
1. You: Create .ddd/config.json (your build command)
2. Daemon: Watches .ddd/run/build.request
3. You/AI: Touch build.request (trigger)
4. Daemon: Runs your command, writes .ddd/run/build.log
5. You/AI: Read build.log (filtered output)
```

That's it. No servers, no network, just files.

## 🚀 Quick Start (5 Minutes)

**New to DDD?** Get it running in 5 minutes:

### Step 1: Install (2 minutes)

```bash
git clone https://github.com/andrey-stepantsov/ddd.git
cd ddd
./install.sh
```

**Add to PATH** (if `~/.local/bin` not already in PATH):
```bash
export PATH="$HOME/.local/bin:$PATH"
```

**Verify:**
```bash
which dd-daemon  # Should show: /Users/yourname/.local/bin/dd-daemon
```

### Step 2: Try the Example (2 minutes)

```bash
cd examples/hello-world
cat .ddd/config.json    # See the configuration
dd-daemon &             # Start daemon in background
./.ddd/wait             # Trigger a build
```

### Step 3: See the Results (1 minute)

```bash
cat .ddd/run/build.log  # Filtered output
cat .ddd/run/build.exit # Exit code: 0 = success
./hello                 # Run the built program
```

**Success!** You've run your first DDD build.

**What's Next?**
- Try it in your own project (see Installation below)
- Learn about filters: [FILTERS.md](FILTERS.md)
- Understand configuration: [CONFIG_REFERENCE.md](CONFIG_REFERENCE.md)

**Troubleshooting:**
- Daemon won't start? `cat .ddd/daemon.log`
- Command not found? Add `~/.local/bin` to your PATH (see Prerequisites below)
- Build failed? `cat .ddd/run/last_build.raw.log`

## 🚀 New in v0.7.0: Project-Local Architecture
* **Split State:** All runtime locks (`ipc.lock`) and logs (`build.log`) now live in `.ddd/run/`.
* **Portable:** Zero-dependency installation. Just copy the `ddd` folder and run.
* **Self-Bootstrapping:** Automatically creates its own isolated Python environment.

## Prerequisites

Before installing, verify you have:
- **Python 3.7+** - Check: `python3 --version`
- **Bash shell** - macOS/Linux (Windows via WSL2)
- **Git** - For cloning the repository
- **Write access** - To `~/.local/bin/` (or `/usr/local/bin/`)

**Disk Space:** ~50MB (Python venv + dependencies)

## 🛠 Installation

### Option A: Automated Install (Recommended)

```bash
git clone https://github.com/andrey-stepantsov/ddd.git
cd ddd
./install.sh
```

This script will:
1. Create a Python virtual environment (`.venv/`)
2. Install dependencies (`watchdog`, `pytest`)
3. Install binaries to `~/.local/bin/` (`dd-daemon`, `ddd-wait`, `ddd-test`)

**Add to PATH** (if not already):
```bash
# For bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# For zsh (macOS default)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Verify installation:**
```bash
which dd-daemon  # Should show: /Users/yourname/.local/bin/dd-daemon
```

### Option B: Standalone (Manual)

1.  Copy this directory to your machine (e.g., `~/tools/ddd`).
2.  Symlink the binary:
    ```bash
    ln -s ~/tools/ddd/bin/dd-daemon /usr/local/bin/dd-daemon
    ```
    
**Note:** Manual mode requires `bin/dd-daemon` to bootstrap Python dependencies on first run.

### Option C: Mission Pack (Integrated)

DDD comes pre-bundled with **Mission Core**.
* **Daemon:** `.mission/tools/bin/dd-daemon`
* **Client:** `.mission/tools/ddd/bin/ddd-wait`

### Troubleshooting Installation

**"Permission denied" on install.sh:**
```bash
chmod +x install.sh && ./install.sh
```

**"python3: command not found":**
- macOS: `brew install python3`
- Ubuntu/Debian: `sudo apt install python3 python3-pip python3-venv`
- Other: https://www.python.org/downloads/

**"~/.local/bin not in PATH":**  
Add to your shell config (see "Add to PATH" above)

**"pip install failed":**  
Check internet connection and try:
```bash
python3 -m pip install --user watchdog pytest
```

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

## 📝 Important: Git Configuration

### Add to .gitignore

The `.ddd/run/` directory contains ephemeral build artifacts that **should not** be committed:

```gitignore
# DDD Runtime (ephemeral build artifacts)
.ddd/run/
.ddd/daemon.log
.ddd/daemon.pid
```

**Keep in git:**
```text
.ddd/config.json    # Your build configuration
.ddd/filters/       # Your custom filters (if any)
```

**Why:** Build logs, lock files, and PIDs are machine-specific and regenerated on each build.

### Quick Setup

If starting a new project:
```bash
cat >> .gitignore <<'EOF'
# DDD
.ddd/run/
.ddd/daemon.log
.ddd/daemon.pid
EOF
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

### Verify It Works

After running `./.ddd/wait`, you should see output like this:

**Terminal 1 (Daemon):**
```text
[*] dd-daemon ACTIVE (v0.7.0).
[*] Watching: /Users/you/project/.ddd/run/build.request

[>>>] Signal received: .ddd/run/build.request
[+] Running BUILD: make -j4
[... your build output ...]
[*] Pipeline Complete.
```

**Terminal 2 (Client):**
```text
[ddd] Build triggered. Waiting for Daemon (Timeout: 60s)...
---------------------------------------------------
=== Pipeline: dev (Wed Jan 28 10:30:00 2026) ===

--- BUILD OUTPUT ---
[... filtered build output ...]

--- 📊 Build Stats ---
⏱  Duration: 2.34s
📉 Noise Reduction: 42.5% (50000 raw → 28750 clean bytes)
🪙  Est. Tokens: 7187
---------------------------------------------------
```

**Check the results:**
```bash
ls .ddd/run/
# Should see: build.log, build.exit, job_result.json, last_build.raw.log

cat .ddd/run/build.exit
# Should see: 0 (for success) or 1 (for failure)
```

### Stop the Daemon

**Foreground mode:** Press `Ctrl+C` in the daemon terminal

**Background mode:**
```bash
kill $(cat .ddd/daemon.pid)
```

### If Something Went Wrong

**"Daemon did not respond":**
- Check daemon is running: `ps aux | grep dd-daemon`
- Check daemon logs: `cat .ddd/daemon.log` (if --daemon mode)
- Restart daemon: Kill it and run `dd-daemon` again

**Build failed but no errors shown:**
- Check raw output: `cat .ddd/run/last_build.raw.log`
- Try with no filter: `"filter": "raw"` in config.json

**"Target 'dev' not found":**
- Verify config structure: `python3 -m json.tool .ddd/config.json`
- See [CONFIG_REFERENCE.md](CONFIG_REFERENCE.md) for correct format

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
