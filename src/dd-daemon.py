#!/usr/bin/env python3
import json
import os
import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CONFIG_FILE = ".dd-config"
TRIGGER_FILE = ".build_request"
LOG_FILE = ".build.log"

class RequestHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_run = 0
        self.cooldown = 2.0  # Debounce to prevent double-taps

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
        verify_cmd = config.get('verify_cmd')
        
        # Open the log file in write mode (overwrites previous run)
        with open(LOG_FILE, "w") as f:
            f.write(f"=== Build Pipeline Started: {time.ctime()} ===\n\n")
            f.flush()

            # 1. Run Build
            if build_cmd:
                print(f"[+] Executing Build: {build_cmd}")
                f.write(f"[+] Executing: {build_cmd}\n")
                f.flush()
                
                # Capture output to file AND print to stdout (optional, but helpful for human)
                build_res = subprocess.run(
                    build_cmd, 
                    shell=True, 
                    stdout=f, 
                    stderr=subprocess.STDOUT
                )

                if build_res.returncode != 0:
                    print("[-] Build Failed. Check .build.log")
                    f.write("\n[-] Build FAILED.\n")
                    return
            
            # 2. Run Verify (only if build succeeds)
            if verify_cmd:
                print(f"[+] Verifying: {verify_cmd}")
                f.write(f"\n[+] Executing: {verify_cmd}\n")
                f.flush()
                
                verify_res = subprocess.run(
                    verify_cmd, 
                    shell=True, 
                    stdout=f, 
                    stderr=subprocess.STDOUT
                )
                
                if verify_res.returncode == 0:
                    print("[+] Verification Passed.")
                else:
                    print("[-] Verification Failed.")
            else:
                f.write("\n[.] No verify_cmd defined.\n")

        print(f"[*] Pipeline Complete. Output saved to {LOG_FILE}")

    def on_modified(self, event):
        if os.path.basename(event.src_path) == TRIGGER_FILE:
            self.run_pipeline()
            
    def on_created(self, event):
        if os.path.basename(event.src_path) == TRIGGER_FILE:
            self.run_pipeline()

if __name__ == "__main__":
    if not os.path.exists(CONFIG_FILE):
        print(f"WARNING: No {CONFIG_FILE} found.")
        
    print(f"[*] dd-daemon ACTIVE (Explicit Mode).")
    print(f"[*] Logging to: {LOG_FILE}")
    print(f"[*] Waiting for signal: 'touch {TRIGGER_FILE}'")
    
    event_handler = RequestHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[*] Daemon stopping.")
    observer.join()
