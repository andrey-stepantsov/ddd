# Plan: First-Time User Experience Improvements

**Created:** Jan 28, 2026  
**Context:** Post v0.7.0 documentation overhaul  
**Goal:** Make DDD accessible to new users within 5 minutes  
**Current Score:** 7.4/10 → **Target:** 9/10

---

## Executive Summary

DDD v0.7.0 has excellent technical documentation for intermediate users, but lacks onboarding support for first-time users. This plan addresses:

1. **Critical barriers** preventing quick success (no quick start, jargon-heavy intro)
2. **Missing context** that causes confusion (what success looks like, gitignore)
3. **Learning aids** that accelerate understanding (runnable examples, use cases)

**Total Estimated Effort:** 4-6 hours  
**Expected Impact:** 30% increase in successful first-time setups

---

## Phase 1: Critical Onboarding Fixes (2-3 hours)

### 1.1 Add Quick Start Section to README

**Location:** README.md, after Overview (before Installation)  
**Estimated Time:** 45 minutes

**Content Structure:**

```markdown
## 🚀 Quick Start (5 Minutes)

Want to try DDD right now? Here's the fastest path:

### Step 1: Install
```bash
git clone https://github.com/andrey-stepantsov/ddd.git
cd ddd
./install.sh
# Add to PATH if not already: export PATH="$HOME/.local/bin:$PATH"
```

### Step 2: Try the Hello World Example
```bash
cd examples/hello-world
cat .ddd/config.json    # See the configuration
dd-daemon &             # Start daemon in background
./.ddd/wait             # Trigger a build
```

### Step 3: See the Results
```bash
cat .ddd/run/build.log  # Filtered output
cat .ddd/run/build.exit # Exit code: 0 = success
```

**Success!** You've just run your first DDD build. The daemon watched for a trigger,
ran your command, and wrote the results. 

**What's Next?**
- Try it in your own project (see "Installation" below)
- Learn about filters (see FILTERS.md)
- Understand configuration (see CONFIG_REFERENCE.md)

**Troubleshooting:**
- Daemon won't start? Check: `cat .ddd/daemon.log`
- Command not found? Add `~/.local/bin` to your PATH
- Build failed? Check: `cat .ddd/run/last_build.raw.log`
```

**Implementation Notes:**
- Depends on examples/hello-world (see Phase 2)
- Should work with zero prior knowledge
- Must complete in < 5 minutes on any system

---

### 1.2 Rewrite Overview Section

**Location:** README.md, lines 5-11  
**Estimated Time:** 30 minutes

**Current Problem:** Starts with jargon ("physical-to-virtual bridge")

**New Structure:**

```markdown
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

Like a spy's dead drop, DDD uses files (`.ddd/run/build.request`) to pass messages
between isolated environments without direct communication.

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
```

**Why This Works:**
- Starts with user pain (relatable)
- Shows value proposition immediately
- Explains "Dead Drop" name (sticky memory)
- Sets expectations for who should use it

---

### 1.3 Add Prerequisites & Troubleshooting to Installation

**Location:** README.md, before Installation section  
**Estimated Time:** 30 minutes

**New Content:**

```markdown
## Prerequisites

Before installing, verify you have:
- **Python 3.7+** - Check: `python3 --version`
- **Bash shell** - macOS/Linux (Windows via WSL2)
- **Write access** - To `~/.local/bin/` or `/usr/local/bin/`
- **Git** - For cloning (or download ZIP)

**Disk Space:** ~50MB (Python venv + dependencies)

## 🛠 Installation

### Option A: Automated (Recommended)

```bash
git clone https://github.com/andrey-stepantsov/ddd.git
cd ddd
./install.sh
```

This script will:
1. Create a Python virtual environment (`.venv/`)
2. Install dependencies (`watchdog`, `pytest`)
3. Install binaries to `~/.local/bin/` (dd-daemon, ddd-wait, ddd-test)

**Add to PATH** (if not already):
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc  # or ~/.zshrc
source ~/.bashrc  # or source ~/.zshrc
```

**Verify installation:**
```bash
which dd-daemon  # Should show: /Users/yourname/.local/bin/dd-daemon
dd-daemon --help # Should show usage (will add in future)
```

### Option B: Standalone (Manual)
[existing content]

### Option C: Mission Pack (Integrated)
[existing content]

### Troubleshooting Installation

**"Permission denied" on install.sh**
```bash
chmod +x install.sh && ./install.sh
```

**"python3: command not found"**
Install Python 3.7+:
- macOS: `brew install python3`
- Ubuntu: `sudo apt install python3 python3-pip python3-venv`
- Other: See https://www.python.org/downloads/

**"~/.local/bin not in PATH"**
Add to your shell config:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

**"pip install failed"**
Check your internet connection and try:
```bash
pip3 install --user watchdog pytest
```
```

**Why This Helps:**
- New users know what they need upfront
- Clear success indicators ("Verify installation")
- Common errors pre-answered
- No assumptions about environment

---

### 1.4 Add "Verify It Works" Section

**Location:** README.md, after Basic Usage step 4  
**Estimated Time:** 30 minutes

**New Content:**

```markdown
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

**"Daemon did not respond"**
- Check daemon is running: `ps aux | grep dd-daemon`
- Check daemon logs: `cat .ddd/daemon.log` (if --daemon mode)
- Restart daemon: Kill it and run `dd-daemon` again

**Build failed but no errors shown**
- Check raw output: `cat .ddd/run/last_build.raw.log`
- Try with no filter: `"filter": "raw"` in config.json

**"Target 'dev' not found"**
- Verify config structure: `python3 -m json.tool .ddd/config.json`
- See CONFIG_REFERENCE.md for correct format

For more help, see: (future: link to TROUBLESHOOTING.md)
```

**Why This Helps:**
- New users know what success looks like
- Reduces "is it working?" anxiety
- Provides immediate debugging path
- Sets expectations for outputs

---

### 1.5 Add .gitignore Documentation

**Location:** README.md, after Directory Structure  
**Estimated Time:** 15 minutes

**New Content:**

```markdown
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

### Starter .gitignore

If starting fresh:
```bash
cat >> .gitignore <<'EOF'
# DDD
.ddd/run/
.ddd/daemon.log
.ddd/daemon.pid
EOF
```
```

**Why This Helps:**
- Prevents accidental commit of build artifacts
- Clear guidance on what to commit vs ignore
- Copy-paste ready solution

---

## Phase 2: Learning Aids (1.5-2 hours)

### 2.1 Create examples/ Directory

**Location:** `/examples/` (new directory)  
**Estimated Time:** 60 minutes

**Structure:**

```text
examples/
├── README.md (index of examples)
├── hello-world/
│   ├── README.md
│   ├── .ddd/
│   │   └── config.json
│   ├── .gitignore
│   ├── Makefile
│   └── hello.c
├── python-pytest/
│   ├── README.md
│   ├── .ddd/
│   │   └── config.json
│   ├── requirements.txt
│   ├── src/
│   │   └── calculator.py
│   └── tests/
│       └── test_calculator.py
└── multi-stage/
    ├── README.md
    ├── .ddd/
    │   └── config.json
    ├── Makefile
    └── src/
        └── app.c
```

**examples/hello-world/hello.c:**
```c
#include <stdio.h>

int main() {
    printf("Hello from DDD!\n");
    printf("Build system: Working!\n");
    return 0;
}
```

**examples/hello-world/Makefile:**
```makefile
all:
	@echo "Building hello world..."
	@gcc -o hello hello.c
	@echo "✓ Build successful!"
```

**examples/hello-world/.ddd/config.json:**
```json
{
  "targets": {
    "dev": {
      "build": {
        "cmd": "make",
        "filter": "raw"
      }
    }
  }
}
```

**examples/hello-world/README.md:**
```markdown
# Hello World Example

Minimal DDD setup with a C program.

## Run It

```bash
cd examples/hello-world
dd-daemon &
./.ddd/wait
./hello
```

## What's Happening

1. Daemon watches `.ddd/run/build.request`
2. Client (`.ddd/wait`) touches that file
3. Daemon runs `make` (compiles hello.c)
4. Output written to `.ddd/run/build.log`
5. You see the results

## Customize

Edit `.ddd/config.json` to:
- Change the build command
- Add filters (try `"gcc_json"`)
- Add verify stage
```

**Other examples:**
- **python-pytest/**: Python testing with pytest
- **multi-stage/**: Build + verify stages with filters

**examples/README.md:**
```markdown
# DDD Examples

Learn by doing. Each example is fully runnable.

## Available Examples

### [hello-world/](hello-world/)
Minimal C program with DDD. **Start here.**
- Simple Makefile
- Raw output filter
- 1 build stage

### [python-pytest/](python-pytest/)
Python project with pytest testing.
- No compilation, just tests
- Demonstrates non-C workflows
- Raw filter for test output

### [multi-stage/](multi-stage/)
Complex build with build + verify stages.
- Multi-stage pipeline
- Filter chaining (gcc_make → gcc_json)
- Demonstrates full DDD capabilities

## Running an Example

```bash
cd examples/<example-name>
dd-daemon &
./.ddd/wait
```

## Next Steps

Once you've tried an example:
1. Copy `.ddd/config.json` to your project
2. Customize the `cmd` for your build
3. Read CONFIG_REFERENCE.md for advanced config
```

**Why This Helps:**
- Learning by doing (most effective)
- Immediate validation (it works!)
- Templates for copy-paste to real projects
- Covers common languages/workflows

---

### 2.2 Add "Use Cases" Section to README

**Location:** README.md, after Overview, before Prerequisites  
**Estimated Time:** 20 minutes

**New Content:**

```markdown
## 💡 Common Use Cases

### 1. AI Pair Programming
**Problem:** Aider/Cursor run in containers, native builds are faster  
**Solution:** AI agent triggers DDD, reads filtered output  
**Speed gain:** 2-5x faster than in-container builds

### 2. Parasitic CI/CD
**Problem:** Need Linux CI but develop on macOS with Xcode  
**Solution:** Linux CI container triggers host macOS compiler  
**Use case:** Cross-platform testing without cross-compilation

### 3. Multi-Tool Development
**Problem:** VSCode, Vim, Emacs all need build results  
**Solution:** One DDD daemon serves all editors  
**Benefit:** Consistent build output, shared cache

### 4. Resource-Constrained Environments
**Problem:** Building in Docker uses 10-50% more CPU/RAM  
**Solution:** Container edits, host builds (native speed)  
**Use case:** Laptop development, CI cost reduction

### When NOT to Use DDD

- **Simple local dev**: Just run `make` directly
- **Pure interpreted languages**: No build step (Python, Ruby, JS)
- **Cloud-only builds**: No local machine to run daemon
- **Single-tool workflow**: Editor has built-in build integration

If you're in the "Use Cases" list, keep reading. Otherwise, DDD might be overkill.
```

**Why This Helps:**
- Self-selection (is DDD right for me?)
- Concrete scenarios (not abstract concepts)
- Sets expectations for benefits
- Prevents misuse/confusion

---

### 2.3 Create QUICKSTART.md

**Location:** `/QUICKSTART.md` (new file)  
**Estimated Time:** 30 minutes

**Purpose:** Single-page guide for absolute beginners

**Structure:**

```markdown
# DDD Quick Start Guide

**Goal:** Get DDD running in your project in 10 minutes.

## What You'll Need

- Python 3.7+ installed
- A project with a build command (make, cmake, pytest, etc.)
- 10 minutes

## Step 1: Install DDD (2 minutes)

[Installation instructions - condensed version]

## Step 2: Configure Your Build (3 minutes)

[Config creation - simple template]

## Step 3: Start the Daemon (1 minute)

[Starting daemon]

## Step 4: Trigger a Build (1 minute)

[Triggering and seeing results]

## Step 5: Integrate with Your Workflow (3 minutes)

### For AI Agents (Aider, Cursor)
[Integration instructions]

### For CI/CD
[CI integration]

### For Manual Use
[Keyboard shortcuts, aliases]

## What's Next?

- **Learn filters**: FILTERS.md
- **Advanced config**: CONFIG_REFERENCE.md
- **Troubleshooting**: (future: TROUBLESHOOTING.md)
- **Join discussion**: [GitHub Issues]

## Quick Reference

### Essential Commands
```bash
dd-daemon              # Start foreground
dd-daemon --daemon     # Start background
./.ddd/wait            # Trigger build
cat .ddd/run/build.log # View output
kill $(cat .ddd/daemon.pid)  # Stop daemon
```

### Essential Files
```text
.ddd/config.json       - Your build config
.ddd/run/build.log     - Filtered output
.ddd/run/build.exit    - Exit code (0=success)
```

### Need Help?
- Check daemon logs: `cat .ddd/daemon.log`
- Check raw output: `cat .ddd/run/last_build.raw.log`
- Validate config: `python3 -m json.tool .ddd/config.json`
```

**Why This Helps:**
- Standalone reference (share this link)
- Time-boxed steps (builds confidence)
- Quick reference section (cheat sheet)
- Clear next steps

---

## Phase 3: Polish & Support (1 hour)

### 3.1 Create TROUBLESHOOTING.md

**Location:** `/TROUBLESHOOTING.md` (new file)  
**Estimated Time:** 45 minutes

**Structure:**

```markdown
# Troubleshooting Guide

## Installation Issues

### "python3: command not found"
[Solution]

### "Permission denied" errors
[Solution]

### "Module not found: watchdog"
[Solution]

## Daemon Issues

### Daemon won't start
[Diagnostics and solutions]

### "Daemon did not respond"
[Lock file issues, process checks]

### Daemon crashes silently
[Log checking, common causes]

## Build Issues

### Build never completes
[Timeout issues, lock cleanup]

### Output is empty/truncated
[Filter issues, command problems]

### Build succeeds but exit code is 1
[Sentinel file explanation]

## Configuration Issues

### "Target 'dev' not found"
[Config structure validation]

### "Filter 'xyz' not found"
[Filter loading, naming issues]

### JSON syntax errors
[Validation commands]

## Integration Issues

### AI agent can't trigger builds
[File permissions, path issues]

### CI/CD exit codes wrong
[Use build.exit instead of wait exit code]

## Getting Help

Still stuck? Here's how to get help:

1. **Check logs:**
   ```bash
   cat .ddd/daemon.log
   cat .ddd/run/last_build.raw.log
   ```

2. **Validate config:**
   ```bash
   python3 -m json.tool .ddd/config.json
   ```

3. **Test daemon manually:**
   ```bash
   # Stop existing daemon
   # Start in foreground
   # Watch for errors
   ```

4. **Open an issue:**
   [GitHub Issues Link]
   Include: OS, Python version, config.json, error logs
```

**Why This Helps:**
- Reduces support burden
- Builds user confidence
- Common issues pre-answered
- Clear escalation path

---

### 3.2 Update README with Links to New Resources

**Location:** README.md, multiple locations  
**Estimated Time:** 15 minutes

**Changes:**

1. Add link to QUICKSTART.md in Overview:
   ```markdown
   **New to DDD?** See [QUICKSTART.md](QUICKSTART.md) for a 10-minute guide.
   ```

2. Update Documentation section:
   ```markdown
   ## 📚 Documentation
   
   **Getting Started:**
   - **[QUICKSTART.md](QUICKSTART.md)** - 10-minute beginner guide
   - **[examples/](examples/)** - Runnable example projects
   
   **Reference:**
   - **[CONFIG_REFERENCE.md](CONFIG_REFERENCE.md)** - Configuration guide
   - **[FILTERS.md](FILTERS.md)** - Filter reference
   
   **Advanced:**
   - **[PARASITIC_MODE.md](PARASITIC_MODE.md)** - Containerized workflows
   - **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development guide
   
   **Support:**
   - **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues
   - **[ROADMAP.md](ROADMAP.md)** - Feature roadmap
   ```

3. Add "Learn More" to end of Quick Start section:
   ```markdown
   **Learn More:**
   - Try other examples: `ls examples/`
   - Understand configuration: [CONFIG_REFERENCE.md](CONFIG_REFERENCE.md)
   - Troubleshoot issues: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
   ```

---

## Implementation Plan

### Sprint 1: Critical Path (Week 1)
**Goal:** First-time users can succeed in 5 minutes

- [ ] Day 1: Phase 1.1 - Quick Start section (README)
- [ ] Day 1: Phase 1.2 - Rewrite Overview (README)
- [ ] Day 2: Phase 2.1 - Create examples/hello-world
- [ ] Day 2: Phase 1.3 - Prerequisites & Install improvements
- [ ] Day 3: Phase 1.4 - "Verify It Works" section
- [ ] Day 3: Phase 1.5 - .gitignore documentation

**Deliverable:** README + examples/hello-world fully functional

### Sprint 2: Learning Support (Week 2)
**Goal:** Users can learn at their own pace

- [ ] Day 4: Phase 2.1 - Complete examples/ (python-pytest, multi-stage)
- [ ] Day 4: Phase 2.2 - Use Cases section
- [ ] Day 5: Phase 2.3 - QUICKSTART.md
- [ ] Day 5: Phase 3.1 - TROUBLESHOOTING.md
- [ ] Day 6: Phase 3.2 - Update all cross-links

**Deliverable:** Complete learning path from beginner to advanced

### Testing & Validation
- [ ] Fresh Ubuntu VM test (simulates new Linux user)
- [ ] Fresh macOS test (simulates new Mac user)
- [ ] Non-technical friend test (ultimate validation)
- [ ] Measure time-to-first-success (target: < 10 minutes)

---

## Success Metrics

### Quantitative
- **Time to first successful build:** < 10 minutes (currently ~20-30 min)
- **Documentation score:** 9/10 (currently 7.4/10)
- **GitHub stars increase:** 20% within 1 month of release
- **Issue reduction:** 30% fewer "how do I..." issues

### Qualitative
- Users report "easy to get started" in feedback
- No documentation questions in first 24h of new releases
- Examples cited in user issues/PRs
- Positive mentions in Reddit/HN/Twitter

---

## Risk Mitigation

### Risk: Examples become stale
**Mitigation:** 
- Add CI check that runs all examples
- Update examples with each major version
- Examples have version tags in README

### Risk: Quick Start doesn't work on all platforms
**Mitigation:**
- Test on Ubuntu, macOS, Windows WSL2
- Provide platform-specific alternatives
- Link to detailed install.sh documentation

### Risk: Too many docs = information overload
**Mitigation:**
- Clear "start here" signposting (QUICKSTART.md)
- Progressive disclosure (basic → advanced)
- Visual navigation (emojis, clear headers)

---

## Post-Implementation Review

After completing this plan, gather feedback on:

1. **First impression:** Is the value proposition clear?
2. **Installation:** Did prerequisites help? Any missing steps?
3. **Examples:** Which example did users try first? Was it helpful?
4. **Troubleshooting:** Were common issues covered?
5. **Next steps:** Did users know where to go after Quick Start?

**Feedback channels:**
- GitHub issue template: "Documentation Feedback"
- Survey link in QUICKSTART.md (optional)
- Monitor #ddd discussions (if exists)

---

## Appendix: Content Principles

When creating new user documentation, follow these principles:

### 1. Show, Don't Tell
❌ "DDD is a file-watching daemon that..."  
✅ "Here's what DDD does: [working example]"

### 2. Time-Box Everything
❌ "Install DDD"  
✅ "Install DDD (2 minutes)"

### 3. Validate Early
❌ "Run these 10 steps"  
✅ "Run step 1, verify it worked, then step 2..."

### 4. Assume Nothing
❌ "Add to your PATH"  
✅ "Add to your PATH: `echo 'export PATH=...' >> ~/.bashrc`"

### 5. Provide Escape Hatches
Always include:
- "If this doesn't work..."
- "Alternative method..."
- "Skip this if..."

### 6. Use Progressive Disclosure
- Overview → Quick Start → Installation → Advanced → Reference
- Don't dump everything at once
- Link to details from summaries

---

## Version History

- **v1.0** (Jan 28, 2026) - Initial plan post-v0.7.0 documentation overhaul
- **Target:** v0.7.1 or v0.8.0 release
