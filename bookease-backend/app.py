from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# This tells Flask to create a local SQLite database file called 'bookease.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookease.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DATABASE MODELS ---

# 1. Users Table 
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    passwordHash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='Student')
    bio = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)

# 2. Services Table 
class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False) 
    is_active = db.Column(db.Boolean, default=True)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, nullable=False)
    provider_id = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Active')

class ProviderService(db.Model):
    __tablename__ = 'provider_services'
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, nullable=False)
    service_id = db.Column(db.Integer, nullable=False)
    duration_min = db.Column(db.Integer, nullable=False) 
    is_active = db.Column(db.Boolean, default=True)

# This creates the database file and tables if they don't exist yet
with app.app_context():
    db.create_all()

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400
    hashed_password = generate_password_hash(data['password'])
    
    new_user = User(
        name=data['name'],
        email=data['email'],
        passwordHash=hashed_password,
        role=data.get('role', 'Student') 
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User successfully registered!"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and check_password_hash(user.passwordHash, data['password']):
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "name": user.name,
                "role": user.role
            }
        }), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401
    
@app.route('/api/services', methods=['GET'])
def get_services():
    return jsonify({"status": "Database is ready for BookEase"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)