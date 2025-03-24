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
db_path = os.path.join(os.path.dirname(__file__), 'RAG_sample_data.db')  # 현재 스크립트 파일 위치 기준으로 상대 경로 설정

def fetch_data_from_db():
    # db_path 사용
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT id, 제목, 내용 FROM news")
    rows = cursor.fetchall()
    connection.close()
    return rows

def document_splits():
    rows = fetch_data_from_db()
    docs = [Document(page_content=row[2], metadata={"title": row[1]}) for row in rows]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)
    return splits

def create_vectorstore():    # 벡터스토어 생성 및 저장
    splits = document_splits()
    
    # text-embedding-3-small 임베딩 모델 설정
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")  # 모델 변경
    vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
    save_path = "C:/langchain"
    vectorstore.save_local(save_path)
    return vectorstore

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def top_8_docs(query):
    vectorstore = create_vectorstore()
    top_k = 8
    retrieved_docs_with_scores = vectorstore.similarity_search_with_score(query, k=top_k)
    print("\n **검색된 문서 k=8 및 유사도 점수**")
    for rank, (doc, score) in enumerate(retrieved_docs_with_scores, 1):
        print(f"\n k={rank} 문서 (유사도 점수: {score:.4f})")
        print(doc.page_content[:300] + "...")  # 내용 일부 출력

def get_rag_answer(query):
    # top_8_docs(query=query)
    vectorstore=create_vectorstore()

    prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="다음은 참고할 문서입니다:\n\n{context}\n\n질문: {question}\n\n답변:"
    )

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    retriever = vectorstore.as_retriever()
    rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
    )
    answer = rag_chain.invoke(query)
    return answer


# query = "나도브릭의 유상증자는 어떻게 진행되나요?"
# answer = get_rag_answer(query)
# print(answer)
