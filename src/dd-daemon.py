#!/usr/bin/env python3
import json
import os
import subprocess
import time
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Patch: Force Unbuffered Output ---
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from filters import load_plugins, REGISTRY

# --- Constants ---
DDD_DIR = ".ddd"
CONFIG_FILE = os.path.join(DDD_DIR, "config.json")
TRIGGER_FILENAME = "build.request"
LOG_FILE = os.path.join(DDD_DIR, "build.log")
RAW_LOG_FILE = os.path.join(DDD_DIR, "last_build.raw.log")
LOCK_FILE = os.path.join(DDD_DIR, "run.lock")

class RequestHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_run = 0
        self.cooldown = 1.0
        load_plugins()
        print(f"[*] Loaded filters: {list(REGISTRY.keys())}")

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
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

        print(f"\n[>>>] Signal received: {TRIGGER_FILENAME}")
        
        # 1. SET BUSY SIGNAL
        with open(LOCK_FILE, 'w') as f:
            f.write(str(time.time()))

        try:
            self._execute_logic()
        finally:
            # 2. CLEAR BUSY SIGNAL
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)

    def _execute_logic(self):
        config = self.load_config()
        if not config: return

        target_name = "dev"
        target = config.get("targets", {}).get(target_name)
        if not target:
            print(f"[-] Target '{target_name}' not found.")
            return

        with open(LOG_FILE, "w") as f_clean, open(RAW_LOG_FILE, "w") as f_raw:
            header = f"=== Pipeline: {target_name} ({time.ctime()}) ===\n"
            f_clean.write(header)
            f_raw.write(header)
            
            # --- STAGE 1: BUILD ---
            build_cfg = target.get("build", {})
            if self._run_stage("BUILD", build_cfg, f_clean, f_raw) == False:
                return 

            # --- STAGE 2: VERIFY ---
            verify_cfg = target.get("verify", {})
            if "cmd" in verify_cfg:
                self._run_stage("VERIFY", verify_cfg, f_clean, f_raw)

        print(f"[*] Pipeline Complete.")

    def _run_stage(self, name, stage_config, f_clean, f_raw):
        cmd = stage_config.get("cmd")
        if not cmd: return True 

        print(f"[+] Running {name}: {cmd}")
        f_raw.write(f"\n--- {name} RAW OUTPUT ---\n")
        
        filter_name = stage_config.get("filter", "raw")
        FilterClass = REGISTRY.get(filter_name, REGISTRY["raw"])
        processor = FilterClass(stage_config)

        process = subprocess.Popen(
            cmd, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True
        )
        
        raw_output_buffer = []
        for line in process.stdout:
            print(line, end='')
            f_raw.write(line)
            raw_output_buffer.append(line)
        
        process.wait()

        clean_text = processor.process("".join(raw_output_buffer))
        f_clean.write(f"\n--- {name} OUTPUT ---\n")
        f_clean.write(clean_text)

        if process.returncode != 0:
            print(f"[-] {name} Failed.")
            return False
        return True

    def on_modified(self, event):
        if os.path.basename(event.src_path) == TRIGGER_FILENAME:
            self.run_pipeline()
            
    def on_created(self, event):
        if os.path.basename(event.src_path) == TRIGGER_FILENAME:
            self.run_pipeline()

if __name__ == "__main__":
    if not os.path.exists(DDD_DIR):
        os.makedirs(DDD_DIR)
        
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

    print(f"[*] dd-daemon ACTIVE.")
    print(f"[*] Watching: {DDD_DIR}/")
    
    event_handler = RequestHandler()
    observer = Observer()
    observer.schedule(event_handler, path=DDD_DIR, recursive=False)
    observer.start()

    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
