# Parasitic Mode

In this mode, the **Builder** runs on your Host machine (Mac/Linux), not in Docker. 
The AI agent (e.g., Aider) remains in a container but "remote controls" your local shell via the daemon.

## Architecture

1. **The Host:** Runs `dd-daemon`. Watches `.ddd/run/build.request`.
2. **The Host:** Executes build commands directly (using local toolchain: clang/gcc/make).
3. **The Container:** Runs AI agent. Mounts source directory. Triggers builds via `.ddd/wait`. Reads `.ddd/run/build.log`.

## Setup

### 1. Configure Build on Host

Create `.ddd/config.json` in your project root:

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

**Note:** This is the v0.7.0 config format. See `CONFIG_REFERENCE.md` for details.

### 2. Start Daemon on Host

```bash
cd /path/to/your/project
dd-daemon
```

Or run in background:
```bash
dd-daemon --daemon
```

### 3. Launch AI Container

Mount your project directory so the container can access `.ddd/`:

```bash
docker run -it --rm \
  -v $(pwd):/workspace \
  your-ai-image:latest
```

### 4. Trigger Builds from Container

Inside the container, trigger builds using the injected client:

```bash
cd /workspace
./.ddd/wait
```

The daemon (on host) will:
1. Detect the trigger file
2. Run your build command with the host's toolchain
3. Write results to `.ddd/run/build.log`
4. AI agent reads the log

## Advantages

- **No Docker Toolchain:** Use your native compiler (faster, better debugging)
- **IDE Integration:** Build artifacts work with your host IDE
- **Performance:** Native builds avoid Docker overhead
- **Flexibility:** Mix containerized AI with local development tools

## Example Workflow

```bash
# On Host (Terminal 1)
dd-daemon --daemon

# In Container (Terminal 2 - AI Agent)
aider> /run make
# Internally triggers: ./.ddd/wait
# Build runs on host, AI reads output
```

## Migration Note

**Old config format (pre-v0.7.0) is no longer supported:**

```json
{
  "build_cmd": "make -j4",
  "verify_cmd": "./dd-verify",
  "watch_dir": "."
}
```

**New format required:**

```json
{
  "targets": {
    "dev": {
      "build": { "cmd": "make -j4" },
      "verify": { "cmd": "./dd-verify" }
    }
  }
}
```

See `CONFIG_REFERENCE.md` for complete documentation.

## Troubleshooting

### Container can't trigger builds
- Ensure `.ddd/` is in the mounted volume
- Check file permissions (container user must write to `.ddd/run/`)
- Verify daemon is running: `ps aux | grep dd-daemon`

### Build runs but container doesn't see output
- Check that volume mount is read-write (not `:ro`)
- Ensure `.ddd/run/build.log` is readable by container user

### Daemon not picking up triggers
- Check `.ddd/run/` directory exists
- Look for errors in `.ddd/daemon.log`
- Restart daemon: `kill $(cat .ddd/daemon.pid) && dd-daemon --daemon`
