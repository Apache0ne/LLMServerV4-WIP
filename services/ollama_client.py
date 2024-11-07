# services/ollama_client.py

from .base_client import ServiceClient
import aiohttp
from typing import Dict, Any, List
from utils.logger import get_logger
import json  # Add this import at the top of the file
from json.decoder import JSONDecodeError  # Add this import as well

logger = get_logger(__name__)

class OllamaClient(ServiceClient):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = f"http://{config.get('host', 'localhost')}:{config.get('port', 11434)}"
        logger.info(f"Ollama client initialized with base URL: {self.base_url}")

    async def generate_response(self, context: Any) -> str:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{self.base_url}/api/chat", json={
                    "model": context.model,
                    "messages": self.prepare_messages(context),
                    "stream": context.settings.stream,
                    "options": {
                        "num_predict": context.settings.num_predict,
                        "temperature": context.settings.temperature,
                        "top_k": context.settings.top_k,
                        "top_p": context.settings.top_p,
                        "repeat_penalty": context.settings.repeat_penalty
                    }
                }) as resp:
                    if context.settings.stream:
                        response_text = ""
                        async for line in resp.content:
                            if line:
                                chunk = line.decode().strip()
                                if chunk.startswith('data: '):
                                    chunk = chunk[6:]  # Remove 'data: ' prefix
                                    try:
                                        chunk_data = json.loads(chunk)
                                        content = chunk_data['message']['content']
                                        response_text += content
                                        print(content, end='', flush=True)
                                    except JSONDecodeError as e:
                                        logger.error(f"Error decoding JSON: {e}")
                                        continue
                        print()
                        return response_text
                    else:
                        result = await resp.json()
                        return result['message']['content']
            except Exception as e:
                return await self.handle_error(e)

    async def list_models(self) -> List[str]:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/api/tags") as resp:
                    result = await resp.json()
                    return [model['name'] for model in result['models']]
            except Exception as e:
                logger.error(f"Error listing Ollama models: {str(e)}")
                return []

    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        # Ollama doesn't provide detailed model info, so we return basic info
        return {
            "name": model_name,
            "created": "N/A",
            "description": "An Ollama language model",
        }

    async def handle_error(self, error: Exception) -> str:
        error_msg = f"Ollama API Error: {str(error)}"
        logger.error(error_msg)
        return error_msg