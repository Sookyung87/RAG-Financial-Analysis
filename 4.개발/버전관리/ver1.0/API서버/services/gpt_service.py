# api키, api모델 설정
# DB에서 데이터를 가져와서 GPT에게 전달할 형태로 포멧
# GPT 답변 생성 후 내용 뒤에 출처 표기

import os
from openai import OpenAI

openai_client = OpenAI(api_key="REMOVED_OPENAI_API_KEY")


def format_financial_metrics(data: dict) -> str:
    metrics = []
    
    if 'eps' in data and data['eps'] is not None:
        metrics.append(f"주당순이익(EPS): {data['eps']:,.0f}원")
    if 'per' in data and data['per'] is not None:
        metrics.append(f"주가수익비율(PER): {data['per']:.2f}배")
    if 'pbr' in data and data['pbr'] is not None:
        metrics.append(f"주가순자산비율(PBR): {data['pbr']:.2f}배")
    if 'bps' in data and data['bps'] is not None:
        metrics.append(f"주당순자산(BPS): {data['bps']:,.0f}원")
    if 'dividend_yield' in data and data['dividend_yield'] is not None:
        metrics.append(f"배당수익률: {data['dividend_yield']:.2f}%")
        
    return "\n".join(f"- {metric}" for metric in metrics)

def format_price_info(price_data: dict) -> str:
    if 'error' in price_data:
        return "현재 주가 정보를 불러올 수 없습니다."
        
    return f"""
- 현재가: {price_data['price']:,.0f}원
- 등락: {price_data['change']:+,.0f}원 ({price_data['change_percent']:+.2f}%)
- 거래량: {price_data['volume']:,.0f}주
- 기준일: {price_data['date']}
"""

def generate_gpt_response(query: str, data: dict) -> str:
    company = data.get('company', '삼성전자')
    query_type = data.get('query_type', 'general')
    
    # Build context based on query type
    context_parts = [f"회사: {company}"]
    sources = []
    
    if query_type in ['price', 'general'] and 'price' in data:
        context_parts.append("주가 정보:" + format_price_info(data))
        if 'source' in data:
            sources.append(data['source'])
    
    if query_type in ['analysis', 'general'] and 'eps' in data:
        context_parts.append("재무 분석:" + format_financial_metrics(data))
        if 'source' in data:
            sources.append(data['source'])
    
    if query_type in ['disclosure', 'general'] and 'disclosures' in data:
        disclosures = data['disclosures']
        if disclosures:
            context_parts.append("최근 공시:")
            # 최대 한 개의 공시만 출력하도록 제한
            disc = disclosures[0]
            context_parts.append(f"- {disc['date']}: {disc['title']}")
            if 'source' in disc:
                sources.append(disc['source'])
    
    context = "\n\n".join(context_parts)
    
    # 시스템 메시지 (GPT에게 질문과 함께 전달됨)
    system_message = """
당신은 한국 주식시장 전문가입니다. 다음과 같은 원칙을 따라 응답해 주세요:
1. 객관적이고 전문적인 분석을 제공합니다.
2. 불확실한 정보는 명확히 언급합니다.
3. 투자 위험성을 항상 고려합니다.
4. 간결하면서도 정보가 풍부한 답변을 제공합니다.
5. 모든 수치는 적절한 단위와 함께 제시합니다.
"""

    # 프롬프트 (질문 내용과 DB 자료를 가공하여 GPT에게 전달)
    prompt = f"""
분석 요청: {query}

제공된 정보:
{context}

요구사항:
1. 요청된 정보 유형({query_type})에 집중
2. 핵심 정보를 먼저 제시
3. 관련 수치 데이터를 명확하게 포함
4. 간단한 시장 맥락 제공 (필요한 경우)
5. 균형 잡힌 결론으로 마무리
"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        if response.choices and response.choices[0].message and response.choices[0].message.content:
            gpt_response = response.choices[0].message.content.strip()
            
            # Add source attribution
            sources = list(set(sources))  # Remove duplicates
            if sources:
                source_text = ", ".join(sources)
                gpt_response += f"\n\n[데이터 출처: {source_text}]"
            else:
                gpt_response += "\n\n[주의: 이 답변은 GPT-4의 학습 데이터를 기반으로 작성되었으며, 실시간 시장 데이터가 포함되지 않았을 수 있습니다.]"
            
            return gpt_response
            
        return "응답 생성 중 오류가 발생했습니다."
    except Exception as e:
        return f"분석 생성 중 오류가 발생했습니다: {str(e)}"
