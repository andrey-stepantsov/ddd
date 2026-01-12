#!/usr/bin/env python3
import json
import os
import subprocess
import time
import sys
import stat
import shutil
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Patch: Force Unbuffered Output ---
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# --- Namespace Resolution ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TOOL_ROOT = os.path.dirname(CURRENT_DIR)

if TOOL_ROOT not in sys.path:
    sys.path.insert(0, TOOL_ROOT)

from src.filters import load_plugins, REGISTRY

# --- Constants ---
DDD_DIR = ".ddd"
RUN_DIR = os.path.join(DDD_DIR, "run")
CONFIG_FILE = os.path.join(DDD_DIR, "config.json")
TRIGGER_FILE = os.path.join(RUN_DIR, "build.request")
LOG_FILE = os.path.join(RUN_DIR, "build.log")
RAW_LOG_FILE = os.path.join(RUN_DIR, "last_build.raw.log")
LOCK_FILE = os.path.join(RUN_DIR, "ipc.lock")

# Client Injection
INJECTED_CLIENT = os.path.join(DDD_DIR, "wait")
MASTER_CLIENT_PATH = os.path.abspath(os.path.join(TOOL_ROOT, "bin", "ddd-wait"))

class RequestHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_run = 0
        self.cooldown = 1.0
        self.inject_client()

    def inject_client(self):
        if not os.path.exists(MASTER_CLIENT_PATH):
            print(f"[!] Warning: Master client not found at {MASTER_CLIENT_PATH}")
            return
        try:
            with open(MASTER_CLIENT_PATH, 'r') as f_src:
                content = f_src.read()
            with open(INJECTED_CLIENT, "w") as f_dst:
                f_dst.write(content)
            st = os.stat(INJECTED_CLIENT)
            os.chmod(INJECTED_CLIENT, st.st_mode | stat.S_IEXEC)
        except Exception as e:
            print(f"[!] Failed to inject client: {e}")

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
        print(f"\n[>>>] Signal received: {TRIGGER_FILE}")
        
        with open(LOCK_FILE, 'w') as f:
            f.write(str(time.time()))

        try:
            self._execute_logic()
        finally:
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)

    def _execute_logic(self):
        start_time = time.time()
        load_plugins(project_root=os.getcwd())
        
        config = self.load_config()
        if not config: return

        target_name = "dev"
        target = config.get("targets", {}).get(target_name)
        if not target:
            print(f"[-] Target '{target_name}' not found.")
            return

        total_raw_bytes = 0
        total_clean_bytes = 0

        with open(LOG_FILE, "w") as f_clean, open(RAW_LOG_FILE, "w") as f_raw:
            header = f"=== Pipeline: {target_name} ({time.ctime()}) ===\n"
            f_clean.write(header)
            f_raw.write(header)
            
            # STAGE 1: BUILD
            build_cfg = target.get("build", {})
            success, raw_len, clean_len = self._run_stage("BUILD", build_cfg, f_clean, f_raw)
            total_raw_bytes += raw_len
            total_clean_bytes += clean_len
            
            if not success:
                self._write_stats(f_clean, start_time, total_raw_bytes, total_clean_bytes)
                return 

            # STAGE 2: VERIFY
            verify_cfg = target.get("verify", {})
            if "cmd" in verify_cfg:
                _, raw_len, clean_len = self._run_stage("VERIFY", verify_cfg, f_clean, f_raw)
                total_raw_bytes += raw_len
                total_clean_bytes += clean_len

            self._write_stats(f_clean, start_time, total_raw_bytes, total_clean_bytes)

        print(f"[*] Pipeline Complete.")

    def _write_stats(self, f_handle, start_time, raw_bytes, clean_bytes):
        duration = time.time() - start_time
        tokens = int(clean_bytes / 4)
        if raw_bytes > 0:
            reduction = (1 - (clean_bytes / raw_bytes)) * 100
        else:
            reduction = 0.0

        stats = (
            f"\n--- 📊 Build Stats ---\n"
            f"⏱  Duration: {duration:.2f}s\n"
            f"📉 Noise Reduction: {reduction:.1f}% ({raw_bytes} raw → {clean_bytes} clean bytes)\n"
            f"🪙  Est. Tokens: {tokens}\n"
        )
        f_handle.write(stats)

    def _run_stage(self, name, stage_config, f_clean, f_raw):
        cmd = stage_config.get("cmd")
        if not cmd: return (True, 0, 0)

        print(f"[+] Running {name}: {cmd}")
        f_raw.write(f"\n--- {name} RAW OUTPUT ---\n")
        
        filter_entry = stage_config.get("filter", "raw")
        if isinstance(filter_entry, str):
            filter_names = [filter_entry]
        else:
            filter_names = filter_entry

        process = subprocess.Popen(
            cmd, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True
        )
        
        raw_output_buffer = []
        raw_bytes = 0
        
        for line in process.stdout:
            print(line, end='')
            f_raw.write(line)
            raw_output_buffer.append(line)
            raw_bytes += len(line)
        
        process.wait()

        current_text = "".join(raw_output_buffer)
        for fname in filter_names:
            FilterClass = REGISTRY.get(fname)
            if not FilterClass:
                print(f"[!] Warning: Filter '{fname}' not found. Skipping.")
                continue
            processor = FilterClass(stage_config)
            current_text = processor.process(current_text)

        clean_bytes = len(current_text)
        f_clean.write(f"\n--- {name} OUTPUT ---\n")
        f_clean.write(current_text)

        if process.returncode != 0:
            print(f"[-] {name} Failed.")
            return (False, raw_bytes, clean_bytes)
            
        return (True, raw_bytes, clean_bytes)

    def on_modified(self, event):
        if os.path.basename(event.src_path) == "build.request":
            self.run_pipeline()
            
    def on_created(self, event):
        if os.path.basename(event.src_path) == "build.request":
            self.run_pipeline()

if __name__ == "__main__":
    # --- 1. Argument Parsing ---
    parser = argparse.ArgumentParser(description="DDD: Distributed Developer Daemon")
    parser.add_argument("--version", action="version", version="%(prog)s 0.6.1")
    # --help is added automatically by argparse
    args = parser.parse_args()

    # --- 2. Main Execution ---
    if not os.path.exists(DDD_DIR):
        os.makedirs(DDD_DIR)
    
    if os.path.exists(RUN_DIR):
        shutil.rmtree(RUN_DIR)
    os.makedirs(RUN_DIR)
    
    print(f"[*] dd-daemon ACTIVE.")
    print(f"[*] Watching: {RUN_DIR}/build.request")
    
    event_handler = RequestHandler()
    observer = Observer()
    observer.schedule(event_handler, path=RUN_DIR, recursive=False)
    observer.start()

    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
