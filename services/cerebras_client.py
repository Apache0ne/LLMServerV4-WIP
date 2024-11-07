# services/cerebras_client.py

from .base_client import ServiceClient
from cerebras.cloud.sdk import Cerebras
from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)

class CerebrasClient(ServiceClient):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = Cerebras(api_key=config['api_key'])
        logger.info("Cerebras client initialized")

    async def generate_response(self, context: Any) -> str:
        try:
            response = await self.client.chat.completions.create(
                messages=self.prepare_messages(context),
                model=context.model,
                temperature=context.settings.temperature,
                max_tokens=context.settings.max_tokens,
                top_p=context.settings.top_p,
                stream=context.settings.stream,
                tools=context.settings.tools if context.settings.use_tools else None
            )
            if context.settings.stream:
                response_text = ""
                async for chunk in response:
                    content = chunk.choices[0].delta.content
                    if content:
                        response_text += content
                        print(content, end='', flush=True)
                print()
                return response_text
            else:
                return response.choices[0].message.content
        except Exception as e:
            return await self.handle_error(e)

    async def list_models(self) -> List[str]:
        # Since we're now using a fixed list, we don't need to make an API call
        return [
            'llama3.1-8b',
            'llama3.1-70b'
        ]

    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        # Provide basic info for the Cerebras models
        if model_name in ['llama3.1-8b', 'llama3.1-70b']:
            return {
                "name": model_name,
                "created": "N/A",
                "description": f"Cerebras {model_name} model",
            }
        else:
            logger.warning(f"Unknown model: {model_name}")
            return {"name": model_name, "error": "Unknown model"}

    async def handle_error(self, error: Exception) -> str:
        error_msg = f"Cerebras API Error: {str(error)}"
        logger.error(error_msg)
        return error_msg