import json
import sqlite3

# JSON 파일 읽기 (환경에 맞춰 수정)
with open('C:\\Users\\nighc\\Desktop\\Crawl\\CrawlData.json', 'r', encoding='utf-8') as file:
    data = json.load(file)


# SQLite 데이터베이스에 연결 (혹은 생성)``
conn = sqlite3.connect('C:\\Users\\nighc\\Desktop\\Crawl\\CrawlData.db')
cursor = conn.cursor()

# 테이블 생성 (필드명은 JSON 데이터 구조에 따라 설정)
cursor.execute('''
CREATE TABLE IF NOT EXISTS stock_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    stock_name TEXT,
    broker TEXT,
    date TEXT,
    goal_price TEXT,
    recommendation TEXT,
    sub_title TEXT,
    body TEXT,
    url TEXT,
    stock_code TEXT
)
''')

# JSON 데이터 삽입
for item in data:
    cursor.execute('''
    INSERT INTO stock_analysis (title, stock_name, broker, date, goal_price, recommendation, sub_title, body, url, stock_code)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (item['title'], item['stock_name'], item['broker'], item['date'], item['goal_price'], item['recommendation'], item['sub_title'], item['body'], item['url'], item['stock_code']))

# 변경사항 저장 및 연결 닫기
conn.commit()
conn.close()

print("데이터베이스 생성 및 데이터 삽입 완료!")
