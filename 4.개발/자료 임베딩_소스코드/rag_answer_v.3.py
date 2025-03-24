import openai
from pinecone import Pinecone
from transformers import AutoTokenizer, AutoModel
from konlpy.tag import Okt
from langchain_teddynote.korean import stopwords
import numpy as np
import torch
import sqlite3
import hashlib
import re

# 방법2 - 기사 데이터 텍스트를 쪼개어 임베딩하는 방법


# OpenAI API 키 설정
openai.api_key = "REMOVED_OPENAI_API_KEY"

class PineconeManager:
    def __init__(self, api_key, index_name):
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name

        if index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=index_name,
                dimension=768,
                metric="cosine",
            )
        self.index = self.pc.Index(index_name)

    def query(self, vector, top_k=3, namespace="ns1"):
        return self.index.query(
            vector=vector.tolist(),
            top_k=top_k,
            include_metadata=True,
            namespace=namespace,
        )

    def upsert_data(self, vectors, namespace="ns1"):
        self.index.upsert(vectors=vectors, namespace=namespace)
        print(f"{len(vectors)}개의 벡터가 성공적으로 업로드되었습니다.")

class NLPProcessor:
    def __init__(self, model_name="kakaobank/kf-deberta-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.okt = Okt()
        self.stop_words = set(stopwords())

    def preprocess_text(self, text):
        if not text:
            return ""
        words = self.okt.nouns(text)
        filtered_words = [word for word in words if word not in self.stop_words]
        return " ".join(filtered_words)

    def get_embedding(self, text):
        preprocessed_text = self.preprocess_text(text)
        if not preprocessed_text:
            return np.zeros(768)
        inputs = self.tokenizer(preprocessed_text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            model_output = self.model(**inputs)
        return model_output.last_hidden_state[:, 0, :].squeeze().numpy()

def generate_answer_with_context(question, pinecone_manager, nlp_processor, top_k=10):
    try:
        question_embedding = nlp_processor.get_embedding(question)
        search_results = pinecone_manager.query(question_embedding, top_k=top_k)

        if not search_results.matches:
            return {
                "success": False,
                "message": "관련 정보를 찾을 수 없습니다. 주식 관련 질문을 다시 입력해주세요."
            }

        top_matches = search_results.matches[:3]  # 상위 3개 문맥 선택
        contexts = []
        for match in top_matches:
            metadata = match.metadata
            similarity = match.score
            contexts.append({
                "title": metadata.get("title", ""),
                "content": metadata.get("body", ""),
                "similarity": similarity
            })

        context_text = "\n\n".join([
            f"Title: {context['title']}\nContent: {context['content']}\nSimilarity: {context['similarity']:.4f}"
            for context in contexts
        ])

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 한국말로 답변을 제공하는 주식 전문 자문 챗봇입니다. 사용자의 질문에 대해 주어진 자료를 활용하여 올바르게 대답해주세요."},
                {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {question}"}
            ],
            max_tokens=300,
            temperature=0.7,
        )

        answer = response["choices"][0]["message"]["content"].strip()

        return {
            "success": True,
            "answer": answer,
            "contexts": contexts
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
    pinecone_api_key = "pcsk_1jdim_KL9H4gTcBXzBVr7z6j11yHHtm5QJo7f3zwQhLsvd4rroVuYUC7VBSNdmDUdB8RG"
    pinecone_index_name = "stock-research"

    pinecone_manager = PineconeManager(pinecone_api_key, pinecone_index_name)
    nlp_processor = NLPProcessor()

    while True:
        question = input("질문을 입력하세요 (종료하려면 'exit' 입력): ").strip()
        if question.lower() == "exit":
            break

        result = generate_answer_with_context(question, pinecone_manager, nlp_processor, top_k=15)
        if result["success"]:
            print(f"\n답변: {result['answer']}\n")
            for idx, context in enumerate(result["contexts"], start=1):
                print(f"문맥 {idx}:\n- 제목: {context['title']}\n- 본문: {context['content']}\n- 유사도: {context['similarity']:.4f}\n")
        else:
            print(f"\n오류: {result['message']}")
