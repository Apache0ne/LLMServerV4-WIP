# conversation_manager.py

import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from game_settings import get_default_settings
from utils.logger import get_logger
from utils.error_handler import ErrorHandler

logger = get_logger(__name__)

@dataclass
class ConversationContext:
    name: str
    service: str
    model: str
    system_prompt: str
    settings: Any
    history: List[Dict[str, Any]] = field(default_factory=list)

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "service": self.service,
            "model": self.model,
            "system_prompt": self.system_prompt,
            "settings": self.settings.__dict__ if hasattr(self.settings, '__dict__') else self.settings,
            "history": self.history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationContext':
        settings = get_default_settings(data["service"])
        for key, value in data["settings"].items():
            setattr(settings, key, value)
        return cls(
            name=data["name"],
            service=data["service"],
            model=data["model"],
            system_prompt=data["system_prompt"],
            settings=settings,
            history=data.get("history", [])
        )

class ConversationManager:
    def __init__(self, storage_backend=None):
        self.contexts: Dict[str, ConversationContext] = {}
        self.storage_backend = storage_backend
        self.load_all_contexts()

    def load_all_contexts(self):
        if self.storage_backend:
            try:
                stored_contexts = self.storage_backend.load_all()
                for context_data in stored_contexts:
                    context = ConversationContext.from_dict(context_data)
                    self.contexts[context.name] = context
                logger.info(f"Loaded {len(self.contexts)} contexts from storage")
            except Exception as e:
                logger.error(f"Error loading contexts: {str(e)}")

    def save_context(self, context: ConversationContext):
        if self.storage_backend:
            try:
                self.storage_backend.save(context.name, context.to_dict())
                logger.debug(f"Saved context: {context.name}")
            except Exception as e:
                logger.error(f"Error saving context {context.name}: {str(e)}")

    def create_context(self, name: str, service: str, model: str, system_prompt: str, settings: Any = None) -> Dict[str, Any]:
        try:
            if name in self.contexts:
                return {"success": False, "message": f"Context '{name}' already exists."}

            if settings is None:
                settings = get_default_settings(service)

            context = ConversationContext(name, service, model, system_prompt, settings)
            context.add_message("system", system_prompt)
            self.contexts[name] = context
            self.save_context(context)
            return {"success": True, "message": f"Context '{name}' created successfully."}
        except Exception as e:
            return ErrorHandler.handle_error(e, f"Error creating context '{name}'")

    def list_contexts(self) -> Dict[str, Any]:
        try:
            return {
                "success": True,
                "contexts": [
                    {
                        "name": ctx.name,
                        "service": ctx.service,
                        "model": ctx.model,
                        "system_prompt": ctx.system_prompt[:50] + '...' if len(ctx.system_prompt) > 50 else ctx.system_prompt
                    } for ctx in self.contexts.values()
                ]
            }
        except Exception as e:
            return ErrorHandler.handle_error(e, "Error listing contexts")

    def delete_context(self, name: str) -> Dict[str, Any]:
        try:
            if name in self.contexts:
                del self.contexts[name]
                if self.storage_backend:
                    self.storage_backend.delete(name)
                return {"success": True, "message": f"Context '{name}' deleted."}
            return {"success": False, "message": f"Context '{name}' does not exist."}
        except Exception as e:
            return ErrorHandler.handle_error(e, f"Error deleting context '{name}'")

    def get_context(self, name: str) -> Optional[ConversationContext]:
        return self.contexts.get(name)

    async def send_prompt(self, name: str, prompt: str, service_client) -> Dict[str, Any]:
        try:
            if name not in self.contexts:
                return {"success": False, "message": f"Context '{name}' does not exist.", "response": None}

            context = self.contexts[name]
            context.add_message("user", prompt)
            
            response = await service_client.generate_response(context)

            if response:
                context.add_message("assistant", response)
                self.save_context(context)
                return {"success": True, "response": response}
            return {"success": False, "message": "Failed to get a response.", "response": None}
        except Exception as e:
            return ErrorHandler.handle_error(e, f"Error sending prompt for context '{name}'")

    def copy_context(self, source_name: str, new_name: str, num_messages: Optional[int] = None) -> Dict[str, Any]:
        try:
            if source_name not in self.contexts:
                return {"success": False, "message": f"Source context '{source_name}' does not exist."}
            if new_name in self.contexts:
                return {"success": False, "message": f"Context '{new_name}' already exists."}

            source_context = self.contexts[source_name]
            new_context = ConversationContext(
                name=new_name,
                service=source_context.service,
                model=source_context.model,
                system_prompt=source_context.system_prompt,
                settings=source_context.settings,
                history=list(source_context.history)
            )

            if num_messages is not None:
                new_context.history = [new_context.history[0]] + new_context.history[-num_messages:]

            self.contexts[new_name] = new_context
            self.save_context(new_context)
            return {"success": True, "message": f"Context '{new_name}' copied from '{source_name}'."}
        except Exception as e:
            return ErrorHandler.handle_error(e, f"Error copying context from '{source_name}' to '{new_name}'")