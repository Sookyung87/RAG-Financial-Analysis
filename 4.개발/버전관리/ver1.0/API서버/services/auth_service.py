# 회원가입 & 아이디 비번 대조 코드
from app import db
from models import User


def authenticate_user(user_id: str, password: str) -> dict:
    user = User.query.filter_by(id=user_id).first() #DB에서 입력한 user 이름이 있는지 확인하는 과정
    
    #만약 사용자 id가 존재한다면
    if user: 
        if user.check_password(password):
            return {'success': True, 'message': 'Authentication successful'}
        return {'success': False, 'message': '잘못된 아이디나 비밀번호입니다.'}
    
    # 만약 사용자 id가 존재하지 않는다면 아이디 생성
    new_user = User()
    new_user.id = user_id
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return {'success': True, 'message': 'New user created'}
