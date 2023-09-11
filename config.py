
class BaseConfig:
    SECRET_KEY = 'SECRETKEY'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS=False


class DevelopmentConfig(BaseConfig):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'postgresql://pv_user:development@127.0.0.1:5432/auction'

    MAIL_USERNAME = 'MAIL_USERNAME'
    MAIL_DEFAULT_SENDER = 'MAIL_DEFAULT_SENDER'
    MAIL_PASSWORD = 'MAIL_PASSWORD'
