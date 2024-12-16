import os
import sqlite3
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
from langchain_teddynote.korean import stopwords
from konlpy.tag import Okt
import numpy as np
import hashlib
import logging
import openai

# 로깅 설정
logging.basicConfig(
    level=logging.ERROR,
    filename='error.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# OpenAI API 키 설정
openai.api_key = "REMOVED_OPENAI_API_KEY"

# Pinecone 인스턴스 생성
API_KEY = "pcsk_1jdim_KL9H4gTcBXzBVr7z6j11yHHtm5QJo7f3zwQhLsvd4rroVuYUC7VBSNdmDUdB8RG"
pc = Pinecone(api_key=API_KEY)

# 인덱스 생성 또는 연결
index_name = "stock-research"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=768,
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )

# 인덱스 객체 가져오기
index = pc.Index(index_name)

# 모델 및 토크나이저 로드
tokenizer = AutoTokenizer.from_pretrained("kakaobank/kf-deberta-base")
model = AutoModel.from_pretrained("kakaobank/kf-deberta-base")

# 형태소 분석기 (konlpy)
okt = Okt()

# 불용어 리스트 가져오기
stop_words = set(stopwords())

# 텍스트 전처리 함수
def preprocess_text(text):
    if not text:
        return ""
    # 형태소 분석 및 명사 추출
    words = okt.nouns(text)
    # 불용어 제거
    filtered_words = [word for word in words if word not in stop_words]
    # 단어를 공백으로 연결
    return " ".join(filtered_words)

# 텍스트 임베딩 생성 함수
def get_embedding(text):
    preprocessed_text = preprocess_text(text)
    if not preprocessed_text:
        return np.zeros(768)  # 빈 텍스트 처리
    inputs = tokenizer(preprocessed_text, return_tensors="pt", padding=True, truncation=True)
    model_output = model(**inputs)
    embedding = model_output.last_hidden_state.mean(dim=1).squeeze().detach().numpy()
    return embedding

# ID 생성 함수
def generate_ascii_id(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

# Pinecone에 SQLite 데이터베이스의 데이터를 업로드하는 함수
def upsert_data_from_db(db_path):
    # 데이터베이스 연결
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 데이터 선택
    cursor.execute("SELECT id, title, stock_name, broker, date, goal_price, recommendation, sub_title, body, stock_code, url FROM stock_analysis")
    rows = cursor.fetchall()

    vectors = []
    for row in rows:
        id, title, stock_name, broker, date, goal_price, recommendation, sub_title, body, stock_code, url = row
        try:
            # 필드별 임베딩 생성
            title_embedding = get_embedding(title)
            subtitle_embedding = get_embedding(sub_title)
            body_embedding = get_embedding(body)
            
            # 가중치 적용 최종 벡터
            final_embedding = 0.2 * title_embedding + 0.3 * subtitle_embedding + 0.5 * body_embedding

            # 벡터 ID 생성
            item_id = generate_ascii_id(f"{id}-{stock_name}")
            goal_price = goal_price if goal_price is not None else "0"

            vectors.append({
                "id": item_id,
                "values": final_embedding.tolist(),
                "metadata": {
                    "title": title,
                    "stock_name": stock_name,
                    "broker": broker,
                    "date": date,
                    "goal_price": goal_price,
                    "recommendation": recommendation,
                    "sub_title": sub_title,
                    "body": body,
                    "stock_code": stock_code,
                    "url": url
                }
            })

        except Exception as e:
            logging.error(f"데이터 처리 중 오류 발생: {e}")


    # Pinecone에 벡터 업로드
    if vectors:
        index.upsert(vectors=vectors, namespace="ns1")

    print("데이터가 성공적으로 Pinecone에 업로드되었습니다.")

    # 데이터베이스 연결 종료
    conn.close()

# 질문 전처리 함수 추가
def preprocess_question(question):
    return preprocess_text(question)

# 텍스트 임베딩 생성 함수 수정
def get_embedding(text):
    preprocessed_text = preprocess_text(text)
    if not preprocessed_text:
        return np.zeros(768)  # 빈 텍스트 처리
    inputs = tokenizer(preprocessed_text, return_tensors="pt", padding=True, truncation=True)
    model_output = model(**inputs)
    embedding = model_output.last_hidden_state.mean(dim=1).squeeze().detach().numpy()
    return embedding

# Pinecone에서 유사한 데이터 검색 함수 수정
def search_similar_data(question, top_k=2):
    # 질문을 전처리 후 임베딩 생성
    question_embedding = get_embedding(preprocess_question(question))
    
    # Pinecone에서 검색
    search_results = index.query(
        vector=question_embedding.tolist(),
        top_k=top_k,
        include_metadata=True,
        namespace="ns1"
    )
    return search_results

# 검색 결과를 기반으로 답변 생성
def generate_answer_with_context(question):
    # Pinecone에서 검색
    search_results = search_similar_data(question)
    
    if not search_results.matches:
        return "관련 정보를 찾을 수 없습니다. 주식과 관련된 다른 질문을 해주세요."

    # 검색 결과에서 컨텍스트 추출
    context = "\n".join([
        f"Title: {match.metadata['title']}\nContent: {match.metadata['body']}"
        for match in search_results.matches
    ])

    # OpenAI ChatCompletion 사용(프롬프트 추가)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": ""},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ],
        max_tokens=500,
        temperature=0.7
    )
    return response['choices'][0]['message']['content'].strip()
 
# SQLite 데이터베이스 경로
db_path = "C:/Users/이수경/Desktop/Capstone_Normalization/Normalization/산출물/정보 수집/CrawlData.db"

# SQLite 데이터베이스에서 데이터 읽기 및 Pinecone에 업로드
# upsert_data_from_db(db_path)

# 사용자 질문 예제
user_question = "솔브레인 주식을 지금 매수하는 게 좋을까요?"

# 검색 결과를 포함한 답변 생성
response = generate_answer_with_context(user_question)

# Pinecone 검색 결과 출력
search_results = search_similar_data(user_question)
print("검색 결과:")
# 검색 결과 출력 (유사도 점수 포함)
for match in search_results.matches:
    print(f"ID: {match.id}, Score: {match.score}, Title: {match.metadata.get('title')}, Content: {match.metadata.get('body')}")

# 최종 답변 출력
print(f"\nAI 응답: {response}")