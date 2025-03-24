import os
import sqlite3
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings  # OpenAIEmbeddings 임포트
from langchain_core.prompts import PromptTemplate
from flask import Flask, request, jsonify

# 환경변수에서 OpenAI API 키 가져오기
os.environ['OPENAI_API_KEY'] = 'REMOVED_OPENAI_API_KEY'  # 보안상 환경변수를 사용하는 것이 좋음.

app = Flask(__name__)

# 상대 경로로 DB 파일 연결
db_path = os.path.join(os.path.dirname(__file__), 'EN_RAG_sample_data.db')  # 현재 스크립트 파일 위치 기준으로 상대 경로 설정

def fetch_data_from_db():
    """DB에서 데이터를 가져오는 함수"""
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT id, 제목, 내용, 링크 FROM news")  # 링크도 가져오기
    rows = cursor.fetchall()
    connection.close()
    return rows

def document_splits():
    """문서 분할"""
    rows = fetch_data_from_db()
    docs = [Document(page_content=row[2], metadata={"title": row[1], "link": row[3]}) for row in rows]  # 링크 포함
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)
    return splits

def create_vectorstore(model_name="text-embedding-3-small"):    
    """모델별 벡터스토어 생성 및 저장"""
    splits = document_splits()
    
    # OpenAI 임베딩 모델 설정
    embeddings = OpenAIEmbeddings(model=model_name)
    
    # 상대 경로로 폴더에 저장
    base_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 스크립트의 절대 경로
    vs_file = os.path.join(base_dir, 'EN-text-embedding-3-small_FAISS')
    
    if not os.path.exists(vs_file):  # 경로가 없으면 생성
        os.makedirs(vs_file)
    
    vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
    vectorstore.save_local(vs_file)  # 생성된 벡터스토어를 지정된 경로에 저장
    return vectorstore

def format_docs(docs):
    """문서 내용 형식화"""
    return "\n\n".join(doc.page_content for doc in docs)

def top_5_docs(query):
    """유사도 기반으로 상위 5개 문서 검색 (중복 제거)"""
    vectorstore = create_vectorstore()
    top_k = 10  # 더 많은 문서를 가져와서 중복을 필터링
    retrieved_docs_with_scores = vectorstore.similarity_search_with_score(query, k=top_k)

    seen_titles = set()
    unique_docs = []

    for doc, score in retrieved_docs_with_scores:
        title = doc.metadata["title"]
        if title not in seen_titles:
            seen_titles.add(title)
            unique_docs.append({
                "rank": len(unique_docs) + 1,
                "score": round(float(score), 2),
                "content": doc.page_content[:300] + "...",
                "title": title,
                "link": doc.metadata["link"]
            })
        
        if len(unique_docs) >= 5:  # 최대 5개 문서까지만 저장
            break

    return unique_docs

def get_rag_answer(query, model_name="text-embedding-3-small"):
    """질문을 받아 RAG 시스템을 통해 답변 생성"""
    vectorstore = create_vectorstore(model_name=model_name)

    prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "You are an AI assistant that analyzes news articles and provides clear, insightful answers in a conversational tone. "
        "Use only the provided context and avoid making assumptions.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Please respond in Korean in a friendly and engaging manner, as if you were explaining to someone curious about the topic. "
        "Make sure to summarize key points, analyze their significance, and provide additional details naturally within the conversation.\n\n"
        "답변:"
    )
    )



    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    retriever = vectorstore.as_retriever()
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    answer = rag_chain.invoke(query)
    
    # 유사도 점수와 함께 반환
    reference_docs = top_5_docs(query)
    
    # 원하는 형식으로 출력
    result = {
        "answer": answer,
    }
    
    # 제목, 링크, score를 세트로 묶어서 출력 (순서대로 title, link, score)
    for i, doc in enumerate(reference_docs):
        result[f"doc{i+1}"] = {
            "title": doc["title"],
            "link": doc["link"],
            "score": doc["score"]
        }
    
    return result

# query = "LG전자의 연봉 1위는 누구니?"
# answer = get_rag_answer(query)
# print(answer)
