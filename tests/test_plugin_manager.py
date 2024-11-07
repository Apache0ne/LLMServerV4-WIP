import pytest
from plugins.plugin_manager import PluginManager

@pytest.fixture
def plugin_manager(tmp_path):
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    (plugin_dir / "test_plugin.py").write_text("""
class TestPlugin:
    def execute(self, *args, **kwargs):
        return {"status": "success", "args": args, "kwargs": kwargs}

def register_plugin():
    return TestPlugin()
    """)
    return PluginManager(str(plugin_dir))

def test_load_plugins(plugin_manager):
    assert 'test_plugin' in plugin_manager.plugins

def test_get_plugin(plugin_manager):
    plugin = plugin_manager.get_plugin('test_plugin')
    assert plugin is not None

def test_execute_plugin(plugin_manager):
    result = plugin_manager.execute_plugin('test_plugin', 'arg1', kwarg1='value1')
    assert result['status'] == 'success'
    assert result['args'] == ('arg1',)
    assert result['kwargs'] == {'kwarg1': 'value1'}

def test_list_plugins(plugin_manager):
    plugins = plugin_manager.list_plugins()
    assert 'test_plugin' in plugins