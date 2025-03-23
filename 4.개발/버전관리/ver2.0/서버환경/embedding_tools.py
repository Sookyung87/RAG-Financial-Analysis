import os
import sqlite3
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

os.environ['OPENAI_API_KEY'] = 'REMOVED_OPENAI_API_KEY'
os.environ['COHERE_API_KEY'] = 'Rs6c5TrXEwoawvTI3ZN0cvQwYlb5AXBuKcuemiwE'

def fetch_data_from_db():
    db_file = 'RAG_sample_data.db'
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute("SELECT id, 제목, 내용 FROM news")
    rows = cursor.fetchall()
    connection.close()
    return rows

def document_splits():
    rows = fetch_data_from_db()
    docs = [Document(page_content=row[2], metadata={"title": row[1]}) for row in rows]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)
    return splits

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

