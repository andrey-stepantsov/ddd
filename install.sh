#!/bin/bash
set -e
DAEMON_NAME="dd-daemon"
SOURCE_SCRIPT="$(pwd)/src/dd-daemon.py"
INSTALL_DIR="$HOME/.local/bin"
TARGET_LINK="$INSTALL_DIR/$DAEMON_NAME"

if [ ! -d "$INSTALL_DIR" ]; then mkdir -p "$INSTALL_DIR"; fi
chmod +x "$SOURCE_SCRIPT"

if [ -L "$TARGET_LINK" ]; then rm "$TARGET_LINK"; fi
ln -s "$SOURCE_SCRIPT" "$TARGET_LINK"

if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo "WARNING: Add $INSTALL_DIR to your PATH."
else
    echo "Installation complete. Run '$DAEMON_NAME' to start."
fi
