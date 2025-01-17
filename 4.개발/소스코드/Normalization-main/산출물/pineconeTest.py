import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import json
import hashlib

# API 키 설정 및 Pinecone 인스턴스 생성
pc = Pinecone(
    api_key="0d510937-0343-41b9-9904-f04cbf816405"
)

# 인덱스 이름 설정
index_name = "stock-research"

# 기존 인덱스가 존재하면 삭제
if index_name in pc.list_indexes().names():
    pc.delete_index(index_name)

# 인덱스 생성하기
pc.create_index(
    name=index_name,
    dimension=384,  # 모델 임베딩 차원에 맞게 수정
    metric='cosine',
    spec=ServerlessSpec(
        cloud='aws',  # 또는 gcp, 사용 중인 클라우드에 맞게 변경
        region='us-east-1'  # 사용 중인 리전에 맞게 변경
    )
)

# 인덱스 객체 가져오기
index = pc.Index(index_name)

# JSON 파일 로드
with open("C:\\Users\\이수경\\Desktop\\Capstone_Normalization\\Normalization\\산출물\\stock_analysis.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 임베딩 모델 로드
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# ID 생성 함수
def generate_ascii_id(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

# 벡터 데이터 생성 및 업로드
vectors = []
for item in data:
    item_id = generate_ascii_id(item["stock_name"])
    embedding = model.encode(item["body"]).tolist()
    vectors.append({
        "id": item_id,
        "values": embedding,
        "metadata": {
            "title": item["title"],
            "stock_name": item["stock_name"],
            "broker": item["broker"],
            "date": item["date"],
            "goal_price": item["goal_price"],
            "recommendation": item["recommendation"],
            "sub_title": item["sub_title"]
        }
    })

# Pinecone에 벡터 업로드
index.upsert(vectors=vectors, namespace="ns1")

print("Data successfully uploaded to Pinecone.")
