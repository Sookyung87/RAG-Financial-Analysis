from openai import OpenAI
from flask import Flask, request, jsonify

# 환경변수에서 OpenAI API 키 가져오기
openai_client = OpenAI(api_key="REMOVED_OPENAI_API_KEY")

app = Flask(__name__)

def get_llm_answer(query):
    #프롬프트
    prompt = f"""
    질문 : {query}
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini", #gpt-4o-mini가 더 저렴하긴 한데 좀 멍청함
        messages=[
            {"role": "user", "content" : prompt}
        ],
        max_tokens=2000, #최대 토큰값
        n=1, #답변 수
        stop=None, #중도정지기능 x
        temperature = 0 #창의력 값을 0으로 설정하여 원하는 결과만 유도
    )
    answer = response.choices[0].message.content.strip()
    return answer