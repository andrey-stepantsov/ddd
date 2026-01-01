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
        ├── build.request    <-- The Trigger (touch this)
        ├── build.log        <-- The Output (read this)
        └── scripts/         <-- (Optional) Your verify scripts

### 3. The Protocol (How to use)

To prevent infinite loops and broken builds, the Daemon **ignores all file changes** except one.

1.  **Edit:** Modify as many files as needed.
2.  **Signal:** Run `touch .ddd/build.request`.
3.  **React:** Daemon sees signal -> Runs Build -> Runs Verify -> **Writes output to `.ddd/build.log`**.
4.  **Feedback:** Read `.ddd/build.log` to check for errors and iterate.

### 4. Configuration

Create `.ddd/config.json` in your project root to define your targets.

    {
      "targets": {
        "dev": {
          "build": {
            "cmd": "make -j4",
            "filter": "gcc_make",
            "path_strip": ""
          },
          "verify": {
            "cmd": ".ddd/scripts/verify.sh",
            "filter": "raw"
          }
        }
      }
    }

### 5. Setup

1.  **Install:** `./install.sh`
2.  **Run:** `dd-daemon` inside your project root.
