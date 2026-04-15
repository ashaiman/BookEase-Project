from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Simplified models for BookEase class project.
# We keep only the fields needed for users, services, and bookings.

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')  # customer or provider
    bio = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)

    bookings = db.relationship('Booking', foreign_keys='Booking.user_id', backref='user', lazy=True)
    provider_bookings = db.relationship('Booking', foreign_keys='Booking.provider_id', backref='provider', lazy=True)
    provider_services = db.relationship('ProviderService', backref='provider', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role
        }

class Service(db.Model):
    __tablename__ = 'service'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    duration = db.Column(db.Integer, nullable=False)  # minutes
    category = db.Column(db.String(50), nullable=True)

    bookings = db.relationship('Booking', backref='service', lazy=True)
    provider_services = db.relationship('ProviderService', backref='service', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'duration': self.duration,
            'category' : self.category
        }

class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='confirmed')  # confirmed, cancelled, reserved
    reserved_until = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        # only essential fields
        return {
            'id': self.id,
            'user_id': self.user_id,
            'service_id': self.service_id,
            'provider_id': self.provider_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'status': self.status,
            'reserved_until': self.reserved_until.isoformat() if self.reserved_until else None
        }

class ProviderService(db.Model):
    __tablename__ = 'provider_service'
    # allow redefining when module is reloaded (helps during interactive sessions)
    __table_args__ = (db.UniqueConstraint('provider_id', 'service_id', name='unique_provider_service'),
                     {'extend_existing': True})

    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'provider_id': self.provider_id,
            'service_id': self.service_id
        }
    
class Feedback(db.Model):
    __tablename__= 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False )
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 
            'booking_id': self.booking_id,
            'user_id': self.user_id,
            'service_id': self.service_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()

        }
    
class ProviderSchedule(db.Model):
    __tablename__ = 'provider_schedule'
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.String(5), nullable=False)
    end_time = db.Column(db.String(5), nullable=False)
    max_attendees = db.Column(db.Integer, nullable=False, default = 1)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return {
            'id': self.id,
            'provider_id': self.provider_id,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'max_attendees': self.max_attendees,
            'is_active': self.is_active

        }
class CancellationPolicy(db.Model):
    __tablename__ = 'cancellation_policy'
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    hours_before = db.Column(db.Integer, nullable=False)
    penalty = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id' : self.id,
            'service_id': self.service_id,
            'hours_before': self.hours_before,
            'penalty': self.penalty,
            'description': self.description
        }  