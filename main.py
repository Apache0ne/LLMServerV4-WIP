# main.py

import asyncio
import argparse
from flask import Flask, request, jsonify
from flask_cors import CORS
from manager_instance import manager, send_prompt, plugin_manager
from console.cli import start_console
from game.engine import GameEngine
from utils.logger import get_logger
from config.config_loader import get_api_config, get_console_config

logger = get_logger(__name__)

# Flask server configuration
api_config = get_api_config()
FLASK_HOST = api_config.get('host', '127.0.0.1')
FLASK_PORT = api_config.get('port', 5000)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

game_engine = GameEngine(manager)

def create_route(route, methods, func, endpoint=None):
    endpoint = endpoint or f"{func.__name__}_{route}"
    @app.route(route, methods=methods, endpoint=endpoint)
    async def wrapper():
        if request.method == 'GET':
            return jsonify(await func())
        else:
            data = request.json or {}
            return jsonify(await func(**data))
    return wrapper

# Register API routes
create_route('/create_context', ['POST'], manager.create_context)
create_route('/list_contexts', ['GET'], manager.list_contexts)
create_route('/delete_context', ['POST'], manager.delete_context)
create_route('/send_prompt', ['POST'], send_prompt)
create_route('/copy_context', ['POST'], manager.copy_context)

@app.route('/list_models', methods=['GET'])
async def list_models():
    service = request.args.get('service', '').lower()
    try:
        client = manager.get_service_client(service)
        models = await client.list_models()
        return jsonify({"models": models})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error listing models for {service}: {str(e)}")
        return jsonify({"error": "An error occurred while listing models"}), 500

@app.route('/start_game', methods=['POST'])
async def start_game():
    data = request.json
    context_name = data.get('context_name')
    if not context_name or context_name not in manager.contexts:
        return jsonify({"error": "Invalid or missing context name"}), 400
    
    initial_state = await game_engine.start_game(context_name)
    return jsonify({"initial_state": initial_state})

@app.route('/game_turn', methods=['POST'])
async def game_turn():
    data = request.json
    context_name = data.get('context_name')
    user_input = data.get('user_input')
    
    if not context_name or context_name not in manager.contexts:
        return jsonify({"error": "Invalid or missing context name"}), 400
    if not user_input:
        return jsonify({"error": "Missing user input"}), 400
    
    game_response = await game_engine.process_turn(context_name, user_input)
    return jsonify({"game_response": game_response})

@app.route('/execute_plugin', methods=['POST'])
def execute_plugin():
    data = request.json
    plugin_name = data.get('plugin_name')
    plugin_args = data.get('args', [])
    plugin_kwargs = data.get('kwargs', {})
    
    if not plugin_name:
        return jsonify({"error": "Missing plugin name"}), 400
    
    try:
        result = plugin_manager.execute_plugin(plugin_name, *plugin_args, **plugin_kwargs)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": f"Failed to execute plugin {plugin_name}: {str(e)}"}), 500

async def run_server():
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = [f"{FLASK_HOST}:{FLASK_PORT}"]
    await serve(app, config)

async def main():
    parser = argparse.ArgumentParser(description='LLM Server')
    parser.add_argument('--no-console', action='store_true', help='Disable console interface')
    args = parser.parse_args()

    console_config = get_console_config()
    run_console = console_config.get('enabled', True) and not args.no_console

    tasks = [run_server()]
    if run_console:
        tasks.append(start_console(manager, game_engine, plugin_manager))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())