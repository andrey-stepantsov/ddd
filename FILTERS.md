# Filter Reference

Filters transform build output to reduce noise and improve readability for AI agents and humans.

## What Are Filters?

Filters process the raw output from your build commands:
- **Input:** Raw stdout/stderr from `make`, `gcc`, etc.
- **Output:** Cleaned, structured text written to `.ddd/run/build.log`
- **Raw preserved:** Original output always saved to `.ddd/run/last_build.raw.log`

## Built-in Filters

### `raw`
**Description:** Pass-through filter (no processing).

**Use when:**
- You want the complete, unmodified output
- Debugging filter issues
- Your build output is already clean

**Example:**
```json
{
  "build": {
    "cmd": "pytest tests/ -v",
    "filter": "raw"
  }
}
```

---

### `gcc_make`
**Description:** Parses GNU Make output to reduce noise.

**What it does:**
- Strips make progress indicators (`[1/10]`, `[2/10]`, etc.)
- Removes verbose directory change messages
- Preserves actual compilation commands and errors
- Reduces token count by ~30-50%

**Use when:**
- Building with `make`
- You want cleaner output but don't need structured errors

**Example:**
```json
{
  "build": {
    "cmd": "make -j4",
    "filter": "gcc_make"
  }
}
```

---

### `gcc_json`
**Description:** Produces structured, machine-readable error output.

**What it does:**
- Extracts compiler errors/warnings into JSON format
- Provides file, line, column, severity, and message
- Ideal for AI agents to parse and understand errors
- Detects empty output (no errors extracted) and injects synthetic error

**Use when:**
- You need programmatic error parsing
- AI agents need to understand compilation failures
- You want structured diagnostics

**Example:**
```json
{
  "build": {
    "cmd": "gcc -Wall -Werror src/main.c",
    "filter": "gcc_json"
  }
}
```

**Output format:**
```json
{
  "diagnostics": [
    {
      "file": "src/main.c",
      "line": 42,
      "column": 5,
      "severity": "error",
      "message": "undeclared identifier 'foo'"
    }
  ]
}
```

**Safety feature:** If build fails but no errors are extracted, `gcc_json` injects:
```json
{
  "diagnostics": [
    {
      "severity": "error",
      "message": "Build failed but no structured errors were detected. Check raw log."
    }
  ]
}
```

---

### `crash_detector`
**Description:** Detects segmentation faults and signal crashes.

**What it does:**
- Identifies segfaults (SIGSEGV)
- Detects other crash signals (SIGABRT, SIGBUS, etc.)
- Highlights crash messages for visibility
- Useful for test suites

**Use when:**
- Running native code tests
- You need to catch crashes in verify stage
- Debugging segfaults

**Example:**
```json
{
  "verify": {
    "cmd": "./tests/run_all",
    "filter": "crash_detector"
  }
}
```

---

### `base`
**Description:** Abstract base class for custom filters.

**Use when:**
- Creating your own filters (see "Creating Custom Filters" below)

**Not used directly in config.**

---

## Filter Chaining

Apply multiple filters in sequence by providing an array:

```json
{
  "build": {
    "cmd": "make -j8",
    "filter": ["gcc_make", "gcc_json"]
  }
}
```

**Execution order:** Left to right
1. Raw output → `gcc_make` (cleans make noise)
2. `gcc_make` output → `gcc_json` (extracts structured errors)
3. Final result → `.ddd/run/build.log`

**Common chains:**

| Chain | Use Case |
|-------|----------|
| `["gcc_make", "gcc_json"]` | Clean make output + structured errors |
| `["raw"]` | No processing (debugging) |
| `["crash_detector"]` | Test output with crash detection |

---

## Creating Custom Filters

### Quick Start

1. Create `.ddd/filters/my_filter.py`:

```python
from src.filters import register_filter
from src.filters.base import BaseFilter

@register_filter("my_filter")
class MyFilter(BaseFilter):
    def process(self, text):
        """
        Transform the input text.
        
        Args:
            text (str): Input text to process
            
        Returns:
            str: Transformed text
        """
        # Example: Remove lines containing "DEBUG"
        lines = text.splitlines()
        filtered = [line for line in lines if "DEBUG" not in line]
        return "\n".join(filtered) + "\n"
```

2. Use in your config:

```json
{
  "build": {
    "cmd": "make",
    "filter": "my_filter"
  }
}
```

3. Test your filter:

Create `.ddd/filters/test_my_filter.py`:

```python
from my_filter import MyFilter

def test_removes_debug_lines():
    f = MyFilter({})
    input_text = "INFO: Starting\nDEBUG: Details\nERROR: Failed\n"
    output = f.process(input_text)
    assert "DEBUG" not in output
    assert "INFO" in output
    assert "ERROR" in output
```

Run tests:
```bash
ddd-test
```

### Advanced: Access Config

Filters receive the stage config (from `config.json`):

```python
@register_filter("configurable_filter")
class ConfigurableFilter(BaseFilter):
    def process(self, text):
        # Access stage config
        stage_config = self.config
        
        # Example: Get custom threshold
        threshold = stage_config.get("threshold", 10)
        
        # Use config in processing
        lines = text.splitlines()
        return "\n".join(lines[:threshold])
```

Use in config:
```json
{
  "build": {
    "cmd": "make",
    "filter": "configurable_filter",
    "threshold": 20
  }
}
```

### Filter Best Practices

1. **Always return a string** (even if empty: `""`)
2. **Preserve newlines** for readability
3. **Don't crash** - wrap risky operations in try/except
4. **Test your filters** - create `test_*.py` files
5. **Keep them fast** - they run on every build

### Filter Loading Order

DDD loads filters from multiple locations (cascade):

1. **Built-in filters** (src/filters/) - Always available
2. **Project filters** (.ddd/filters/) - Project-specific

Later filters override earlier ones with the same name.

---

## Troubleshooting

### "Filter 'xyz' not found"

**Causes:**
- Typo in filter name (names are case-sensitive)
- Filter file starts with `_` (ignored by loader)
- Filter file has syntax errors

**Solutions:**
1. Check spelling in config.json
2. Check daemon logs: `cat .ddd/daemon.log`
3. Test filter import: `python -c "from my_filter import MyFilter"`

### Filter produces empty output

**Causes:**
- Filter is too aggressive (removes everything)
- Filter crashed but exception was caught

**Solutions:**
1. Check `.ddd/run/last_build.raw.log` to see original output
2. Add debug prints to your filter (shows in daemon output)
3. Test filter standalone:
   ```python
   f = MyFilter({})
   print(f.process("test input"))
   ```

### Filter not being used

**Causes:**
- Config not reloaded (daemon caches it per-run)
- Filter not in `.ddd/filters/` or has wrong name

**Solutions:**
1. Trigger a new build (each build reloads plugins)
2. Verify filter location: `ls .ddd/filters/`
3. Check filter is registered:
   ```python
   from src.filters import REGISTRY
   print(REGISTRY.keys())
   ```

---

## See Also

- `CONFIG_REFERENCE.md` - How to configure filters in config.json
- `CONTRIBUTING.md` - Plugin development guide
- `README.md` - Basic usage and installation
