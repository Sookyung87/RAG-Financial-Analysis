import os
from flask import Flask, render_template, request, jsonify
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///stocks.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query_stock', methods=['POST'])
def query_stock():
    try:
        data = request.json
        user_id = data.get('user_id')
        password = data.get('password')
        message = data.get('message')  # Changed from query to message

        response = requests.post(
            'http://144.24.84.78:8000/api/stock-query',
            json={
                'id': user_id,
                'password': password,
                'message': message
            }
        )
        
        if response.status_code == 200:
            return jsonify({"success": True, "data": response.json()})
        else:
            return jsonify({
                "success": False, 
                "error": f"API request failed with status code: {response.status_code}"
            }), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

with app.app_context():
    import models
    db.create_all()
