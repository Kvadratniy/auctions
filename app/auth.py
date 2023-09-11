
from flask import Blueprint, request, jsonify, session, current_app
import jwt
from datetime import datetime, timedelta
from app import db
from .models import User

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return jsonify({'message': 'Пользователь с таким именем уже существует'})

    hashed_password = User.make_password_hash(password)
    new_user = User(username=username, password=hashed_password, email=email)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Регистрация прошла успешно'})

@auth.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not User.is_password_valid(user, password):
        return jsonify({'message': 'Неверные имя пользователя или пароль'}), 401

    session['logged_in'] = True
    token = jwt.encode({
        'user': username,
        'expiration': str(datetime.utcnow() + timedelta(seconds=60))
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({ 'token': token })

@auth.route('/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Выход выполнен'})
