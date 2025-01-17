from openai import OpenAI
from DB_structure import finance_data
from __init__ import db
openai_client = OpenAI(api_key="REMOVED_OPENAI_API_KEY")



def get_stock_code(question: str) -> str:
    #프롬프트
    prompt = f"""
    질문 : {question}
    반환 형식 : integer
    예시 : 123456
    """
    
    response = openai_client.chat.completions.create(
        model="gpt-4o", #gpt-4o-mini가 더 저렴하긴 한데 좀 멍청함
        messages=[
            {"role": "system", "content" : "주어진 질문에서 질문 종목의 종목 코드를 6자리 정수형으로만 대답하세요."},
            {"role": "user", "content" : prompt}
        ],
        max_tokens=100, #최대 토큰값
        n=1, #답변 수
        stop=None, #중도정지기능 x
        temperature = 0 #창의력 값을 0으로 설정하여 원하는 결과만 유도
    )
    answer = response.choices[0].message.content.strip()
    return answer


def get_stock_analyze(question: str) :

    code = get_stock_code(question)
    
    if code not in ['373220', '207940', '005930', '000660', '005380', '000270', '068270', '105560', '035420', '055550']:
        return ({
            'success' : True,
            'answer' : '아직 해당 기업에 대한 데이터가 존재하지 않습니다.'
        })     


    data = finance_data.query.filter_by(stock_code=code).first()


    prompt_question = f"""
        질문 : {question}
        자료
    """

    prompt_data = f"""**"지표 종류" : "해당 기업의 지표" / "해당 기업이 속한 산업의 평균 지표"**
        **TTM = 12개월 추적분 | 5YA = 5년 평균 | MRQ = 가장 최근 분기 | ANN = 연간**
        "주가수익비율","TTM" : {data.PE_Ratio_TTM}
        "주당매출액 비율","TTM" : {data.Price_to_Sales_TTM}
        "주당현금흐름 비율","MRQ" : {data.Price_to_Cash_Flow_MRQ}
        "주당잉여현금흐름 비율","TTM" : {data.Price_to_Free_Cash_Flow_TTM} 
        "주당순자산 비율","MRQ" : {data.Price_to_Book_MRQ}
        "주당유형자산 비율","MRQ" : {data.Price_to_Tangible_Book_MRQ}
        "매출총이익률","TTM" : {data.Gross_margin_TTM}
        "매출총이익률","5YA" : {data.Gross_margin_5YA}
        "영업이익률","TTM" : {data.Operating_margin_TTM}
        "영업이익률","5YA" : {data.Operating_margin_5YA}
        "세전수익률","TTM" : {data.Pretax_margin_TTM}
        "세전수익률","5YA" : {data.Pretax_margin_5YA}
        "순이익률","TTM" : {data.Net_Profit_margin_TTM}
        "순이익률","5YA" : {data.Net_Profit_margin_5YA}
        "주당수익","TTM" : {data.Revenue_Share_TTM}
        "기본 EPS","ANN" : {data.Basic_EPS_ANN}
        "희석 EPS","ANN" : {data.Diluted_EPS_ANN}
        "주당순자산","MRQ" : {data.Book_Value_Share_MRQ}
        "주당장부가","MRQ" : {data.Tangible_Book_Value_Share_MRQ}
        "주당현금","MRQ" : {data.Cash_Share_MRQ}
        "주당현금흐름","TTM" : {data.Cash_Flow_Share_TTM}
        "자기자본이익률","TTM" : {data.Return_on_Equity_TTM}
        "자기자본이익률","5YA" : {data.Return_on_Equity_5YA}
        "자산수익률","TTM" : {data.Return_on_Assets_TTM}
        "자산수익률","5YA" : {data.Return_on_Assets_5YA}
        "투자수익률","TTM" : {data.Return_on_Investment_TTM}
        "투자수익률","5YA" : {data.Return_on_Investment_5YA}
        "1년전 분기 대비 (최근 분기) EPS","MRQ" : {data.EPS_MRQvsQtr_1Yr_Ago_MRQ}
        "1년전 12개월추적분(TTM) 대비 (12개월추적분(TTM)) EPS","TTM" : {data.EPS_TTMvsTTM_1Yr_Ago_TTM}
        "5년간 EPS 성장률","5YA" : {data.EPS_Growth_5YA}
        "1년전 분기 대비 (최근 분기) 매출","MRQ" : {data.Sales_MRQvsQtr_1Yr_Ago_MRQ}
        "1년전 12개월추적분(TTM) 대비 (12개월추적분(TTM)) 매출","TTM" : {data.Sales_TTMvsTTM_1Yr_Ago_TTM}
        "5년간 매출 성장률","5YA" : {data.Sales_Growth_5YA}
        "5년간 자본 지출 증가율","5YA" : {data.Capital_Spending_Growth_5YA}
        "당좌비율","MRQ" : {data.Quick_Ratio_MRQ}
        "유동비율","MRQ" : {data.Current_Ratio_MRQ}
        "장기부채비율","MRQ" : {data.LT_Debt_to_Equity_MRQ}
        "총부채비율","MRQ" : {data.Total_Debt_to_Equity_MRQ}
        "자산회전율","TTM" : {data.Asset_Turnover_TTM}
        "재고자산회전율","TTM" : {data.Inventory_Turnover_TTM}
        "종업원 일인당 수익","TTM" : {data.Revenue_Employee_TTM}
        "종업원 일인당 순이익","TTM" : {data.Net_Income_Employee_TTM}
        "매출채권회전율","TTM" : {data.Receivable_Turnover_TTM}
        "배당수익률","ANN" : {data.Dividend_Yield_ANN}
        "배당수익률 5년 평균","5YA" : {data.Dividend_Yield_5Year_Avg_5YA}
        "배당증가율","ANN" : {data.Dividend_Growth_Rate_ANN}
        "배당성향","TTM" : {data.Payout_Ratio_TTM}
    """
  
    response = openai_client.chat.completions.create(
        model="gpt-4o", #gpt-4o-mini가 더 저렴하긴 한데 좀 멍청함
        messages=[
            {"role": "system", "content" : "당신은 주식 종목 분석가입니다. 제공되는 종목 분석 데이터를 바탕으로 사용자의 질문에 한국어로 올바르게 대답하세요. 해당 종목의 종합적인 의견이 필요할 경우 데이터를 분석, 종합하여 결과를 도출하세요."},
            {"role": "user", "content" : prompt_question + prompt_data}
        ],
        n=1, #답변 수
        stop=None, #중도정지기능 x
        temperature = 0.1 #아주 약간의 창의성 첨가
    )

    response2 = openai_client.chat.completions.create(
        model="gpt-4o", #gpt-4o-mini가 더 저렴하긴 한데 좀 멍청함
        messages=[
            {"role": "user", "content" : question}
        ],
    )

    answer2 =  response2.choices[0].message.content.strip()
    answer = response.choices[0].message.content.strip()
    return ({
        '1.success' : True,
        '2.used_data' : f'Investing.com {code} Ratios.csv',
        '3.data' : prompt_data,
        '4.RAGanswer' : answer,
        '5.LLManswer' : answer2
    })

    
