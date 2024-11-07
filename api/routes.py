from flask import Flask
from .handlers import create_context, list_contexts, delete_context, send_prompt, list_models, start_game, game_turn

def setup_routes(services):
    app = Flask(__name__)

    @app.route('/create_context', methods=['POST'])
    def route_create_context():
        return create_context(services)

    @app.route('/list_contexts', methods=['GET'])
    def route_list_contexts():
        return list_contexts(services)

    @app.route('/delete_context', methods=['POST'])
    def route_delete_context():
        return delete_context(services)

    @app.route('/send_prompt', methods=['POST'])
    def route_send_prompt():
        return send_prompt(services)

    @app.route('/list_models', methods=['GET'])
    def route_list_models():
        return list_models(services)

    @app.route('/start_game', methods=['POST'])
    def route_start_game():
        return start_game(services)

    @app.route('/game_turn', methods=['POST'])
    def route_game_turn():
        return game_turn(services)

    return app