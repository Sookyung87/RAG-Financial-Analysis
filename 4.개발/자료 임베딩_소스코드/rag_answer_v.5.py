import openai
from langchain_pinecone import Pinecone as LangPinecone
from langchain_pinecone import Pinecone as PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pinecone import Pinecone, ServerlessSpec
import sqlite3

# OpenAI API Key 설정
openai.api_key = "REMOVED_OPENAI_API_KEY"

# Pinecone API Key 및 설정
pinecone_api_key = "pcsk_1jdim_KL9H4gTcBXzBVr7z6j11yHHtm5QJo7f3zwQhLsvd4rroVuYUC7VBSNdmDUdB8RG"
pinecone_index_name = "stock-research"
index_host = "https://stock-research-mi8t0io.svc.aped-4627-b74a.pinecone.io"

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
    
    # 변경된 스키마에 맞게 SELECT 문 수정
    cursor.execute("SELECT id, 제목, 내용 FROM news")

    vectors = []
    embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)
    for row in cursor.fetchall():
        (id, title, body) = row

        # 본문(body) 필드로 임베딩 생성
        embedding = embeddings.embed_query(body)

        # Pinecone에 업로드할 데이터 작성
        vectors.append({
            "id": str(id),  # ID는 반드시 문자열이어야 합니다.
            "values": embedding,
            "metadata": {
                "title": title,
                "body": body,
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
        embedding=OpenAIEmbeddings(openai_api_key=openai.api_key),  # 임베딩 함수
        text_key="body",  # 본문에서 검색
        namespace="ns1",
    )

    # Retriever 생성 (검색된 문서 개수 k=8로 변경)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 8})

    # Prompt Template 설정
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "당신은 주식 자문 시스템입니다. 다음 문맥을 참고하여 질문에 답변하세요: "
            "문맥: {context}\n\n"
            "질문: {question}"
        ),
    )

    # ChatOpenAI로 LLM 초기화
    llm = ChatOpenAI(
        model="gpt-4",
        openai_api_key=openai.api_key,
    )

    # RetrievalQA Chain 생성
    chain = RetrievalQA.from_chain_type(
        retriever=retriever,
        llm=llm,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt_template},
    )

    return chain, vectorstore

# QA 실행 및 검색된 문서 출력
def ask_question(chain, vectorstore, question):
    # 검색 실행 (유사도 포함)
    retrieved_docs_with_scores = vectorstore.similarity_search_with_score(question, k=8)

    print("\n[검색된 문서 및 유사도 점수]")
    if retrieved_docs_with_scores:
        for i, (doc, score) in enumerate(retrieved_docs_with_scores):
            print(f"문서 {i + 1}:")
            print(f" - 제목: {doc.metadata.get('title', 'N/A')}")
            print(f" - 본문: {doc.page_content[:100]}...")  # 본문 일부만 출력
            print(f" - 유사도 점수: {score:.4f}")
            print("-----")
    else:
        print("관련 문서를 찾을 수 없습니다.")

    # RAG 체인 실행 및 답변 출력
    response = chain.invoke({"query": question})
    return response.get("output_text", "검색된 결과가 없습니다.")


# Main 실행
if __name__ == "__main__":
    sqlite_db_path = "C:/Users/이수경/Desktop/cap/정확도향상테스트/RAG_sample_data.db"

    # Pinecone Manager 초기화
    pinecone_manager = PineconeManager(pinecone_index)

    # 데이터 업로드 (필요 시 실행)
    upload_data_to_pinecone(sqlite_db_path, pinecone_manager)

    # LangChain QA 시스템 구축
    qa_chain, vectorstore = build_langchain_qa(pinecone_index_name)

    # 질문 루프
    while True:
        question = input("질문을 입력하세요 (종료하려면 'exit' 입력): ").strip()
        if question.lower() == "exit":
            break
        answer = ask_question(qa_chain, vectorstore, question)
        print(f"답변: {answer}")
