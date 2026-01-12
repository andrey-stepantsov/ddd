import pytest
import json
import time
import sys
import textwrap
from pathlib import Path

# Ensure we can import src
TOOL_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(TOOL_ROOT))

def test_filter_chaining_logic(ddd_workspace, daemon_proc):
    """
    Verifies that the daemon can execute a list of filters in sequence.
    Chain: Raw Input -> Filter A -> Filter B -> Final Log
    """
    
    # 1. Define Paths (UPDATED for Split-State)
    ddd_dir = ddd_workspace / ".ddd"
    run_dir = ddd_dir / "run"           # <--- NEW
    filters_dir = ddd_dir / "filters"
    filters_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = ddd_dir / "config.json"
    trigger_file = run_dir / "build.request" # <--- NEW
    clean_log = run_dir / "build.log"        # <--- NEW

    # 2. Create Custom Filter A (Appends tag A)
    code_a = textwrap.dedent("""
        from src.filters import register_filter
        from src.filters.base import BaseFilter

        @register_filter("chain_a")
        class FilterA(BaseFilter):
            def process(self, text):
                return text.strip() + " [A]"
    """)
    (filters_dir / "chain_a.py").write_text(code_a)

    # 3. Create Custom Filter B (Appends tag B)
    code_b = textwrap.dedent("""
        from src.filters import register_filter
        from src.filters.base import BaseFilter

        @register_filter("chain_b")
        class FilterB(BaseFilter):
            def process(self, text):
                return text.strip() + " [B]"
    """)
    (filters_dir / "chain_b.py").write_text(code_b)

    # 4. Configure Daemon to use Chain ["chain_a", "chain_b"]
    config_data = {
        "targets": {
            "dev": {
                "build": { 
                    "cmd": "echo 'ORIGINAL'", 
                    "filter": ["chain_a", "chain_b"] 
                }
            }
        }
    }
    config_file.write_text(json.dumps(config_data))

    # 5. Trigger Build
    trigger_file.touch()

    # 6. Wait for Log (Poll for ~2s)
    found = False
    for _ in range(20):
        if clean_log.exists():
            content = clean_log.read_text()
            if "[B]" in content:
                found = True
                break
        time.sleep(0.1)
    
    # 7. Assertions
    if not found:
        if clean_log.exists():
            print(f"DEBUG LOG CONTENT: {clean_log.read_text()}")
        pytest.fail("Chain did not complete. Expected output missing.")

    final_content = clean_log.read_text()
    
    # Check Order: Original -> A -> B
    assert "ORIGINAL [A] [B]" in final_content
