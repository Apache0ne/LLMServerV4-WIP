# services/ollama_client.py

from .base_client import ServiceClient
from ollama import Client
from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)

class OllamaClient(ServiceClient):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        host = config.get('host', 'localhost')
        port = config.get('port', 11434)
        self.client = Client(host=f"http://{host}:{port}")
        logger.info(f"Ollama client initialized with host {host} and port {port}")

    def generate_response(self, context: Any) -> str:
        try:
            response = self.client.chat(
                model=context.model,
                messages=self.prepare_messages(context),
                stream=context.settings.stream,
                options={
                    "num_predict": context.settings.num_predict,
                    "temperature": context.settings.temperature,
                    "top_k": context.settings.top_k,
                    "top_p": context.settings.top_p,
                    "repeat_penalty": context.settings.repeat_penalty
                }
            )
            if context.settings.stream:
                response_text = ""
                for chunk in response:
                    content = chunk['message']['content']
                    response_text += content
                    print(content, end='', flush=True)
                print()
                return response_text
            else:
                return response['message']['content']
        except Exception as e:
            return self.handle_error(e)

    def list_models(self) -> List[str]:
        try:
            models = self.client.list()
            if isinstance(models, list):
                return [model['name'] for model in models if isinstance(model, dict) and 'name' in model]
            elif isinstance(models, dict) and 'models' in models:
                return [model['name'] for model in models['models'] if isinstance(model, dict) and 'name' in model]
            else:
                logger.error(f"Unexpected format for Ollama models: {models}")
                return []
        except Exception as e:
            logger.error(f"Error listing Ollama models: {str(e)}")
            return []

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        try:
            models = self.client.list()
            model_list = models if isinstance(models, list) else models.get('models', [])
            for model in model_list:
                if model.get('name') == model_name:
                    return {
                        "name": model['name'],
                        "created": model.get('modified_at', 'N/A'),
                        "description": f"An Ollama language model: {model['name']}",
                    }
            logger.warning(f"Model not found: {model_name}")
            return {"name": model_name, "error": "Model not found"}
        except Exception as e:
            logger.error(f"Error getting Ollama model info: {str(e)}")
            return {"name": model_name, "error": str(e)}

    def handle_error(self, error: Exception) -> str:
        error_msg = f"Ollama API Error: {str(error)}"
        logger.error(error_msg)
        return error_msg