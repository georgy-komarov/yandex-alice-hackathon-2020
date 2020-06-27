import os
from dotenv import load_dotenv
from random import choice
from datetime import datetime, timedelta

from flask import Flask, Response, jsonify, request

from extensions import db, migrate
from models import User, UserVerification, UserChannel

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


@app.route('/api/user/<ya_id>/')
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


@app.route('/api/user/telegram/<tg_id>/')
def user_get_by_tg(tg_id: str):
    response = {}

    user = db.session.query(User).filter(User.tg_id == tg_id).first()
    if not user:
        exists = False
    else:
        exists = True
        response.update(row2dict(user))

    response['success'] = True
    response['exists'] = exists

    return jsonify(response)


@app.route('/api/user/telegram/<tg_id>/feed/')
def user_tg_feed(tg_id: str):
    response = {}

    user = db.session.query(User).filter(User.tg_id == tg_id).first()
    if not user:
        success = False
    else:
        user_feed_query = db.session.query(UserChannel).filter(UserChannel.user_id == user.id).order_by(
            UserChannel.id.desc())
        user_feed = [row2dict(x) for x in list(user_feed_query)]

        response['feed'] = user_feed
        success = True

    response['success'] = success

    return jsonify(response)


@app.route('/api/user/telegram/<tg_id>/feed/add/', methods=['POST'])
def user_tg_feed_add(tg_id: str):
    source_url = request.form['tape_url']
    source_name = request.form['tape_name']
    source_type = 'Telegram'

    response = {}

    user = db.session.query(User).filter(User.tg_id == tg_id).first()
    if not user:
        success = False
    else:
        user_feed_new = UserChannel(user_id=user.id, source_url=source_url, source_name=source_name,
                                    source_type=source_type)
        db.session.add(user_feed_new)
        db.session.commit()

        success = True

    response['success'] = success

    return jsonify(response)


@app.route('/api/user/telegram/<tg_id>/feed/delete/', methods=['POST'])
def user_tg_feed_delete(tg_id: str):
    source_number = int(request.form['tape_id'])

    response = {}

    user = db.session.query(User).filter(User.tg_id == tg_id).first()
    if not user:
        success = False
    else:
        user_feed_query = db.session.query(UserChannel).filter(UserChannel.user_id == user.id).order_by(
            UserChannel.id.desc())
        user_feed = list(user_feed_query)

        to_delete = user_feed[source_number - 1]
        db.session.delete(to_delete)
        db.session.commit()

        success = True
        response['deleted'] = row2dict(to_delete)

    response['success'] = success

    return jsonify(response)


@app.route('/api/user/vk/<vk_id>/')
def user_get_by_vk(vk_id: str):
    response = {}

    user = db.session.query(User).filter(User.vk_id == vk_id).first()
    if not user:
        exists = False
    else:
        exists = True
        response.update(row2dict(user))

    response['success'] = True
    response['exists'] = exists

    return jsonify(response)


@app.route('/api/user/vk/<vk_id>/feed/')
def user_vk_feed(vk_id: str):
    response = {}

    user = db.session.query(User).filter(User.vk_id == vk_id).first()
    if not user:
        success = False
    else:
        user_feed_query = db.session.query(UserChannel).filter(UserChannel.user_id == user.id).order_by(
            UserChannel.id.desc())
        user_feed = [row2dict(x) for x in list(user_feed_query)]

        response['feed'] = user_feed
        success = True

    response['success'] = success

    return jsonify(response)


@app.route('/api/user/vk/<vk_id>/feed/add', methods=['POST'])
def user_vk_feed_add(vk_id: str):
    source_id = int(request.form['group_id'])
    source_name = request.form['group_name']
    source_type = 'VK'

    response = {}

    user = db.session.query(User).filter(User.vk_id == vk_id).first()
    if not user:
        success = False
    else:
        user_feed_new = UserChannel(user_id=user.id, source_id=source_id, source_name=source_name,
                                    source_type=source_type)
        db.session.add(user_feed_new)
        db.session.commit()

        success = True

    response['success'] = success

    return jsonify(response)


@app.route('/api/user/telegram/<vk_id>/feed/delete/', methods=['POST'])
def user_vk_feed_delete(vk_id: str):
    source_number = int(request.form['group_id'])

    response = {}

    user = db.session.query(User).filter(User.vk_id == vk_id).first()
    if not user:
        success = False
    else:
        user_feed_query = db.session.query(UserChannel).filter(UserChannel.user_id == user.id).order_by(
            UserChannel.id.desc())
        user_feed = list(user_feed_query)

        to_delete = user_feed[source_number - 1]
        db.session.delete(to_delete)
        db.session.commit()

        success = True
        response['deleted'] = row2dict(to_delete)

    response['success'] = success

    return jsonify(response)


@app.route('/api/user/<ya_id>/code/generate/')
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


@app.route('/api/user/<ya_id>/code/check/')
def code_check(ya_id, complete=False):
    user = db.session.query(User).filter(User.ya_id == ya_id).first()
    if not user:
        return jsonify(
            {'success': False, 'message': 'Почему-то Вас нет в нашей базе данных. Попробуйте перезайти в навык!'})

    user_verification = db.session.query(UserVerification).filter(UserVerification.user_id == user.id).order_by(
        UserVerification.id.desc()).first()
    if not user_verification:
        return jsonify(
            {'success': False, 'message': 'Что-то пошло не так... Повторите попытку авторизации в боте!'})

    message = user_verification.received_from
    if not message:
        return jsonify({'success': False, 'message': message})

    if complete:
        if bot_type := user_verification.bot_type == 'Telegram':
            user.tg_id = user_verification.bot_user_id
        elif bot_type == 'VK':
            user.vk_id = user_verification.bot_user_id
        else:
            return jsonify(
                {'success': False, 'message': 'Что-то пошло не так... Повторите попытку авторизации в боте!'})

        db.session.add(user)
        db.session.commit()
        return jsonify({'success': True})

    return jsonify({'success': True, 'message': message})


@app.route('/api/user/<ya_id>/code/complete/')
def code_complete(ya_id):
    return code_check(ya_id, complete=True)


@app.route('/api/code/confirm/', methods=['POST'])
def code_confirm():
    received_from = request.form['received_from']
    code = request.form['code']
    bot_type = request.form['bot_type']
    bot_user_id = request.form['bot_user_id']

    user_verification = db.session.query(UserVerification).filter(UserVerification.code == code).filter(
        UserVerification.expires >= datetime.utcnow()).order_by(UserVerification.id.desc()).first()

    if user_verification:
        user_verification.received_from = received_from
        user_verification.bot_type = bot_type
        user_verification.bot_user_id = bot_user_id
        user_verification.expires = datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0)

        db.session.add(user_verification)
        db.session.commit()

        return jsonify({'success': True})
    return jsonify({'success': False})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True, load_dotenv=True)
