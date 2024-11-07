from flask import request, jsonify
from conversation_manager import ConversationManager

manager = ConversationManager()

def create_context(services):
    data = request.json
    service_name = data.get('service')
    if service_name not in services:
        return jsonify({"error": f"Invalid service: {service_name}"}), 400
    
    result = manager.create_context(
        name=data.get('name'),
        service=service_name,
        model=data.get('model'),
        system_prompt=data.get('system_prompt'),
        settings=data.get('settings', {})
    )
    return jsonify(result)

def list_contexts(services):
    result = manager.list_contexts()
    return jsonify(result)

def delete_context(services):
    data = request.json
    result = manager.delete_context(data.get('name'))
    return jsonify(result)

async def send_prompt(services):
    data = request.json
    context = manager.get_context(data.get('context_name'))
    if not context:
        return jsonify({"error": "Context not found"}), 404
    
    service = services[context.service]
    response = await service.generate_response(context)
    
    result = manager.add_message(context.name, "assistant", response)
    return jsonify(result)

async def list_models(services):
    service_name = request.args.get('service')
    if service_name not in services:
        return jsonify({"error": f"Invalid service: {service_name}"}), 400
    
    models = await services[service_name].list_models()
    return jsonify({"models": models})

def start_game(services):
    data = request.json
    # Implement game initialization logic here
    return jsonify({"message": "Game started"})

def game_turn(services):
    data = request.json
    # Implement game turn logic here
    return jsonify({"message": "Turn processed"})