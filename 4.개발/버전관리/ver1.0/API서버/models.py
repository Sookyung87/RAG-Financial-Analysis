# 사용자, 공시, 주식 분석 데이터를 저장하고 관리하는 데이터베이스 모델을 정의
# 이 코드를 통해 DB에서 사용자 정보를 관리하고, 주식 관련 데이터를 저장하고 조회할 수 있음

from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(64), primary_key=True)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Chat(db.Model):
    __tablename__ = 'chats'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.String(64), db.ForeignKey('users.id'), nullable=False)
    questions = db.Column(db.JSON)
    answers = db.Column(db.JSON)

class Disclosure(db.Model):
    __tablename__ = 'disclosures'
    id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    title = db.Column(db.String(200))
    body = db.Column(db.Text)
    source = db.Column(db.String(200))

class StockAnalysis(db.Model):
    __tablename__ = 'stock_analysis'
    id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String(100), nullable=False)
    eps = db.Column(db.Float)
    bps = db.Column(db.Float)
    per = db.Column(db.Float)
    industry_per = db.Column(db.Float)
    pbr = db.Column(db.Float)
    dividend_yield = db.Column(db.Float)
    source = db.Column(db.String(200))
