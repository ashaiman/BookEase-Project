from flask import request, jsonify
from app import app, db
from datetime import datetime, timedelta
from functools import wraps
import jwt
import os

# read secret from environment (loaded by app.py)
SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from models import User
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            token = token.split(' ')[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# User Authentication Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    from models import User
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400

    user = User(username=data['username'], email=data['email'], role=data.get('role', 'customer'))
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    from models import User
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        token = jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=24)},
                          SECRET_KEY, algorithm='HS256')
        return jsonify({'token': token, 'user': user.to_dict()})
    return jsonify({'message': 'Invalid credentials'}), 401

# Service Routes
@app.route('/api/services', methods=['GET'])
def get_services():
    from models import Service
    services = Service.query.all()
    return jsonify([service.to_dict() for service in services])

@app.route('/api/services', methods=['POST'])
@token_required
def create_service(current_user):
    from models import Service, ProviderService
    if current_user.role != 'provider':
        return jsonify({'message': 'Only providers can create services'}), 403

    data = request.get_json()
    service = Service(
        name=data['name'],
        description=data.get('description'),
        duration=data['duration']
    )
    db.session.add(service)
    db.session.commit()

    # Associate service with provider
    provider_service = ProviderService(provider_id=current_user.id, service_id=service.id)
    db.session.add(provider_service)
    db.session.commit()

    return jsonify(service.to_dict()), 201

@app.route('/api/services/<int:service_id>', methods=['PUT'])
@token_required
def update_service(current_user, service_id):
    from models import Service, ProviderService
    service = Service.query.get_or_404(service_id)
    # Check if user is the provider of this service
    if not ProviderService.query.filter_by(provider_id=current_user.id, service_id=service_id).first():
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()
    service.name = data.get('name', service.name)
    service.description = data.get('description', service.description)
    service.duration = data.get('duration', service.duration)
    db.session.commit()
    return jsonify(service.to_dict())

@app.route('/api/services/<int:service_id>', methods=['DELETE'])
@token_required
def delete_service(current_user, service_id):
    from models import Service, ProviderService
    service = Service.query.get_or_404(service_id)
    # Check if user is the provider of this service
    if not ProviderService.query.filter_by(provider_id=current_user.id, service_id=service_id).first():
        return jsonify({'message': 'Unauthorized'}), 403

    db.session.delete(service)
    db.session.commit()
    return jsonify({'message': 'Service deleted'})


# Booking Routes
@app.route('/api/bookings', methods=['GET'])
@token_required
def get_bookings(current_user):
    from models import Booking
    if current_user.role == 'customer':
        bookings = Booking.query.filter_by(user_id=current_user.id).all()
    else:  # provider
        bookings = Booking.query.filter_by(provider_id=current_user.id).all()

    return jsonify([booking.to_dict() for booking in bookings])

@app.route('/api/bookings', methods=['POST'])
@token_required
def create_booking(current_user):
    from models import Service, User, Booking, ProviderService
    data = request.get_json()
    service = Service.query.get_or_404(data['service_id'])
    provider = User.query.get_or_404(data['provider_id'])

    if provider.role != 'provider':
        return jsonify({'message': 'Invalid provider'}), 400

    # Check if provider offers this service
    if not ProviderService.query.filter_by(provider_id=provider.id, service_id=service.id).first():
        return jsonify({'message': 'Provider does not offer this service'}), 400

    start_time = datetime.fromisoformat(data['start_time'])
    end_time = start_time + timedelta(minutes=service.duration)

    # Check for conflicts
    conflict = Booking.query.filter(
        Booking.provider_id == provider.id,
        Booking.status.in_(['confirmed', 'reserved']),
        db.or_(
            db.and_(Booking.start_time <= start_time, Booking.end_time > start_time),
            db.and_(Booking.start_time < end_time, Booking.end_time >= end_time),
            db.and_(Booking.start_time >= start_time, Booking.end_time <= end_time)
        )
    ).first()

    if conflict:
        return jsonify({'message': 'Time slot is not available'}), 409

    # Create booking
    booking = Booking(
        user_id=current_user.id,
        service_id=service.id,
        provider_id=provider.id,
        start_time=start_time,
        end_time=end_time,
        status='confirmed'
    )
    db.session.add(booking)
    db.session.commit()

    return jsonify(booking.to_dict()), 201

@app.route('/api/bookings/<int:booking_id>/reserve', methods=['POST'])
@token_required
def reserve_booking(current_user, booking_id):
    from models import Service, User, Booking
    data = request.get_json()
    service = Service.query.get_or_404(data['service_id'])
    provider = User.query.get_or_404(data['provider_id'])

    start_time = datetime.fromisoformat(data['start_time'])
    end_time = start_time + timedelta(minutes=service.duration)

    # Check for conflicts
    conflict = Booking.query.filter(
        Booking.provider_id == provider.id,
        Booking.status.in_(['confirmed', 'reserved']),
        db.or_(
            db.and_(Booking.start_time <= start_time, Booking.end_time > start_time),
            db.and_(Booking.start_time < end_time, Booking.end_time >= end_time),
            db.and_(Booking.start_time >= start_time, Booking.end_time <= end_time)
        )
    ).first()

    if conflict:
        return jsonify({'message': 'Time slot is not available'}), 409

    # Create temporary reservation (15 minutes)
    booking = Booking(
        user_id=current_user.id,
        service_id=service.id,
        provider_id=provider.id,
        start_time=start_time,
        end_time=end_time,
        status='reserved',
        reserved_until=datetime.utcnow() + timedelta(minutes=15)
    )
    db.session.add(booking)
    db.session.commit()

    return jsonify(booking.to_dict()), 201

@app.route('/api/bookings/<int:booking_id>/confirm', methods=['PUT'])
@token_required
def confirm_booking(current_user, booking_id):
    from models import Booking
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403

    if booking.status != 'reserved':
        return jsonify({'message': 'Booking is not reserved'}), 400

    if datetime.utcnow() > booking.reserved_until:
        db.session.delete(booking)
        db.session.commit()
        return jsonify({'message': 'Reservation expired'}), 410

    booking.status = 'confirmed'
    booking.reserved_until = None
    db.session.commit()

    return jsonify(booking.to_dict())

@app.route('/api/bookings/<int:booking_id>/cancel', methods=['PUT'])
@token_required
def cancel_booking(current_user, booking_id):
    from models import Booking
    booking = Booking.query.get_or_404(booking_id)
    # only the customer who made it or the provider may cancel
    if booking.user_id != current_user.id and booking.provider_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403
    booking.status = 'cancelled'
    db.session.commit()
    return jsonify(booking.to_dict())


