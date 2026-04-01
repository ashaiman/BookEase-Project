from flask import Flask
from flask_sqlalchemy import SQLAlchemy
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
db_path = os.path.join(instance_path, 'bookease.db')
#db_uri = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
db_uri = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print(f"Using database: {db_path}")
db = SQLAlchemy(app)

# Import models and routes after db initialization
from models import *
from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)