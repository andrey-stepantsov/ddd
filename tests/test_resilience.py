import pytest
import json
import sys
from pathlib import Path

# Ensure we can import src
TOOL_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(TOOL_ROOT))

from src.filters.crash_detector import CrashDetectorFilter
from src.filters.gcc_json import GccJsonFilter

def test_crash_detector_segfault():
    """Verify that 'Segmentation fault' triggers a fatal JSON error."""
    f = CrashDetectorFilter()
    # Typical C output mixed with a crash
    raw_input = """
    gcc -c main.c
    Segmentation fault (core dumped)
    """
    output = f.process(raw_input)
    
    # Assert it returns JSON
    data = json.loads(output)
    assert isinstance(data, list)
    
    # Assert the first item is the fatal error
    error = data[0]
    assert error["type"] == "fatal"
    assert "Process Crashed" in error["message"]
    assert "Segmentation fault" in error["message"]

def test_crash_detector_preserves_existing_json():
    """Verify crash detector injects into existing JSON stream."""
    f = CrashDetectorFilter()
    # Input is already JSON (from previous filter) + a crash appended
    previous_json = '[{"file":"a.c","line":1,"type":"error","message":"foo"}]'
    raw_input = previous_json + "\nBus error"
    
    output = f.process(raw_input)
    data = json.loads(output)
    
    assert len(data) == 2
    # Crash should be inserted at the top
    assert data[0]["type"] == "fatal"
    assert "Bus error" in data[0]["message"]
    # Existing error preserved
    assert data[1]["message"] == "foo"

def test_gcc_json_nothing_to_be_done():
    """Verify the patch allows 'Nothing to be done' as success."""
    f = GccJsonFilter()
    raw_input = "make: Nothing to be done for 'all'."
    
    output = f.process(raw_input)
    data = json.loads(output)
    
    # Should be an empty list (Success), NOT an error object
    assert isinstance(data, list)
    assert len(data) == 0

def test_gcc_json_still_catches_real_errors():
    """Verify legitimate compiler errors are still caught."""
    f = GccJsonFilter()
    raw_input = "main.c:10:5: error: missing semicolon"
    
    output = f.process(raw_input)
    data = json.loads(output)
    
    assert len(data) == 1
    assert data[0]["type"] == "error"
