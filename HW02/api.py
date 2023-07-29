from flask import Flask, jsonify
from result import result

# creat flask application
app = Flask(__name__)

# adding path to ouput result dictionary as result, could be done with method but this works for now
@app.route('/v1/health')
def api():
    # convert python dictionary into JSON 
    return jsonify(result)

if __name__ == '__main__':
    app.run()