import arxiv #arxiv 모듈 불러오기, arxiv 라이브러리 (arxiv 논문 사이트 크롤링 라이브러리)
import re
from pathlib import Path #pathlib 모듈에서 Path 기능 가져오기 
from llama_index.readers.file.docs import PDFReader 

paper = next(arxiv.Client().results(arxiv.Search(id_list=["1603.09320"])))
paper.download_pdf(filename="hnsw.pdf")

loader = PDFReader() 

#\N이 유니코드로 인식되어 \\N으로 수정
documents = loader.load_data(file=Path('C:\Clove106\CST\\Normalization\hnsw.pdf'))


#ducumets의 내용에서 불필요한 텍스트를 지우는 과정 
def clean_up_text(content: str)-> str:
    

    content = re.sub(r'(\w+)-\n(\w+)', r'\1\2', content)

    unwanted_patterns = [
        "\\n", "  —", "——————————", "—————————", "—————",
        r'\\u[\dA-Fa-f]{4}', r'\uf075', r'\uf0b7'
    ]

    for pattern in unwanted_patterns:
        content = re.sub(pattern, "", content)  

    content = re.sub(r'(\w)\s*-\s*(\w)', r'\1-\2', content)
    content = re.sub(r'\s+', ' ', content)

    return content


cleaned_docs = []
for d in documents:
    cleaned_text = clean_up_text(d.text)
    d.text = cleaned_text
    cleaned_docs.append(d)

#결과 출력라인
# print("documents[0]의 출력 결과:", documents[0])
# print("cleaned_docs[0].get_content()의 출력 결과: ", cleaned_docs[0].get_content())
# print("cleaned_docs[0].metadata의 출력 결과: ", cleaned_docs[0].metadata)

#라마 인덱스를 활용하여 PDF파일을 불러오고 불필요한 텍스트를 제거하여 정돈된 데이터를 얻을 수 있는 실습.
