from flask import Flask
from flask import request

# Custom imports
import mister.__main__ as M
from mister.errors import *


# Request keys for Mister API
Mister_KEYS = [
    'formation', 'n',
    'nteams', 'players'
]

Methods = {
    'ALL': ['GET', 'POST', 'PUT',
            'DELETE', 'PATCH', 'HEAD'],
    
    'ALLOWED': ['POST']
}


app = Flask(__name__)

@app.route('/make-teams', methods=Methods['ALL'])
def make_teams():
    if not request.method \
            in Methods['ALLOWED']:
        return {
            'error': 'Method not allowed'
               }, 405

    scenario_data = request.json
    scenario_keys = scenario_data.keys()

    if not set(Mister_KEYS) \
            == set(scenario_keys):
        return {
            'error': 'Missing parameters'
               }, 400

    try:
        return M.fromjson(scenario_data), 200
    except (DuplicatePlayersError,
            NoSolutionError,
            InvalidFormationError,
            NotEnoughPlayersError,
            TooManyPlayersError) as e:
        return {
            'error': str(e)
               }, 400
    except Exception:
        return {
            'error': 'Unknown'
               }, 500

if __name__ == '__main__':
    app.run(host='127.0.0.1',
            port=8000, debug=True)
