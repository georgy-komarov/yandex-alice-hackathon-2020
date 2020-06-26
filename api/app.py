import os
from dotenv import load_dotenv

from flask import Flask, Response, jsonify

from extensions import db, migrate
from models import User

APP_PATH = os.path.dirname(os.path.abspath(__file__))
REPOSITORY_PATH = os.path.dirname(APP_PATH)

load_dotenv(os.path.join(REPOSITORY_PATH, '.env'))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)

row2dict = lambda r: {c.name: str(getattr(r, c.name)) if getattr(r, c.name) else None for c in r.__table__.columns}


@app.route('/')
@app.route('/api/')
def index():
    return Response('API for yandex-alice-hackathon-2020')


@app.route('/user/<ya_id>/')
def user_get_or_create(ya_id: str):
    user = db.session.query(User).first()
    if not user:
        user = User(ya_id=ya_id)
        db.session.add(user)
        db.session.commit()

    return jsonify(row2dict(user))


@app.route('/user/code/create/')
def create_code():
    return jsonify('API for yandex-alice-hackathon-2020')


@app.route('/user/code/verify/')
def create_verify():
    return jsonify('API for yandex-alice-hackathon-2020')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True, load_dotenv=True)
