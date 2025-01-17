import os
from datasets import load_dataset
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever

os.environ["OPENAI_API_KEY"] ="REMOVED_OPENAI_API_KEY"

dataset = load_dataset('klue', 'mrc', split='train')

text_list = dataset[:100]['context']
documents = [Document(text = t) for t in text_list]

vector_index = VectorStoreIndex.from_documents(documents)

print((dataset[0]['question']))

retrieval_engine = VectorIndexRetriever(index=vector_index, similarity_top_k=5)
response = retrieval_engine.retrieve(dataset[0]['question'])

print(len(response))
print(response[0].node.text)
