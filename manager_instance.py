# manager_instance.py

import os
import asyncio
from dotenv import load_dotenv
from conversation_manager import ConversationManager
from services.groq_client import GroqClient
from services.ollama_client import OllamaClient
from services.cerebras_client import CerebrasClient
from storage.tinydb_storage import TinyDBStorage
from config.config_loader import load_config, get_service_config, get_logging_config
from utils.logger import setup_logging, get_logger
from utils.error_handler import setup_global_error_handler

# Load environment variables
load_dotenv()

# Load configuration
config = load_config()

# Setup logging
logging_config = get_logging_config()
setup_logging(logging_config)
logger = get_logger(__name__)

# Setup global error handler
setup_global_error_handler()

# Initialize storage
storage = TinyDBStorage('all_contexts.json')

# Initialize ConversationManager
manager = ConversationManager(storage_backend=storage)

# Initialize service clients
service_clients = {}

# Groq setup
groq_config = get_service_config('groq')
if groq_config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY") or groq_config.get('api_key')
    if GROQ_API_KEY:
        service_clients['groq'] = GroqClient({'api_key': GROQ_API_KEY})
        logger.info("Groq client initialized")
    else:
        logger.warning("GROQ_API_KEY is not set. Groq functionality will be limited.")

# Ollama setup
ollama_config = get_service_config('ollama')
if ollama_config:
    OLLAMA_HOST = ollama_config.get('host', 'http://localhost')
    OLLAMA_PORT = ollama_config.get('port', 11434)
    service_clients['ollama'] = OllamaClient({'host': OLLAMA_HOST, 'port': OLLAMA_PORT})
    logger.info(f"Ollama client initialized with host {OLLAMA_HOST} and port {OLLAMA_PORT}")

# Cerebras setup
cerebras_config = get_service_config('cerebras')
if cerebras_config:
    CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY") or cerebras_config.get('api_key')
    if CEREBRAS_API_KEY:
        service_clients['cerebras'] = CerebrasClient({'api_key': CEREBRAS_API_KEY})
        logger.info("Cerebras client initialized")
    else:
        logger.warning("CEREBRAS_API_KEY is not set. Cerebras functionality will be limited.")

# Verify connections
for service_name, client in service_clients.items():
    try:
        models = client.list_models()
        logger.info(f"Successfully connected to {service_name}. Available models: {len(models)}")
    except Exception as e:
        logger.error(f"Could not connect to {service_name} server. Error: {str(e)}")

# Plugin setup
from plugins import PluginManager
plugin_manager = PluginManager()
logger.info(f"Loaded plugins: {plugin_manager.list_plugins()}")

logger.info("ConversationManager instance and services created and configured.")

def get_service_client(service_name):
    client = service_clients.get(service_name)
    if not client:
        raise ValueError(f"No client available for service: {service_name}")
    return client

async def send_prompt(name: str, prompt: str):
    context = manager.get_context(name)
    if not context:
        return {"success": False, "message": f"Context '{name}' does not exist.", "response": None}
    
    service_client = get_service_client(context.service)
    return await manager.send_prompt(name, prompt, service_client)

async def initialize_services():
    for service_name, client in service_clients.items():
        try:
            models = await client.list_models()
            logger.info(f"Successfully connected to {service_name}. Available models: {len(models)}")
        except Exception as e:
            logger.error(f"Could not connect to {service_name} server. Error: {str(e)}")

asyncio.run(initialize_services())

logger.info("ConversationManager instance and services created and configured.")

# Export the functions and objects that should be accessible from other modules
__all__ = ['manager', 'send_prompt', 'plugin_manager']