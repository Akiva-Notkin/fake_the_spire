from flask import Flask, jsonify, request
from combat import Game, GameOver

app = Flask(__name__)


class GameManager:
    _instance = None

    @staticmethod
    def get_instance(reset: bool = False):
        if GameManager._instance is None or reset:
            GameManager._instance = GameManager()
        return GameManager._instance

    def __init__(self):
        if GameManager._instance is not None:
            raise Exception("This class is a singleton!")
        self.current_game = Game('character')


@app.route('/start_game', methods=['POST'])
def start_game():
    """
    Starts the game.
    """

    game = GameManager.get_instance(True).current_game

    options = game.current_options

    # Respond to the client with the result
    # The client decides whether to make another request based on this response
    game_state = game.to_dict()
    return jsonify({"game": game_state, "options": options}), 200


@app.route('/take_action', methods=['POST'])
def take_action():
    """
    Receives an action from the client and processes it.
    """
    # Receive the action from the client
    action = request.json.get('action')

    if not action:
        return jsonify({"error": "No action provided"}), 400

    # Get the current game
    game = GameManager.get_instance().current_game

    if game is not None:
        valid_action = game.validate_action(action)
        options = game.current_options
        game_state = game.to_dict()
        if not valid_action:
            return jsonify({"error": "Invalid action", "game": game_state, "options": options}), 400
        try:
            game.action_initiate(action)
        except GameOver:
            return jsonify({"error": "Game over", "game": game_state}), 200
        options = game.current_options
        game_state = game.to_dict()
        return jsonify({"game": game_state, "options": options}), 200


if __name__ == "__main__":
    app.run(debug=True)
