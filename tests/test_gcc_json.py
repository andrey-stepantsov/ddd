import json
import pytest
import sys
from pathlib import Path

# Ensure we can import src
REPO_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO_ROOT))

from src.filters.gcc_json import GccJsonFilter

def test_gcc_json_parsing():
    # 1. Sample GCC Output
    raw_input = """
main.c:10:5: error: expected ';' before 'return'
src/utils.c:25: warning: unused variable 'x'
    """
    
    # 2. Process
    f = GccJsonFilter()
    output = f.process(raw_input)
    
    # 3. Parse JSON to verify structure
    data = json.loads(output)
    
    assert isinstance(data, list)
    assert len(data) == 2
    
    # Check Error
    assert data[0]["file"] == "main.c"
    assert data[0]["line"] == 10
    assert data[0]["col"] == 5
    assert data[0]["type"] == "error"
    assert "expected ';'" in data[0]["message"]
    
    # Check Warning
    assert data[1]["file"] == "src/utils.c"
    assert data[1]["line"] == 25
    assert data[1]["type"] == "warning"