# DDD - Distributed Developer Daemon (v0.8.0)

**Repository:** [github.com/stepants/ddd](https://github.com/stepants/ddd)

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

## 🚀 Quick Start (3 Minutes)

**New to DDD?** Get it running in 3 minutes with project-local installation:

### Step 1: Bootstrap DDD in Your Project (1 minute)

```bash
cd your-project
curl -sSL https://raw.githubusercontent.com/stepants/ddd/main/bootstrap-ddd.sh | bash -s .
```

**Or using local copy:**
```bash
git clone https://github.com/stepants/ddd.git /tmp/ddd
/tmp/ddd/bootstrap-ddd.sh your-project
```

This creates `.ddd/` directory with everything you need.

### Step 2: Try the Example (1 minute)

```bash
cd examples/hello-world

# Option 1: Use Makefile
make -f .ddd/Makefile ddd-daemon-bg
make -f .ddd/Makefile ddd-build

# Option 2: Direct paths
.ddd/bin/dd-daemon --daemon
.ddd/wait
```

### Step 3: See the Results (1 minute)

```bash
cat .ddd/run/build.log  # Filtered output
cat .ddd/run/build.exit # Exit code: 0 = success
./hello                 # Run the built program
```

**Success!** You've run your first DDD build.

**What's Next?**
- Configure for your project: [CONFIG_REFERENCE.md](CONFIG_REFERENCE.md)
- Learn about filters: [FILTERS.md](FILTERS.md)
- Integrate with your Makefile (see Installation below)

**Troubleshooting:**
- Daemon won't start? `cat .ddd/daemon.log`
- Bootstrap failed? Check `.ddd/.gitignore` for patterns to add manually
- Build failed? `cat .ddd/run/last_build.raw.log`

## 🆕 New in v0.8.0: Project-Local Bootstrap
* **Zero Global Install:** DDD installs locally in each project's `.ddd/` directory
* **No Conflicts:** Each project gets its own isolated DDD installation  
* **Makefile Integration:** Optional `-include .ddd/Makefile` for seamless integration
* **Git Friendly:** Smart `.gitignore` updates (optional), vendored source in `.ddd/ddd/`
* **Backward Compatible:** v0.7.x projects still work with updated binaries

## Prerequisites

Before installing, verify you have:
- **Python 3.7+** - Check: `python3 --version`
- **Bash shell** - macOS/Linux (Windows via WSL2)
- **Git** - For cloning the repository
- **Write access** - To `~/.local/bin/` (or `/usr/local/bin/`)

**Disk Space:** ~50MB (Python venv + dependencies)

## 🛠 Installation

### Option A: Project-Local Bootstrap (Recommended)

**Best for:** Individual projects, trying DDD, no global install needed

```bash
cd your-project
curl -sSL https://raw.githubusercontent.com/stepants/ddd/main/bootstrap-ddd.sh | bash -s .
```

**Or with local copy (development):**
```bash
LOCAL_DDD_PATH=/path/to/ddd /path/to/ddd/bootstrap-ddd.sh your-project
```

**What it creates:**
```
your-project/
├── .ddd/
│   ├── bin/              # Wrapper scripts (in PATH with direnv)
│   ├── ddd/              # Vendored DDD source
│   ├── run/              # Build artifacts (gitignored)
│   ├── Makefile          # DDD make targets
│   └── wait -> bin/ddd-wait
```

**Usage options after bootstrap:**

1. **Standalone:** `make -f .ddd/Makefile ddd-daemon-bg`
2. **Integrated:** Add `-include .ddd/Makefile` to your Makefile, then use `make ddd-daemon-bg`
3. **Direct:** `.ddd/bin/dd-daemon --daemon`
4. **With direnv:** Add `.ddd/bin` to PATH, then use `dd-daemon --daemon`

### Option B: Git Submodule (Shared across projects)

**Best for:** Multiple projects sharing one DDD version, CI/CD pipelines

```bash
cd your-project
git submodule add https://github.com/stepants/ddd.git .ddd/ddd
# Then run bootstrap to create wrappers
bash .ddd/ddd/bootstrap-ddd.sh .
```

**Update DDD:**
```bash
git submodule update --remote .ddd/ddd
```

### Option C: Developer Install (Global)

**Best for:** DDD development, testing multiple projects

```bash
git clone https://github.com/stepants/ddd.git ~/ddd
cd ~/ddd
./install.sh
```

This installs binaries to `~/.local/bin/` (add to PATH if needed).

**Verify:**
```bash
which dd-daemon  # Should show: /Users/yourname/.local/bin/dd-daemon
```

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

## 🏗 Directory Structure (v0.8.0)

```text
your-project/
├── .ddd/
│   ├── bin/                   # [Generated] Wrapper scripts
│   │   ├── dd-daemon          # → calls .ddd/ddd/bin/dd-daemon
│   │   ├── ddd-wait           # → calls .ddd/ddd/bin/ddd-wait
│   │   └── ddd-test           # → calls .ddd/ddd/bin/ddd-test
│   ├── ddd/                   # [Vendored] DDD source (gitignored)
│   │   ├── bin/               # Original binaries (smart path resolution)
│   │   ├── src/               # Python daemon source
│   │   ├── bootstrap.sh       # Hermetic bootstrapper
│   │   └── ...                # Full DDD repo
│   ├── config.json            # [User] Build configuration ✓ commit
│   ├── filters/               # [User] Custom filters ✓ commit
│   ├── run/                   # [Runtime] Build artifacts (gitignored)
│   │   ├── ipc.lock           # Daemon busy signal
│   │   ├── build.request      # Trigger file
│   │   ├── build.log          # Filtered output
│   │   ├── build.exit         # Exit code (0=success)
│   │   ├── job_result.json    # Build metrics
│   │   └── last_build.raw.log # Unfiltered output
│   ├── daemon.log             # [Runtime] Daemon stdout/stderr (gitignored)
│   ├── daemon.pid             # [Runtime] Daemon PID (gitignored)
│   ├── wait -> bin/ddd-wait   # [Generated] Convenience symlink
│   ├── Makefile               # [Generated] DDD make targets
│   └── .gitignore             # [Reference] Patterns to add
├── Makefile                   # [Optional] Your project Makefile
│   # Add: -include .ddd/Makefile
└── src/                       # Your source code
```

**Key differences from v0.7.0:**
- `.ddd/ddd/` - Vendored DDD source (was global in v0.7.x)
- `.ddd/bin/` - Wrapper scripts for easy invocation
- `.ddd/Makefile` - DDD-specific targets (no conflicts with your Makefile)

## 📝 Important: Git Configuration (v0.8.0)

### What to Commit

✅ **DO commit:**
- `.ddd/config.json` - Your build configuration
- `.ddd/filters/` - Your custom filters
- `.ddd/Makefile` - Generated but useful for consistency

❌ **DON'T commit:**
- `.ddd/run/` - Build artifacts (ephemeral)
- `.ddd/ddd/` - Vendored DDD source (large, changes with updates)
- `.ddd/daemon.log`, `.ddd/daemon.pid` - Runtime files
- `.ddd/bin/`, `.ddd/wait` - Generated wrappers

### Automatic .gitignore Update

Bootstrap automatically updates `.gitignore` unless you set `DDD_UPDATE_GITIGNORE=no`.

**Patterns added:**
```gitignore
# DDD Runtime
.ddd/run/
.ddd/daemon.log
.ddd/daemon.pid

# DDD Vendored Source (regenerate with bootstrap)
.ddd/ddd/

# DDD Generated Files
.ddd/bin/
.ddd/wait
.ddd/Makefile
```

### Manual Setup (If Bootstrap Skipped)

If you set `DDD_UPDATE_GITIGNORE=no`, copy patterns from `.ddd/.gitignore`:

```bash
# Reference file created by bootstrap
cat .ddd/.gitignore >> .gitignore
```

### Why Vendor `.ddd/ddd/`?

**Option 1: Gitignore (Recommended)**
- Smaller repo size
- Update via re-bootstrap
- Each developer can use different DDD versions

**Option 2: Commit (Alternative)**
- Reproducible builds (locked DDD version)
- No bootstrap needed for new clones
- Larger repo (+~500KB)

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
