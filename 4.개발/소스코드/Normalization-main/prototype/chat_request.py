import os
from openai import OpenAI
from flask import current_app as app

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") 
openai_client = None #openai_client 변수를 None으로 초기화, 



# API 키가 설정되었는지 확인하는 함수
def is_api_key_set():
    return OPENAI_API_KEY is not None or openai_client is not None  #API 키가 


def set_openai_api_key(api_key):
    global OPENAI_API_KEY, openai_client
    OPENAI_API_KEY = api_key
    openai_client = OpenAI(api_key=api_key)

def send_openai_request(prompt: str, api_key: str = None) -> str:
    try:
        client = OpenAI(api_key=api_key or OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4-turbo", #답변 모델로 gpt4 turbo를 사용
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content 
        if not content:
            raise ValueError("OpenAI returned an empty response.")
        return content
    except Exception as e:
        app.logger.error(f"Error in OpenAI request: {str(e)}")
        raise Exception(f"OpenAI 요청 중 오류 발생: {str(e)}")
