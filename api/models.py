from app import app

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    __tablename__ = 'users'

    ya_id = db.Column(db.Integer, primary_key=True)
    tg_id = db.Column(db.Integer, nullable=True)
    vk_id = db.Column(db.Integer, nullable=True)

    tg_code = db.Column(db.Integer, nullable=False)
    tg_code_expires = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    vk_code = db.Column(db.Integer, nullable=False)
    vk_code_expires = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
