import os
import sqlite3
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# ✅ OpenAI API 키 설정
os.environ['OPENAI_API_KEY'] = 'REMOVED_OPENAI_API_KEY'

def fetch_data_from_db():
    db_path = os.path.join(os.path.dirname(__file__), 'RAG_sample_data.db')
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # ✅ 영어제목, 영어내용, 링크 추출
    cursor.execute("SELECT 영어제목, 영어내용, 링크 FROM news WHERE 영어제목 IS NOT NULL AND 영어내용 IS NOT NULL")
    rows = cursor.fetchall()
    connection.close()
    return rows

def document_splits():
    rows = fetch_data_from_db()
    docs = [Document(page_content=row[1], metadata={"title": row[0], "link": row[2]}) for row in rows]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return text_splitter.split_documents(docs)

def create_and_save_vectorstore():
    splits = document_splits()
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vs_path = os.path.join(os.path.dirname(__file__), 'text-embedding-3-small_FAISS')
    if not os.path.exists(vs_path):
        os.makedirs(vs_path)
    vectorstore = FAISS.from_documents(splits, embeddings)
    vectorstore.save_local(vs_path)
    print("✅ FAISS 벡터스토어가 성공적으로 생성되었습니다.")

if __name__ == '__main__':
    create_and_save_vectorstore()