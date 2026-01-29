# Migration Guide: v0.7.x → v0.8.0

Guide for upgrading existing DDD projects from v0.7.x to v0.8.0.

## Overview

**v0.8.0** introduces project-local DDD installation, eliminating global dependencies and enabling per-project DDD versions.

### Key Changes

| Aspect | v0.7.x | v0.8.0 |
|--------|--------|--------|
| **Installation** | Global (`~/.local/bin/`) | Project-local (`.ddd/ddd/`) |
| **Binaries** | System PATH | `.ddd/bin/` wrappers |
| **Updates** | System-wide reinstall | Per-project bootstrap |
| **Versions** | Single global version | Different per project |
| **Makefile** | User-managed | Generated `.ddd/Makefile` |

### Breaking Changes

✅ **Backward Compatible:** v0.8.0 binaries work with v0.7.x projects (no `.ddd/ddd/` needed)

⚠️ **New Projects:** Should use bootstrap for project-local installation

---

## Migration Strategies

### Strategy A: Gradual (Recommended)

Keep v0.7.x globally, migrate projects individually.

**Timeline:** 1-4 weeks per project  
**Risk:** Low (projects can coexist)  
**Effort:** Medium (per-project work)

### Strategy B: Fresh Start

New v0.8.0 installation, migrate all projects.

**Timeline:** 1 day (all at once)  
**Risk:** Medium (affects all projects)  
**Effort:** High (batch migration)

### Strategy C: Hybrid

Keep v0.7.x for old projects, v0.8.0 for new projects.

**Timeline:** Ongoing  
**Risk:** Low (gradual adoption)  
**Effort:** Low (no forced migration)

---

## Strategy A: Gradual Migration (Recommended)

### Phase 1: Verify v0.7.x Projects Still Work

v0.8.0 binaries are backward compatible with v0.7.x projects.

**Test existing projects:**
```bash
# Update global DDD to v0.8.0
cd ~/ddd
git pull origin main
./install.sh

# Test v0.7.x project (should still work)
cd ~/old-project
dd-daemon &            # Uses global v0.8.0 binary
./.ddd/wait            # Works with v0.7.x .ddd/ structure
cat .ddd/run/build.log
```

**Expected:** No changes needed, everything works.

### Phase 2: Migrate Projects One-by-One

For each project, convert to project-local installation:

```bash
cd ~/project1

# Backup existing config
cp .ddd/config.json /tmp/config.backup.json

# Bootstrap v0.8.0 structure
bash ~/ddd/bootstrap-ddd.sh .

# Verify config preserved
diff .ddd/config.json /tmp/config.backup.json

# Test
.ddd/bin/dd-daemon --help
```

### Phase 3: Update Workflows

**Old workflow (v0.7.x):**
```bash
dd-daemon &           # Global binary
./.ddd/wait
```

**New workflow (v0.8.0):**
```bash
# Option 1: Use Makefile
make -f .ddd/Makefile ddd-daemon-bg

# Option 2: Direct paths
.ddd/bin/dd-daemon --daemon

# Option 3: Integrate with your Makefile
# Add to Makefile: -include .ddd/Makefile
make ddd-daemon-bg
```

### Phase 4: Update CI/CD

**Old CI (v0.7.x):**
```yaml
# .github/workflows/build.yml
- name: Install DDD
  run: |
    git clone https://github.com/stepants/ddd.git /tmp/ddd
    cd /tmp/ddd
    ./install.sh
- name: Build
  run: dd-daemon & && sleep 1 && ./.ddd/wait
```

**New CI (v0.8.0):**
```yaml
# .github/workflows/build.yml
- name: Bootstrap DDD
  run: |
    curl -sSL https://raw.githubusercontent.com/stepants/ddd/main/bootstrap-ddd.sh | bash -s .
- name: Build
  run: |
    .ddd/bin/dd-daemon --daemon
    .ddd/wait
```

---

## Strategy B: Fresh Start Migration

### Step 1: Backup Configurations

```bash
# Create backup directory
mkdir ~/ddd-migration-backup

# Backup all project configs
for project in ~/projects/*; do
  if [ -f "$project/.ddd/config.json" ]; then
    mkdir -p ~/ddd-migration-backup/$(basename "$project")
    cp "$project/.ddd/config.json" ~/ddd-migration-backup/$(basename "$project")/
    cp -r "$project/.ddd/filters" ~/ddd-migration-backup/$(basename "$project")/ 2>/dev/null || true
  fi
done
```

### Step 2: Install v0.8.0

```bash
# Update global DDD
cd ~/ddd
git pull origin main
./install.sh

# Verify
dd-daemon --version
```

### Step 3: Migrate All Projects

```bash
# Bootstrap script for all projects
for project in ~/projects/*; do
  if [ -f "$project/.ddd/config.json" ]; then
    echo "Migrating $project"
    bash ~/ddd/bootstrap-ddd.sh "$project"
    
    # Verify config preserved
    if ! diff "$project/.ddd/config.json" ~/ddd-migration-backup/$(basename "$project")/config.json; then
      echo "WARNING: Config changed in $project"
    fi
  fi
done
```

### Step 4: Update All CI/CD

Update all `.github/workflows/` files using sed:

```bash
# Find all workflow files
find ~/projects -name "*.yml" -path "*/.github/workflows/*" | while read workflow; do
  # Replace old install with bootstrap
  sed -i.bak 's|./install.sh|curl -sSL https://raw.githubusercontent.com/stepants/ddd/main/bootstrap-ddd.sh | bash -s .|g' "$workflow"
  
  # Replace dd-daemon with .ddd/bin/dd-daemon
  sed -i.bak 's|dd-daemon|.ddd/bin/dd-daemon|g' "$workflow"
done
```

### Step 5: Test Everything

```bash
# Test each project
for project in ~/projects/*; do
  if [ -f "$project/.ddd/bin/dd-daemon" ]; then
    echo "Testing $project"
    cd "$project"
    .ddd/bin/dd-daemon --help || echo "FAILED: $project"
  fi
done
```

---

## Strategy C: Hybrid Approach

Keep v0.7.x for existing projects, use v0.8.0 for new projects.

### Coexistence Rules

1. **v0.7.x projects:** Use global `dd-daemon` from PATH
2. **v0.8.0 projects:** Use `.ddd/bin/dd-daemon` local wrapper
3. **Both versions installed:** v0.8.0 binaries work for both

### Setup

```bash
# Keep v0.7.x global install
which dd-daemon  # ~/.local/bin/dd-daemon

# For new projects, use bootstrap
cd new-project
bash ~/ddd/bootstrap-ddd.sh .

# For old projects, no changes needed
cd old-project
dd-daemon &  # Still works with v0.8.0 global binary
```

---

## Migration Checklist

### Pre-Migration

- [ ] Backup all `.ddd/config.json` files
- [ ] Backup all `.ddd/filters/` directories
- [ ] Document current workflows (CI/CD, Makefiles)
- [ ] Test v0.8.0 on non-critical project first
- [ ] Review [INSTALLATION.md](INSTALLATION.md)

### Migration

- [ ] Run bootstrap on project: `bash bootstrap-ddd.sh .`
- [ ] Verify config.json preserved
- [ ] Verify filters/ preserved
- [ ] Test daemon: `.ddd/bin/dd-daemon --help`
- [ ] Test build: `.ddd/bin/dd-daemon --daemon && .ddd/wait`
- [ ] Update Makefile (optional): `-include .ddd/Makefile`
- [ ] Update CI/CD (if applicable)
- [ ] Update documentation (if applicable)

### Post-Migration

- [ ] Test full build cycle
- [ ] Verify gitignore patterns
- [ ] Commit changes: `.ddd/Makefile`, updated `.gitignore`
- [ ] Update team documentation
- [ ] Monitor first few builds

---

## Rollback Plan

If migration fails, rollback to v0.7.x:

### Immediate Rollback

```bash
# Remove v0.8.0 structure
rm -rf .ddd/ddd .ddd/bin .ddd/Makefile .ddd/wait

# Restore config from backup
cp ~/ddd-migration-backup/$(basename $PWD)/config.json .ddd/

# Use global v0.7.x binary
dd-daemon &
./.ddd/wait
```

### Complete Rollback

```bash
# Downgrade global DDD
cd ~/ddd
git checkout v0.7.0
./install.sh

# Remove all v0.8.0 structures
for project in ~/projects/*; do
  rm -rf "$project/.ddd/ddd" "$project/.ddd/bin" "$project/.ddd/Makefile"
done
```

---

## Troubleshooting Migration Issues

### Issue: Config Not Preserved

**Symptom:** `.ddd/config.json` reset to template

**Cause:** Bootstrap didn't detect existing config

**Solution:**
```bash
# Restore from backup
cp ~/ddd-migration-backup/$(basename $PWD)/config.json .ddd/

# Or manually copy
cp /tmp/config.backup.json .ddd/config.json
```

### Issue: Daemon Can't Find DDD

**Symptom:** `Error: Cannot find DDD installation`

**Cause:** Incomplete bootstrap

**Solution:**
```bash
# Verify structure
ls -la .ddd/ddd/bootstrap.sh

# Re-run bootstrap
bash ~/ddd/bootstrap-ddd.sh .

# Check wrappers
cat .ddd/bin/dd-daemon  # Should reference ../ddd/bin/
```

### Issue: Makefile Conflicts

**Symptom:** `make: *** No rule to make target 'ddd-daemon-bg'`

**Cause:** Project Makefile doesn't include `.ddd/Makefile`

**Solution:**
```bash
# Option 1: Use explicit path
make -f .ddd/Makefile ddd-daemon-bg

# Option 2: Include in your Makefile
echo '-include .ddd/Makefile' >> Makefile
make ddd-daemon-bg
```

### Issue: CI/CD Failures

**Symptom:** CI can't find `dd-daemon`

**Cause:** CI uses old global install method

**Solution:**
```yaml
# Update CI workflow
- name: Bootstrap DDD
  run: bash .ddd/ddd/bootstrap-ddd.sh . || curl -sSL https://ddd.sh/bootstrap | bash -s .
- name: Build
  run: .ddd/bin/dd-daemon --daemon && .ddd/wait
```

### Issue: Multiple DDD Versions

**Symptom:** Different projects show different DDD behavior

**Cause:** Mixed v0.7.x and v0.8.0 installations

**Solution:**
```bash
# Check project structure
ls -la .ddd/  # v0.8.0 has .ddd/ddd/, v0.7.x doesn't

# Migrate remaining v0.7.x projects
bash ~/ddd/bootstrap-ddd.sh .
```

---

## Differences in Daily Usage

### Starting Daemon

**v0.7.x:**
```bash
dd-daemon &             # Global binary from PATH
dd-daemon --daemon      # Background mode
```

**v0.8.0:**
```bash
.ddd/bin/dd-daemon &                 # Local wrapper
make -f .ddd/Makefile ddd-daemon-bg  # Via Makefile
```

### Triggering Builds

**v0.7.x:**
```bash
./.ddd/wait            # Client in .ddd/ (symlink)
```

**v0.8.0:**
```bash
./.ddd/wait                      # Same (backward compatible)
make -f .ddd/Makefile ddd-build  # Via Makefile
```

### Checking Status

**v0.7.x:**
```bash
cat .ddd/daemon.log
ps aux | grep dd-daemon
```

**v0.8.0:**
```bash
# Same commands work
cat .ddd/daemon.log
make -f .ddd/Makefile ddd-status  # Plus Makefile target
```

### Updating DDD

**v0.7.x:**
```bash
cd ~/ddd
git pull origin main
./install.sh
# Affects ALL projects
```

**v0.8.0:**
```bash
# Per-project update
bash ~/ddd/bootstrap-ddd.sh your-project

# Or update all
for p in ~/projects/*; do
  bash ~/ddd/bootstrap-ddd.sh "$p"
done
```

---

## Comparison Table

| Feature | v0.7.x | v0.8.0 |
|---------|--------|--------|
| **Install location** | `~/.local/bin/` | `.ddd/ddd/` |
| **Binary paths** | Global | `.ddd/bin/` wrappers |
| **Config location** | `.ddd/config.json` | `.ddd/config.json` ✅ Same |
| **Runtime files** | `.ddd/run/` | `.ddd/run/` ✅ Same |
| **Update method** | `./install.sh` (global) | `bootstrap-ddd.sh` (per-project) |
| **Multi-version** | ❌ No | ✅ Yes |
| **Disk usage** | ~50MB (shared) | ~500KB per project |
| **PATH required** | ✅ Yes | ❌ No |
| **Makefile** | User-created | Auto-generated `.ddd/Makefile` |
| **Backward compat** | N/A | ✅ Works with v0.7.x projects |

---

## Testing Migration

### Manual Test

```bash
# 1. Verify structure
ls -la .ddd/ddd/bootstrap.sh  # Should exist
ls -la .ddd/bin/dd-daemon     # Should exist

# 2. Test daemon
.ddd/bin/dd-daemon --help

# 3. Test build cycle
.ddd/bin/dd-daemon --daemon
sleep 1
.ddd/wait
cat .ddd/run/build.log
cat .ddd/run/build.exit

# 4. Stop daemon
pkill -f dd-daemon
```

### Automated Test

```bash
#!/bin/bash
# test-migration.sh

PROJECT_DIR="$1"
BACKUP_DIR="/tmp/ddd-test-backup"

# Backup
mkdir -p "$BACKUP_DIR"
cp "$PROJECT_DIR/.ddd/config.json" "$BACKUP_DIR/"

# Migrate
bash ~/ddd/bootstrap-ddd.sh "$PROJECT_DIR"

# Test
cd "$PROJECT_DIR"
.ddd/bin/dd-daemon & 
DAEMON_PID=$!
sleep 2

# Trigger build
.ddd/wait
sleep 1

# Verify
if [ -f .ddd/run/build.log ]; then
  echo "✅ Migration successful: $PROJECT_DIR"
else
  echo "❌ Migration failed: $PROJECT_DIR"
fi

# Cleanup
kill $DAEMON_PID 2>/dev/null
```

---

## FAQ

**Q: Can I use both v0.7.x and v0.8.0?**  
A: Yes! v0.8.0 binaries are backward compatible.

**Q: Do I need to migrate immediately?**  
A: No. v0.7.x projects continue working with v0.8.0 global install.

**Q: Will migration affect my builds?**  
A: No. Builds use same protocol, only installation method changes.

**Q: Can I rollback?**  
A: Yes. Remove `.ddd/ddd/` and use global binaries.

**Q: What about submodules?**  
A: Bootstrap works with submodules. Run after `git submodule update`.

**Q: Will team members need to migrate?**  
A: Yes, after pushing `.ddd/ddd/` structure or telling them to re-bootstrap.

---

## Support

**Issues:** https://github.com/stepants/ddd/issues  
**Docs:** [INSTALLATION.md](INSTALLATION.md) | [README.md](README.md) | [CONFIG_REFERENCE.md](CONFIG_REFERENCE.md)  

**Version:** v0.8.0  
**Last Updated:** 2026-01-29
