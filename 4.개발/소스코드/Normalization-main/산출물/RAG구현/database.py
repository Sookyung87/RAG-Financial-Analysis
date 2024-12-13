import sqlite3
import json
import os

# 데이터베이스 연결 및 테이블 생성
conn = sqlite3.connect('CrawlData.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS research (
        id TEXT PRIMARY KEY,
        title TEXT,
        stock_name TEXT,
        broker TEXT,
        date DATE,
        goal_price INTEGER,
        recommendation TEXT,
        sub_title TEXT,
        body TEXT
    )
''')

# JSON 파일 경로
file_path = 'C:/Users/이수경/Desktop/Capstone_Normalization/Normalization/산출물/RAG구현/CrawlData.json'

# JSON 파일 확인 및 로드
if not os.path.exists(file_path):
    print("파일을 찾을 수 없습니다:", file_path)
else:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        print("데이터가 로드되었습니다.")

# goal_price 값 변환 함수
def convert_goal_price(value):
    try:
        # 숫자로 변환할 수 있는 경우 ',' 제거 후 정수로 변환
        return int(value.replace(",", ""))
    except (ValueError, TypeError):
        # 변환할 수 없는 경우 None 반환
        return None

# 데이터 삽입
for entry in data:
    cursor.execute('''
        INSERT OR IGNORE INTO research (id, title, stock_name, broker, date, goal_price, recommendation, sub_title, body)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (entry.get('id'), entry['title'], entry['stock_name'], entry['broker'], entry['date'],
          convert_goal_price(entry.get('goal_price')), entry.get('recommendation'), entry.get('sub_title'), entry.get('body')))

conn.commit()

# 데이터 확인을 위해 쿼리 실행 및 출력
cursor.execute("SELECT * FROM research WHERE broker = ?", ("신한투자증권",))
rows = cursor.fetchall()
for row in rows:
    print(row)

# 데이터베이스 연결 종료
conn.close()
