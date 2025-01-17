import FinanceDataReader as fdr
from app import db
from models import Disclosure, StockAnalysis
from datetime import datetime, timedelta

# 해당 4개의 기업에 대한 이름과 종목코드를 매치
def extract_stock_code(message: str) -> str:

    stock_mapping = {
        '삼성전자': '005930',
        'SK하이닉스': '000660',
        'LG에너지솔루션': '373220',
        '현대차': '005380'
    }
    
    for company, code in stock_mapping.items():
        if company in message:
            return code
    return '005930'  # 일단 오류 예방을 위해 4개 기업 외에는 삼성이 뜨게끔 설정

# 주어진 주식 코드에 대한 최신 주식 가격 정보를 가져오는 함수
def get_stock_price(stock_code: str) -> dict:
    try:
        df = fdr.DataReader(stock_code) #주식 코드로 데이터 조회
        if df is not None and not df.empty:
            latest_price = df.iloc[-1] #최근 가격정보 저장
            previous_price = df.iloc[-2] if len(df) > 1 else latest_price #전날 가격정보 저장
            price_change = latest_price['Close'] - previous_price['Close'] #변동금액 저장
            change_percent = (price_change / previous_price['Close']) * 100 #변동률 저장
            
            return {
                'price': float(latest_price['Close']), 
                'change': float(price_change), 
                'change_percent': float(change_percent),            
                'volume': float(latest_price['Volume']),
                'date': latest_price.name.strftime('%Y-%m-%d'),
                'source': 'FinanceDataReader'
            }
        return {'error': 'No data available'}
    except Exception as e:
        return {'error': f'Failed to fetch stock data: {str(e)}'}

# 주어진 주식 이름에 대한 최근 공시 정보 5개를 가져옴.
def get_stock_disclosure(stock_name: str) -> dict:
    try:
        recent_disclosures = Disclosure.query.filter_by(
            stock_name=stock_name
        ).order_by(Disclosure.date.desc()).limit(5).all()
        
        return {
            'disclosures': [
                {
                    'date': d.date.strftime('%Y-%m-%d'),
                    'title': d.title,
                    'body': d.body,
                    'source': d.source
                } for d in recent_disclosures
            ]
        }
    except Exception as e:
        return {'error': f'Failed to fetch disclosures: {str(e)}'}

# DB에서 질문에 적힌 주식명을 통해 재무 분석 데이터를 불러옴
def get_stock_analysis(stock_name: str) -> dict:
    try:
        analysis = StockAnalysis.query.filter_by(stock_name=stock_name).first() 
        if analysis:
            return {
                'eps': analysis.eps,
                'bps': analysis.bps,
                'per': analysis.per,
                'industry_per': analysis.industry_per,
                'pbr': analysis.pbr,
                'dividend_yield': analysis.dividend_yield,
                'source': analysis.source
            }
        return {'error': 'Analysis not found'}
    except Exception as e:
        return {'error': f'Failed to fetch analysis data: {str(e)}'}

# 주어진 질문 유형에 맞는 주식 정보를 처리하여 반환
def process_stock_query(query_type: str, message: str) -> dict: 
    stock_code = extract_stock_code(message) #질문에서 주식 코드를 추출
    company_name = next((name for name, code in {
                        '삼성전자': '005930',
                        'SK하이닉스': '000660',
                        'LG에너지솔루션': '373220',
                        '현대차': '005380'
                    }.items() 
                    if code == stock_code), '삼성전자')  # 기본값은 삼성전자
    
    stock_info = {'company': company_name, 'query_type': query_type}
    
    # 질문 유형이 'price'일 경우, 거기에 주식 가격 정보를 추가함
    if query_type == 'price':
        stock_info.update(get_stock_price(stock_code))

    # 질문 유형이 'disclosure'일 경우, 거기에 공시 정보를 추가함
    if query_type == 'disclosure':
        stock_info.update(get_stock_disclosure(company_name))
    
    # 질문 유형이 'analysis' 또는 'general'일 경우, 거기에 재무 분석 정보를 추가함
    if query_type in ['analysis', 'general']:
        stock_info.update(get_stock_analysis(company_name))
         # 만약 질문 유형이 'general'이면, 추가로 주식 가격 정보도 추가함
        if query_type == 'general':
            stock_info.update({'price_data': get_stock_price(stock_code)})
    
    return stock_info
