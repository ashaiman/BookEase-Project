from flask import Flask
from extensions import db
from flask_cors import CORS
import os
from dotenv import load_dotenv

# load variables from .env file if present
load_dotenv()

app = Flask(__name__)
CORS(app)
# Ensure instance folder exists
instance_path = os.path.join(os.path.dirname(__file__), 'instance')
os.makedirs(instance_path, exist_ok=True)

# Database configuration using absolute path
#db_path = os.path.join(instance_path, 'bookease.db')
#db_uri = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
db_uri = os.environ.get('DATABASE_URL')
#db_uri = f'sqlite:///{db_path}'
if db_uri:
    if db_uri.startswith("postgres://"):
        db_uri = db_uri.replace("postgres://", "postgresql://", 1)
else: 
    db_path = os.path.join(instance_path, 'bookease.db')
    db_uri = f'sqlite:///{db_path}'
        
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}
#print(f"Using database: {db_path}")
db.init_app(app)

# Import models and routes after db initialization
from models import *
from routes import *

with app.app_context():
    from models import User
    db.create_all()
    print(f'Registered Tables: {db.metadata.tables.keys()}')
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
