# DDD - "Dead Drop Daemon"

**Repository:** [github.com/andrey-stepantsov/ddd](https://github.com/andrey-stepantsov/ddd)

## DDD: The Triple-Head Development Architecture

DDD is a physical-to-virtual bridge that allows modern AI agents and host tools to control a persistent, isolated build container.

### 1. The Architecture

The system runs as three distinct "Heads":

* **The Builder (Container):** Holds the compiler state, object files, and dependencies. Never exits.
* **The Watcher (Host Daemon):** Watches for signals, triggers builds, filters logs, and runs verification.
* **The Coder (AI/You):** Edits source code and signals when ready.

### 2. The Clean Structure

DDD uses a dedicated hidden directory to avoid polluting your source tree.

    YourProject/
    ├── src/
    └── .ddd/                <-- Isolated DDD Context
        ├── config.json      <-- Target definitions
        ├── filters/         <-- Project-specific Plugins
        ├── build.request    <-- The Trigger (touch this)
        ├── build.log        <-- AI Log (Filtered, clean)
        └── last_build.raw.log <-- Human Log (Raw, full detail)

### 3. The Protocol (How to use)

To prevent infinite loops and broken builds, the Daemon **ignores all file changes** except one.

1.  **Edit:** Modify as many files as needed.
2.  **Signal:** Run `touch .ddd/build.request`.
3.  **React:** Daemon sees signal -> Runs Build -> Runs Verify.
4.  **Feedback:** Read `.ddd/build.log` to check for errors and iterate.

### 4. Configuration

Create `.ddd/config.json` in your project root to define your targets.

```json
{
  "targets": {
    "dev": {
      "build": {
        "cmd": "make -j4",
        "filter": ["gcc_make", "gcc_json"],
        "path_strip": ""
      },
      "verify": {
        "cmd": ".ddd/scripts/verify.sh",
        "filter": "raw"
      }
    }
  }
}
```

### 5. Advanced Features

#### Filter Chaining
You can pipe the output of one filter into another by providing a list of strings in `config.json`.
* **Example:** `["gcc_make", "gcc_json"]`
* **Flow:** `Raw Output` -> `gcc_make` (Cleans noise) -> `gcc_json` (Formats to JSON) -> `build.log`.

#### Structured Logging (JSON)
The `gcc_json` filter parses standard GCC/Clang error messages into machine-readable JSON. This allows AI agents to ingest errors programmatically rather than guessing from text blobs.

**Output Format:**
```json
[
  {
    "file": "main.c",
    "line": 10,
    "col": 5,
    "type": "error",
    "message": "expected ';'"
  }
]
```

### 6. Setup

1.  **Install:** `./install.sh`
2.  **Run:** `dd-daemon` inside your project root.

### 7. Custom Plugins

DDD supports a "Cascade" loading system for build parsers.
* **Project Local:** `.ddd/filters/*.py`
* **User Global:** `~/.config/ddd/filters/*.py`
* **Built-in:** `src/filters/*.py`

**How to write a plugin:**
Create `.ddd/filters/my_tool.py`:

```python
from src.filters import register_filter
from src.filters.base import BaseFilter

@register_filter("my_tool")
class MyToolFilter(BaseFilter):
    def process(self, text: str) -> str:
        return "Parsed: " + text
```

**Testing Plugins:**
Run the test runner to verify your custom filters:
    
    ddd-test