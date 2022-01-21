from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({'Hello':'World'})

if __name__ == '__main__':
    app.run(debug=True)

# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:Bun_zees5@my-postgres-db.ca2fymsujo5f.us-east-2.rds.amazonaws.com:5432/flaskapp"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


db = SQLAlchemy(app)

class Item(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(80), unique=True, nullable=False)
  content = db.Column(db.String(120), unique=True, nullable=False)

  def _init_(self, title, content):
    self.title = title
    self.content = content


db.create_all()



@app.route('/items/<id>', methods=['GET'])
def get_item(id):
  item = Item.query.get(id)
  del item._dict_['_sa_instance_state']
  return jsonify(item._dict_)


@app.route('/items', methods=['GET'])
def get_items():
  items = []
  for item in db.session.query(Item).all():
    del item._dict_['_sa_instance_state']
    items.append(item._dict_)
  return jsonify(items)


@app.route('/items', methods=['POST'])
def create_item():
  body = request.get_json()
  db.session.add(Item(body['title'], body['content']))
  db.session.commit()
  return "item created"