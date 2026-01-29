# Configuration Reference (v0.8.0)

DDD uses `.ddd/config.json` to define build targets and processing pipelines.

## Installation & Setup

Before configuring, install DDD in your project:

```bash
# Bootstrap DDD into your project
cd your-project
curl -sSL https://raw.githubusercontent.com/stepants/ddd/main/bootstrap-ddd.sh | bash -s .
```

This creates:
- `.ddd/config.json` - Build configuration (edit this)
- `.ddd/ddd/` - Vendored DDD source
- `.ddd/bin/` - Wrapper scripts
- `.ddd/Makefile` - DDD make targets
- `.ddd/run/` - Build artifacts (created on first build)

See [INSTALLATION.md](INSTALLATION.md) for detailed installation options.

## Basic Structure

```json
{
  "targets": {
    "<target_name>": {
      "build": { ... },
      "verify": { ... },
      "sentinel_file": "..."
    }
  }
}
```

## Target Names

**Current Behavior (v0.8.0):**
- The daemon always looks for a target named `"dev"` (hardcoded)
- Only one target is active at a time

**Future:** CLI argument support for selecting targets (see ROADMAP.md)

## Stage Configuration

### Build Stage (Required)

The `build` stage defines the primary build command.

```json
"build": {
  "cmd": "make -j4",
  "filter": "gcc_json"
}
```

**Fields:**
- `cmd` (string, required): Shell command to execute
- `filter` (string or array, optional): Filter(s) to process output (default: `"raw"`)

### Verify Stage (Optional)

The `verify` stage runs after a successful build for testing/validation.

```json
"verify": {
  "cmd": "./tests/run.sh",
  "filter": "crash_detector"
}
```

**Fields:**
- `cmd` (string, required): Shell command to execute
- `filter` (string or array, optional): Filter(s) to process output

**Behavior:**
- Only runs if build stage succeeds
- Failure does not trigger verify stage

### Sentinel File (Optional)

Used for background or asynchronous build processes that may exit before completion.

```json
"sentinel_file": "/tmp/build_success.flag"
```

**Behavior:**
1. Daemon deletes the sentinel file at build start (if it exists)
2. If build fails BUT sentinel file appears, build is marked as SUCCESS
3. Use case: Background compiler that forks and exits immediately

## Filter Configuration

### Single Filter

```json
"filter": "gcc_json"
```

### Filter Chaining

Process output through multiple filters in sequence:

```json
"filter": ["gcc_make", "gcc_json"]
```

**Execution order:** Output flows left-to-right through the chain.

**Available filters:** See `FILTERS.md` for complete reference.

## Complete Examples

### Example 1: Basic C/C++ Build

```json
{
  "targets": {
    "dev": {
      "build": {
        "cmd": "make -j4",
        "filter": "gcc_json"
      }
    }
  }
}
```

### Example 2: Build + Test Pipeline

```json
{
  "targets": {
    "dev": {
      "build": {
        "cmd": "cmake --build build --parallel",
        "filter": ["gcc_make", "gcc_json"]
      },
      "verify": {
        "cmd": "./build/run_tests",
        "filter": "crash_detector"
      }
    }
  }
}
```

### Example 3: Python Project with pytest

```json
{
  "targets": {
    "dev": {
      "build": {
        "cmd": "python -m pytest tests/ -v",
        "filter": "raw"
      }
    }
  }
}
```

### Example 4: Background Build with Sentinel

Useful for tools that fork to background (e.g., some Rust/Go builds).

```json
{
  "targets": {
    "dev": {
      "build": {
        "cmd": "cargo build --release",
        "filter": "raw"
      },
      "sentinel_file": "./target/release/myapp"
    }
  }
}
```

### Example 5: Multi-Stage Build (Complex)

```json
{
  "targets": {
    "dev": {
      "build": {
        "cmd": "cd src && make clean && make -j8",
        "filter": ["gcc_make", "gcc_json"]
      },
      "verify": {
        "cmd": "./tests/integration.sh && ./tests/unit.sh",
        "filter": "crash_detector"
      }
    }
  }
}
```

### Example 6: Parasitic Mode (Host Build)

Build on host machine, AI agent in container reads output.

```json
{
  "targets": {
    "dev": {
      "build": {
        "cmd": "make -j4",
        "filter": "gcc_json"
      },
      "verify": {
        "cmd": "./payload/dd-verify"
      }
    }
  }
}
```

## Tips & Best Practices

### Command Composition

You can use shell features in `cmd`:

```json
"cmd": "cd subdir && make || echo 'Build failed'"
```

### Filter Selection

- **Raw output needed:** Use `"filter": "raw"`
- **Make builds:** Use `"gcc_make"` to strip progress noise
- **AI/Machine parsing:** Chain with `"gcc_json"` for structured errors
- **Native code testing:** Add `"crash_detector"` to verify stage

### Performance

- Use `-j` flag with make for parallel builds
- Keep verify commands fast (< 5s) for quick feedback loops

### Debugging

If your build isn't working:
1. Check `.ddd/run/last_build.raw.log` for unfiltered output
2. Verify your command works standalone: `bash -c "your cmd here"`
3. Check daemon logs: `cat .ddd/daemon.log` (if using `--daemon`)

## Migration from Old Formats

**If you have old config format (pre-v0.7.0):**

Old format (REMOVED):
```json
{
  "build_cmd": "make",
  "verify_cmd": "./test",
  "watch_dir": "."
}
```

New format (required):
```json
{
  "targets": {
    "dev": {
      "build": { "cmd": "make" },
      "verify": { "cmd": "./test" }
    }
  }
}
```

## Troubleshooting

### "Target 'dev' not found"
- Ensure your config has `"targets"` → `"dev"` structure
- Check for JSON syntax errors: `python -m json.tool .ddd/config.json`

### "Filter 'xyz' not found"
- Check filter name spelling (case-sensitive)
- See `FILTERS.md` for available filters
- Check `.ddd/daemon.log` for plugin load errors

### Build runs but output is empty
- Check if filter is too aggressive
- Try `"filter": "raw"` to see unfiltered output
- Check `.ddd/run/last_build.raw.log`

## See Also

- `FILTERS.md` - Available filters and custom filter development
- `README.md` - Installation and basic usage
- `CONTRIBUTING.md` - Plugin development guide
