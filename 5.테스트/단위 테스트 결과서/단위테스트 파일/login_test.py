import requests
import json

# API 엔드포인트
url = 'http://localhost:8000/rag'  # Flask 서버가 localhost에서 8000 포트로 실행 중인 경우

# 샘플 요청 데이터
data = {
    'id': 'new_user123',
    'pw': 'secure_password',
}

# POST 요청 보내기
response = requests.post(url, json=data)
