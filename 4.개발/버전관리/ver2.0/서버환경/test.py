import requests
import json

#API 엔드포인트
url = 'http://127.0.0.1:8000/rag'  # Flask 서버가 localhost에서 8000 포트로 실행 중인 경우

#샘플 요청 데이터
data = {
    'question': '최근 홈플러스 소식은?'  # 예시 질문
}

#POST 요청 보내기
response = requests.post(url, json=data)

try:
    data = response.json()
    print("JSON 데이터:", data)
except requests.exceptions.JSONDecodeError:
    print("JSON 디코딩 오류: 응답이 JSON 형식이 아닙니다.")