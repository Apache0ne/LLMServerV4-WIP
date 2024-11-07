# LLM Server

LLM Server is a flexible and extensible platform for interacting with various Large Language Models (LLMs) through a unified interface. It supports multiple LLM services, provides both API and console interfaces, and includes a simple game engine for text-based adventures.

## Features

- Support for multiple LLM services (Groq, Ollama, Cerebras)
- RESTful API for integration with other applications
- Interactive console interface for direct interaction
- Conversation context management
- Simple text-based game engine
- Plugin system for easy extensibility
- Flexible configuration management

## Installation

1. Clone the repository:

git clone https://github.com/yourusername/llm-server.git cd llm-server


2. Create a virtual environment and activate it:
python -m venv venv source venv/bin/activate # On Windows, use venv\Scripts\activate


3. Install the required dependencies:
pip install -r requirements.txt


4. Set up your configuration:
   - Copy `config/services.yaml.example` to `config/services.yaml`
   - Edit `config/services.yaml` to add your API keys and adjust settings

## Usage

### Starting the Server

Run the following command to start both the API server and the console interface:
python main.py


To start only the API server without the console interface:
python main.py --no-console


### API Endpoints

- `POST /create_context`: Create a new conversation context
- `GET /list_contexts`: List all available contexts
- `POST /delete_context`: Delete a specific context
- `POST /send_prompt`: Send a prompt to a specific context
- `GET /list_models`: List available models for a service
- `POST /start_game`: Start a new game in a specific context
- `POST /game_turn`: Take a turn in an active game
- `POST /execute_plugin`: Execute a plugin with optional arguments

Refer to the API documentation for detailed usage of each endpoint.

### Console Commands

In the console interface, you can use the following commands:

- `help`: Show available commands
- `create_context`: Create a new conversation context
- `list_contexts`: List all available contexts
- `delete_context`: Delete a specific context
- `send_prompt`: Send a prompt to a specific context
- `list_models`: List available models for a service
- `start_game`: Start a new game in a specific context
- `game_turn`: Take a turn in an active game
- `execute_plugin`: Execute a plugin with optional arguments
- `exit`: Exit the console

## Configuration

The `config/services.yaml` file allows you to configure:

- API keys for different services
- Default models and parameters for each service
- API server settings
- Logging settings
- Plugin settings

## Extending the Server

### Adding a New Service

1. Create a new file in the `services/` directory (e.g., `new_service_client.py`)
2. Implement the `ServiceClient` interface
3. Add the new service to the `SERVICE_REGISTRY` in `manager_instance.py`

### Creating Plugins

1. Create a new file in the `plugins/` directory (e.g., `my_plugin.py`)
2. Implement the plugin interface (refer to existing plugins for examples)
3. The plugin will be automatically loaded by the `PluginManager`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.