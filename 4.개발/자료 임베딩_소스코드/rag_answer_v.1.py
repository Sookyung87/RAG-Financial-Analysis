import openai
from pinecone import Pinecone
from transformers import AutoTokenizer, AutoModel
from konlpy.tag import Okt
from langchain_teddynote.korean import stopwords
import numpy as np
import torch
import sqlite3
import hashlib

# 기존 프로그램의 질의응답(기준)

# OpenAI API 키 설정
openai.api_key = "REMOVED_OPENAI_API_KEY"

class PineconeManager:
    """Pinecone 관련 기능을 관리하는 클래스"""

    def __init__(self, api_key, index_name):
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name

        # 인덱스 생성 또는 가져오기
        if index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=index_name,
                dimension=768,  # kakaobank/kf-deberta-base의 임베딩 차원
                metric="cosine",
            )
        self.index = self.pc.Index(index_name)

    def query(self, vector, top_k=3, namespace="ns1"):
        """Pinecone에서 벡터 기반 데이터 검색"""
        return self.index.query(
            vector=vector.tolist(),
            top_k=top_k,
            include_metadata=True,
            namespace=namespace,
        )
    
    def upsert_data(self, vectors, namespace="ns1"):
        """벡터 데이터 및 메타데이터를 Pinecone에 업로드"""
        self.index.upsert(vectors=vectors, namespace=namespace)
        print(f"{len(vectors)}개의 벡터가 성공적으로 업로드되었습니다.")

class NLPProcessor:
    """텍스트 전처리 및 임베딩 생성을 관리하는 클래스"""

    def __init__(self, model_name="kakaobank/kf-deberta-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.okt = Okt()
        self.stop_words = set(stopwords())

    def preprocess_text(self, text):
        """텍스트를 전처리"""
        if not text:
            return ""
        words = self.okt.nouns(text)
        filtered_words = [word for word in words if word not in self.stop_words]
        return " ".join(filtered_words)

    def get_embedding(self, text):
        """텍스트 임베딩 생성"""
        preprocessed_text = self.preprocess_text(text)
        if not preprocessed_text:
            return np.zeros(768)
        inputs = self.tokenizer(preprocessed_text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            model_output = self.model(**inputs)
        return model_output.last_hidden_state[:, 0, :].squeeze().numpy()

def upload_data_to_pinecone(sqlite_db_path, pinecone_manager, nlp_processor):
    """SQLite 데이터베이스에서 데이터를 읽어 Pinecone에 업로드"""
    conn = sqlite3.connect(sqlite_db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, stock_name, broker, date, goal_price, recommendation, sub_title, body, url, stock_code FROM stock_analysis")
    rows = cursor.fetchall()

    vectors = []
    for row in rows:
        id, title, stock_name, broker, date, goal_price, recommendation, sub_title, body, url, stock_code = row
        try:
            if not body:  # body 열이 비어있는 경우 건너뛰기
                print(f"ID {id}: 'body' 열이 비어 있어 건너뜁니다.")
                continue

            item_id = hashlib.md5(f"{id}-{stock_name}".encode('utf-8')).hexdigest()
            embedding = nlp_processor.get_embedding(body).tolist()

            # 모든 값이 0인 벡터는 건너뛰기
            if all(value == 0 for value in embedding):
                print(f"ID {id}: 임베딩 벡터가 모두 0으로 이루어져 있어 건너뜁니다.")
                continue

            vectors.append({
                "id": item_id,
                "values": embedding,
                "metadata": {
                    "title": title,
                    "stock_name": stock_name,
                    "broker": broker,
                    "date": date,
                    "goal_price": goal_price,
                    "recommendation": recommendation,
                    "sub_title":sub_title,
                    "body": body,
                    "url": url,
                    "stock_code": stock_code
                }
            })
        except Exception as e:
            print(f"Error processing row {id}: {e}")

    if vectors:
        pinecone_manager.index.upsert(vectors=vectors, namespace="ns1")
        print("Data successfully uploaded to Pinecone.")
    else:
        print("No data to upload.")
        
    conn.close()  # 연결 종료

def generate_answer_with_context(question, pinecone_manager, nlp_processor):
    """질문을 기반으로 Pinecone 검색 후 OpenAI로 답변 생성"""
    try:
        # 질문 임베딩 생성
        question_embedding = nlp_processor.get_embedding(question)
        search_results = pinecone_manager.query(question_embedding)

        if not search_results.matches:
            return {
                "success": False,
                "message": "관련 정보를 찾을 수 없습니다. 주식 관련 질문을 다시 입력해주세요."
            }

         # 유사도가 높은 상위 3개의 결과 가져오기
        top_matches = search_results.matches[:3]  # 상위 3개 결과 선택
        contexts = []
        for match in top_matches:
            metadata = match.metadata
            similarity = match.score
            context = {
                "title": metadata.get("title", ""),
                "content": metadata.get("body", ""),
                "similarity": similarity
            }
            contexts.append(context)

        # 첫 번째 결과를 컨텍스트로 사용하여 답변 생성
        main_context = f"Title: {contexts[0]['title']}\nContent: {contexts[0]['content']}"

        # OpenAI를 사용하여 답변 생성
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 한국말로 답변을 제공하는 주식 전문 자문 챗봇입니다. 사용자의 질문에 대해 주어진 자료를 활용하여 올바르게 대답해주세요."},
                {"role": "user", "content": f"Context:\n{main_context}\n\nQuestion: {question}"}
            ],
            max_tokens=300,
            temperature=0.7,
        )

        answer = response["choices"][0]["message"]["content"].strip()

        # 최종 결과 반환
        return {
            "success": True,
            "answer": answer,
            "contexts": contexts  # 상위 3개 문맥 포함
        }
    except openai.error.OpenAIError as e:
        return {
            "success": False,
            "message": f"OpenAI API 오류 발생: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"기타 오류 발생: {str(e)}"
        }

# 실행 테스트
if __name__ == "__main__":
    # Pinecone 초기화
    pinecone_api_key = "pcsk_6xMyja_JBUJ9QMKT2yJyKNJbBGyMe7Rmi3hGm7T3LqRWocNjUovYiE8ZgFCp1yKKXbtgty"
    pinecone_index_name = "stock-research"
    sqlite_db_path = "C:/Users/이수경/Desktop/cap/정확도향상테스트/Updated_RAGdata.db"

    pinecone_manager = PineconeManager(pinecone_api_key, pinecone_index_name)

    # NLPProcessor 초기화
    nlp_processor = NLPProcessor()

    upload_data_to_pinecone(sqlite_db_path, pinecone_manager, nlp_processor)

   # 질문 처리 루프
while True:
    question = input("질문을 입력하세요 (종료하려면 'exit' 입력): ").strip()
    if not question:
        print("질문을 입력해주세요.")
        continue
    if question.lower() == "exit":
        break

    result = generate_answer_with_context(question, pinecone_manager, nlp_processor)
    if result["success"]:
        print(f"\n답변: {result['answer']}\n")
        for idx, context in enumerate(result["contexts"], start=1):
            print(f"문맥 {idx}:\n- 제목: {context['title']}\n- 본문: {context['content']}\n- 유사도: {context['similarity']:.4f}\n")
    else:
        print(f"\n오류: {result['message']}")