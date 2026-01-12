import time
import json
import re
import textwrap
import sys
from pathlib import Path

# Ensure we can import src
TOOL_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(TOOL_ROOT))

def test_stats_footer_generation(ddd_workspace, daemon_proc):
    """
    Verifies that the daemon appends the observability footer 
    with correct 'Duration', 'Noise Reduction', and 'Tokens'.
    """
    
    # 1. Setup Paths (UPDATED for Split-State)
    ddd_dir = ddd_workspace / ".ddd"
    run_dir = ddd_dir / "run"           # <--- NEW
    filters_dir = ddd_dir / "filters"
    filters_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = ddd_dir / "config.json"
    trigger_file = run_dir / "build.request" # <--- NEW
    clean_log = run_dir / "build.log"        # <--- NEW

    # 2. Create a "Reducer" Filter
    filter_code = textwrap.dedent("""
        from src.filters import register_filter
        from src.filters.base import BaseFilter

        @register_filter("test_reducer")
        class ReducerFilter(BaseFilter):
            def process(self, text):
                lines = text.splitlines()
                # Keep only lines that do NOT contain "NOISE"
                filtered = [L for L in lines if "NOISE" not in L]
                return "\\n".join(filtered) + "\\n"
    """)
    (filters_dir / "reducer.py").write_text(filter_code)

    # 3. Configure Daemon
    cmd = "echo 'KEEP_LINE_1'; echo 'NOISE_LINE_1'; sleep 0.2; echo 'KEEP_LINE_2'; echo 'NOISE_LINE_2'"
    
    config_data = {
        "targets": {
            "dev": {
                "build": { 
                    "cmd": cmd, 
                    "filter": "test_reducer" 
                }
            }
        }
    }
    config_file.write_text(json.dumps(config_data))

    # 4. Trigger Build
    trigger_file.touch()

    # 5. Wait for Log (Poll for ~2s)
    footer_found = False
    log_content = ""
    
    for _ in range(30):
        if clean_log.exists():
            log_content = clean_log.read_text()
            if "📊 Build Stats" in log_content:
                footer_found = True
                break
        time.sleep(0.1)

    assert footer_found, "Stats footer was not found in build.log"

    # 6. Verify Content via Regex
    # Check Duration (Should be >= 0.2s)
    dur_match = re.search(r"⏱\s+Duration:\s+([0-9\.]+)s", log_content)
    assert dur_match, "Duration metric missing"
    duration = float(dur_match.group(1))
    assert duration >= 0.2, f"Duration {duration}s is suspiciously fast (expected > 0.2s)"

    # Check Reduction
    red_match = re.search(r"📉\s+Noise Reduction:\s+([0-9\.]+)%", log_content)
    assert red_match, "Reduction metric missing"
    reduction = float(red_match.group(1))
    assert 40.0 < reduction < 60.0, f"Reduction {reduction}% is off (expected ~50%)"

    # Check Tokens
    tok_match = re.search(r"🪙\s+Est\. Tokens:\s+(\d+)", log_content)
    assert tok_match, "Token metric missing"
    tokens = int(tok_match.group(1))
    assert tokens > 0, "Token count should be positive"
