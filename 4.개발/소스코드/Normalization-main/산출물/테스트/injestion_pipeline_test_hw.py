#pinecoone Ingestion Pipeline 실습
# 
#pinecone 5.3.1
#arxiv 2.1.3
#llama-index 0.11.16
#llama-index-vector-stores-pinecone 0.2.1
#llama-index-readers-file 0.2.2
# 
#  
import os
import llamatest_hw

from llama_index.core.node_parser import SemanticSplitterNodeParser #문서를 노드로 분할함
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever

from pinecone.grpc import PineconeGRPC
from pinecone import ServerlessSpec

from llama_index.vector_stores.pinecone import PineconeVectorStore

#Openai API키 입력 
os.environ["OPENAI_API_KEY"]="REMOVED_OPENAI_API_KEY"
#임베딩 모델 정의 
embed_model = OpenAIEmbedding(embed_batch_size=10, model="text-embedding-3-small")

#pinecone api키 입력
pc=PineconeGRPC(api_key="d139d7c0-a790-4107-ae0d-8578afb1e411")

#pinecone db의 인덱스 이름 선언
index_name = "llama-integration-example"

#Pinecone 인덱스 생성 (한번 실행되고 재실행하면 이미 생성된 인덱스라고 하며 오류가 발생함)

# pc.create_index(
#     index_name,
#     dimension=1536,
#     spec=ServerlessSpec(cloud="aws", region="us-east-1"),
# )

pinecone_index = pc.Index(index_name)

#PineconeVectorstore 초기화 
#vectorstore는 RAG의 핵심 구성요소로, llamaindex를 사용하는 모든 프로그램에 직접, 간접적으로 사용함.
#pinecone 인덱스에 저장함.
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

#Pinepline 선언 
#데이터를 효과적으로 수집, 전처리, 인덱스하여 검색 및 질의 응답 성능을 최적화 하기 위함.
pipeline = IngestionPipeline(
    transformations=[
        SemanticSplitterNodeParser(
            buffer_size=1,
            breakpoint_percentile_threshold=95,
            embed_model=embed_model,),
        embed_model,
    ],
    vector_store=vector_store #변환된 데이터를 pinecone 인덱스에 업서트함. 
)

#pineline 실행
pipeline.run(documents=llamatest_hw.cleaned_docs)


#pinecone에는 인덱스의 레코드를 네임스페이스로 분할할 수 있음.
#describe_index_stats 작업은 네임스페이스별 할당된 백터수, 벡터 차원수, 인덱스 충만도를 포함하여 인데스 내용에 대한 통계를 반환함.
#pincone_index의 전체적 정보를 반환
pinecone_index.describe_index_stats()

#pinecone 자체에서 검색 결과를 가져오기 위해서 VectorStoreIndex 객체와, VectorIndexRetrever객체를 만들어야함.

#vector_store 객체로부터 VectorStoreIndex 객체를 인스턴스화
vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

#가장 유사한 5개의 검색결과를 가져옴.
retriever = VectorIndexRetriever(index=vector_index, similarity_top_k=5)

#질문 쿼리
answer = retriever.retrieve('How does logarithmic complexity affect graph construction?')

#답변 출력 
print([i.get_content() for i in answer])

#llamatest_hw.py에서 정돈된 문서를 임베딩화하여 pinecone db에 저장을 하였음. 
#pinecone db에서 유사한 5개의 검색 결과를 가져옴.
