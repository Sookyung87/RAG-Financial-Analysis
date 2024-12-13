from pinecone.grpc import PineconeGRPC as Pinecone

pc = Pinecone(api_key="d139d7c0-a790-4107-ae0d-8578afb1e411")
index = pc.Index("llm-book") 
# llm-book 인덱스 768차원임

index.upsert(
    vectors = [
    {"id": "vec1", "values": [1.0] * 768, "metadata": {"genre": "drama"}},
    {"id": "vec2", "values": [2.0] * 768, "metadata": {"genre": "action"}},
    {"id": "vec3", "values": [0.1] * 768, "metadata": {"genre": "drama"}},
    {"id": "vec4", "values": [1.0] * 768, "metadata": {"genre": "action"}}
]
,
    namespace= "ns1"
)

response = index.query(
    namespace="ns1",
    vector=[0.1] * 768,  
    top_k=2,
    include_values=True,
    include_metadata=True,
    
)

with open("output.txt", "w") as f:
    print(response, file=f)