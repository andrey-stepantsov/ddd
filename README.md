# DDD - "Dead Drop Daemon"

## DDD: The Triple-Head Development Architecture

DDD is a physical-to-virtual bridge that allows modern AI agents and host tools to control a persistent, isolated build container.

### The Architecture

The system runs as three distinct "Heads" in three terminals:

1.  **The Builder (`*-dev` container)**
    * **Role:** Passive persistence.
    * **Job:** Holds the compiler state, object files, and dependencies. Never exits.
    * **Mechanism:** Docker container running `sleep infinity`.

2.  **The Watcher (`dd-daemon`)**
    * **Role:** The Nervous System.
    * **Job:** Watches for the specific signal (`.build_request`), triggers the build inside the container, and runs verification.
    * **Mechanism:** Python script on Host using `watchdog`.

3.  **The Coder (AI Agent / You)**
    * **Role:** The Brain.
    * **Job:** Edits source code and signals when ready.
    * **Mechanism:** Aider (inside a container) or Neovim (on host).

### The Protocol (Explicit Mode)

To prevent infinite loops and broken builds, the Daemon **ignores all file changes** except one.

1.  **Edit:** Modify as many files as needed.
2.  **Signal:** Run `touch .build_request`.
3.  **React:** Daemon sees signal -> Runs Build -> Runs Verify.

### Setup

1.  **Install:** `./install.sh` (Puts tools in `~/.local/bin`)
2.  **Configure:** Create `.dd-config` in your project root:
    ```json
    {
      "build_cmd": "docker exec -t nethack-dev make -j4",
      "verify_cmd": "docker exec -t nethack-dev /mission/bin/dd-verify",
      "watch_dir": "."
    }
    ```
3.  **Run:** `dd-daemon`

