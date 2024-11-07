# api/routes.py

from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest
from typing import Dict, Any

def setup_routes(services, manager, game_engine, plugin_manager):
    app = Flask(__name__)

    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, BadRequest):
            return jsonify({"error": "Bad request", "message": str(e)}), 400
        app.logger.error(f"Unhandled exception: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

    @app.route('/create_context', methods=['POST'])
    def route_create_context():
        data = request.json
        try:
            result = manager.create_context(
                name=data['name'],
                service=data['service'],
                model=data['model'],
                system_prompt=data['system_prompt'],
                settings=data.get('settings', {})
            )
            return jsonify(result)
        except KeyError as e:
            raise BadRequest(f"Missing required field: {str(e)}")

    @app.route('/list_contexts', methods=['GET'])
    def route_list_contexts():
        result = manager.list_contexts()
        return jsonify(result)

    @app.route('/delete_context', methods=['POST'])
    def route_delete_context():
        data = request.json
        if 'name' not in data:
            raise BadRequest("Missing 'name' field")
        result = manager.delete_context(data['name'])
        return jsonify(result)

    @app.route('/send_prompt', methods=['POST'])
    async def route_send_prompt():
        data = request.json
        if 'context_name' not in data or 'prompt' not in data:
            raise BadRequest("Missing 'context_name' or 'prompt' field")
        context = manager.get_context(data['context_name'])
        if not context:
            return jsonify({"error": "Context not found"}), 404
        
        service = services[context.service]
        response = await service.generate_response(context)
        
        result = manager.add_message(context.name, "assistant", response)
        return jsonify(result)

    @app.route('/list_models', methods=['GET'])
    async def route_list_models():
        service_name = request.args.get('service')
        if not service_name or service_name not in services:
            raise BadRequest(f"Invalid or missing service: {service_name}")
        
        models = await services[service_name].list_models()
        return jsonify({"models": models})

    @app.route('/start_game', methods=['POST'])
    async def route_start_game():
        data = request.json
        if 'context_name' not in data:
            raise BadRequest("Missing 'context_name' field")
        
        initial_state = await game_engine.start_game(data['context_name'])
        return jsonify({"initial_state": initial_state})

    @app.route('/game_turn', methods=['POST'])
    async def route_game_turn():
        data = request.json
        if 'context_name' not in data or 'user_input' not in data:
            raise BadRequest("Missing 'context_name' or 'user_input' field")
        
        game_response = await game_engine.process_turn(data['context_name'], data['user_input'])
        return jsonify({"game_response": game_response})

    @app.route('/execute_plugin', methods=['POST'])
    def route_execute_plugin():
        data = request.json
        if 'plugin_name' not in data:
            raise BadRequest("Missing 'plugin_name' field")
        
        plugin_name = data['plugin_name']
        plugin_args = data.get('args', [])
        plugin_kwargs = data.get('kwargs', {})
        
        try:
            result = plugin_manager.execute_plugin(plugin_name, *plugin_args, **plugin_kwargs)
            return jsonify({"result": result})
        except Exception as e:
            app.logger.error(f"Failed to execute plugin {plugin_name}: {str(e)}")
            return jsonify({"error": f"Failed to execute plugin {plugin_name}"}), 500

    return app