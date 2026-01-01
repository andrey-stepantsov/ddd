# Parasitic Mode

In this mode, the **Builder** runs on your Host machine (Mac/Linux), not in Docker. 
Aider remains in a container but "remote controls" your local shell via the daemon.

## Architecture

1. **The Host:** Runs `dd-daemon`. Watches files.
2. **The Host:** Executes `make` directly (using local clang/gcc).
3. **The Container:** Runs Aider. Mounts source. Reads `.build.log`.

## Setup

1. Create a `.dd-config` that uses local commands:
   ```json
   {
     "build_cmd": "make -j4",
     "verify_cmd": "./dd-verify",
     "watch_dir": "."
   }
   ```

2. Run `dd-daemon` on the host.

3. Launch Aider (Standard Docker command):
   ```bash
   docker run -it --rm -v $(pwd):/src ... aider-vertex ...
   ```
