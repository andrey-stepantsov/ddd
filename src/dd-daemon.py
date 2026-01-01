#!/usr/bin/env python3
import json
import os
import subprocess
import time
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CONFIG_FILE = ".dd-config"

class BuildHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_run = 0
        self.cooldown = 1.0  # Debounce: Wait 1s between triggers

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            print(f"[!] {CONFIG_FILE} not found in {os.getcwd()}")
            return None
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Error reading config: {e}")
            return None

    def run_pipeline(self):
        if time.time() - self.last_run < self.cooldown:
            return
        self.last_run = time.time()

        config = self.load_config()
        if not config: return

        build_cmd = config.get('build_cmd')
        if not build_cmd:
            print("[!] No 'build_cmd' defined.")
            return

        print(f"\n[+] Build Triggered: {build_cmd}")
        build_res = subprocess.run(build_cmd, shell=True)
        
        if build_res.returncode != 0:
            print("[-] Build Failed. Skipping verification.")
            return

        verify_cmd = config.get('verify_cmd')
        if verify_cmd:
            print(f"[+] Verifying: {verify_cmd}")
            subprocess.run(verify_cmd, shell=True)
        else:
            print("[.] No 'verify_cmd' defined.")

    def on_modified(self, event):
        if event.is_directory or CONFIG_FILE in event.src_path: return
        if os.path.basename(event.src_path).startswith('.'): return
            
        print(f"[*] Detected change in {event.src_path}")
        self.run_pipeline()

if __name__ == "__main__":
    if not os.path.exists(CONFIG_FILE):
        print(f"Usage: Run this from a project root containing a {CONFIG_FILE}")

    print(f"[*] dd-daemon active. Watching: {os.getcwd()}")
    
    event_handler = BuildHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()

    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[*] Daemon stopping.")
    observer.join()
