import sys
import traceback
from .logger import get_logger

logger = get_logger(__name__)

class ErrorHandler:
    @staticmethod
    def handle_error(error, context=None):
        error_type = type(error).__name__
        error_message = str(error)
        stack_trace = traceback.format_exc()

        logger.error(f"Error occurred: {error_type} - {error_message}")
        if context:
            logger.error(f"Context: {context}")
        logger.debug(f"Stack trace:\n{stack_trace}")

        return {
            "error": error_type,
            "message": error_message,
            "context": context
        }

    @staticmethod
    def global_exception_handler(exctype, value, tb):
        logger.critical("Unhandled exception:")
        logger.critical(''.join(traceback.format_exception(exctype, value, tb)))

def setup_global_error_handler():
    sys.excepthook = ErrorHandler.global_exception_handler