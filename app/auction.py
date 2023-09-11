from flask import Blueprint, request, jsonify
from sqlalchemy import desc
from datetime import datetime
from app import db, scheduler
from .models import Auction, Bid, User
from .utils import token_required, send_mail

auction = Blueprint('auction', __name__)

def complete_auction(auction_id):
    bids = Bid.query.filter_by(auction_id=auction_id).order_by(desc(Bid.bid_amount))
    winner_bid = bids.first()

    recipients = []
    for bid in bids:
        recipients.append(bid.user.email)

    send_mail(
        'Торги закрыты',
        recipients=[recipients],
        msg=f'Торги закрыты, победитель {winner_bid.user.username}'
    )

# Создание аукциона
@auction.route('/auction', methods=['POST'])
@token_required
def create_auction():
    data = request.get_json()
    end_time = datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S')

    new_auction = Auction(
        user_id=data['user_id'],
        end_time=end_time,
        item_description=data['item_description'],
        starting_price=data['starting_price'],
        price_increment=data['price_increment'],
        current_price=data['price_increment'],
    )

    db.session.add(new_auction)
    db.session.commit()

    users = User.query.filter(User.id != data['user_id']).all()
    recipients = []
    for user in users:
        recipients.append(user.email)

    send_mail(
        'Торги открыты',
        recipients=[recipients],
        msg='Торги открыты'
    )

    scheduler.add_job(
        id=f'end_auction_{new_auction.id}',
        func=complete_auction,
        trigger='date',
        run_date=end_time,
        args=[new_auction.id]
    )

    return jsonify({'message': end_time})

# Получение списка аукционов
@auction.route('/auctions', methods=['GET'])
@token_required
def get_all_auctions():
    filter_type = request.args.get('filter', 'all')

    if filter_type == 'active':
        auctions = Auction.query.filter(Auction.end_time > datetime.now()).all()
    elif filter_type == 'completed':
        auctions = Auction.query.filter(Auction.end_time <= datetime.now()).all()
    else:
        auctions = Auction.query.all()

    result = []
    for auction in auctions:
        result.append({
            'id': auction.id,
            'user_id': auction.user_id,
            'end_time': auction.end_time,
            'item_description': auction.item_description,
            'starting_price': auction.starting_price,
            'price_increment': auction.price_increment,
            'current_price': auction.current_price
        })
    return jsonify(result)

# Получение расширенного списка аукционов со ставками
@auction.route('/auctions/<int:auction_id>', methods=['GET'])
@token_required
def get_auction_details(auction_id):
    auction = Auction.query.get(auction_id)

    if not auction:
        return jsonify({'message': 'Аукцион не найден'}), 404

    # Получаем список ставок для аукциона
    bids = Bid.query.filter_by(auction_id=auction.id).all()

    # Создаем список, содержащий информацию о ставках и именах пользователей
    bids_info = []
    for bid in bids:
        user = User.query.get(bid.user_id)
        bids_info.append({
            'bid_amount': bid.bid_amount,
            'user_name': user.username
        })

    return jsonify({
        'user_id': auction.user_id,
        'end_time': auction.end_time,
        'item_description': auction.item_description,
        'price_increment': auction.price_increment,
        'current_price': auction.current_price,
        'bids': bids_info
    })

# Создание ставки
@auction.route('/auctions/<int:auction_id>/bids', methods=['POST'])
@token_required
def create_bid(auction_id):
    data = request.get_json()
    user_id = data['user_id']

    auction = Auction.query.get(auction_id)

    if not auction:
        return jsonify({'message': 'Аукцион не найден'}), 404

    if auction.user_id == user_id:
        return jsonify({'message': 'Вы не можете делать ставки на свой собственный аукцион'}), 403

    if not auction.is_active:
        return jsonify({'message': 'Аукцион неактивен'}), 403

    if auction.end_time <= datetime.now():
        return jsonify({'message': 'Аукцион завершен'}), 403

    lowerPrice = auction.current_price + auction.price_increment
    if data['bid_amount'] <= lowerPrice:
        return jsonify({'message': 'Сумма ставки должна быть больше ' + str(lowerPrice)}), 400

    new_bid = Bid(
        auction_id=auction_id,
        user_id=user_id,
        bid_amount=data['bid_amount']
    )

    auction.current_price=data['bid_amount']
    db.session.add(new_bid)
    db.session.commit()

    bids = Bid.query.filter_by(auction_id=auction_id).filter(User.id != data['user_id']).all()
    recipients = []
    for bid in bids:
        recipients.append(bid.user.email)

    send_mail(
        'Цена изменилась',
        recipients=[recipients],
        msg='Цена изменилась'
    )

    return jsonify({'message': 'Ставка установлена'})
