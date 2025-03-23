import requests
import deepl
import json

auth_key = "2fc705ba-7ffd-48ba-b3a1-78c2b24bd0d9:fx"
translator = deepl.Translator(auth_key=auth_key)

question_ko = "최근 금양이 유상증자를 철회한 이유는 무엇인가요?"
question_en = translator.translate_text(question_ko, target_lang="EN-US").text  # 번역 후 .text 사용

#API 엔드포인트
url = 'http://127.0.0.1:8000/rag'  # Flask 서버가 localhost에서 8000 포트로 실행 중인 경우

#샘플 요청 데이터
data = {
    'question': question_en  # 예시 질문
}

#POST 요청 보내기
response = requests.post(url, json=data)

try:
    data = response.json()
    print("JSON 데이터:", data)
except requests.exceptions.JSONDecodeError:
    print("JSON 디코딩 오류: 응답이 JSON 형식이 아닙니다.")
    