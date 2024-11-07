# game/engine.py

import json
from .state import GameState
from utils.logger import get_logger
from utils.error_handler import ErrorHandler
from typing import Dict, Any, List  # Add List to this import

logger = get_logger(__name__)

class GameEngine:
    def __init__(self, conversation_manager):
        self.conversation_manager = conversation_manager
        self.states: Dict[str, GameState] = {}

    async def start_game(self, context_name: str) -> Dict[str, Any]:
        try:
            context = self.conversation_manager.get_context(context_name)
            if not context:
                raise ValueError(f"Context '{context_name}' does not exist.")

            initial_prompt = (
                "Start a new isekai anime-themed adventure game. "
                "Describe the opening scene where the player is transported to a fantasy world. "
                "Provide a vivid description, suggest initial actions, and set the stage for the adventure."
            )

            response = await self._generate_response(context, initial_prompt)
            game_state = GameState(context_name, response)
            self.states[context_name] = game_state
            logger.info(f"Started new game for context: {context_name}")
            return game_state.get_current_state()
        except Exception as e:
            error_info = ErrorHandler.handle_error(e, f"Error starting game for context '{context_name}'")
            logger.error(f"Game start error: {error_info}")
            return {"error": str(e)}

    async def process_turn(self, context_name: str, action: str) -> Dict[str, Any]:
        try:
            if context_name not in self.states:
                raise ValueError(f"No active game for context: {context_name}")
            
            game_state = self.states[context_name]
            context = self.conversation_manager.get_context(context_name)
            
            prompt = (
                f"The player takes the following action: {action}\n\n"
                "Continue the story based on this action. Describe the outcome, "
                "the new situation, and provide new action options for the player. "
                "Remember to maintain consistency with the previous state and the game world."
            )
            
            response = await self._generate_response(context, prompt)
            game_state.update(response)
            logger.info(f"Processed turn for game in context: {context_name}")
            return game_state.get_current_state()
        except Exception as e:
            error_info = ErrorHandler.handle_error(e, f"Error processing turn for context '{context_name}'")
            logger.error(f"Game turn error: {error_info}")
            return {"error": str(e)}

    async def _generate_response(self, context, prompt: str) -> Dict[str, Any]:
        try:
            service_client = self.conversation_manager.get_service_client(context.service)
            response = await service_client.generate_response(context)
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # If the response isn't valid JSON, try to extract JSON from it
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end != -1:
                    try:
                        return json.loads(response[start:end])
                    except json.JSONDecodeError:
                        raise ValueError("Could not parse response as JSON")
                else:
                    raise ValueError("No JSON object found in response")
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    def end_game(self, context_name: str) -> None:
        if context_name in self.states:
            del self.states[context_name]
            logger.info(f"Ended game for context: {context_name}")
        else:
            logger.warning(f"Attempted to end non-existent game for context: {context_name}")

    def get_game_state(self, context_name: str) -> Dict[str, Any]:
        if context_name in self.states:
            return self.states[context_name].get_current_state()
        else:
            logger.warning(f"Attempted to get state for non-existent game in context: {context_name}")
            return {"error": "No active game for this context"}

    def list_active_games(self) -> List[str]:
        return list(self.states.keys())