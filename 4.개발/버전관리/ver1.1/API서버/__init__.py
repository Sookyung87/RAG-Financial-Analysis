from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy() #SQLAlchemy 객체 생성

def run_app():
    app = Flask(__name__) #Flask 객체 생성
    app.config['SECRET_KEY'] = 'LLMJSH_test_key' #비밀키 설정, 배포 시 복잡한 암호로 수정해야함
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///RAGdata.db" #RAGdata.db가 해당 디렉토리(app)에 존재하지 않으면 새로 만들고, 존재하면 그것을 사용.
    db.init_app(app) #Flask 객체와 SQLAlchemy를 연결

    with app.app_context():
        import DB_structure #db구조 정의
        db.create_all() #db생성

    from routes import setup_routes 
    setup_routes(app) #라우트 연결


    return app