#!/bin/bash
set -euo pipefail

# bootstrap-ddd.sh - DDD Project Bootstrapper
# Creates project-local DDD installation in .ddd/ directory
# Version: 0.8.0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DDD_VERSION="${DDD_VERSION:-main}"
DDD_REPO="${DDD_REPO:-https://github.com/stepants/ddd.git}"
INSTALL_METHOD="${INSTALL_METHOD:-auto}"  # auto, submodule, curl, local
LOCAL_DDD_PATH="${LOCAL_DDD_PATH:-}"  # Path to local DDD repo for testing

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Determine target directory
TARGET_DIR="${1:-.}"
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

log_info "Bootstrapping DDD in: $TARGET_DIR"

# Check if we're already inside a DDD repo
if [ -f "$TARGET_DIR/bootstrap.sh" ] && [ -f "$TARGET_DIR/src/dd-daemon.py" ]; then
    log_error "You appear to be inside the DDD repository itself."
    log_error "Please run this from your project directory, not the DDD repo."
    exit 1
fi

# Determine installation method
if [ "$INSTALL_METHOD" = "auto" ]; then
    if [ -n "$LOCAL_DDD_PATH" ] && [ -d "$LOCAL_DDD_PATH" ]; then
        INSTALL_METHOD="local"
        log_info "Using local DDD path: $LOCAL_DDD_PATH"
    elif git -C "$TARGET_DIR" rev-parse --git-dir >/dev/null 2>&1; then
        INSTALL_METHOD="submodule"
        log_info "Detected git repository, will use submodule"
    else
        INSTALL_METHOD="curl"
        log_info "Not a git repository, will use curl"
    fi
fi

# Create .ddd directory structure
log_info "Creating .ddd directory structure..."
mkdir -p "$TARGET_DIR/.ddd/bin"
mkdir -p "$TARGET_DIR/.ddd/run"
mkdir -p "$TARGET_DIR/.ddd/filters"

# Install DDD source
log_info "Installing DDD source ($INSTALL_METHOD method)..."

install_via_submodule() {
    if [ -d "$TARGET_DIR/.ddd/ddd/.git" ] || [ -f "$TARGET_DIR/.ddd/ddd/.git" ]; then
        log_warn ".ddd/ddd already exists as submodule, updating..."
        (cd "$TARGET_DIR" && git submodule update --init --recursive .ddd/ddd)
        return 0
    else
        log_info "Adding DDD as git submodule..."
        if (cd "$TARGET_DIR" && git submodule add --force "$DDD_REPO" .ddd/ddd 2>&1); then
            log_success "Submodule added successfully"
            return 0
        else
            log_warn "Submodule add failed, falling back to curl method"
            return 1
        fi
    fi
}

if [ "$INSTALL_METHOD" = "submodule" ]; then
    # Git submodule method with fallback
    if ! install_via_submodule; then
        INSTALL_METHOD="curl"
    fi
fi

if [ "$INSTALL_METHOD" = "curl" ]; then
    # Curl/tar method
    if [ -d "$TARGET_DIR/.ddd/ddd" ]; then
        log_warn ".ddd/ddd already exists, removing and re-downloading..."
        rm -rf "$TARGET_DIR/.ddd/ddd"
    fi
    
    log_info "Downloading DDD from GitHub..."
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf $TEMP_DIR" EXIT
    
    # Download and extract
    if [ "$DDD_VERSION" = "main" ]; then
        if ! curl -sSLf "$DDD_REPO/archive/refs/heads/main.tar.gz" | tar xz -C "$TEMP_DIR"; then
            log_error "Failed to download DDD from $DDD_REPO"
            exit 1
        fi
        mv "$TEMP_DIR/ddd-main" "$TARGET_DIR/.ddd/ddd"
    else
        if ! curl -sSLf "$DDD_REPO/archive/refs/tags/$DDD_VERSION.tar.gz" | tar xz -C "$TEMP_DIR"; then
            log_error "Failed to download DDD version $DDD_VERSION from $DDD_REPO"
            exit 1
        fi
        mv "$TEMP_DIR/ddd-${DDD_VERSION#v}" "$TARGET_DIR/.ddd/ddd"
    fi
elif [ "$INSTALL_METHOD" = "local" ]; then
    # Local copy method (for testing)
    if [ -z "$LOCAL_DDD_PATH" ] || [ ! -d "$LOCAL_DDD_PATH" ]; then
        log_error "LOCAL_DDD_PATH not set or doesn't exist: $LOCAL_DDD_PATH"
        exit 1
    fi
    
    # Check if valid installation exists
    if [ -f "$TARGET_DIR/.ddd/ddd/bootstrap.sh" ]; then
        log_info ".ddd/ddd already exists and is valid, skipping copy"
    else
        if [ -d "$TARGET_DIR/.ddd/ddd" ]; then
            log_warn ".ddd/ddd exists but is incomplete, removing..."
            rm -rf "$TARGET_DIR/.ddd/ddd"
        fi
        
        log_info "Copying DDD from local path: $LOCAL_DDD_PATH"
        mkdir -p "$TARGET_DIR/.ddd/ddd"
        
        # Use rsync to skip problematic files, or tar to preserve structure
        if command -v rsync >/dev/null 2>&1; then
            rsync -a --exclude='.devbox' --exclude='.git' --exclude='test_workspace' --exclude='.cursor' \
                  "$LOCAL_DDD_PATH/" "$TARGET_DIR/.ddd/ddd/"
        else
            # Fallback: use tar to copy (handles permissions better)
            (cd "$LOCAL_DDD_PATH" && tar cf - --exclude='.devbox' --exclude='.git' --exclude='test_workspace' --exclude='.cursor' .) | \
            (cd "$TARGET_DIR/.ddd/ddd" && tar xf -)
        fi
    fi
else
    log_error "Unknown installation method: $INSTALL_METHOD"
    exit 1
fi

# Verify DDD source was installed
if [ ! -f "$TARGET_DIR/.ddd/ddd/bootstrap.sh" ]; then
    log_error "Failed to install DDD source (bootstrap.sh not found)"
    exit 1
fi

log_success "DDD source installed"

# Create wrapper scripts in .ddd/bin/
log_info "Creating wrapper scripts..."

# dd-daemon wrapper
cat > "$TARGET_DIR/.ddd/bin/dd-daemon" <<'EOF'
#!/bin/bash
# dd-daemon wrapper - calls vendored DDD
DIR="$(cd "$(dirname "$0")" && pwd)"
DDD_ROOT="$DIR/../ddd"

if [ ! -f "$DDD_ROOT/bootstrap.sh" ]; then
    echo "Error: DDD installation not found at $DDD_ROOT"
    exit 1
fi

exec "$DDD_ROOT/bin/dd-daemon" "$@"
EOF
chmod +x "$TARGET_DIR/.ddd/bin/dd-daemon"

# ddd-wait wrapper
cat > "$TARGET_DIR/.ddd/bin/ddd-wait" <<'EOF'
#!/bin/bash
# ddd-wait wrapper - calls vendored DDD
DIR="$(cd "$(dirname "$0")" && pwd)"
DDD_ROOT="$DIR/../ddd"

if [ ! -f "$DDD_ROOT/bootstrap.sh" ]; then
    echo "Error: DDD installation not found at $DDD_ROOT"
    exit 1
fi

exec "$DDD_ROOT/bin/ddd-wait" "$@"
EOF
chmod +x "$TARGET_DIR/.ddd/bin/ddd-wait"

# ddd-test wrapper
cat > "$TARGET_DIR/.ddd/bin/ddd-test" <<'EOF'
#!/bin/bash
# ddd-test wrapper - calls vendored DDD
DIR="$(cd "$(dirname "$0")" && pwd)"
DDD_ROOT="$DIR/../ddd"

if [ ! -f "$DDD_ROOT/bootstrap.sh" ]; then
    echo "Error: DDD installation not found at $DDD_ROOT"
    exit 1
fi

exec "$DDD_ROOT/bin/ddd-test" "$@"
EOF
chmod +x "$TARGET_DIR/.ddd/bin/ddd-test"

# Create symlink for .ddd/wait (injected client)
log_info "Creating .ddd/wait symlink..."
ln -sf bin/ddd-wait "$TARGET_DIR/.ddd/wait"

log_success "Wrapper scripts created"

# Create config.json if it doesn't exist
if [ ! -f "$TARGET_DIR/.ddd/config.json" ]; then
    log_info "Creating default config.json..."
    cat > "$TARGET_DIR/.ddd/config.json" <<'EOF'
{
  "targets": {
    "dev": {
      "build": {
        "cmd": "make",
        "filter": "gcc_json"
      }
    }
  }
}
EOF
    log_success "config.json created (edit to customize)"
else
    log_info "config.json already exists, preserving"
fi

# Create DDD Makefile (separate from project Makefile)
log_info "Creating .ddd/Makefile (DDD-specific targets)..."
cat > "$TARGET_DIR/.ddd/Makefile" <<'EOF'
# DDD Makefile - Standalone DDD commands
# Usage: make -f .ddd/Makefile <target>
# Or include in your project Makefile: include .ddd/Makefile

.PHONY: daemon daemon-bg ddd-build ddd-stop ddd-logs ddd-clean ddd-help

DDD_BIN := .ddd/bin
DDD_WAIT := .ddd/wait

ddd-help:
	@echo "DDD Commands (use: make -f .ddd/Makefile <target>):"
	@echo "  ddd-daemon      - Start daemon in foreground"
	@echo "  ddd-daemon-bg   - Start daemon in background"
	@echo "  ddd-build       - Trigger DDD build"
	@echo "  ddd-stop        - Stop background daemon"
	@echo "  ddd-logs        - Show daemon logs"
	@echo "  ddd-clean       - Clean DDD artifacts"

ddd-daemon:
	$(DDD_BIN)/dd-daemon

ddd-daemon-bg:
	$(DDD_BIN)/dd-daemon --daemon
	@echo "Daemon started. PID: $$(cat .ddd/daemon.pid 2>/dev/null || echo 'unknown')"

ddd-build:
	$(DDD_WAIT)

ddd-stop:
	@if [ -f .ddd/daemon.pid ]; then \
		kill $$(cat .ddd/daemon.pid) 2>/dev/null && echo "Daemon stopped" || echo "Daemon not running"; \
		rm -f .ddd/daemon.pid; \
	else \
		echo "Daemon not running (no PID file)"; \
	fi

ddd-logs:
	@if [ -f .ddd/daemon.log ]; then \
		tail -f .ddd/daemon.log; \
	else \
		echo "No daemon logs found"; \
	fi

ddd-clean:
	rm -rf .ddd/run/*
	@echo "DDD artifacts cleaned"
EOF
log_success ".ddd/Makefile created"

# Optionally create convenience Makefile if none exists
if [ ! -f "$TARGET_DIR/Makefile" ]; then
    log_info "No project Makefile found, creating convenience Makefile..."
    cat > "$TARGET_DIR/Makefile" <<'EOF'
# Project Makefile
# Includes DDD commands via .ddd/Makefile

# Include DDD targets (optional)
-include .ddd/Makefile

# Your project build targets go here
.PHONY: help

help:
	@echo "Project Makefile"
	@echo ""
	@make -f .ddd/Makefile ddd-help
EOF
    log_success "Convenience Makefile created"
else
    log_info "Project Makefile exists, preserving it"
    log_info "→ Use: make -f .ddd/Makefile <target> for DDD commands"
    log_info "→ Or add this line to your Makefile: -include .ddd/Makefile"
fi

# Create .envrc if it doesn't exist
if [ ! -f "$TARGET_DIR/.envrc" ]; then
    log_info "Creating .envrc (optional direnv support)..."
    cat > "$TARGET_DIR/.envrc" <<'EOF'
# DDD direnv configuration - Generated by bootstrap-ddd.sh
# Enables: direnv allow && dd-daemon

# Add DDD binaries to PATH
export PATH="$PWD/.ddd/bin:$PATH"

# Optional: DDD-specific environment variables
export DDD_ROOT="$PWD/.ddd"
export DDD_TIMEOUT=60

# To use: direnv allow
EOF
    log_success ".envrc created (run 'direnv allow' to use)"
else
    log_info ".envrc already exists, preserving"
fi

# Create .ddd/.gitignore (DDD-specific ignores)
log_info "Creating .ddd/.gitignore..."
cat > "$TARGET_DIR/.ddd/.gitignore" <<'EOF'
# DDD .gitignore - What NOT to commit
# Add these patterns to your project's .gitignore

# System files (never commit)
run/
daemon.log
daemon.pid
bin/
ddd/
wait
Makefile

# User files (DO commit these)
!config.json
!filters/
EOF
log_success ".ddd/.gitignore created"

# Optionally update project .gitignore
if [ "${DDD_UPDATE_GITIGNORE:-yes}" = "yes" ]; then
    GITIGNORE_ENTRIES=(
        "# DDD - System files (do not commit)"
        ".ddd/run/"
        ".ddd/daemon.log"
        ".ddd/daemon.pid"
        ".ddd/bin/"
        ".ddd/ddd/"
        ".ddd/wait"
        ".ddd/Makefile"
        ""
        "# DDD - User files (commit these)"
        "# .ddd/config.json"
        "# .ddd/filters/"
    )

    if [ ! -f "$TARGET_DIR/.gitignore" ]; then
        log_info "Creating project .gitignore..."
        printf "%s\n" "${GITIGNORE_ENTRIES[@]}" > "$TARGET_DIR/.gitignore"
        log_success "Project .gitignore created"
    else
        # Check if DDD entries already exist
        if ! grep -q "^.ddd/run/" "$TARGET_DIR/.gitignore" 2>/dev/null; then
            log_info "Adding DDD entries to project .gitignore..."
            echo "" >> "$TARGET_DIR/.gitignore"
            printf "%s\n" "${GITIGNORE_ENTRIES[@]}" >> "$TARGET_DIR/.gitignore"
            log_success "Project .gitignore updated"
        else
            log_info "Project .gitignore already has DDD entries"
        fi
    fi
else
    log_info "Skipping project .gitignore update (DDD_UPDATE_GITIGNORE=no)"
    log_info "→ See .ddd/.gitignore for recommended patterns"
fi

# Final success message
echo ""
log_success "DDD bootstrap complete!"
echo ""
echo "Next steps:"
echo ""
echo "  1. Review configuration:"
echo -e "     ${BLUE}cat .ddd/config.json${NC}"
echo ""
echo "  2. Start daemon:"
echo -e "     ${BLUE}make -f .ddd/Makefile ddd-daemon-bg${NC}"
echo -e "     ${BLUE}.ddd/bin/dd-daemon --daemon${NC}  (direct)"
echo ""
echo "  3. Trigger build:"
echo -e "     ${BLUE}make -f .ddd/Makefile ddd-build${NC}"
echo -e "     ${BLUE}.ddd/wait${NC}  (direct)"
echo ""
echo "  4. View logs:"
echo -e "     ${BLUE}make -f .ddd/Makefile ddd-logs${NC}"
echo ""
echo "Convenience options:"
if [ -f "$TARGET_DIR/Makefile" ] && ! grep -q "include .ddd/Makefile" "$TARGET_DIR/Makefile" 2>/dev/null; then
    echo -e "  - Add to your Makefile: ${BLUE}-include .ddd/Makefile${NC}"
fi
echo -e "  - Use direnv: ${BLUE}direnv allow${NC} (adds .ddd/bin to PATH)"
echo -e "  - See all DDD commands: ${BLUE}make -f .ddd/Makefile ddd-help${NC}"
echo ""
if [ "${DDD_UPDATE_GITIGNORE:-yes}" != "yes" ]; then
    echo "Note: Add patterns from .ddd/.gitignore to your project's .gitignore"
    echo ""
fi
echo -e "Documentation: ${BLUE}cat .ddd/ddd/README.md${NC}"
echo ""
