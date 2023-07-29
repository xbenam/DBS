from flask import Flask, jsonify
import result

# creat flask application
app = Flask(__name__)


@app.before_request
def before_request():
    result.DBconnect()

@app.after_request
def after_request(response):
    result.DBdisconnect()
    return response 

# adding path to ouput result dictionary as result, could be done with method but this works for now
@app.route('/v1/health')
def api():
    # convert python dictionary into JSON 
    return jsonify(result.version())

@app.route('/v2/patches/')
def patch():
    # convert python dictionary into JSON 
    return jsonify(result.patches())

@app.route('/v2/players/<int:player_id>/game_exp/')
def game_experience(player_id):
    # convert python dictionary into JSON 
    return jsonify(result.game_exp(player_id))
    
@app.route('/v2/players/<int:player_id>/game_objectives/')
def game_objective(player_id):
    # convert python dictionary into JSON 
    return jsonify(result.game_obj(player_id))
    
@app.route('/v2/players/<int:player_id>/abilities/')
def game_ability(player_id):
    # convert python dictionary into JSON 
    return jsonify(result.abilities(player_id))

@app.route('/v3/matches/<int:match_id>/top_purchases/')
def top_purchases(match_id):
    # convert python dictionary into JSON 
    return (result.purchase_item(match_id))

@app.route('/v3/abilities/<int:ability_id>/usage/')
def ability_usage(ability_id):
    # convert python dictionary into JSON 
    return (result.usage(ability_id))

@app.route('/v3/statistics/tower_kills/')
def tower_kills():
    # convert python dictionary into JSON 
    return (result.tower_kills_by_hero())
    

if __name__ == '__main__':
    app.run()