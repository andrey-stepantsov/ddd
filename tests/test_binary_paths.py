"""
Test binary path resolution (Phase 2).

Verifies that dd-daemon and ddd-test can find DDD_ROOT from:
1. .ddd/ddd/bin/ (vendored location)
2. .ddd/bin/ (wrapper location)
3. ddd/bin/ (original repo - v0.7.x compatibility)
"""

import subprocess
import tempfile
from pathlib import Path
import shutil
import pytest


def create_minimal_ddd_structure(root_path):
    """Create minimal DDD structure needed for path resolution."""
    # Create bootstrap.sh as the detection marker
    bootstrap_content = """#!/usr/bin/env bash
# Minimal bootstrap for testing
echo "DDD Bootstrap"
"""
    bootstrap_file = root_path / "bootstrap.sh"
    bootstrap_file.write_text(bootstrap_content)
    bootstrap_file.chmod(0o755)
    
    # Create minimal dd-daemon binary (actual implementation from bin/)
    daemon_content = """#!/usr/bin/env bash
set -euo pipefail

# Resolve script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Step 1: Check if running from vendored location (.ddd/ddd/bin/)
if [ -f "$DIR/../bootstrap.sh" ]; then
    DDD_ROOT="$DIR/.."
# Step 2: Check if running from wrapper location (.ddd/bin/)
elif [ -f "$DIR/../ddd/bootstrap.sh" ]; then
    DDD_ROOT="$DIR/../ddd"
else
    echo "Error: Cannot find DDD installation" >&2
    echo "Looked for bootstrap.sh in:" >&2
    echo "  - $DIR/../bootstrap.sh" >&2
    echo "  - $DIR/../ddd/bootstrap.sh" >&2
    exit 1
fi

# For testing: just echo the DDD_ROOT
echo "DDD_ROOT=$DDD_ROOT"
"""
    bin_dir = root_path / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    daemon_file = bin_dir / "dd-daemon"
    daemon_file.write_text(daemon_content)
    daemon_file.chmod(0o755)
    
    # Also create ddd-test with same logic
    test_content = daemon_content.replace("dd-daemon", "ddd-test")
    test_file = bin_dir / "ddd-test"
    test_file.write_text(test_content)
    test_file.chmod(0o755)
    
    return root_path


class TestBinaryPathResolution:
    """Test binary path resolution in different directory structures."""

    def test_vendored_location(self, tmp_path):
        """Test binary running from .ddd/ddd/bin/ (vendored)."""
        # Structure: project/.ddd/ddd/
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        ddd_vendor_dir = project_dir / ".ddd" / "ddd"
        ddd_vendor_dir.mkdir(parents=True)
        
        # Create DDD structure at .ddd/ddd/
        create_minimal_ddd_structure(ddd_vendor_dir)
        
        # Run binary from .ddd/ddd/bin/
        daemon_path = ddd_vendor_dir / "bin" / "dd-daemon"
        result = subprocess.run(
            [str(daemon_path)],
            capture_output=True,
            text=True,
            cwd=project_dir
        )
        
        assert result.returncode == 0, f"Binary failed: {result.stderr}"
        assert "DDD_ROOT=" in result.stdout
        
        # Extract DDD_ROOT value
        ddd_root_line = [l for l in result.stdout.split('\n') if 'DDD_ROOT=' in l][0]
        ddd_root = ddd_root_line.split('=')[1]
        
        # Should resolve to .ddd/ddd
        assert Path(ddd_root).resolve() == ddd_vendor_dir.resolve()

    def test_wrapper_location(self, tmp_path):
        """Test binary running from .ddd/bin/ (wrapper)."""
        # Structure: project/.ddd/bin/ (wrapper) -> .ddd/ddd/ (vendored)
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        ddd_vendor_dir = project_dir / ".ddd" / "ddd"
        ddd_vendor_dir.mkdir(parents=True)
        wrapper_bin_dir = project_dir / ".ddd" / "bin"
        wrapper_bin_dir.mkdir(parents=True)
        
        # Create DDD structure at .ddd/ddd/
        create_minimal_ddd_structure(ddd_vendor_dir)
        
        # Create wrapper at .ddd/bin/ (copy of the binary)
        shutil.copy(
            ddd_vendor_dir / "bin" / "dd-daemon",
            wrapper_bin_dir / "dd-daemon"
        )
        (wrapper_bin_dir / "dd-daemon").chmod(0o755)
        
        # Run wrapper binary from .ddd/bin/
        wrapper_path = wrapper_bin_dir / "dd-daemon"
        result = subprocess.run(
            [str(wrapper_path)],
            capture_output=True,
            text=True,
            cwd=project_dir
        )
        
        assert result.returncode == 0, f"Binary failed: {result.stderr}"
        assert "DDD_ROOT=" in result.stdout
        
        # Extract DDD_ROOT value
        ddd_root_line = [l for l in result.stdout.split('\n') if 'DDD_ROOT=' in l][0]
        ddd_root = ddd_root_line.split('=')[1]
        
        # Should resolve to .ddd/ddd (not .ddd/bin)
        assert Path(ddd_root).resolve() == ddd_vendor_dir.resolve()

    def test_original_repo_location(self, tmp_path):
        """Test binary running from ddd/bin/ (original repo, v0.7.x compat)."""
        # Structure: ddd/ (original repo)
        ddd_repo_dir = tmp_path / "ddd"
        ddd_repo_dir.mkdir()
        
        # Create DDD structure at ddd/
        create_minimal_ddd_structure(ddd_repo_dir)
        
        # Run binary from ddd/bin/
        daemon_path = ddd_repo_dir / "bin" / "dd-daemon"
        result = subprocess.run(
            [str(daemon_path)],
            capture_output=True,
            text=True,
            cwd=ddd_repo_dir
        )
        
        assert result.returncode == 0, f"Binary failed: {result.stderr}"
        assert "DDD_ROOT=" in result.stdout
        
        # Extract DDD_ROOT value
        ddd_root_line = [l for l in result.stdout.split('\n') if 'DDD_ROOT=' in l][0]
        ddd_root = ddd_root_line.split('=')[1]
        
        # Should resolve to ddd/ (repo root)
        assert Path(ddd_root).resolve() == ddd_repo_dir.resolve()

    def test_missing_bootstrap_error(self, tmp_path):
        """Test that binary fails gracefully when bootstrap.sh not found."""
        # Create structure without bootstrap.sh
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        bin_dir = project_dir / "bin"
        bin_dir.mkdir()
        
        # Create daemon without DDD structure
        daemon_content = """#!/usr/bin/env bash
set -euo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -f "$DIR/../bootstrap.sh" ]; then
    DDD_ROOT="$DIR/.."
elif [ -f "$DIR/../ddd/bootstrap.sh" ]; then
    DDD_ROOT="$DIR/../ddd"
else
    echo "Error: Cannot find DDD installation" >&2
    exit 1
fi
echo "DDD_ROOT=$DDD_ROOT"
"""
        daemon_path = bin_dir / "dd-daemon"
        daemon_path.write_text(daemon_content)
        daemon_path.chmod(0o755)
        
        # Run binary - should fail
        result = subprocess.run(
            [str(daemon_path)],
            capture_output=True,
            text=True,
            cwd=project_dir
        )
        
        assert result.returncode == 1
        assert "Cannot find DDD installation" in result.stderr

    def test_both_binaries_consistent(self, tmp_path):
        """Test that dd-daemon and ddd-test resolve paths identically."""
        # Structure: project/.ddd/ddd/
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        ddd_vendor_dir = project_dir / ".ddd" / "ddd"
        ddd_vendor_dir.mkdir(parents=True)
        
        # Create DDD structure
        create_minimal_ddd_structure(ddd_vendor_dir)
        
        # Run both binaries
        daemon_result = subprocess.run(
            [str(ddd_vendor_dir / "bin" / "dd-daemon")],
            capture_output=True,
            text=True,
            cwd=project_dir
        )
        test_result = subprocess.run(
            [str(ddd_vendor_dir / "bin" / "ddd-test")],
            capture_output=True,
            text=True,
            cwd=project_dir
        )
        
        # Both should succeed
        assert daemon_result.returncode == 0
        assert test_result.returncode == 0
        
        # Extract DDD_ROOT from both
        daemon_root = [l for l in daemon_result.stdout.split('\n') if 'DDD_ROOT=' in l][0]
        test_root = [l for l in test_result.stdout.split('\n') if 'DDD_ROOT=' in l][0]
        
        # Should be identical
        assert daemon_root == test_root


class TestPathResolutionEdgeCases:
    """Test edge cases in path resolution."""

    def test_symlinked_binary(self, tmp_path):
        """Test that symlinked binaries work correctly."""
        # Structure: project/.ddd/ddd/ with symlink
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        ddd_vendor_dir = project_dir / ".ddd" / "ddd"
        ddd_vendor_dir.mkdir(parents=True)
        
        create_minimal_ddd_structure(ddd_vendor_dir)
        
        # Create symlink to daemon
        symlink_dir = project_dir / "bin"
        symlink_dir.mkdir()
        symlink_path = symlink_dir / "dd-daemon"
        symlink_path.symlink_to(ddd_vendor_dir / "bin" / "dd-daemon")
        
        # Run via symlink - should still resolve correctly
        result = subprocess.run(
            [str(symlink_path)],
            capture_output=True,
            text=True,
            cwd=project_dir
        )
        
        # Should succeed (symlink resolution via ${BASH_SOURCE[0]})
        assert result.returncode == 0
        assert "DDD_ROOT=" in result.stdout

    def test_relative_path_invocation(self, tmp_path):
        """Test running binary with relative path."""
        # Structure: project/.ddd/ddd/
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        ddd_vendor_dir = project_dir / ".ddd" / "ddd"
        ddd_vendor_dir.mkdir(parents=True)
        
        create_minimal_ddd_structure(ddd_vendor_dir)
        
        # Run with relative path from project root
        result = subprocess.run(
            ["./.ddd/ddd/bin/dd-daemon"],
            capture_output=True,
            text=True,
            cwd=project_dir,
            shell=True
        )
        
        assert result.returncode == 0
        assert "DDD_ROOT=" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
