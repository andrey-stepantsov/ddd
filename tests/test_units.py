import unittest
from unittest.mock import MagicMock, patch, mock_open, call
import sys
import os
import json
import time

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

# Mock filters before importing dd-daemon
sys.modules["src.filters"] = MagicMock()
sys.modules["src.filters"].REGISTRY = {"raw": MagicMock()}

import importlib
dd_daemon = importlib.import_module("dd-daemon")

class TestDaemonUnits(unittest.TestCase):
    def setUp(self):
        self.handler = dd_daemon.RequestHandler()
        # Mock config loading
        self.handler.load_config = MagicMock()
        
    @patch("subprocess.Popen")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("time.time")
    def test_execute_logic_build_success(self, mock_time, mock_exists, mock_file, mock_popen):
        """Test the core pipeline logic with a successful build."""
        mock_time.return_value = 1000.0
        self.handler.stdbuf_available = True # Force True
        
        # specific mocks
        mock_exists.return_value = False # No sentinel
        
        # Config
        self.handler.load_config.return_value = {
            "targets": {
                "dev": {
                    "build": {"cmd": "make"},
                    "verify": {"cmd": "test"}
                }
            }
        }
        
        # Process Mock (Build Success)
        proc_mock = MagicMock()
        proc_mock.stdout = ["Build Output\n"]
        proc_mock.returncode = 0
        proc_mock.wait.return_value = None
        
        # Process Mock (Verify Success)
        proc_verify = MagicMock()
        proc_verify.stdout = ["Verify Output\n"]
        proc_verify.returncode = 0
        
        mock_popen.side_effect = [proc_mock, proc_verify]
        
        # Run
        self.handler._write_artifacts = MagicMock()
        self.handler._execute_logic()
        
        # Debug
        # print(f"\n[DEBUG] Popen Calls: {mock_popen.call_args_list}")

        # Verify calls manually
        build_seen = False
        verify_seen = False
        
        for call_obj in mock_popen.call_args_list:
            args, _ = call_obj
            cmd = args[0]
            if "make" in cmd: build_seen = True
            if "test" in cmd: verify_seen = True

        self.assertTrue(build_seen, "Build command missing")
        self.assertTrue(verify_seen, "Verify command missing")
        
        # 3. Artifacts Written (Success)
        self.handler._write_artifacts.assert_called_with(True, 0.0, 26, 26)

    @patch("subprocess.Popen")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("time.time")
    def test_execute_logic_build_fail(self, mock_time, mock_exists, mock_file, mock_popen):
        """Test pipeline stops on build failure."""
        mock_time.return_value = 1000.0
        mock_exists.return_value = False
        
        self.handler.load_config.return_value = {
            "targets": { "dev": { "build": {"cmd": "bad_make"} } }
        }
        
        # Run
        self.handler._write_artifacts = MagicMock()
        self.handler._execute_logic()
        
        # Verify calls manually to avoid strict Popen matching issues
        cmd_seen = False
        for call_obj in mock_popen.call_args_list:
            args, _ = call_obj
            if "bad_make" in args[0]:
                cmd_seen = True
        
        self.assertTrue(cmd_seen, "Build command not passed to Popen")
        
        self.handler._write_artifacts.assert_called_with(False, 0.0, 6, 6)

    @patch("subprocess.Popen")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_sentinel_recovery(self, mock_exists, mock_file, mock_popen):
        """Test build failure overridden by sentinel file."""
        self.handler.load_config.return_value = {
            "targets": { 
                "dev": { 
                    "build": {"cmd": "fail"},
                    "sentinel_file": "/tmp/success.flag"
                } 
            }
        }
        
        # Mock sentinel existing logic:
        # 1. initial check (remove) -> True
        # 2. check after build -> True
        mock_exists.side_effect = [True, True]
        
        proc_mock = MagicMock()
        proc_mock.stdout = []
        proc_mock.returncode = 1
        mock_popen.return_value = proc_mock
        
        self.handler._write_artifacts = MagicMock()
        
        # Hook os.remove to avoid error
        with patch("os.remove") as mock_rm:
            self.handler._execute_logic()
            mock_rm.assert_called_with("/tmp/success.flag")

        # Should be SUCCESS because sentinel appeared
        args = self.handler._write_artifacts.call_args
        self.assertTrue(args[0][0]) # success=True

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="client_binary_content")
    @patch("os.chmod")
    @patch("os.stat")
    def test_inject_client(self, mock_stat, mock_chmod, mock_file, mock_exists):
        """Test client injection logic."""
        mock_exists.return_value = True
        mock_stat.return_value.st_mode = 0o644
        
        self.handler.inject_client()
        
        # Verify read master
        mock_file.assert_any_call(dd_daemon.MASTER_CLIENT_PATH, 'r')
        # Verify write injected
        mock_file.assert_any_call(dd_daemon.INJECTED_CLIENT, 'w')
        # Verify chmod
        mock_chmod.assert_called()

    @patch("time.time")
    def test_on_modified(self, mock_time):
        """Test event handling."""
        mock_time.return_value = 2000.0
        
        event = MagicMock()
        event.src_path = "/path/to/build.request"
        
        self.handler.run_pipeline = MagicMock()
        self.handler.on_modified(event)
        
        self.handler.run_pipeline.assert_called_once()

if __name__ == "__main__":
    unittest.main()
