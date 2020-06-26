import os
from dotenv import load_dotenv
from random import choice
from datetime import datetime, timedelta

from flask import Flask, Response, jsonify

from extensions import db, migrate
from models import User, UserVerification

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
    exists = True
    user = db.session.query(User).filter(User.ya_id == ya_id).first()
    if not user:
        exists = False
        user = User(ya_id=ya_id)
        db.session.add(user)
        db.session.commit()

    response = row2dict(user)
    response['success'] = True
    response['exists'] = exists

    return jsonify(response)


@app.route('/user/<ya_id>/code/generate/')
def code_generate(ya_id):
    user = db.session.query(User).filter(User.ya_id == ya_id).first()
    if not user:
        user = User(ya_id=ya_id)
        db.session.add(user)
        db.session.commit()

    expires_before, expires_after = datetime.utcnow() - timedelta(minutes=15), datetime.utcnow() + timedelta(minutes=15)

    existing_codes_query = db.session.query(UserVerification).filter(UserVerification.expires > expires_before)
    existing_codes = [x.code for x in existing_codes_query]
    all_codes = list(map(lambda x: str(x).zfill(6), range(10 ** 6)))

    available_codes = list(set(all_codes) - set(existing_codes))

    user_verification = UserVerification(user_id=user.id, code=choice(available_codes), expires=expires_after)
    db.session.add(user_verification)
    db.session.commit()

    response = row2dict(user_verification)
    response['success'] = True

    return jsonify(response)


@app.route('/user/<ya_id>/code/check/')
def code_check(ya_id):
    user = db.session.query(User).filter(User.ya_id == ya_id).first()
    if not user:
        return jsonify(
            {'success': False, 'message': 'Почему-то Вас нет в нашей базе данных. Попробуйте перезайти в навык!'})

    user_verification = db.session.query(UserVerification).filter(UserVerification.user_id == user.id).first()
    if not user_verification:
        return jsonify(
            {'success': False, 'message': 'Что-то пошло не так... Повторите попытку авторизации в боте!'})

    message = user_verification.received_from
    return jsonify({'success': True, 'message': message})


@app.route('/code/confirm/', methods=['POST'])
def code_confirm():
    return jsonify('API for yandex-alice-hackathon-2020')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True, load_dotenv=True)
