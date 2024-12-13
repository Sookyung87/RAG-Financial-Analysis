# 이 함수는 if 문을 통해 질문의 주요 단어들을 파악하고, 해당하는 질문 종류에 점수를 부여하여 질문 의도를 파악한다.
# 주가 관련 질문 / 공시 관련 질문 / 재무 분석 관련 질문 / 기타 일반적인 질문

def classify_query(message: str) -> str:

    message = message.lower()
    
    # Price related keywords with context
    price_keywords = [
        '주가', '가격', '시세', '얼마', '값', '시가', '종가', '현재가',
        '거래량', '시총', '거래대금', '주식', '전일비', '등락률'
    ]
    
    # Disclosure related keywords with business context
    disclosure_keywords = [
        '공시', '발표', '뉴스', '소식', '공지', '공고', '보도', '공표',
        '발표자료', '보도자료', '사업보고서', '실적발표', '공시사항'
    ]
    
    # Analysis related keywords with financial metrics
    analysis_keywords = [
        '분석', 'per', 'eps', '실적', '성과', '재무', '배당', 
        '손익', '이익', '매출', '영업이익', 'pbr', 'bps', 'roe',
        '영업이익률', '순이익률', '부채비율', '유동비율', '당기순이익',
        '매출액', '영업실적', '재무상태', '손익계산서'
    ]
    
    # Create a scoring system for better classification
    scores = {
        'price': sum(2 if keyword in message else 0 for keyword in price_keywords),
        'disclosure': sum(2 if keyword in message else 0 for keyword in disclosure_keywords),
        'analysis': sum(2 if keyword in message else 0 for keyword in analysis_keywords)
    }
    
    # Add context-based scoring
    if '?' in message or '얼마' in message:
        scores['price'] += 1
    if '발표' in message and ('했' in message or '된' in message):
        scores['disclosure'] += 1
    if any(term in message for term in ['어떻', '어떨', '어떠']):
        scores['analysis'] += 1
    
    # Get the highest scoring category
    max_score = max(scores.values())
    if max_score > 0:
        for category, score in scores.items():
            if score == max_score:
                return category
    
    return 'general'
