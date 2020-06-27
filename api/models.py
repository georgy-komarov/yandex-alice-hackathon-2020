from datetime import datetime

from extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    ya_id = db.Column(db.String(64), nullable=False)
    tg_id = db.Column(db.Integer, nullable=True)
    vk_id = db.Column(db.Integer, nullable=True)


class UserVerification(db.Model):
    __tablename__ = 'users_verification'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    code = db.Column(db.String(6), nullable=False)
    expires = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    bot_type = db.Column(db.String(8), nullable=True)
    bot_user_id = db.Column(db.Integer, nullable=True)
    received_from = db.Column(db.String(512), nullable=True)


class UserChannel(db.Model):
    __tablename__ = 'users_channels'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    source_id = db.Column(db.Integer, nullable=True)
    source_url = db.Column(db.String(1024), nullable=True)
    source_name = db.Column(db.String(512), nullable=False)
    source_type = db.Column(db.String(8), nullable=False)
