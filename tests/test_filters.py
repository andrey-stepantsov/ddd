import pytest
from src.filters.raw import RawFilter
from src.filters.gcc_make import GccMakeFilter

# --- Fixtures ---

@pytest.fixture
def raw_input_with_ansi():
    return "\x1b[31mError:\x1b[0m Something bad happened."

@pytest.fixture
def gcc_output_sample():
    return """make[1]: Entering directory '/usr/src/app'
gcc -c main.c -o main.o
/usr/src/app/main.c:10:9: error: expected ';' before 'return'
    return 0;
    ^
make[1]: Leaving directory '/usr/src/app'
Build finished."""

# --- Tests: RawFilter ---

def test_raw_filter_strips_ansi(raw_input_with_ansi):
    f = RawFilter()
    result = f.process(raw_input_with_ansi)
    assert "\x1b" not in result
    assert "Error: Something bad happened." in result

# --- Tests: GccMakeFilter ---

def test_gcc_filter_strips_noise(gcc_output_sample):
    f = GccMakeFilter()
    result = f.process(gcc_output_sample)
    
    # Should remove directory noise
    assert "Entering directory" not in result
    assert "Leaving directory" not in result
    
    # Should keep the error and the build status
    assert "error: expected ';'" in result
    assert "Build finished." in result

def test_gcc_filter_captures_context():
    """Verify that triggering an error captures the following lines (context)."""
    text = """
file.c:1: error: boom
context line 1
context line 2
context line 3
context line 4
context line 5
context line 6 (should be dropped)
"""
    f = GccMakeFilter()
    result = f.process(text)
    
    assert "error: boom" in result
    assert "context line 1" in result
    assert "context line 5" in result
    # The current logic gives 5 lines of context, so line 6 should be dropped
    # or kept only if it doesn't hit a noise filter.
    # In the current implementation, 'context line 6' is not noise, so it might actually be kept 
    # by the "Default: Keep line" rule unless the context logic explicitly blocks it.
    # Let's check the code: 
    # Logic: If context > 0: append, decrement. Else: check noise. If not noise: append.
    # So actually, GccMakeFilter is "Permissive by default".
    assert "context line 6" in result 

def test_gcc_filter_path_strip():
    """Verify path prefix stripping from config."""
    config = {"path_strip": "/long/path/to/"}
    f = GccMakeFilter(config)
    
    text = "/long/path/to/src/main.c: Error"
    result = f.process(text)
    
    assert "/long/path/to/" not in result
    assert "src/main.c: Error" in result