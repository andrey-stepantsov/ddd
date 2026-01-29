# Hello World Example

The simplest possible DDD setup with a C program.

## What's Included

- `hello.c` - Simple C program that prints a greeting
- `Makefile` - Basic build script
- `.ddd/config.json` - DDD configuration (single build stage, raw filter)
- `.gitignore` - Proper git ignore rules

## Quick Start

```bash
cd examples/hello-world

# Start the daemon
dd-daemon &

# Trigger a build
./.ddd/wait

# Run the program
./hello
```

## What's Happening

1. **Daemon watches** `.ddd/run/build.request`
2. **Client (`.ddd/wait`)** touches that file to trigger a build
3. **Daemon runs** `make` (compiles hello.c)
4. **Output written** to `.ddd/run/build.log`
5. **You see** the filtered results

## Expected Output

### Terminal 1 (Daemon)
```
[*] dd-daemon ACTIVE (v0.7.0).
[*] Watching: /path/to/hello-world/.ddd/run/build.request

[>>>] Signal received: .ddd/run/build.request
[+] Running BUILD: make
🔨 Compiling hello.c...
✅ Build successful! Run './hello' to test.
[*] Pipeline Complete.
```

### Terminal 2 (Client)
```
[ddd] Build triggered. Waiting for Daemon (Timeout: 60s)...
---------------------------------------------------
=== Pipeline: dev (Wed Jan 28 10:30:00 2026) ===

--- BUILD OUTPUT ---
🔨 Compiling hello.c...
✅ Build successful! Run './hello' to test.

--- 📊 Build Stats ---
⏱  Duration: 0.12s
📉 Noise Reduction: 0.0% (89 raw → 89 clean bytes)
🪙  Est. Tokens: 22
---------------------------------------------------
```

### Running the Program
```bash
$ ./hello
========================================
  Hello from DDD!
========================================

✓ Build system: Working!
✓ DDD Protocol: Successful!
✓ Your first DDD build completed!

Next steps:
  1. Try modifying this file
  2. Run './.ddd/wait' again
  3. See the rebuild happen automatically
```

## Try It Yourself

### Experiment 1: Modify the Code

Edit `hello.c` and change the greeting. Then:

```bash
./.ddd/wait
./hello
```

The daemon rebuilds automatically!

### Experiment 2: Add a Filter

Edit `.ddd/config.json`:

```json
{
  "targets": {
    "dev": {
      "build": {
        "cmd": "make",
        "filter": "gcc_make"
      }
    }
  }
}
```

Now the output will be cleaner (build noise removed).

### Experiment 3: Add an Error

Break the code:

```c
int main() {
    printf("Missing semicolon here")  // <-- No semicolon!
    return 0;
}
```

Trigger a build and see how DDD shows errors:

```bash
./.ddd/wait
cat .ddd/run/build.log  # See the error
```

## Understanding the Configuration

**`.ddd/config.json` breakdown:**

```json
{
  "targets": {           // All build configurations
    "dev": {             // Target name (currently must be "dev")
      "build": {         // Build stage (required)
        "cmd": "make",   // Shell command to run
        "filter": "raw"  // Output filter (raw = no filtering)
      }
    }
  }
}
```

**Available filters:**
- `raw` - No filtering (everything shown)
- `gcc_make` - Remove make noise
- `gcc_json` - Structured error output (JSON)
- See [FILTERS.md](../../FILTERS.md) for details

## Files Generated

After running a build, check `.ddd/run/`:

```bash
ls -la .ddd/run/

# You'll see:
# - build.request      (trigger file, created by client)
# - build.log          (filtered output, created by daemon)
# - build.exit         (exit code: 0=success, 1=failure)
# - job_result.json    (rich metrics: duration, compression, etc.)
# - last_build.raw.log (unfiltered original output)
```

## Stop the Daemon

```bash
# Find the daemon process
ps aux | grep dd-daemon

# Kill it
kill $(cat .ddd/daemon.pid)

# Or use Ctrl+C if running in foreground
```

## Next Steps

Once you're comfortable with this example:

1. **Try your own project**: Copy `.ddd/config.json` to your project root
2. **Customize the command**: Change `"cmd": "make"` to your build command
3. **Explore filters**: Try `gcc_json` for better error parsing
4. **Read the docs**:
   - [CONFIG_REFERENCE.md](../../CONFIG_REFERENCE.md) - Full config guide
   - [FILTERS.md](../../FILTERS.md) - Filter reference
   - [README.md](../../README.md) - Complete documentation

## Troubleshooting

### "dd-daemon: command not found"
Add `~/.local/bin` to your PATH (see main README.md)

### "No such file or directory: .ddd/wait"
The daemon creates this file on startup. Make sure daemon is running first.

### Build doesn't trigger
- Check daemon is running: `ps aux | grep dd-daemon`
- Check daemon logs: `cat .ddd/daemon.log`
- Manually trigger: `touch .ddd/run/build.request`

### "gcc: command not found"
Install gcc/clang:
- macOS: `xcode-select --install`
- Ubuntu: `sudo apt install build-essential`
