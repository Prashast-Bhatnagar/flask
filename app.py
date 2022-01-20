from flask import Flask
from flask.json import jsonify

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({'Hello':'world'})

if __name__ == '__main__':
    app.run(host="0.0.0.0")
