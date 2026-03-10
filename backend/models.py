from app import db
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

    bookings = db.relationship('Booking', backref='service', lazy=True)
    provider_services = db.relationship('ProviderService', backref='service', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'duration': self.duration
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