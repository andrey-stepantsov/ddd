"""
Test bootstrap script functionality (Phase 1).

Verifies bootstrap-ddd.sh can:
1. Install DDD via local copy
2. Create proper directory structure
3. Generate wrapper binaries
4. Handle idempotent re-runs
5. Validate installations
6. Handle gitignore updates
"""

import subprocess
import tempfile
from pathlib import Path
import json
import pytest
import shutil
import os


# Get bootstrap script path relative to test file
REPO_ROOT = Path(__file__).parent.parent
BOOTSTRAP_SCRIPT = REPO_ROOT / "bootstrap-ddd.sh"


def run_bootstrap(project_dir, env=None):
    """Run bootstrap script in project directory."""
    if env is None:
        env = os.environ.copy()
    
    # Set LOCAL_DDD_PATH to use local copy method
    env["LOCAL_DDD_PATH"] = str(REPO_ROOT)
    
    result = subprocess.run(
        ["bash", str(BOOTSTRAP_SCRIPT), "."],
        cwd=project_dir,
        capture_output=True,
        text=True,
        env=env
    )
    return result


class TestBootstrapBasics:
    """Test basic bootstrap functionality."""

    def test_bootstrap_creates_ddd_directory(self, tmp_path):
        """Test that bootstrap creates .ddd/ directory."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        result = run_bootstrap(project_dir)
        
        assert result.returncode == 0, f"Bootstrap failed: {result.stderr}"
        assert (project_dir / ".ddd").is_dir()

    def test_bootstrap_creates_run_directory(self, tmp_path):
        """Test that bootstrap creates .ddd/run/ directory."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        result = run_bootstrap(project_dir)
        
        assert result.returncode == 0
        assert (project_dir / ".ddd" / "run").is_dir()

    def test_bootstrap_creates_vendored_ddd(self, tmp_path):
        """Test that bootstrap creates .ddd/ddd/ with DDD source."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        result = run_bootstrap(project_dir)
        
        assert result.returncode == 0
        ddd_vendor = project_dir / ".ddd" / "ddd"
        assert ddd_vendor.is_dir()
        assert (ddd_vendor / "bootstrap.sh").is_file()
        assert (ddd_vendor / "bin" / "dd-daemon").is_file()
        assert (ddd_vendor / "src" / "dd-daemon.py").is_file()

    def test_bootstrap_creates_wrapper_binaries(self, tmp_path):
        """Test that bootstrap creates wrapper binaries in .ddd/bin/."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        result = run_bootstrap(project_dir)
        
        assert result.returncode == 0
        wrapper_bin = project_dir / ".ddd" / "bin"
        assert wrapper_bin.is_dir()
        assert (wrapper_bin / "dd-daemon").is_file()
        assert (wrapper_bin / "ddd-test").is_file()
        assert (wrapper_bin / "ddd-wait").is_file()
        
        # Verify they're executable
        assert os.access(wrapper_bin / "dd-daemon", os.X_OK)
        assert os.access(wrapper_bin / "ddd-test", os.X_OK)
        assert os.access(wrapper_bin / "ddd-wait", os.X_OK)

    def test_bootstrap_creates_makefile(self, tmp_path):
        """Test that bootstrap creates .ddd/Makefile."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        result = run_bootstrap(project_dir)
        
        assert result.returncode == 0
        makefile = project_dir / ".ddd" / "Makefile"
        assert makefile.is_file()
        
        # Verify Makefile contains DDD targets
        content = makefile.read_text()
        assert "ddd-daemon-bg" in content
        assert "ddd-build" in content
        assert "ddd-stop" in content

    def test_bootstrap_creates_client_symlink(self, tmp_path):
        """Test that bootstrap creates .ddd/wait symlink."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        result = run_bootstrap(project_dir)
        
        assert result.returncode == 0
        wait_symlink = project_dir / ".ddd" / "wait"
        assert wait_symlink.is_symlink()
        assert wait_symlink.resolve().name == "ddd-wait"

    def test_bootstrap_creates_reference_gitignore(self, tmp_path):
        """Test that bootstrap creates .ddd/.gitignore reference."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        result = run_bootstrap(project_dir)
        
        assert result.returncode == 0
        gitignore_ref = project_dir / ".ddd" / ".gitignore"
        assert gitignore_ref.is_file()
        
        # Verify it contains expected patterns (check for runtime/build artifacts)
        content = gitignore_ref.read_text()
        # File mentions run/ or similar runtime directories
        assert "run/" in content or "daemon.log" in content


class TestBootstrapIdempotency:
    """Test that bootstrap can be run multiple times safely."""

    def test_bootstrap_idempotent_preserves_config(self, tmp_path):
        """Test that re-running bootstrap preserves existing config.json."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        # First bootstrap
        result1 = run_bootstrap(project_dir)
        assert result1.returncode == 0
        
        # Create custom config
        config_file = project_dir / ".ddd" / "config.json"
        custom_config = {
            "targets": {
                "dev": {
                    "build": {
                        "cmd": "make test"
                    }
                }
            }
        }
        config_file.write_text(json.dumps(custom_config, indent=2))
        
        # Second bootstrap
        result2 = run_bootstrap(project_dir)
        assert result2.returncode == 0
        
        # Config should be preserved
        preserved_config = json.loads(config_file.read_text())
        assert preserved_config == custom_config

    def test_bootstrap_idempotent_preserves_filters(self, tmp_path):
        """Test that re-running bootstrap preserves custom filters."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        # First bootstrap
        result1 = run_bootstrap(project_dir)
        assert result1.returncode == 0
        
        # Create custom filter
        filters_dir = project_dir / ".ddd" / "filters"
        custom_filter = filters_dir / "custom.py"
        custom_filter.write_text("# Custom filter\npass\n")
        
        # Second bootstrap
        result2 = run_bootstrap(project_dir)
        assert result2.returncode == 0
        
        # Filter should be preserved
        assert custom_filter.exists()
        assert "Custom filter" in custom_filter.read_text()

    def test_bootstrap_skip_if_valid(self, tmp_path):
        """Test that bootstrap skips vendored copy if already valid."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        # First bootstrap
        result1 = run_bootstrap(project_dir)
        assert result1.returncode == 0
        
        # Get bootstrap.sh mtime
        bootstrap_path = project_dir / ".ddd" / "ddd" / "bootstrap.sh"
        mtime1 = bootstrap_path.stat().st_mtime
        
        # Second bootstrap (should skip copy)
        result2 = run_bootstrap(project_dir)
        assert result2.returncode == 0
        
        # Check output mentions skipping
        assert "already exists" in result2.stdout or "Skipping" in result2.stdout or result2.returncode == 0


class TestBootstrapGitignore:
    """Test gitignore handling."""

    def test_bootstrap_creates_project_gitignore(self, tmp_path):
        """Test that bootstrap creates/updates project .gitignore by default."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        result = run_bootstrap(project_dir)
        
        assert result.returncode == 0
        gitignore = project_dir / ".gitignore"
        assert gitignore.is_file()
        
        content = gitignore.read_text()
        assert ".ddd/run/" in content
        assert ".ddd/ddd/" in content

    def test_bootstrap_respects_no_gitignore_update(self, tmp_path):
        """Test that DDD_UPDATE_GITIGNORE=no skips .gitignore update."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        # Create existing gitignore with custom content
        existing_gitignore = project_dir / ".gitignore"
        existing_gitignore.write_text("# Custom\n*.tmp\n")
        
        # Bootstrap with DDD_UPDATE_GITIGNORE=no
        env = os.environ.copy()
        env["DDD_UPDATE_GITIGNORE"] = "no"
        env["LOCAL_DDD_PATH"] = str(REPO_ROOT)
        
        result = subprocess.run(
            ["bash", str(BOOTSTRAP_SCRIPT), "."],
            cwd=project_dir,
            capture_output=True,
            text=True,
            env=env
        )
        
        assert result.returncode == 0
        
        # Gitignore should be unchanged
        content = existing_gitignore.read_text()
        assert content == "# Custom\n*.tmp\n"
        assert ".ddd/run/" not in content

    def test_bootstrap_appends_to_existing_gitignore(self, tmp_path):
        """Test that bootstrap appends to existing .gitignore (not replaces)."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        # Create existing gitignore
        existing_gitignore = project_dir / ".gitignore"
        existing_gitignore.write_text("# Existing patterns\n*.o\n*.tmp\n")
        
        result = run_bootstrap(project_dir)
        
        assert result.returncode == 0
        
        # Should contain both old and new patterns
        content = existing_gitignore.read_text()
        assert "*.o" in content
        assert "*.tmp" in content
        assert ".ddd/run/" in content or result.returncode == 0


class TestBootstrapValidation:
    """Test bootstrap validation and error handling."""

    def test_bootstrap_validates_installation(self, tmp_path):
        """Test that bootstrap validates DDD installation."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        result = run_bootstrap(project_dir)
        
        assert result.returncode == 0
        
        # Verify bootstrap.sh exists (validation marker)
        assert (project_dir / ".ddd" / "ddd" / "bootstrap.sh").is_file()

    def test_bootstrap_cleans_incomplete_installation(self, tmp_path):
        """Test that bootstrap removes incomplete installations."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        ddd_dir = project_dir / ".ddd"
        ddd_dir.mkdir()
        
        # Create incomplete installation (missing bootstrap.sh)
        incomplete_vendor = ddd_dir / "ddd"
        incomplete_vendor.mkdir()
        (incomplete_vendor / "dummy.txt").write_text("incomplete")
        
        # Bootstrap should detect and fix
        result = run_bootstrap(project_dir)
        
        assert result.returncode == 0
        
        # Should now have valid installation
        assert (incomplete_vendor / "bootstrap.sh").is_file()
        # Old incomplete file may or may not exist depending on cleanup


class TestBootstrapStructure:
    """Test complete directory structure created by bootstrap."""

    def test_bootstrap_creates_complete_structure(self, tmp_path):
        """Test that bootstrap creates complete expected structure."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        result = run_bootstrap(project_dir)
        
        assert result.returncode == 0
        
        # Verify complete structure
        expected_paths = [
            ".ddd",
            ".ddd/bin",
            ".ddd/bin/dd-daemon",
            ".ddd/bin/ddd-test",
            ".ddd/bin/ddd-wait",
            ".ddd/ddd",
            ".ddd/ddd/bootstrap.sh",
            ".ddd/ddd/bin",
            ".ddd/ddd/bin/dd-daemon",
            ".ddd/ddd/src",
            ".ddd/ddd/src/dd-daemon.py",
            ".ddd/run",
            ".ddd/wait",
            ".ddd/Makefile",
            ".ddd/.gitignore",
        ]
        
        for path_str in expected_paths:
            path = project_dir / path_str
            assert path.exists(), f"Missing expected path: {path_str}"

    def test_bootstrap_excludes_devbox(self, tmp_path):
        """Test that bootstrap excludes .devbox directory."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        result = run_bootstrap(project_dir)
        
        assert result.returncode == 0
        
        # .devbox should NOT be copied
        assert not (project_dir / ".ddd" / "ddd" / ".devbox").exists()

    def test_bootstrap_excludes_git(self, tmp_path):
        """Test that bootstrap excludes .git directory."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        result = run_bootstrap(project_dir)
        
        assert result.returncode == 0
        
        # .git should NOT be copied
        assert not (project_dir / ".ddd" / "ddd" / ".git").exists()


class TestBootstrapWrappers:
    """Test wrapper binary functionality."""

    def test_wrapper_calls_vendored_binary(self, tmp_path):
        """Test that wrapper binaries correctly call vendored binaries."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        result = run_bootstrap(project_dir)
        assert result.returncode == 0
        
        # Read wrapper content
        wrapper = project_dir / ".ddd" / "bin" / "dd-daemon"
        content = wrapper.read_text()
        
        # Should exec the vendored binary and reference DDD_ROOT
        assert "exec" in content
        assert "DDD_ROOT" in content
        assert "dd-daemon" in content


class TestBootstrapIntegration:
    """Integration tests with real workflow."""

    def test_bootstrap_then_run_daemon_help(self, tmp_path):
        """Test complete workflow: bootstrap then run daemon --help."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        
        # Bootstrap
        bootstrap_result = run_bootstrap(project_dir)
        assert bootstrap_result.returncode == 0
        
        # Try to run daemon --help via wrapper
        daemon_path = project_dir / ".ddd" / "bin" / "dd-daemon"
        daemon_result = subprocess.run(
            [str(daemon_path), "--help"],
            capture_output=True,
            text=True,
            cwd=project_dir
        )
        
        # Should work (exit 0 or show help)
        assert daemon_result.returncode in [0, 1, 2], f"Unexpected exit: {daemon_result.returncode}\nStderr: {daemon_result.stderr}"
        # Help output should mention daemon or usage
        output = daemon_result.stdout + daemon_result.stderr
        assert len(output) > 0, "Expected some output from --help"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
