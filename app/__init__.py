from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

db = SQLAlchemy(app)
mail = Mail(app)
scheduler = APScheduler()

from .auth import auth
from .auction import auction

app.register_blueprint(auth, url_prefix='/')
app.register_blueprint(auction, url_prefix='/')

scheduler.start()