from flask import request, jsonify
from app import app, db
from datetime import datetime, timedelta
from functools import wraps
from apscheduler.schedulers.background import BackgroundScheduler
import jwt
import os

# read secret from environment (loaded by app.py)
SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

def clean_exp_reservations():
    with app.app_context():
        from models import Booking
        now = datetime.utcnow()
        expired = Booking.query.filter(
            Booking.status == 'reserved',
            Booking.reserved_until < now
        ).all()
        for booking in expired:
            db.session.delete(booking)
        db.session.commit()
        print(f'Cleaned up {len(expired)} expired reservations.')

scheduler = BackgroundScheduler()
scheduler.add_job(clean_exp_reservations, 'interval', minutes=5)
scheduler.start()

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

    if not data:
        return jsonify({'message': 'No data provided'}), 400
    if not data.get('username'):
        return jsonify({'message': 'Username is required'}), 400
    if not data.get('email'):
        return jsonify({'message': 'Email is required'}), 400
    if not data.get('password'):
        return jsonify({'message': 'Password is required'}), 400
    if not data.get('role') and data['role'] not in ['customer', 'provider']:
        return jsonify({'message': 'Role must be customer or provider'}), 400
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
    category = request.args.get('category')
    if category:
        services = Service.query.filter_by(category=category).all()
    else:
        services = Service.query.all()
    return jsonify([service.to_dict() for service in services])


@app.route('/api/services', methods=['POST'])
@token_required
def create_service(current_user):
    from models import Service, ProviderService
    if current_user.role != 'provider':
        return jsonify({'message': 'Only providers can create services'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    if not data.get('name'):
        return jsonify({'message': 'Service name is required'}), 400
    if not data.get('duration'):
        return jsonify({'message': 'Duration is required'}), 400
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

    if not data:
        return jsonify({'message': 'No data provided'}), 400
    if not data.get('service_id'):
        return jsonify({'message': 'Please select a service'}), 400
    if not data.get('provider_id'):
        return jsonify({'message': 'PLease select a provider'}), 400
    if not data.get('start_time'):
        return jsonify({'message': 'service_id is required'}), 400
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

    if not data:
        return jsonify({'message': 'No data provided'}), 400
    if not data.get('service_id'):
        return jsonify({'message': 'Please select a service'}), 400
    if not data.get('provider_id'):
        return jsonify({'message': 'PLease select a provider'}), 400
    if not data.get('start_time'):
        return jsonify({'message': 'service_id is required'}), 400
    service = Service.query.get_or_404(data['service_id'])
    provider = User.query.get_or_404(data['provider_id'])
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
    from models import Booking, CancellationPolicy
    booking = Booking.query.get_or_404(booking_id)
    # only the customer who made it or the provider may cancel
    if booking.user_id != current_user.id and booking.provider_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    policy = CancellationPolicy.query.filter_by(service_id=booking.service_id).first()
    if policy:
        now = datetime.utcnow()
        start = booking.start_time if hasattr(booking.start_time, 'hour') else datetime.fromisoformat(booking.start_time)
        hours_until = (start - now).total_seconds() / 3600

        if hours_until < policy.hours_before:
            return jsonify({'message': f'Cannot cancel — policy requires {policy.hours_before} hours notice',
                'penalty_percent': policy.penalty_percent,
                'description': policy.description}), 400
        
    booking.status = 'cancelled'
    db.session.commit()
    return jsonify(booking.to_dict())

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from models import User
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        if current_user.role != 'admin':
            return jsonify({'message': 'Admin access required'}),401
        return f(current_user, *args, **kwargs)
    return decorated 

@app.route('/api/bookings/history', methods=['GET'])
@token_required
def booking_history(current_user):
    from models import Booking
    now = datetime.utcnow().isoformat()
    if current_user.role == 'customer':
        bookings = Booking.query.filter(Booking.user_id == current_user.id,
            Booking.end_time < now
        ).all()
    else:
        bookings = Booking.query.filter(Booking.provider_id == current_user.id, 
            Booking.end_time < now).all()
    return jsonify([booking.to_dict() for booking in bookings]), 200

@app.route('/api/bookings/upcoming', methods=['GET'])
@token_required
def upcoming_sessions(current_user):
    from models import Booking
    now = datetime.utcnow().isoformat()
    if current_user.role == 'customer':
        bookings = Booking.query.filter(Booking.user_id == current_user.id, 
            Booking.start_time > now, Booking.status == 'confirmed').all()
    else:
        bookings = Booking.query.filter(Booking.provider_id == current_user.id, 
            Booking.start_time > now, Booking.status == 'confirmed').all()
    return jsonify([booking.to_dict() for booking in bookings]), 200

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_all_users(current_user):
    from models import User
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@app.route('/api/admin/bookings', methods=['GET'])
@admin_required
def get_all_bookings(current_user):
    from models import Booking
    bookings = Booking.query.all()
    return jsonify([booking.to_dict() for booking in bookings]), 200

@app.route('/api/admin/users/<int:user_id>/roles', methods=['PUT'])
@admin_required
def update_user_role(current_user, user_id):
    from models import User 
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    newRole = data.get('role')

    if newRole not in ['customer', 'provider', 'admin']:
        return jsonify({'message': 'Invalid role.'})
    
    user.role = newRole
    db.session.commit()
    return jsonify({'message': f'User role updated to {newRole}', 'user': user.to_dict()}), 200

@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify(current_user.to_dict()), 200

@app.route('/api/profile', methods=['PUT'])
@token_required
def edit_profile(current_user):
    from models import User
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided'}), 400    
    if 'username' in data:
        existing = User.query.filter_by(username=data['username']).first()
        if existing and existing.id != current_user.id:
            return jsonify({'message': 'Username is already taken'}), 400
        current_user.username = data['username']
    
    if 'bio' in data:
        current_user.bio = data['bio']
    if 'image' in data:
        current_user.image = data['image']
    db.session.commit()
    return jsonify({'message': 'Profile successfully updated!', 'user': current_user.to_dict()})

@app.route('/api/feedback', methods=['POST'])
@token_required
def create_feedback(current_user):
    from models import Feedback, Booking
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided'}), 400
    if not data.get('booking_id'):
        return jsonify({'message': 'Booking id is required'}), 400
    if not data.get('service_id'):
        return jsonify({'message': 'Service id is required'}), 400
    if not data.get('rating'):
        return jsonify({'message': 'Rating is required'}), 400
    if not isinstance(data['rating'], int) or data['rating'] < 1 or data['rating'] > 5:
        return jsonify({'message': 'Rating must be between 1 and 5'}), 400
    
    booking = Booking.query.get_or_404(data['booking_id'])
    if booking.user_id != current_user.id:
        return jsonify({'message': 'You can only leave feedback for your own bookings'}), 400
    if booking.status != 'confirmed':
        return jsonify({'message': 'You can only leave feedback for confirmed bookings'}), 400
    
    existing = Feedback.query.filter_by(booking_id=data['booking_id'], user_id=current_user.id).first()
    if existing:
        return jsonify({'message': 'You have already left feedback for this booking'})
    
    feedback = Feedback(
        booking_id=data['booking_id'],
        user_id=current_user.id,
        service_id=data['service_id'],
        rating=data['rating'],
        comment=data.get('comment')
    )
    db.session.add(feedback)
    db.session.commit()
    return jsonify(feedback.to_dict()), 201

@app.route('/api/feedback/service/<int:service_id>', methods=['GET'])
def get_feedback(service_id):
    from models import Feedback
    feedback = Feedback.query.filter_by(service_id=service_id).all()
    return jsonify([f.to_dict() for f in feedback]), 200

@app.route('/api/schedule', methods=['GET'])
@token_required
def get_schedule(current_user):
    from models import ProviderSchedule
    if current_user.role != 'provider':
        return jsonify({'message': 'Only providers can view their schedule'}), 403
    
    schedule = ProviderSchedule.query.filter_by(provider_id = current_user.id, is_active=True).all()
    return jsonify([slot.to_dict() for slot in schedule]), 200

@app.route('/api/schedule', methods=['POST'])
@token_required
def create_schedule(current_user):
    from models import ProviderSchedule
    if current_user.role != 'provider':
        return jsonify({'message': 'Only providers can set their schedule'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400
    if data.get('day_of_week') is None:
        return jsonify({'message': 'day_of_week is required (0=Monday, 6=Sunday)'}), 400
    if not data.get('start_time'):
        return jsonify({'message': 'Start time is required (format: 09:00)'}), 400
    if not data.get('end_time'):
        return jsonify({'message': 'End time is required (format: 17:00)'}), 400
    
    slot = ProviderSchedule(provider_id=current_user.id, day_of_week=data['day_of_week'],
        start_time=data['start_time'], end_time=data['end_time'], max_attendees=data.get('max_attendees', 1))
    db.session.add(slot)
    db.session.commit()
    return jsonify(slot.to_dict()), 201

@app.route('/api/schedule/<int:slot_id>', methods=['PUT'])
@token_required
def update_schedule(current_user, slot_id):
    from models import ProviderSchedule
    slot = ProviderSchedule.query.get_or_404(slot_id)
    if slot.provider_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    if 'day_of_week' in data:
        slot.day_of_week = data['day_of_week']
    if 'start_time' in data:
        slot.start_time = data['start_time']
    if 'end_time' in data:
        slot.end_time = data['end_time']
    if 'is_active' in data:
        slot.is_active = data['is_active']
    db.session.commit()
    return jsonify(slot.to_dict()), 200

@app.route('/api/schedule/<int:slot_id>', methods=['DELETE'])
@token_required
def delete_schedule(current_user, slot_id):
    from models import ProviderSchedule
    slot = ProviderSchedule.query.get_or_404(slot_id)

    if slot.provider_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    slot.is_active = False
    db.session.commit()
    return jsonify({'message': 'Schedule slot removed'}), 200

@app.route('/api/schedule/provider/<int:provider_id>', methods=['GET'])
def get_provider_schedule(provider_id):
    from models import ProviderSchedule
    schedule = ProviderSchedule.query.filter_by(provider_id=provider_id, is_active=True).all()
    return jsonify([slot.to_dict() for slot in schedule]), 200

@app.route('/api/availability/<int:provider_id>', methods=['GET'])
def get_availability(provider_id):
    from models import ProviderSchedule, Booking
    from datetime import date, timedelta

    start_date = request.args.get('start_date', date.today().isoformat())
    end_date = request.args.get('end_date', (date.today() + timedelta(days=7)).isoformat())
    schedule = ProviderSchedule.query.filter_by(provider_id=provider_id, is_active=True).all()
    
    if provider_id != 'provider':
        return jsonify({'message': 'This is not a provider'})
    if not schedule:
        return jsonify({'message': 'Provider has no schedule set'}), 404
    
    existing = Booking.query.filter(
        Booking.provider_id == provider_id, 
        Booking.status.in_(['confirmed', 'reserved']),
        Booking.start_time >= start_date,
        Booking.start_time <= end_date
    ).all()

    booked = [{
        'start_time': b.start_time.isoformat() if hasattr(b.start_time, 'isoformat') else b.start_time, 
        'end_time': b.end_time.isoformat() if hasattr(b.end_time, 'isoformat') else b.end_time
    }for b in existing]

    available = []
    current = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    while current <= end:
        day_of_week = current.weekday()
        daySchedule = [s for s in schedule if s.day_of_week == day_of_week]

        if daySchedule:
            for slot in daySchedule:
                available.append({
                    'date': current.isoformat(),
                    'dayName': slot.to_dict()['dayName'],
                    'start_time': slot.start_time,
                    'end_time': slot.end_time,
                    'max_attendees': slot.max_attendees })
            
        current += timedelta(days=1)
    return jsonify({
        'provider_id': provider_int,
        'available_days': available,
        'booked_slots': booked
    }), 200

@app.route('/api/cancellation-policy', methods=['POST'])
@admin_required
def create_policy(current_user):
    from models import CancellationPolicy
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided'}), 400
    if not data.get('service_id'):
        return jsonify({'message': 'service_id is required'}), 400
    if data.get('hours_before') is None:
        return jsonify({'message': 'hours before is required'}), 400
    
    existing = CancellationPolicy.query.filter_by(service_id=data['service_id']).first()
    if existing:
        return jsonify({'message': 'Policy already exists for this service.'})
    policy = CancellationPolicy(service_id=data['service_id'], hours_before=data['hours_before'],
            penalty=data.get('penalty', 0), description=data.get('description'))
    db.session.add(policy)
    db.session.commit()
    return jsonify(policy.to_dict()), 201

@app.route('/api/cancellation-policy/<int:service_id>', methods=['GET'])
def get_policy(service_id):
    from models import CancellationPolicy
    policy = CancellationPolicy.query.filter_by(service_id=service_id).first()
    if not policy:
        return jsonify({'message': 'No cancellation policy set for this service.'})
    return jsonify(policy.to_dict()), 200

@app.route('/api/cancellation-policy/<int:policy_id>', methods=['PUT'])
@admin_required
def update_policy(current_user, policy_id):
    from models import CancellationPolicy
    policy = CancellationPolicy.query.get_or_404(policy_id)
    data = request.get_json()

    if 'hours_before' in data:
        policy.hours_before = data['hours_before']
    if 'penalty' in data:
        policy.penalty = data['penalty']
    if 'description' in data:
        policy.description = data['description']

    db.session.commit()
    return jsonify(policy.to_dict()), 200
@app.route('/')
def home():
    return 'BookEase is running!'
