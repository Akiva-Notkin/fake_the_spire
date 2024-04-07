from flask import Flask, jsonify, request
from combat import Game, GameOver, FloorOver

app = Flask(__name__)


class GameManager:
    _instance = None

    @staticmethod
    def get_instance():
        if GameManager._instance is None:
            GameManager._instance = GameManager()
        return GameManager._instance

    def __init__(self):
        if GameManager._instance is not None:
            raise Exception("This class is a singleton!")
        self.current_game = Game('character')


@app.route('/play_game', methods=['POST'])
def play_game():
    """
    Starts the game.
    """

    action = request.json.get('action')

    if not action:
        game = GameManager.get_instance().current_game
        options = game.current_options

        # Respond to the client with the result
        # The client decides whether to make another request based on this response
        game_state = game.to_dict()
        return jsonify({"game": game_state, "options": options}), 200
    else:
        game = GameManager.get_instance().current_game
        valid_action = game.validate_action(action)
        options = game.current_options
        game_state = game.to_dict()
        if not valid_action:
            return jsonify({"error": "Invalid action", "game": game_state, "options": options}), 400
        try:
            game.action_initiate(action)
        except GameOver as ge:
            return jsonify({"game_over": str(ge), "game": game_state}), 200
        except FloorOver:
            pass
        options = game.current_options
        game_state = game.to_dict()
        return jsonify({"game": game_state, "options": options}), 200


if __name__ == "__main__":
    app.run(debug=True)
