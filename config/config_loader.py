   # config/config_loader.py

import os
import yaml
from typing import Dict, Any

def load_config(config_path: str = 'config/services.yaml') -> Dict[str, Any]:
    """Load the configuration from the YAML file."""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return _replace_env_vars(config)
    except FileNotFoundError:
        print(f"Configuration file not found: {config_path}")
        print("Please make sure the file exists and the path is correct.")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML configuration: {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error loading configuration: {e}")
        return {}

def _replace_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively replace environment variables in the configuration."""
    for key, value in config.items():
        if isinstance(value, dict):
            config[key] = _replace_env_vars(value)
        elif isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_var = value[2:-1]
            config[key] = os.getenv(env_var, value)
    return config

def get_service_config(service_name: str) -> Dict[str, Any]:
    """Get the configuration for a specific service."""
    config = load_config()
    return config.get('services', {}).get(service_name, {})

def get_api_config() -> Dict[str, Any]:
    """Get the API server configuration."""
    config = load_config()
    return config.get('api', {'host': '127.0.0.1', 'port': 5000})

def get_console_config() -> Dict[str, Any]:
    """Get the console configuration."""
    config = load_config()
    return config.get('console', {'enabled': True})

def get_logging_config() -> Dict[str, Any]:
    """Get the logging configuration."""
    config = load_config()
    return config.get('logging', {'level': 'INFO', 'file': 'llmserver.log'})

def get_plugin_config() -> Dict[str, Any]:
    """Get the plugin configuration."""
    config = load_config()
    return config.get('plugins', {})