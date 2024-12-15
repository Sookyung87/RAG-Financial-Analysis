from datetime import datetime, timedelta
from pinecone.grpc import PineconeGRPC as Pinecone
from openai import OpenAI
openai_client = OpenAI(api_key="REMOVED_OPENAI_API_KEY")

def query_stock_data(question, stock_code):
    pc = Pinecone(api_key="pcsk_6xMyja_JBUJ9QMKT2yJyKNJbBGyMe7Rmi3hGm7T3LqRWocNjUovYiE8ZgFCp1yKKXbtgty")
    index = pc.Index("stock-research")

    today = datetime.now()
    one_week_ago = today - timedelta(days=30)  # 300일 전

    # 날짜를 "YYYYMMDD" 형식의 숫자로 변환
    today_str = today.strftime('%Y%m%d')  # "20241208"
    one_week_ago_str = one_week_ago.strftime('%Y%m%d')  # "20240311"

    # 날짜 범위 필터 설정 (숫자 기준으로 비교)
    query_filter = {
        "stock_code": stock_code,
    }

    # 쿼리 실행
    try:
        response = index.query(
            vector=[0] * 768,
            filter=query_filter,
            top_k=100,
            include_metadata=True,
            namespace="ns1"
        )
    except Exception as e:
        return f"쿼리 중 오류 발생: {str(e)}"

    # # 쿼리 결과 디버깅 출력
    # print("쿼리 응답:", response)

    goal_prices = []
    urls = []
    dates = []
    stock_name = None

    # 반환된 매치가 있는지 확인
    if "matches" not in response or len(response["matches"]) == 0:
        return f"{stock_code}에 해당하는 데이터가 없습니다."

    for match in response.get("matches", []):
        metadata = match.get("metadata", {})
        url = metadata.get("url")
        name = metadata.get("stock_name")
        date_str = metadata.get("date")

        # date가 "YYYY.MM.DD" 형식으로 되어 있다고 가정하고, 이를 datetime 객체로 변환 후 "YYYYMMDD" 숫자 형식으로 변경
        try:
            date_obj = datetime.strptime(date_str, '%Y.%m.%d')  # "2024.10.10" 형태로 가정
            date_str_formatted = date_obj.strftime('%Y%m%d')  # "20241010" 형태로 변환
        except ValueError:
            print(f"날짜 형식 오류: {date_str}")
            continue

        # 날짜 범위 필터 적용
        if one_week_ago_str <= date_str_formatted <= today_str:
            urls.append(url)
            dates.append(date_str_formatted)  # "YYYYMMDD" 형식의 날짜를 저장
            goal_price_str = metadata.get("goal_price")
            if goal_price_str:
                try:
                    goal_price = float(goal_price_str.replace(',', ''))
                    goal_prices.append(goal_price)
                    stock_name = name
                except ValueError:
                    print(f"목표 가격 변환 오류: {goal_price_str}")
                    continue
    

    response2 = openai_client.chat.completions.create(
        model="gpt-4o", #gpt-4o-mini가 더 저렴하긴 한데 좀 멍청함
        messages= [{"role": "user", "content" : question}]
    )
    answer2 = response2.choices[0].message.content.strip() #gpt 응답 중 첫번째 값을 answer변수에 저장. 애초에 n=1로 설정해서 답변은 1개만 생성됨


    # goal_price들의 평균 계산
    if goal_prices:
        avg_goal_price = sum(goal_prices) / len(goal_prices)
        
    else:
        answer = f"해당 기업의 지난 30일간의 증권사 리서치가 존재하지 않습니다. 따라서 해당 기업의 목표가를 예상할 수 없습니다."
        return {
        '1.success' : True,
        '2.answer' : answer,
        '3.LLManswer' : answer2
    }
    # 결과 출력

    answer = f"지난 30일간의 증권사들의 리서치를 종합한 결과 {stock_name}의 예상 목표가는 {int(avg_goal_price) if avg_goal_price is not None else 'N/A'}원 입니다."
    return {
        '1.success' : True,
        '2.url' : urls,
        '3.answer' : answer,
        '4.LLManswer' : answer2
    }