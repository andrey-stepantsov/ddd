import sys
import os
import shutil
from unittest.mock import MagicMock, patch
from pathlib import Path
import importlib.util

# Setup path
TOOL_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(TOOL_ROOT))

# Import dd-daemon dynamically (since it has a hyphen)
spec = importlib.util.spec_from_file_location("dd_daemon", str(TOOL_ROOT / "src/dd-daemon.py"))
dd_daemon = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dd_daemon)

def test_buffering_wraps_shell_commands():
    """
    Verify that complex shell commands (cd, &&) are wrapped in 'sh -c'
    when stdbuf is injected.
    """
    # 1. Mock stdbuf presence to force the logic path
    with patch("shutil.which", return_value="/usr/bin/stdbuf"):
        handler = dd_daemon.RequestHandler()
        
        # 2. Mock subprocess.Popen to capture the command string
        with patch("subprocess.Popen") as mock_popen:
            # Setup mock process behavior
            mock_popen.return_value.stdout = [] 
            mock_popen.return_value.returncode = 0
            mock_popen.return_value.wait.return_value = None
            
            # 3. Run a stage with a complex command
            # The Regression Case: cd dir && make
            cmd_input = "cd asic/zsdk && make -j16"
            stage_config = {"cmd": cmd_input}
            
            # Mock file handles
            f_mock = MagicMock()
            
            handler._run_stage("TEST", stage_config, f_mock, f_mock)
            
            # 4. Verify the executed command
            args, _ = mock_popen.call_args
            executed_cmd = args[0]
            
            print(f"DEBUG: Executed Command -> {executed_cmd}")
            
            # Assertion 1: Must use stdbuf
            assert "stdbuf -oL -eL" in executed_cmd
            
            # Assertion 2: Must use sh -c (The Fix)
            assert "sh -c" in executed_cmd
            
            # Assertion 3: Original command must be preserved inside the shell call
            assert cmd_input in executed_cmd

def test_buffering_handles_quotes_safely():
    """Verify that commands with internal quotes are handled safely."""
    with patch("shutil.which", return_value="/usr/bin/stdbuf"):
        handler = dd_daemon.RequestHandler()
        with patch("subprocess.Popen") as mock_popen:
            mock_popen.return_value.stdout = [] 
            mock_popen.return_value.returncode = 0
            
            # Command with quotes: echo "hello world"
            cmd_input = 'echo "hello world"'
            stage_config = {"cmd": cmd_input}
            f_mock = MagicMock()
            
            handler._run_stage("TEST", stage_config, f_mock, f_mock)
            
            args, _ = mock_popen.call_args
            executed_cmd = args[0]
            
            # Should be quoted safely. 
            # Ideally: stdbuf ... sh -c 'echo "hello world"'
            assert "'echo \"hello world\"'" in executed_cmd or "'echo \"hello world\"'" in executed_cmd

def test_no_buffering_if_stdbuf_missing():
    """Verify we fall back to raw execution if stdbuf is not installed."""
    with patch("shutil.which", return_value=None):
        handler = dd_daemon.RequestHandler()
        with patch("subprocess.Popen") as mock_popen:
            mock_popen.return_value.stdout = [] 
            mock_popen.return_value.returncode = 0
            
            cmd_input = "ls -la"
            stage_config = {"cmd": cmd_input}
            f_mock = MagicMock()
            
            handler._run_stage("TEST", stage_config, f_mock, f_mock)
            
            args, _ = mock_popen.call_args
            executed_cmd = args[0]
            
            # Must match input exactly (no wrapping)
            assert executed_cmd == cmd_input
            assert "stdbuf" not in executed_cmd

