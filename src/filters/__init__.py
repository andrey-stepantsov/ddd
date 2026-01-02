import pkgutil
import importlib
import importlib.util
import os
import sys
from pathlib import Path

REGISTRY = {}

def register_filter(name):
    """Decorator to register a filter class."""
    def decorator(cls):
        REGISTRY[name] = cls
        return cls
    return decorator

def _load_from_directory(directory):
    """Imports all .py files in the given directory (Standalone Mode)."""
    path = Path(directory)
    if not path.exists():
        return

    # Add to sys.path so the plugin can import generic things if needed
    sys.path.insert(0, str(path))
    
    try:
        for file_path in path.glob("*.py"):
            # Skip __init__.py and hidden files
            if file_path.name.startswith("_"):
                continue

            module_name = file_path.stem
            
            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
            except Exception as e:
                print(f"[!] Failed to load plugin {file_path}: {e}")
    finally:
        # Clean up sys.path to prevent pollution
        if str(path) in sys.path:
            sys.path.remove(str(path))

def load_plugins(project_root=None):
    """
    Loads plugins in the 'Cascade' order.
    """
    # 1. Built-in (Package Mode)
    # MUST use pkgutil/import_module to support relative imports in built-ins
    package_dir = os.path.dirname(__file__)
    for _, name, _ in pkgutil.iter_modules([package_dir]):
        if name.startswith("_"): continue
        try:
            importlib.import_module(f".{name}", package=__name__)
        except Exception as e:
            print(f"[!] Failed to load built-in {name}: {e}")

    # 2. User Global (File Mode)
    user_global_dir = Path.home() / ".config" / "ddd" / "filters"
    _load_from_directory(user_global_dir)

    # 3. Project Local (File Mode)
    if project_root:
        local_dir = Path(project_root) / ".ddd" / "filters"
        _load_from_directory(local_dir)