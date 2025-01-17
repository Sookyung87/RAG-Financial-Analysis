import os
import sqlite3
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import numpy as np
import hashlib
import logging


# 로깅 설정
logging.basicConfig(
    level=logging.ERROR,
    filename='error.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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

# 텍스트 임베딩 생성 함수
def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
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
    cursor.execute("SELECT id, title, stock_name, broker, date, goal_price, recommendation, sub_title, body FROM research")
    rows = cursor.fetchall()

    # 가중치 설정
    WEIGHTS = {
        "title": 0.5,
        "subtitle": 0.3,
        "body": 0.2
    }

    # 각 행을 Pinecone에 업로드
    vectors = []
    for row in rows:
        id, title, stock_name, broker, date, goal_price, recommendation, sub_title, body = row
        try:
            # 각 필드의 임베딩 생성
            title_embedding = get_embedding(title) if title else np.zeros(768)
            subtitle_embedding = get_embedding(sub_title) if sub_title else np.zeros(768)
            body_embedding = get_embedding(body) if body else np.zeros(768)
            
             # 가중치 적용하여 최종 벡터 계산
            final_embedding = (
                WEIGHTS["title"] * title_embedding +
                WEIGHTS["subtitle"] * subtitle_embedding +
                WEIGHTS["body"] * body_embedding
            )

             # 벡터 ID 생성 (id와 stock_name을 조합)
            item_id = generate_ascii_id(f"{id}-{stock_name}")

            # goal_price가 None이면 0 또는 빈 문자열로 대체
            goal_price = goal_price if goal_price is not None else "0"

            # 벡터 정보 추가
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
                    "body": body
                }
            })

        except Exception as e:
            logging.error(f"데이터 업로드 중 오류 발생: {e}")
            print(f"데이터 업로드 중 오류 발생: {e}")

    # Pinecone에 벡터 업로드
    if vectors:
        index.upsert(vectors=vectors, namespace="ns1")

    print("데이터가 성공적으로 Pinecone에 업로드되었습니다.")

    # 데이터베이스 연결 종료
    conn.close()

# SQLite 데이터베이스 경로
db_path = "C:/Users/이수경/Desktop/Capstone_Normalization/Normalization/산출물/RAG구현/CrawlData.db"

# SQLite 데이터베이스에서 데이터 읽기 및 Pinecone에 업로드
upsert_data_from_db(db_path)
