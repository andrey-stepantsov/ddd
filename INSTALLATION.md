# DDD Installation Guide (v0.8.0)

Complete guide for installing and setting up DDD in your project.

## Overview

DDD v0.8.0 introduces **project-local installation**, where each project gets its own isolated DDD instance in `.ddd/`. This eliminates version conflicts and simplifies deployment.

**Installation Methods:**
1. **Bootstrap** (Recommended) - Automated project-local setup
2. **Git Submodule** - Shared version control
3. **Manual Copy** - Full control over files
4. **Global Install** - Traditional system-wide installation (developers only)

---

## Method 1: Bootstrap (Recommended)

**Best for:** Most users, trying DDD, individual projects

### Quick Install

```bash
cd your-project
curl -sSL https://raw.githubusercontent.com/stepants/ddd/main/bootstrap-ddd.sh | bash -s .
```

### What It Does

The bootstrap script:
1. Creates `.ddd/` directory structure
2. Copies DDD source to `.ddd/ddd/` (vendored)
3. Generates wrapper scripts in `.ddd/bin/`
4. Creates `.ddd/Makefile` with DDD targets
5. Updates `.gitignore` (optional)
6. Creates reference `.ddd/.gitignore` for manual setup

### Installation Options

**Using curl (production):**
```bash
cd your-project
curl -sSL https://ddd.sh/bootstrap | bash -s .
# Or specify version
curl -sSL https://raw.githubusercontent.com/stepants/ddd/v0.8.0/bootstrap-ddd.sh | bash -s .
```

**Using local copy (development):**
```bash
git clone https://github.com/stepants/ddd.git /tmp/ddd
LOCAL_DDD_PATH=/tmp/ddd /tmp/ddd/bootstrap-ddd.sh your-project
```

**Using git submodule (managed):**
```bash
cd your-project
git submodule add https://github.com/stepants/ddd.git .ddd/ddd
bash .ddd/ddd/bootstrap-ddd.sh .
```

### Environment Variables

Control bootstrap behavior with environment variables:

- `DDD_UPDATE_GITIGNORE=no` - Skip automatic `.gitignore` updates
- `LOCAL_DDD_PATH=/path` - Use local DDD copy instead of GitHub
- `DDD_VERSION=v0.8.0` - Specify DDD version (default: main)
- `DDD_REPO=https://...` - Use custom repository URL

**Example:**
```bash
# Install without modifying .gitignore
DDD_UPDATE_GITIGNORE=no bash bootstrap-ddd.sh .

# Install from local development copy
LOCAL_DDD_PATH=~/dev/ddd bash bootstrap-ddd.sh .
```

### Directory Structure Created

```
your-project/
├── .ddd/
│   ├── bin/                   # Wrapper scripts
│   │   ├── dd-daemon          # Start daemon
│   │   ├── ddd-wait           # Build client
│   │   └── ddd-test           # Run tests
│   ├── ddd/                   # Vendored DDD source
│   │   ├── bin/               # Original binaries
│   │   ├── src/               # Python source
│   │   └── bootstrap.sh       # Self-bootstrapper
│   ├── run/                   # Build artifacts (created on first use)
│   ├── filters/               # Custom filters directory (empty)
│   ├── Makefile               # DDD make targets
│   ├── wait -> bin/ddd-wait   # Convenience symlink
│   └── .gitignore             # Reference patterns
```

### Verification

After bootstrap, verify installation:

```bash
# Check structure
ls -la .ddd/
ls -la .ddd/ddd/

# Test daemon help
.ddd/bin/dd-daemon --help

# Check Makefile targets
make -f .ddd/Makefile help
```

---

## Method 2: Git Submodule

**Best for:** Version control, multiple projects, CI/CD

### Initial Setup

```bash
cd your-project
git submodule add https://github.com/stepants/ddd.git .ddd/ddd

# Run bootstrap to create wrappers
bash .ddd/ddd/bootstrap-ddd.sh .

# Commit submodule
git add .gitmodules .ddd/
git commit -m "Add DDD as submodule"
```

### Cloning Project with Submodule

New clones need submodule initialization:

```bash
# Option 1: Clone with submodules
git clone --recursive https://github.com/yourname/yourproject.git

# Option 2: Initialize after clone
git clone https://github.com/yourname/yourproject.git
cd yourproject
git submodule update --init --recursive

# Then run bootstrap to regenerate wrappers
bash .ddd/ddd/bootstrap-ddd.sh .
```

### Updating DDD

```bash
# Update to latest DDD
git submodule update --remote .ddd/ddd
bash .ddd/ddd/bootstrap-ddd.sh .  # Regenerate wrappers

# Or update to specific version
cd .ddd/ddd
git checkout v0.8.1
cd ../..
git add .ddd/ddd
git commit -m "Update DDD to v0.8.1"
```

### Advantages

- ✅ Version locked (reproducible builds)
- ✅ Easy updates (`git submodule update`)
- ✅ Visible in `git status`
- ✅ Works offline after initial clone

### Disadvantages

- ❌ Requires git knowledge
- ❌ Adds ~500KB to repository
- ❌ Extra steps for new clones

---

## Method 3: Manual Copy

**Best for:** Offline environments, custom modifications, air-gapped systems

### Steps

```bash
# 1. Download DDD
curl -L https://github.com/stepants/ddd/archive/refs/heads/main.tar.gz | tar xz
mv ddd-main your-project/.ddd/ddd

# 2. Run bootstrap
cd your-project
bash .ddd/ddd/bootstrap-ddd.sh .

# 3. Verify
.ddd/bin/dd-daemon --help
```

### Manual Structure Creation (Without Bootstrap)

If bootstrap script unavailable:

```bash
mkdir -p .ddd/{bin,run,filters}

# Create config template
cat > .ddd/config.json <<'EOF'
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
EOF

# Create wrapper scripts manually
# (see bootstrap-ddd.sh for wrapper content)
```

---

## Method 4: Global Install (Developers)

**Best for:** DDD development, testing across multiple projects

### Installation

```bash
# Clone repository
git clone https://github.com/stepants/ddd.git ~/ddd
cd ~/ddd

# Install globally
./install.sh

# Add to PATH if needed
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Verification

```bash
which dd-daemon  # Should show: ~/.local/bin/dd-daemon
dd-daemon --help
```

### Updating

```bash
cd ~/ddd
git pull origin main
./install.sh  # Reinstall binaries
```

### Usage in Projects

With global install, reference binaries directly or use bootstrap to create local wrappers:

```bash
# Option 1: Use global binaries
dd-daemon --daemon

# Option 2: Create local wrappers
bash ~/ddd/bootstrap-ddd.sh your-project
```

---

## Post-Installation Setup

### 1. Create Configuration

Create `.ddd/config.json` for your project:

```json
{
  "targets": {
    "dev": {
      "build": {
        "cmd": "make",
        "filter": "gcc_make"
      }
    }
  }
}
```

See [CONFIG_REFERENCE.md](CONFIG_REFERENCE.md) for details.

### 2. Configure Git

Bootstrap automatically updates `.gitignore`, but verify:

```bash
# Check patterns
cat .gitignore | grep -A 5 "DDD"

# Or add manually
cat .ddd/.gitignore >> .gitignore
```

### 3. Choose Usage Style

**Style A: Standalone (No Makefile Changes)**
```bash
make -f .ddd/Makefile ddd-daemon-bg
make -f .ddd/Makefile ddd-build
```

**Style B: Integrated (Modify Your Makefile)**
```makefile
# Add to your project's Makefile
-include .ddd/Makefile
```

Then use naturally:
```bash
make ddd-daemon-bg
make ddd-build
```

**Style C: Direct Paths**
```bash
.ddd/bin/dd-daemon --daemon
.ddd/wait
```

**Style D: With direnv**
```bash
# Create .envrc
echo 'export PATH="$PWD/.ddd/bin:$PATH"' > .envrc
direnv allow

# Now use directly
dd-daemon --daemon
ddd-wait
```

### 4. Test Installation

```bash
# Start daemon
.ddd/bin/dd-daemon &

# Verify running
ps aux | grep dd-daemon
cat .ddd/daemon.log

# Trigger test build
.ddd/wait
cat .ddd/run/build.log

# Stop daemon
pkill -f dd-daemon
```

---

## Multiple Projects

### Strategy A: Bootstrap Each Project

Each project gets independent DDD:

```bash
bootstrap-ddd.sh project1
bootstrap-ddd.sh project2
bootstrap-ddd.sh project3
```

**Pros:** Independent versions, no conflicts  
**Cons:** Disk usage (~500KB × N projects)

### Strategy B: Shared Submodule

Share DDD source via submodule:

```bash
# Central DDD
mkdir ~/shared-ddd
git init ~/shared-ddd
git -C ~/shared-ddd submodule add https://github.com/stepants/ddd.git

# Reference in projects
cd project1
ln -s ~/shared-ddd/ddd .ddd/ddd
bash .ddd/ddd/bootstrap-ddd.sh .
```

**Pros:** Single DDD source, easy updates  
**Cons:** All projects share same version

---

## Troubleshooting

### Bootstrap Fails

**Error:** `rsync: command not found`

**Solution:** Bootstrap falls back to tar automatically. If both fail:
```bash
# Install rsync (macOS)
brew install rsync

# Or use tar method explicitly
tar cf - -C /path/to/ddd . | tar xf - -C .ddd/ddd/
```

**Error:** `Permission denied: .gitignore`

**Solution:** Skip automatic gitignore updates:
```bash
DDD_UPDATE_GITIGNORE=no bash bootstrap-ddd.sh .
cat .ddd/.gitignore >> .gitignore  # Manual merge
```

### Daemon Won't Start

**Error:** `Cannot find DDD installation`

**Solution:** Verify bootstrap completed:
```bash
ls -la .ddd/ddd/bootstrap.sh
bash .ddd/ddd/bootstrap.sh  # Should see success
```

**Error:** `Python not found`

**Solution:** Install Python 3.7+:
```bash
# macOS
brew install python3

# Ubuntu/Debian
sudo apt install python3 python3-venv
```

### Wrapper Scripts Don't Work

**Error:** `exec: .ddd/ddd/bin/dd-daemon: not found`

**Solution:** Re-run bootstrap:
```bash
bash .ddd/ddd/bootstrap-ddd.sh .
chmod +x .ddd/bin/*
```

### Submodule Issues

**Error:** `fatal: not a git repository`

**Solution:** Initialize git first:
```bash
git init
git add .
git commit -m "Initial commit"
# Then add submodule
```

**Error:** `Submodule already exists`

**Solution:** Use update instead:
```bash
git submodule update --init --recursive
```

---

## Uninstallation

### Remove from Project

```bash
# Remove .ddd directory
rm -rf .ddd

# Remove gitignore patterns (optional)
# Edit .gitignore and remove DDD section
```

### Remove Global Install

```bash
# Remove binaries
rm ~/.local/bin/dd-daemon
rm ~/.local/bin/ddd-wait
rm ~/.local/bin/ddd-test

# Remove source
rm -rf ~/ddd
```

### Remove Submodule

```bash
git submodule deinit -f .ddd/ddd
git rm -f .ddd/ddd
rm -rf .git/modules/.ddd/ddd
git commit -m "Remove DDD submodule"
```

---

## Next Steps

- **Configure builds:** See [CONFIG_REFERENCE.md](CONFIG_REFERENCE.md)
- **Learn filters:** See [FILTERS.md](FILTERS.md)
- **Migration:** See [MIGRATION.md](MIGRATION.md) (upgrading from v0.7.x)
- **Examples:** Check `examples/hello-world/`

---

**Version:** v0.8.0  
**Last Updated:** 2026-01-29  
**Questions?** Open an issue at https://github.com/stepants/ddd/issues
