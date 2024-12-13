from pinecone.grpc import PineconeGRPC as Pinecone
from sentence_transformers import SentenceTransformer
import json
import hashlib

# json 파일 로딩
with open("C:\\Clove106\\CST\\Normalization\\산출물\\stock_analysis.json", "r", encoding="utf-8") as f:
    data = json.load(f)


pc = Pinecone(api_key="d139d7c0-a790-4107-ae0d-8578afb1e411")
index = pc.Index("jsontest")

# 임베딩 모델 (hugging face)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# 한글 텍스트가 유니코드 문자로 인식되어 오류가 발생해서 추가함.
def generate_ascii_id(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

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

# 파인콘에 데이터 업로드
index.upsert(vectors=vectors, namespace="ns1")

print("Data successfully uploaded to Pinecone.")
