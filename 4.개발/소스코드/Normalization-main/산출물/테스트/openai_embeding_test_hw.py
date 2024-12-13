import os

os.environ["OPENAI_API_KEY"] = "REMOVED_OPENAI_API_KEY"

from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings


#Batch size- 일괄적으로 처리되는 집단, 무리 (모델이 동시에 처리할 입력의 개수를 의미함.)
# Batch size가 너무 큰 경우 - 한 번에 처리해야할 데이터의 양이 많아져, 학습 속도가 느려지고, 메모리 부족 문제가 발생할 수 있다.
#Batch size가 너무 작은 경우 - 적은 데이터로 가중치가 자주 업데이트되어 훈련이 불안정해진다. 
#속도와 메모리 사용량의 균형을 조절

#OpenAIEmbedding 클래스는 OpenAI에서 제공하는 임베딩 모델을 활용해 텍스트 데이터를 벡터 형태로 변환한다.
embed_model = OpenAIEmbedding(embed_batch_size=10)
#embed_model의 객체에 특정 기본값이나 전역적인 설정을 저장함.
Settings.embed_model = embed_model

#model="text-embedding-3-large" - OpenAi의 최신 모델 버전중 하나로 정교한 임베딩 벡터를 생성.
#임베딩 모델에는 text-embedding-3-small / text-embedding-3-large 이 최신 버전의 모델임.
embed_model = OpenAIEmbedding(model="text-embedding-3-large")

#아래의 텍스트를 api에 전달하여 임베딩을함.
#embed_batch_size=10으로 설정했으므로, 처음 10개의 텍스트를 api에 전달해 임베딩을 수행함 
embeddings = embed_model.get_text_embedding("Open AI new Embeddings models is great.")
print(embeddings) #임베딩된 데이터 출력.
