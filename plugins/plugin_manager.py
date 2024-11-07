import importlib
import os
from typing import Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)

class PluginManager:
    def __init__(self, plugin_dir: str = 'plugins'):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Any] = {}
        self.load_plugins()

    def load_plugins(self):
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                plugin_name = filename[:-3]  # Remove .py extension
                try:
                    module = importlib.import_module(f'{self.plugin_dir}.{plugin_name}')
                    if hasattr(module, 'register_plugin'):
                        plugin = module.register_plugin()
                        self.plugins[plugin_name] = plugin
                        logger.info(f"Loaded plugin: {plugin_name}")
                    # Remove the else clause that was logging the warning
                except Exception as e:
                    logger.error(f"Error loading plugin {plugin_name}: {str(e)}")

    def get_plugin(self, name: str):
        return self.plugins.get(name)

    def execute_plugin(self, name: str, *args, **kwargs):
        plugin = self.get_plugin(name)
        if plugin:
            try:
                return plugin.execute(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error executing plugin {name}: {str(e)}")
                return None
        else:
            logger.warning(f"Plugin {name} not found")
            return None

    def list_plugins(self):
        return list(self.plugins.keys())