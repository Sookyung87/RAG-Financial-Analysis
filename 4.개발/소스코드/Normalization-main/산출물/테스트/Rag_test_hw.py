from pinecone.grpc import PineconeGRPC as Pinecone
from sentence_transformers import SentenceTransformer
# from llama_index.core import VectorStoreIndex, Document
# Pinecone 초기화
pc = Pinecone(api_key="d139d7c0-a790-4107-ae0d-8578afb1e411")
index = pc.Index("jsontest")

# Sentence Transformer 모델 초기화 (예: all-MiniLM-L6-v2)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# # LlamaIndex 초기화
# llama_index = SimpleIndex()

# 검색 및 응답 함수 정의
def search_with_rag(question):
    # 질문을 벡터화
    question_embedding = model.encode(question).tolist()
    
    # Pinecone에서 유사한 벡터 검색
    response = index.query(
        vector=question_embedding,
        top_k=2,
        include_values=True,
        include_metadata=True,
        namespace="ns1"
    )
    
    return title_result(response)
    # 유사한 결과를 LlamaIndex에 추가
    # documents = []
    # for match in response['matches']:
    #     metadata = match['metadata']
    #     content = metadata['body']  # 검색된 문서의 본문
    #     documents.append(Document(text=content))
    
    # vector_index = VectorStoreIndex(documents)

    # # VectorStoreIndex를 사용해 응답 생성
    # answer = vector_index.query(question)
    # return answer


def title_result(response):
    #검색된 결과를 반환
    results = []
    for match in response['matches']:
        metadata = match['metadata']
        title = metadata.get('title', 'No content available')  # 검색된 문서의 본문
        body = metadata.get('body', 'No body available')
        results.append({"title":title, "body": body})
    
    return results

# 사용 예제
question = "대우건설의 3분기 연결기준 매출액은?"
answer = search_with_rag(question)

for i, result in enumerate(answer, 1):
    print(f"Result {i} Title:\n{result['title']}\n")
    print(f"Result {i} Body:\n{result['body']}\n")