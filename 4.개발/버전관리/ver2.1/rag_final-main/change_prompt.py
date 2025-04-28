import os
from datetime import datetime
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from flask import jsonify
from embed_db import document_splits
from openai import OpenAI

# API 키 설정
os.environ['OPENAI_API_KEY'] = 'REMOVED_OPENAI_API_KEY'
openai_client = OpenAI(api_key="REMOVED_OPENAI_API_KEY")

vectorstore = None

def create_or_load_vectorstore(model_name="text-embedding-3-small"):
    global vectorstore
    base_dir = os.path.dirname(os.path.abspath(__file__))
    vs_path = os.path.join(base_dir, f'{model_name.replace("/", "_")}_FAISS')
    index_file = os.path.join(vs_path, "index.faiss")
    pkl_file = os.path.join(vs_path, "index.pkl")
    embeddings = OpenAIEmbeddings(model=model_name)

    if os.path.exists(index_file) and os.path.exists(pkl_file):
        vectorstore = FAISS.load_local(
            folder_path=vs_path,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
        print("✅ FAISS 인덱스 로드 완료")
    else:
        print("⚠️ FAISS 인덱스가 없어 새로 생성합니다...")
        splits = document_splits()
        vectorstore = FAISS.from_documents(splits, embeddings)
        if not os.path.exists(vs_path):
            os.makedirs(vs_path)
        vectorstore.save_local(vs_path)
        print("✅ 새 FAISS 인덱스 생성 완료")

def top_5_docs(query):
    global vectorstore
    retrieved = vectorstore.similarity_search_with_score(query, k=7)
    seen_titles = set()
    unique_docs = []
    for doc, score in retrieved:
        title = doc.metadata["title"]
        if title not in seen_titles:
            seen_titles.add(title)
            unique_docs.append({
                "title": title,
                "score": round(float(score), 2),
                "content": doc.page_content[:300] + "..."
            })
        if len(unique_docs) >= 5:
            break
    return unique_docs

def get_llm_answer(query):
    #프롬프트
    prompt = f"""
    질문 : {query}
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini", #gpt-4o-mini가 더 저렴하긴 한데 좀 멍청함
        messages=[
            {"role": "user", "content" : prompt}
        ],
        max_tokens=2000, #최대 토큰값
        n=1, #답변 수
        stop=None, #중도정지기능 x
        temperature = 0 #창의력 값을 0으로 설정하여 원하는 결과만 유도
    )
    answer = response.choices[0].message.content.strip()
    return answer


def get_rag_answer(query, model_name="text-embedding-3-small"):
    create_or_load_vectorstore(model_name)
    today_date = datetime.now().strftime("%Y-%m-%d")

    prompt_template = PromptTemplate(
        input_variables=["context", "question", "date"],
        template=(
            "당신은 주식자문 시스템입니다. 주식 시장에 관한 답변을 제공할 때, 최신 데이터를 우선적으로 사용하고, "
            "현재 날짜와 가장 근접한 데이터를 기반으로 답변을 한국어로 제공합니다.\n"
            "제공된 5개 데이터가 전부 질문과 관련 없을 시, 답변하지 말고 다른 질문을 요청하도록 합니다.\n"
            "최신 트렌드, 뉴스, 보고서 및 시장 데이터를 반영하여 고객에게 가장 신뢰할 수 있는 정보를 제공해야 합니다.\n\n"
            "현재 날짜는 {date}이며, 다음은 참고할 문서입니다:\n\n"
            "{context}\n\n"
            "질문: {question}"
        )
    )

    reference_docs = top_5_docs(query)
    similarity_str = "\n".join([
        f"doc{i+1}: {doc['title']}\n유사도: {doc['score']}\n" for i, doc in enumerate(reference_docs)
    ])
    formatted_docs = "\n\n".join([
        f"[{doc['title']}]\n{doc['content']}" for doc in reference_docs
    ])

    formatted_prompt = prompt_template.format(
        context=formatted_docs,
        question=query,
        date=today_date
    )

    # RAG 응답 (문서 기반)
    rag_response = ChatOpenAI(model_name="gpt-4o-mini", temperature=0).invoke(formatted_prompt).content


    llm_response = get_llm_answer(query)

    return jsonify({
        "Similarity": similarity_str,
        "Prompt": formatted_prompt,
        "RAG": rag_response,
        "LLM": llm_response,
        "success": True
    })
