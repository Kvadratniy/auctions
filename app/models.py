from sqlalchemy import func
from app import db
import bcrypt

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    @staticmethod
    def make_password_hash(password):
        hash = bcrypt.hashpw(password=password.encode('utf-8'), salt=bcrypt.gensalt())
        return hash.decode('utf-8')

    def is_password_valid(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def __repr__(self):
        return f'<User {self.username}>'

class Auction(db.Model):
    __tablename__ = 'auctions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('auctions', lazy=True))
    end_time = db.Column(db.DateTime, nullable=False)
    item_description = db.Column(db.String(255), nullable=False)
    starting_price = db.Column(db.Float, nullable=False)
    price_increment = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False, default=0.0)

    def __repr__(self):
        return f'<Auction {self.id}>'


class Bid(db.Model):
    __tablename__ = 'bids'

    id = db.Column(db.Integer, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auctions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('bids', lazy=True))
    bid_amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, server_default=func.now())

    def __repr__(self):
        return f'<Bid {self.id}>'
