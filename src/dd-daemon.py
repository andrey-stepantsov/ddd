#!/usr/bin/env python3
import json
import os
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CONFIG_FILE = ".dd-config"
TRIGGER_FILE = ".build_request"

class RequestHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_run = 0
        self.cooldown = 2.0  # longer cooldown to prevent double-taps

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            print(f"[!] {CONFIG_FILE} not found")
            return None
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Error reading config: {e}")
            return None

    def run_pipeline(self):
        # Debounce
        if time.time() - self.last_run < self.cooldown:
            return
        self.last_run = time.time()

        print(f"\n[>>>] Signal received: {TRIGGER_FILE}")
        
        config = self.load_config()
        if not config: return

        build_cmd = config.get('build_cmd')
        if not build_cmd: return

        print(f"[+] Executing Build: {build_cmd}")
        build_res = subprocess.run(build_cmd, shell=True)
        
        if build_res.returncode != 0:
            print("[-] Build Failed.")
            return

        verify_cmd = config.get('verify_cmd')
        if verify_cmd:
            print(f"[+] Verifying: {verify_cmd}")
            subprocess.run(verify_cmd, shell=True)
        else:
            print("[.] No 'verify_cmd' defined.")

    def on_modified(self, event):
        # STRICT PROTOCOL: Only react to the trigger file
        if os.path.basename(event.src_path) == TRIGGER_FILE:
            self.run_pipeline()
            
    def on_created(self, event):
        # Handle case where file is created for the first time
        if os.path.basename(event.src_path) == TRIGGER_FILE:
            self.run_pipeline()

if __name__ == "__main__":
    if not os.path.exists(CONFIG_FILE):
        print(f"WARNING: No {CONFIG_FILE} found.")
        
    print(f"[*] dd-daemon ACTIVE (Explicit Mode).")
    print(f"[*] Waiting for signal: 'touch {TRIGGER_FILE}'")
    
    event_handler = RequestHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False) # Non-recursive is safer/faster
    observer.start()

    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[*] Daemon stopping.")
    observer.join()
