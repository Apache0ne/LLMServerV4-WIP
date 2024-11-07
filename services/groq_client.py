# services/groq_client.py

from .base_client import ServiceClient
from groq import AsyncGroq
from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)

class GroqClient(ServiceClient):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = AsyncGroq(api_key=config['api_key'])
        logger.info("Groq client initialized")

    async def generate_response(self, context: Any) -> str:
        try:
            chat_completion = await self.client.chat.completions.create(
                messages=self.prepare_messages(context),
                model=context.model,
                temperature=context.settings.temperature,
                max_tokens=context.settings.max_tokens,
                top_p=context.settings.top_p,
                stream=context.settings.stream,
            )
            if context.settings.stream:
                response_text = ""
                async for chunk in chat_completion:
                    content = chunk.choices[0].delta.content
                    if content:
                        response_text += content
                        print(content, end='', flush=True)
                print()
                return response_text
            else:
                return chat_completion.choices[0].message.content
        except Exception as e:
            return await self.handle_error(e)

    async def list_models(self) -> List[str]:
        # Groq doesn't have a list_models API, so we return a predefined list
        return [
            'llama3-groq-70b-8192-tool-use-preview',
            'llama3-groq-8b-8192-tool-use-preview',
            'llama-3.1-70b-versatile',
            'llama-3.1-8b-instant',
            'llama-3.2-1b-preview',
            'llama-3.2-3b-preview',
            'llama3-70b-8192',
            'llama3-8b-8192',
        ]

    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        # Groq doesn't provide detailed model info, so we return basic info
        return {
            "name": model_name,
            "created": "N/A",
            "description": "A Groq language model",
        }

    async def handle_error(self, error: Exception) -> str:
        error_msg = f"Groq API Error: {str(error)}"
        logger.error(error_msg)
        return error_msg