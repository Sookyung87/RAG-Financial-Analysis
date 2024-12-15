from openai import OpenAI
from pinecone import Pinecone
from transformers import AutoTokenizer, AutoModel
from konlpy.tag import Okt
from langchain_teddynote.korean import stopwords
import numpy as np
openai_client = OpenAI(api_key="REMOVED_OPENAI_API_KEY")


class PineconeManager:
    """Pinecone 관련 기능을 관리하는 클래스"""

    def __init__(self, api_key, index_name):
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.index = self.pc.Index(index_name)

    def query(self, vector, top_k=3, namespace="ns1"):
        """Pinecone에서 벡터 기반 데이터 검색"""
        return self.index.query(
            vector=vector.tolist(),
            top_k=top_k,
            include_metadata=True,
            namespace=namespace,
        )

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
        inputs = self.tokenizer(preprocessed_text, return_tensors="pt", padding=True, truncation=True)
        model_output = self.model(**inputs)
        return model_output.last_hidden_state.mean(dim=1).squeeze().detach().numpy()

def generate_answer_with_context(question, pinecone_manager, nlp_processor):
    """질문을 기반으로 Pinecone 검색 후 답변 생성"""
    try:
        question_embedding = nlp_processor.get_embedding(question)
        search_results = pinecone_manager.query(question_embedding)
        print(f"DEBUG: Search results: {search_results}")  # 검색 결과 디버깅

        if not search_results.matches:
            return {
                "success": False,
                "message": "관련 정보를 찾을 수 없습니다. 주식 관련 질문을 다시 입력해주세요."
            }

        # 유사도가 가장 높은 데이터만 사용
        top_match = search_results.matches[0]
        top_metadata = top_match.metadata
        top_similarity = top_match.score
        print(f"DEBUG: Top match metadata: {top_metadata}, Similarity: {top_similarity}")

        context = f"Title: {top_metadata['title']}\nContent: {top_metadata['body']}"

    
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 한국말로 답변을 제공하는 주식 전문 자문 챗봇입니다. 사용자의 질문에 대해 주어진 자료를 활용하여 올바르게 대답해주세요."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
            ],
            max_tokens=500,
            n=1,
            stop=None,
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()
        print(f"DEBUG: OpenAI response: {response}")  # OpenAI 응답 디버깅


        
        response2 = openai_client.chat.completions.create(
            model="gpt-4o", #gpt-4o-mini가 더 저렴하긴 한데 좀 멍청함
            messages= [{"role": "user", "content" : question}]
        )
        answer2 = response2.choices[0].message.content.strip() #gpt 응답 중 첫번째 값을 answer변수에 저장. 애초에 n=1로 설정해서 답변은 1개만 생성됨

        return {
            "success": True,
            "answer": answer,
            "context": context,
            "similarity": top_similarity,
            "answer2" : answer2
        }
    except Exception as e:
        # 디버깅용 로그 출력
        print(f"DEBUG: Exception in generate_answer_with_context - {str(e)}")
        return {
            "success": False,
            "message": f"Error occurred: {str(e)}"
        }
