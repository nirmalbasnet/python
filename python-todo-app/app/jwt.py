import jwt
from flask import current_app


def encode(payload):
    return jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')


def decode(token):
    return jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
