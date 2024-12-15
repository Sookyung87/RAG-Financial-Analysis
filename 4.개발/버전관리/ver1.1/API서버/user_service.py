from flask import jsonify
from DB_structure import User
from __init__ import db
from werkzeug.security import generate_password_hash, check_password_hash

def find_userid (request_id: str) -> jsonify:
    user = User.query.filter_by(id=request_id).first()

    if user:
        return jsonify({
            'success' : False,
            'message' : '해당 아이디가 이미 존재합니다.'
        })
    else :
        return jsonify({
            'success' : True,
            'message' : '해당 아이디를 생성할 수 있습니다.'
        })


def auth_userid (request_id: str, request_pw: str)-> bool:
    user_id = User.query.filter_by(id=request_id).first()
    
    if user_id:
        if check_password_hash(user_id.password_hash, request_pw):
            return True
        else :
            return False
    
    else:
        new_user = User()
        new_user.id = request_id
        new_user.password_hash = generate_password_hash(request_pw)
        db.session.add(new_user)
        db.session.commit()
        return True

