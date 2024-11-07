from .base_client import ServiceClient
from .groq_client import GroqClient
from .ollama_client import OllamaClient
from .cerebras_client import CerebrasClient

SERVICE_REGISTRY = {
    'groq': GroqClient,
    'ollama': OllamaClient,
    'cerebras': CerebrasClient,
}

def initialize_services(config):
    return {name: cls(config.get(name, {})) for name, cls in SERVICE_REGISTRY.items()}