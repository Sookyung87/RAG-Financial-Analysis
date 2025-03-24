import openai
from langchain_pinecone import Pinecone as LangPinecone
from langchain.vectorstores import Pinecone as PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
import sqlite3

# 방법3 - 렝체인을 사용하여 정확도 향상 방법

# OpenAI API Key 설정
openai.api_key = "REMOVED_OPENAI_API_KEY"

# Pinecone API Key 및 설정
pinecone_api_key = "pcsk_1jdim_KL9H4gTcBXzBVr7z6j11yHHtm5QJo7f3zwQhLsvd4rroVuYUC7VBSNdmDUdB8RG"
pinecone_index_name = "stock-research"
index_host = "https://stock-research-mi8t0io.svc.aped-4627-b74a.pinecone.io"  # 제공된 host

# Pinecone 초기화
pc = Pinecone(api_key=pinecone_api_key)

# 인덱스 확인 및 생성
if pinecone_index_name not in pc.list_indexes().names():
    pc.create_index(
        name=pinecone_index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
else:
    print(f"'{pinecone_index_name}' 인덱스가 이미 존재합니다.")

# Pinecone 인덱스 가져오기
pinecone_index = pc.Index(name=pinecone_index_name, host=index_host)
print(f"'{pinecone_index_name}' 인덱스에 연결되었습니다.")

# Pinecone Manager Class
class PineconeManager:
    def __init__(self, index):
        self.index = index

    def upsert(self, vectors, namespace="ns1"):
        self.index.upsert(vectors=vectors, namespace=namespace)
        print(f"{len(vectors)}개의 데이터를 업로드 완료!")

# SQLite 데이터를 Pinecone에 업로드
def upload_data_to_pinecone(sqlite_db_path, pinecone_manager, batch_size=100):
    conn = sqlite3.connect(sqlite_db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            id, title, stock_name, broker, date, goal_price, recommendation, sub_title, body, url, stock_code 
        FROM stock_analysis
    """)

    vectors = []
    embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)
    for row in cursor.fetchall():
        (
            id, title, stock_name, broker, date, 
            goal_price, recommendation, sub_title, body, url, stock_code
        ) = row

        # body 필드로 임베딩 생성
        embedding = embeddings.embed_query(body)

        # Pinecone에 업로드할 데이터 작성
        vectors.append({
            "id": str(id),  # ID는 반드시 문자열이어야 합니다.
            "values": embedding,
            "metadata": {
                "title": title,
                "stock_name": stock_name,
                "broker": broker,
                "date": date,
                "goal_price": goal_price,
                "recommendation": recommendation,
                "sub_title": sub_title,
                "body": body,
                "url": url,
                "stock_code": stock_code
            }
        })

        # 배치 업로드
        if len(vectors) >= batch_size:
            pinecone_manager.upsert(vectors, namespace="ns1")
            vectors = []  # 초기화

    # 남은 데이터 업로드
    if vectors:
        pinecone_manager.upsert(vectors, namespace="ns1")
    conn.close()

# LangChain 기반 QA 시스템 구축
def build_langchain_qa(index_name):
    # PineconeVectorStore 생성
    vectorstore = PineconeVectorStore(
        index=pinecone_index,  # Pinecone 인덱스 객체
        embedding=OpenAIEmbeddings(openai_api_key=openai.api_key), # 임베딩 함수
        text_key="title",               # 메타데이터에서 검색할 텍스트 필드의 키
        namespace="ns1",      # 업로드한 데이터의 namespace
    )

    # Retriever 생성
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

    # Prompt Template 설정
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "다음 문맥을 참고하여 질문에 답변하세요:\n\n"
            "문맥: {context}\n\n"
            "질문: {question}"
        ),
    )

     # ChatOpenAI로 LLM 초기화
    llm = ChatOpenAI(
        model="gpt-4",  # GPT-4 모델 사용
        openai_api_key=openai.api_key,
    )

    # RetrievalQA Chain 생성
    chain = RetrievalQA.from_chain_type(
        retriever=retriever,
        llm=llm,
        chain_type="stuff",
        chain_type_kwargs={
            "prompt": prompt_template,
        },
    )

    return chain

# QA 실행
def ask_question(chain, question):
    # 검색 실행
    result = chain.invoke({"query": question})
    
     # 검색된 문서 메타데이터 출력
    print("\n[검색된 문서 메타데이터]")
    if "source_documents" in result:
        for doc in result["source_documents"]:
            print(f"- Title: {doc.metadata.get('title', 'N/A')}")
            print(f"- Stock Name: {doc.metadata.get('stock_name', 'N/A')}")
            print(f"- Broker: {doc.metadata.get('broker', 'N/A')}")
            print(f"- Date: {doc.metadata.get('date', 'N/A')}")
            print(f"- URL: {doc.metadata.get('url', 'N/A')}")
            print("-----")
    else:
        print("검색된 문서가 없습니다.")
    
    # 결과 텍스트 반환
    return result.get("output_text", "검색된 결과가 없습니다.")

# Main 실행
if __name__ == "__main__":
    sqlite_db_path = "C:/Users/이수경/Desktop/cap/정확도향상테스트/Updated_RAGdata.db"

    # Pinecone Manager 초기화
    pinecone_manager = PineconeManager(pinecone_index)

    # 데이터 업로드 (필요 시 실행)
    upload_data_to_pinecone(sqlite_db_path, pinecone_manager)

    # LangChain QA 시스템 구축
    qa_chain = build_langchain_qa(pinecone_index_name)

    # 질문 루프
    while True:
        question = input("질문을 입력하세요 (종료하려면 'exit' 입력): ").strip()
        if question.lower() == "exit":
            break
        answer = ask_question(qa_chain, question)
        print(f"답변: {answer}")
