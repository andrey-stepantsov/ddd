# DDD Examples

Learn by doing! Each example is fully runnable and demonstrates different DDD features.

## 🚀 Quick Start

Pick an example, run these commands:

```bash
cd examples/<example-name>
dd-daemon &             # Start daemon
./.ddd/wait            # Trigger build
```

That's it! The build runs and you see the results.

## 📚 Available Examples

### 1. [hello-world/](hello-world/) - **Start Here**

Minimal C program with DDD. Perfect for first-time users.

**What you'll learn:**
- Basic DDD setup
- Configuration structure
- Build workflow
- Reading outputs

**Time:** 5 minutes  
**Complexity:** ⭐ Beginner  
**Prerequisites:** gcc/clang

---

### 2. python-pytest/ - Coming Soon

Python project with pytest testing.

**What you'll learn:**
- Non-compilation workflows
- Testing with DDD
- Python project structure

**Status:** Planned for v0.8.0

---

### 3. multi-stage/ - Coming Soon

Complex build with build + verify stages and filter chaining.

**What you'll learn:**
- Multi-stage pipelines
- Filter chaining
- Verify stage usage
- Advanced configuration

**Status:** Planned for v0.8.0

---

## 🎯 Learning Path

**New to DDD?** Follow this path:

1. **Start:** [hello-world/](hello-world/) - Understand basics
2. **Next:** Read [CONFIG_REFERENCE.md](../CONFIG_REFERENCE.md) - Learn config options
3. **Then:** Read [FILTERS.md](../FILTERS.md) - Understand filtering
4. **Finally:** Try DDD in your own project

## 📖 Understanding the Examples

Each example includes:
- ✅ **README.md** - What it does, how to run it
- ✅ **Source code** - Working code you can build
- ✅ **.ddd/config.json** - DDD configuration
- ✅ **.gitignore** - Proper git ignore rules
- ✅ **Build script** - Makefile, package.json, etc.

## 💡 Common Patterns

### Pattern 1: Simple Build
```json
{
  "targets": {
    "dev": {
      "build": {
        "cmd": "make",
        "filter": "raw"
      }
    }
  }
}
```
**Used in:** hello-world/

### Pattern 2: Build + Test
```json
{
  "targets": {
    "dev": {
      "build": {
        "cmd": "make",
        "filter": "gcc_json"
      },
      "verify": {
        "cmd": "./run_tests.sh",
        "filter": "crash_detector"
      }
    }
  }
}
```
**Used in:** multi-stage/ (coming soon)

### Pattern 3: Filter Chaining
```json
{
  "targets": {
    "dev": {
      "build": {
        "cmd": "make",
        "filter": ["gcc_make", "gcc_json"]
      }
    }
  }
}
```
**Used in:** multi-stage/ (coming soon)

## 🛠 Using Examples in Your Project

Once you understand an example:

1. **Copy the config:**
   ```bash
   mkdir -p .ddd
   cp examples/hello-world/.ddd/config.json .ddd/
   ```

2. **Customize for your build:**
   ```json
   {
     "targets": {
       "dev": {
         "build": {
           "cmd": "your-build-command",
           "filter": "appropriate-filter"
         }
       }
     }
   }
   ```

3. **Test it:**
   ```bash
   dd-daemon &
   ./.ddd/wait
   ```

## 🔍 Testing an Example

Want to verify an example works before diving in?

```bash
# Quick validation
cd examples/hello-world
make                    # Test build works standalone
dd-daemon &            # Start DDD
./.ddd/wait           # Trigger via DDD
./hello               # Run the result
kill %1               # Stop daemon
```

If it works, you're ready to explore!

## 🐛 Troubleshooting Examples

### "dd-daemon: command not found"
Install DDD first:
```bash
cd ../..  # Back to repo root
./install.sh
export PATH="$HOME/.local/bin:$PATH"
```

### "No such file or directory: .ddd/wait"
Start the daemon first - it creates this file automatically.

### Build fails in example
Check prerequisites in the example's README.md. Most need:
- gcc/clang for C examples
- python3 for Python examples
- make for Makefile-based examples

### Daemon won't start
Check logs:
```bash
cat .ddd/daemon.log   # Background mode
# or check terminal output in foreground mode
```

## 📦 Example Dependencies

| Example | Requires | Install |
|---------|----------|---------|
| hello-world | gcc/clang | `xcode-select --install` (macOS)<br>`apt install build-essential` (Ubuntu) |
| python-pytest | python3, pytest | `pip install pytest` |
| multi-stage | gcc/clang, make | Same as hello-world |

## 🚀 Contributing Examples

Have a useful DDD setup? Contribute an example!

**Requirements:**
- Self-contained (works in isolation)
- Well-documented README
- Copy-pasteable to real projects
- Tests a specific feature or workflow

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## 📚 Additional Resources

- **[README.md](../README.md)** - Main documentation
- **[CONFIG_REFERENCE.md](../CONFIG_REFERENCE.md)** - Configuration guide
- **[FILTERS.md](../FILTERS.md)** - Filter reference
- **[QUICKSTART.md](../QUICKSTART.md)** - 10-minute beginner guide (coming soon)
- **[TROUBLESHOOTING.md](../TROUBLESHOOTING.md)** - Common issues (coming soon)

## 💬 Get Help

- **Issues:** https://github.com/andrey-stepantsov/ddd/issues
- **Discussions:** https://github.com/andrey-stepantsov/ddd/discussions

---

**Ready to learn?** Start with [hello-world/](hello-world/)!
