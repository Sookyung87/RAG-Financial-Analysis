from openai import OpenAI

openai_client = OpenAI(api_key="REMOVED_OPENAI_API_KEY")


def question_type(question: str):
    #프롬프트
    prompt = f"""
    질문 : {question}
    분류 타입 : "1. 주식의 가격을 묻는 질문, 2. 주식의 미래 가격 추측을 묻는 질문, 3. 주식 종목 상세 수치 분석 질문 (배당 관련 정보 포함), 4. 회사의 활동내용이나 시장의 반응을 포함한 주식과 관련된 그 외의 질문, 5. 주식과 관련없는 질문"
    반환 형식: 숫자 (1, 2, 3, 4, 5 중 하나)
    예시1 :
    질문 : a 기업 저번주 월요일 종가를 알려줘!
    반환 결과 : 1

    예시2 :
    질문 : 안녕. 만나서 반가워!
    반환 결과 : 5
 
    예시3 :
    질문 : 삼성전자 향후 주가가 어떻게 될 것 같니?
    반환 결과 : 2
    """
    
    response = openai_client.chat.completions.create(
        model="gpt-4o", #gpt-4o-mini가 더 저렴하긴 한데 좀 멍청함
        messages=[
            {"role": "system", "content" : "당신은 주식 관련 질문을 구별하는 시스템입니다. 질문에 대해 질문 타입을 분류해주세요. 반환 결과만 숫자로 출력하면 됩니다."},
            {"role": "user", "content" : prompt}
        ],
        max_tokens=100, #최대 토큰값
        n=1, #답변 수
        stop=None, #중도정지기능 x
        temperature = 0 #창의력 값을 0으로 설정하여 원하는 결과만 유도
    )
    answer = response.choices[0].message.content.strip() #gpt 응답 중 첫번째 값을 answer변수에 저장. 애초에 n=1로 설정해서 답변은 1개만 생성됨
    return answer

    