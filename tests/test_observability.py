import time
import json
import re
import textwrap
import sys
from pathlib import Path

# Ensure we can import src
REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))

def test_stats_footer_generation(ddd_workspace, daemon_proc):
    """
    Verifies that the daemon appends the observability footer 
    with correct 'Duration', 'Noise Reduction', and 'Tokens'.
    """
    
    # 1. Setup Paths
    ddd_dir = ddd_workspace / ".ddd"
    filters_dir = ddd_dir / "filters"
    filters_dir.mkdir(parents=True, exist_ok=True)
    config_file = ddd_dir / "config.json"
    trigger_file = ddd_dir / "build.request"
    clean_log = ddd_dir / "build.log"

    # 2. Create a "Reducer" Filter
    # This filter will strip lines containing "NOISE", allowing us to 
    # mathematically predict the reduction ratio.
    # Input:  "KEEP\nNOISE\nKEEP\nNOISE" (20 bytes approx)
    # Output: "KEEP\nKEEP\n" (10 bytes approx) -> ~50% reduction
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
    # Command echoes 4 lines. 2 are noise.
    # We use a slight sleep to ensure Duration > 0.00s
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
    # We look for the Footer specifically
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
    print(f"DEBUG LOG:\n{log_content}")

    # Check Duration (Should be >= 0.2s)
    dur_match = re.search(r"⏱\s+Duration:\s+([0-9\.]+)s", log_content)
    assert dur_match, "Duration metric missing"
    duration = float(dur_match.group(1))
    assert duration >= 0.2, f"Duration {duration}s is suspiciously fast (expected > 0.2s)"

    # Check Reduction
    # Raw is roughly: 4 lines * ~12 chars = ~48 bytes
    # Clean is roughly: 2 lines * ~12 chars = ~24 bytes
    # Reduction should be around 50%
    red_match = re.search(r"📉\s+Noise Reduction:\s+([0-9\.]+)%", log_content)
    assert red_match, "Reduction metric missing"
    reduction = float(red_match.group(1))
    assert 40.0 < reduction < 60.0, f"Reduction {reduction}% is off (expected ~50%)"

    # Check Tokens
    # Clean ~24 bytes / 4 = ~6 tokens
    tok_match = re.search(r"🪙\s+Est\. Tokens:\s+(\d+)", log_content)
    assert tok_match, "Token metric missing"
    tokens = int(tok_match.group(1))
    assert tokens > 0, "Token count should be positive"