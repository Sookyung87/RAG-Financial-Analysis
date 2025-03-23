import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import embedding_tools as et
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate


def top_5_docs(query):
    vectorstore = create_vectorstore()
    top_k = 5
    retrieved_docs_with_scores = vectorstore.similarity_search_with_score(query, k=top_k)

    reference_docs = []
    for rank, (doc, score) in enumerate(retrieved_docs_with_scores, 1):
        reference_docs.append({
            "rank": rank,
            "score": float(score),  
            "content": doc.page_content[:300] + "..."  # 내용 일부만 반환
        })

    return reference_docs

def create_vectorstore():    # 벡터스토어 생성 및 저장
    base_dir = os.path.dirname(os.path.abspath(__file__))
    vs_file = os.path.join(base_dir, 'text_embedding_ada_002_FAISS')  # 실행한 폴더 내에 저장
    
    splits = et.document_splits()
    vectorstore = FAISS.from_documents(documents=splits, embedding=OpenAIEmbeddings())
    vectorstore.save_local(vs_file)
    return vectorstore


def get_rag_answer(query):
    vectorstore=create_vectorstore()

    prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="다음은 참고할 문서입니다:\n\n{context}\n\n질문: {question}\n\n답변:"
    )

    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    retriever = vectorstore.as_retriever()
    rag_chain = (
    {"context": retriever | et.format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
    )
    answer = rag_chain.invoke(query)
    return answer


# query = "나도브릭의 유상증자는 어떻게 진행되나요?"
# answer = get_rag_answer(query)
# print(answer)
# top = top_5_docs(query)
# print(top)