from flask import Flask
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import request

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:Bun_zees5@my-postgres-db.ca2fymsujo5f.us-east-2.rds.amazonaws.com:5432/flaskapp"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


db = SQLAlchemy(app)

@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({'Hello':'world'})

class best(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(80), nullable=False)
  content = db.Column(db.String(120), nullable=False)

db.create_all()

@app.route('/items', methods=['GET'])
def get_items():
  items = []
  for item in db.session.query(best).all():
    items.append(item.title)
  return jsonify(items)


@app.route('/items', methods=['POST'])
def create_item():
  body = request.get_json()
  db.session.add(best(title=body['title'],content= body['content']))
  db.session.commit()
  return "item created"

if __name__ == '__main__':
    app.run(host="0.0.0.0")
