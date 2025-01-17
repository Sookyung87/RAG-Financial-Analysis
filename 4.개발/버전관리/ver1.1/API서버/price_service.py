from openai import OpenAI
from datetime import datetime
import FinanceDataReader as fdr
import json

openai_client = OpenAI(api_key="REMOVED_OPENAI_API_KEY")

current_date = datetime.now().strftime('%Y-%m-%d') #gpt api는 현재 시간을 모르기 때문에 현재 시간을 알려줘야함

def get_stock_price(question: str):
    #프롬프트
    prompt = f"""
    질문 : {question}
    현재 날짜 : {current_date}
    """
    
    content = f"""
    주어진 질문에서 종목 코드와 날짜를 추출하여 예시와 같은 JSON 형식으로 반환해주세요.
    예시 :
    질문 : a기업의 저번주 월요일 종가를 알려줘!
    현재 날짜 : 2024-11-30
    
    반환 json 형식
    {{
        "stock_code" : "111111",
        "date" : "2024-11-18"
    }}

    """
    
    response = openai_client.chat.completions.create(
        model="gpt-4o", #gpt-4o-mini가 더 저렴하긴 한데 좀 멍청함
        messages=[
            {"role": "system", "content" : content},
            {"role": "user", "content" : prompt}
        ],
        max_tokens=100, #최대 토큰값
        n=1, #답변 수
        stop=None, #중도정지기능 x
        temperature = 0 #창의력 값을 0으로 설정하여 원하는 결과만 유도
    )
    answer = response.choices[0].message.content.strip() #gpt 응답 중 첫번째 값을 answer변수에 저장. 애초에 n=1로 설정해서 답변은 1개만 생성됨
    cleaned_answer = answer.strip().replace('```','').replace('json', '').strip() #가끔씩 gpt 응답에서 프롬프트에 맞지 않는 형식으로 출력하는데 그거 가공하는 코드
    finance_code = json.loads(cleaned_answer) #gpt응답을 json화
    code = finance_code['stock_code'] #json화 데이터에서 stock_code 추출 (str형)
    date = finance_code['date'] #json화 데이터에서 data 추출 (str형)
    stock_data = fdr.DataReader(code, date, date) #financedatareader 라이브러리를 통해 해당 날짜 주식 조회


    response2 = openai_client.chat.completions.create(
        model="gpt-4o", #gpt-4o-mini가 더 저렴하긴 한데 좀 멍청함
        messages= [{"role": "user", "content" : question}]
    )
    answer2 = response2.choices[0].message.content.strip() #gpt 응답 중 첫번째 값을 answer변수에 저장. 애초에 n=1로 설정해서 답변은 1개만 생성됨


    if stock_data.empty:
        return {
            'success' : False,
            'message' : '해당 날짜의 주가 데이터가 존재하지 않습니다. 날짜를 확인해주세요.'
        }
    else:
        stock_data_dict = stock_data.to_dict() #DataFrame 형태를 딕셔너리 형태로 변환
        open_price = list(stock_data_dict['Open'].values())
        close_price = list(stock_data_dict['Close'].values())
        high_price = list(stock_data_dict['High'].values())
        low_price = list(stock_data_dict['Low'].values())


        if current_date != date:
                return {
                    '1.success' : True,
                    '2.stock_code' : code,
                    '3.시가' : open_price,
                    '4.종가' : close_price,
                    '5.고가' : high_price,
                    '6.저가' : low_price,
                    '7.date' : date,
                    '8.LLManswer' : answer2
            }     
        else:
                return {
                    '1.success' : True,
                    '2.stock_code' : code,
                    '3.현재가' : close_price,
                    '4.시가' : open_price,
                    '5.고가' : high_price,
                    '6.저가' : low_price,
                    '7.date' : date,
                    '8.LLManswer' : answer2
                }

