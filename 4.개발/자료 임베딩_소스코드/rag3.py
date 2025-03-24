import os
import sqlite3
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings  # HuggingFaceEmbeddings 사용
from langchain_core.prompts import PromptTemplate
from flask import Flask, request, jsonify
from transformers import AutoModel, AutoTokenizer
import torch
import faiss

# 환경변수에서 OpenAI API 키 가져오기
os.environ['OPENAI_API_KEY'] = 'REMOVED_OPENAI_API_KEY'  # 보안상 환경변수를 사용하는 것이 좋음.

# Flask 앱 초기화
app = Flask(__name__)

# KF-DeBERTa 모델과 토크나이저 로드
model_name = "kakaobank/kf-deberta-base"
model = AutoModel.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 상대 경로로 DB 파일 연결
db_path = os.path.join(os.path.dirname(__file__), 'RAG_sample_data.db')  # 현재 스크립트 파일 위치 기준으로 상대 경로 설정

def fetch_data_from_db():
    """DB에서 데이터를 가져오는 함수"""
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT id, 제목, 내용 FROM news")
    rows = cursor.fetchall()
    connection.close()
    return rows

def generate_embeddings(texts):
    """KF-DeBERTa를 사용하여 텍스트 임베딩 벡터 생성"""
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt", max_length=512)
    with torch.no_grad():
        model_output = model(**inputs)
    
    embeddings = model_output.last_hidden_state.mean(dim=1).cpu().numpy()  # 문장 임베딩 (mean pooling)
    return embeddings

def create_vectorstore():
    """새로운 FAISS 벡터 저장소 생성 및 저장"""
    print("새로운 벡터 저장소를 생성합니다...")

    rows = fetch_data_from_db()
    docs = [Document(page_content=row[2], metadata={"title": row[1]}) for row in rows]

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)

    texts = [doc.page_content for doc in splits]
    embeddings = generate_embeddings(texts)

    # FAISS 인덱스 생성
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    # FAISS 인덱스를 로컬에 저장
    faiss.write_index(index, os.path.join("faiss_vector_db", "faiss_index"))

    return splits, index

def load_or_create_vectorstore():
    """기존 FAISS 벡터 저장소가 있으면 불러오고, 없으면 새로 생성"""
    if os.path.exists(os.path.join("faiss_vector_db", "faiss_index")):
        print("기존 벡터 저장소를 불러옵니다...")
        index = faiss.read_index(os.path.join("faiss_vector_db", "faiss_index"))
        rows = fetch_data_from_db()
        docs = [Document(page_content=row[2], metadata={"title": row[1]}) for row in rows]
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        splits = text_splitter.split_documents(docs)
        return splits, index
    else:
        return create_vectorstore()

def search_faiss(query, index, docs, k=8):
    """FAISS에서 입력한 쿼리에 대해 유사도가 높은 문서 검색"""
    query_embedding = generate_embeddings([query])
    _, indices = index.search(query_embedding, k)

    retrieved_docs = [docs[i] for i in indices[0] if i < len(docs)]
    return retrieved_docs

def get_rag_answer(query):
    """질문을 받아 RAG 시스템을 통해 답변 생성"""
    docs, index = load_or_create_vectorstore()

    retrieved_docs = search_faiss(query, index, docs)
    formatted_docs = "\n\n".join(doc.page_content for doc in retrieved_docs)

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="다음은 참고할 문서입니다:\n\n{context}\n\n질문: {question}\n\n답변:"
    )

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    rag_chain = (
        {"context": formatted_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    answer = rag_chain.invoke(query)
    return answer
