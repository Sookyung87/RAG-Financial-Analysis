# 사용자가 id, password, message 형식의 JSON 요청을 보내면 
# 사용자를 인증하고, 주식 질문을 분류하여 적절한 정보를 처리한 후,GPT 모델을 사용하여 최종 응답을 생성하고,그 응답을 JSON 형식으로 반환하는 코드.
from flask import request, jsonify
from app import app, db
from models import Chat
from services.auth_service import authenticate_user
from services.stock_service import process_stock_query
from services.gpt_service import generate_gpt_response
from utils.query_classifier import classify_query

# 루트로 접속했을 경우
@app.route('/')
def index():
    return jsonify({
        'name': 'Stock Analysis API',
        'version': '1.0',
        'endpoints': {
            '/api/stock-query': 'POST - Query stock information'
        }
    })

# 실제 API 호출했을 때 함수
@app.route('/api/stock-query', methods=['POST'])
def stock_query():
    data = request.get_json()
    
    if not all(k in data for k in ['id', 'password', 'message']):
        return jsonify({'error': 'Missing required fields'}), 400

    user_id = data['id']
    password = data['password']
    message = data['message']

    # 아이디&비번 대조
    auth_result = authenticate_user(user_id, password)
    if not auth_result['success']:
        return jsonify({'error': auth_result['message']}), 401

    # 질문 유형 분류 (주가정보, 재무분석, 공시, 그 외)
    query_type = classify_query(message)
    
    # 질문 유형에 맞춰 질문 함수 실행
    query_result = process_stock_query(query_type, message)
    
    # 최종 응답
    
    response = generate_gpt_response(message, query_result)

    new_chat = Chat()
    new_chat.userid = user_id
    new_chat.questions = message
    new_chat.answers = response
    db.session.add(new_chat)
    db.session.commit()

    # 최종 응답 반환
    return jsonify({'response': response}), 200
