import pytest
import sys
from pathlib import Path

# Ensure we can import src
REPO_ROOT = Path(__file__).parent.parent.resolve()
# Use src directly if package resolution fails or add root
sys.path.insert(0, str(REPO_ROOT))

from src.filters import load_plugins, REGISTRY

def test_cascade_loading(tmp_path):
    """
    Verifies that load_plugins() correctly picks up a custom filter
    from a project's .ddd/filters directory.
    """
    # 1. Setup a Mock Project
    project_root = tmp_path / "my_project"
    ddd_filters = project_root / ".ddd" / "filters"
    ddd_filters.mkdir(parents=True)

    # 2. Create a Dummy Plugin
    # This plugin registers itself as 'test_plugin'
    plugin_content = """
from src.filters import register_filter
from src.filters.base import BaseFilter

@register_filter("test_plugin")
class TestFilter(BaseFilter):
    def process(self, text):
        return "PLUGIN_ACTIVE: " + text
"""
    (ddd_filters / "custom.py").write_text(plugin_content)

    # 3. Load Plugins pointing to our mock project
    # Note: REGISTRY is global, so this adds to existing built-ins
    load_plugins(project_root=str(project_root))

    # 4. Verify
    assert "test_plugin" in REGISTRY, "Custom plugin was not loaded into REGISTRY"
    
    # 5. Test Execution
    PluginClass = REGISTRY["test_plugin"]
    plugin = PluginClass()
    assert plugin.process("hello") == "PLUGIN_ACTIVE: hello"