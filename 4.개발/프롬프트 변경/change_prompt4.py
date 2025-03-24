import os
import sqlite3
from datetime import datetime  # 오늘 날짜를 가져오기 위해 추가
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings  # OpenAIEmbeddings 임포트
from langchain_core.prompts import PromptTemplate
from flask import Flask, request, jsonify

# 환경변수에서 OpenAI API 키 가져오기
os.environ['OPENAI_API_KEY'] = 'REMOVED_OPENAI_API_KEY'  # 보안상 환경변수를 사용하는 것이 좋음.

app = Flask(__name__)

# 상대 경로로 DB 파일 연결
db_path = os.path.join(os.path.dirname(__file__), 'RAG_sample_data.db')  # 현재 스크립트 파일 위치 기준으로 상대 경로 설정

def fetch_data_from_db():
    """DB에서 데이터를 가져오는 함수"""
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT id, 제목, 내용, 링크 FROM news")  # '작성일자' 컬럼을 제외하고 데이터만 가져옵니다.
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
    vs_file = os.path.join(base_dir, f'{model_name.replace("/", "_")}_FAISS')  # 폴더 이름에 특수문자 없이 저장
    
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
    top_k = 10  
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

    # 오늘 날짜를 구함
    today_date = datetime.now().strftime("%Y-%m-%d")  # str 형태로 변환

    prompt = PromptTemplate(
        input_variables=["context", "question", "date"],  # 날짜를 프롬프트에 포함
        template="당신은 주식자문 시스템입니다. 주식 시장에 관한 답변을 제공할 때, 최신 데이터를 우선적으로 사용하고, 현재 날짜와 가장 근접한 데이터를 기반으로 답변을 제공합니다. "
                 "최신 트렌드, 뉴스, 보고서 및 시장 데이터를 반영하여 고객에게 가장 신뢰할 수 있는 정보를 제공해야 합니다. 현재 날짜는 {date}이며, 다음은 참고할 문서입니다:\n\n{context}\n\n질문: {question}\n\n답변:"
    )

    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    retriever = vectorstore.as_retriever()
    rag_chain = (
    {
        "context": retriever | format_docs, 
        "question": RunnablePassthrough(), 
        "date": RunnableLambda(lambda _: today_date)  # 문자열을 Runnable로 변환
    }  
    | RunnableLambda(lambda inputs: prompt.format(**inputs))  # PromptTemplate을 Runnable로 변환
    | llm
    | StrOutputParser()
    )
    answer = rag_chain.invoke(query)
    
    # 유사도 점수와 함께 반환
    reference_docs = top_5_docs(query)
    
    # 결과 형식
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

# query = "저번주 화요일에 한국거래서에 어떤일이 있었나요? 지금 현재 날짜도 같이 답해주세요."
# answer = get_rag_answer(query)
# print(answer)
