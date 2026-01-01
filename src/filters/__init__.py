import pkgutil
import importlib
import os

REGISTRY = {}

def register_filter(name):
    """Decorator to register a filter class."""
    def decorator(cls):
        REGISTRY[name] = cls
        return cls
    return decorator

def load_plugins():
    """Dynamically import all modules in this package."""
    package_dir = os.path.dirname(__file__)
    for _, name, _ in pkgutil.iter_modules([package_dir]):
        importlib.import_module(f".{name}", package=__name__)
