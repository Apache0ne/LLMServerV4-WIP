# services/base_client.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)

class ServiceClient(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        logger.info(f"Initializing {self.__class__.__name__} with config: {config}")

    @abstractmethod
    async def generate_response(self, context: Any) -> str:
        """
        Generate a response using the service's model.
        
        :param context: The conversation context containing history, model, and settings.
        :return: The generated response as a string.
        """
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """
        List available models for this service.
        
        :return: A list of model names available for this service.
        """
        pass

    @abstractmethod
    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific model.
        
        :param model_name: The name of the model to get information about.
        :return: A dictionary containing model information.
        """
        pass

    async def validate_response(self, response: str) -> str:
        """
        Validate and potentially clean up the response from the service.
        
        :param response: The raw response from the service.
        :return: The validated and cleaned response.
        """
        # Default implementation just returns the response as-is
        # Subclasses can override this method to implement service-specific validation
        return response

    def get_default_params(self) -> Dict[str, Any]:
        """
        Get the default parameters for this service.
        
        :return: A dictionary of default parameters.
        """
        return {
            "temperature": 0.7,
            "max_tokens": 150,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
        }

    def prepare_messages(self, context: Any) -> List[Dict[str, str]]:
        """
        Prepare the message history for the API request.
        
        :param context: The conversation context containing the message history.
        :return: A list of message dictionaries ready for the API request.
        """
        return [{"role": msg["role"], "content": msg["content"]} for msg in context.history]

    async def handle_error(self, error: Exception) -> str:
        """
        Handle errors that occur during API calls.
        
        :param error: The exception that was raised.
        :return: An error message string.
        """
        error_msg = f"An error occurred: {str(error)}"
        logger.error(error_msg)
        return error_msg

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(config={self.config})"

    def __repr__(self) -> str:
        return self.__str__()