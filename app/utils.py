from threading import Thread
from app import app, mail
from flask_mail import Message
from flask import request, jsonify
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(' ')[1] if len(auth_header.split(' ')) > 1 else None

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:

            # TODO: Проверка с токеном в сессии
            valid = True

            if not valid:
                return jsonify({'message': 'Invalid token'}), 401
        except:
            return jsonify({'message': 'Token verification failed'}), 401

        return f(*args, **kwargs)

    return decorated

def async_send_mail(app, msg):
    with app.app_context():
	    mail.send(msg)

def send_mail(subject, recipients, msg):
    msg = Message(subject, recipients=[recipients])
    thrd = Thread(target=async_send_mail, args=[app,  msg])
    thrd.start()
    return thrd