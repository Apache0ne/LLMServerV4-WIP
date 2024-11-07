import shlex
from conversation_manager import ConversationManager

class CommandHandler:
    def __init__(self, services):
        self.services = services
        self.conversation_manager = ConversationManager()

    async def handle_command(self, command_line):
        parts = shlex.split(command_line)
        command, *args = parts

        if hasattr(self, f"cmd_{command}"):
            method = getattr(self, f"cmd_{command}")
            return await method(*args)
        else:
            return f"Unknown command: {command}. Type 'help' for a list of commands."

    async def cmd_help(self):
        return """
Available commands:
  create_context <name> <service> <model> [system_prompt]
  list_contexts
  delete_context <name>
  send_prompt <context_name> <prompt>
  list_models <service>
  start_game <context_name>
  game_turn <context_name> <action>
  help
"""

    async def cmd_create_context(self, name, service, model, *system_prompt):
        if service not in self.services:
            return f"Invalid service: {service}"
        system_prompt = " ".join(system_prompt) if system_prompt else "You are a helpful assistant."
        result = self.conversation_manager.create_context(name, service, model, system_prompt)
        return f"Context created: {result}"

    async def cmd_list_contexts(self):
        contexts = self.conversation_manager.list_contexts()
        return "\n".join([f"{ctx['name']} ({ctx['service']}:{ctx['model']})" for ctx in contexts['contexts']])

    async def cmd_delete_context(self, name):
        result = self.conversation_manager.delete_context(name)
        return f"Context deleted: {result}"

    async def cmd_send_prompt(self, context_name, *prompt_parts):
        prompt = " ".join(prompt_parts)
        context = self.conversation_manager.get_context(context_name)
        if not context:
            return f"Context not found: {context_name}"
        service = self.services[context.service]
        response = await service.generate_response(context)
        self.conversation_manager.add_message(context_name, "user", prompt)
        self.conversation_manager.add_message(context_name, "assistant", response)
        return f"Assistant: {response}"

    async def cmd_list_models(self, service):
        if service not in self.services:
            return f"Invalid service: {service}"
        models = await self.services[service].list_models()
        return "\n".join(models)

    async def cmd_start_game(self, context_name):
        # Implement game start logic here
        return f"Game started with context: {context_name}"

    async def cmd_game_turn(self, context_name, *action_parts):
        action = " ".join(action_parts)
        # Implement game turn logic here
        return f"Processed game turn for {context_name} with action: {action}"