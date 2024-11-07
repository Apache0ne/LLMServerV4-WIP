# console/cli.py

import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from utils.logger import get_logger
from utils.error_handler import ErrorHandler

logger = get_logger(__name__)

class CLI:
    def __init__(self, conversation_manager, game_engine, plugin_manager):
        self.manager = conversation_manager
        self.game_engine = game_engine
        self.plugin_manager = plugin_manager
        self.session = PromptSession()
        self.command_completer = WordCompleter([
            'help', 'create_context', 'list_contexts', 'delete_context',
            'send_prompt', 'list_models', 'start_game', 'game_turn',
            'execute_plugin', 'exit'
        ])
        self.style = Style.from_dict({
            'prompt': '#ansibrightcyan bold',
            'output': '#ansibrightgreen',
            'error': '#ansired bold', 
        })


    async def run(self):
        print("Welcome to the LLM Server Console. Type 'help' for a list of commands.")
        while True:
            try:
                command = await self.session.prompt_async(
                    "LLM Server > ",
                    completer=self.command_completer,
                    style=self.style
                )
                if command.lower() == 'exit':
                    break
                await self.handle_command(command)
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
        print("Exiting LLM Server Console.")

    async def handle_command(self, command):
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:]

        try:
            if cmd == 'help':
                self.show_help()
            elif cmd == 'create_context':
                await self.create_context(args)
            elif cmd == 'list_contexts':
                await self.list_contexts()
            elif cmd == 'delete_context':
                await self.delete_context(args)
            elif cmd == 'send_prompt':
                await self.send_prompt(args)
            elif cmd == 'list_models':
                await self.list_models(args)
            elif cmd == 'start_game':
                await self.start_game(args)
            elif cmd == 'game_turn':
                await self.game_turn(args)
            elif cmd == 'execute_plugin':
                await self.execute_plugin(args)
            else:
                print("Unknown command. Type 'help' for a list of commands.")
        except Exception as e:
            error_info = ErrorHandler.handle_error(e, f"Error executing command: {command}")
            self.print_error(f"Command execution failed: {error_info['message']}")

    def show_help(self):
        help_text = """
Available commands:
  help                       - Show this help message
  create_context <name> <service> <model> [system_prompt]
                              - Create a new conversation context
  list_contexts              - List all available contexts
  delete_context <name>      - Delete a specific context
  send_prompt <context> <prompt>
                              - Send a prompt to a specific context
  list_models <service>      - List available models for a service
  start_game <context>       - Start a new game in a specific context
  game_turn <context> <action>
                              - Take a turn in an active game
  execute_plugin <name> [args]
                              - Execute a plugin with optional arguments
  exit                       - Exit the console
"""
        print(help_text)

    async def create_context(self, args):
        if len(args) < 3:
            self.print_error("Usage: create_context <name> <service> <model> [system_prompt]")
            return
        name, service, model = args[:3]
        system_prompt = " ".join(args[3:]) if len(args) > 3 else "You are a helpful assistant."
        result = await self.manager.create_context(name, service, model, system_prompt)
        if result['success']:
            self.print_output(result['message'])
        else:
            self.print_error(result['message'])

    async def list_contexts(self):
        result = await self.manager.list_contexts()
        if result['success']:
            for ctx in result['contexts']:
                self.print_output(f"Name: {ctx['name']}, Service: {ctx['service']}, Model: {ctx['model']}")
        else:
            self.print_error(result['message'])

    async def delete_context(self, args):
        if len(args) != 1:
            self.print_error("Usage: delete_context <name>")
            return
        result = await self.manager.delete_context(args[0])
        if result['success']:
            self.print_output(result['message'])
        else:
            self.print_error(result['message'])

    async def send_prompt(self, args):
        if len(args) < 2:
            self.print_error("Usage: send_prompt <context> <prompt>")
            return
        context, prompt = args[0], " ".join(args[1:])
        result = await self.manager.send_prompt(context, prompt)
        if result['success']:
            self.print_output(f"Response: {result['response']}")
        else:
            self.print_error(result['message'])

    async def list_models(self, args):
        if len(args) != 1:
            self.print_error("Usage: list_models <service>")
            return
        service = args[0]
        try:
            client = self.manager.get_service_client(service)
            models = await client.list_models()
            self.print_output(f"Available models for {service}:")
            for model in models:
                self.print_output(f"- {model}")
        except Exception as e:
            self.print_error(f"Error listing models: {str(e)}")

    async def start_game(self, args):
        if len(args) != 1:
            self.print_error("Usage: start_game <context>")
            return
        context = args[0]
        result = await self.game_engine.start_game(context)
        if 'error' not in result:
            self.print_output("Game started. Initial state:")
            self.print_output(result['narration'])
            self.print_output("Available actions:")
            for action in result['actions']:
                self.print_output(f"- {action['description']}")
        else:
            self.print_error(f"Error starting game: {result['error']}")

    async def game_turn(self, args):
        if len(args) < 2:
            self.print_error("Usage: game_turn <context> <action>")
            return
        context, action = args[0], " ".join(args[1:])
        result = await self.game_engine.process_turn(context, action)
        if 'error' not in result:
            self.print_output("Turn processed. New state:")
            self.print_output(result['narration'])
            self.print_output("Available actions:")
            for action in result['actions']:
                self.print_output(f"- {action['description']}")
        else:
            self.print_error(f"Error processing turn: {result['error']}")

    async def execute_plugin(self, args):
        if len(args) < 1:
            self.print_error("Usage: execute_plugin <name> [args]")
            return
        plugin_name, *plugin_args = args
        result = self.plugin_manager.execute_plugin(plugin_name, *plugin_args)
        if result is not None:
            self.print_output(f"Plugin result: {result}")
        else:
            self.print_error(f"Error executing plugin {plugin_name}")

    def print_output(self, message):
        print(self.style.output(message))

    def print_error(self, message):
        print(self.style.error(f"Error: {message}"))

async def start_console(conversation_manager, game_engine, plugin_manager):
    cli = CLI(conversation_manager, game_engine, plugin_manager)
    await cli.run()

