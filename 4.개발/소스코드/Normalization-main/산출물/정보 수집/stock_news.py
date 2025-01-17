import json
import sqlite3
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import uuid

# 원하는 디렉토리 경로 (환경에 맞춰 수정)
new_directory = "C:\\Users\\nighc\\Desktop\\Crawl"
os.chdir(new_directory)
print("Working directory:", os.getcwd())

# stdout 인코딩을 UTF-8로 설정
sys.stdout.reconfigure(encoding='utf-8')

# SQLite 데이터베이스 연결
db_path = 'CrawlData.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 테이블 생성
cursor.execute('''
CREATE TABLE IF NOT EXISTS stock_news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    reporter TEXT
    stock_name TEXT,
    date TEXT, 
    sub_title TEXT,
    body TEXT,
    url TEXT,
    stock_code TEXT
)
''')

# 데이터 중복 확인 함수
def is_duplicate_in_db(cursor, title, date, broker):
    cursor.execute('''
        SELECT COUNT(*)
        FROM stock_news
        WHERE title = ? AND date = ? AND broker = ?
    ''', (title, date, broker))
    return cursor.fetchone()[0] > 0

# 브라우저 설정 및 열기
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 브로커 코드 리스트
item_codes = ["005930", "000660", "373220", "207940", "005380", "000270", "068270", "105560", "035420", "055550"]

# 뉴스 데이터 크롤링
for item_code in item_codes:
    try:
        url = f'https://finance.naver.com/item/news.naver?code={item_code}'
        driver.get(url)

        # 뉴스 테이블 행 가져오기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div/table[1]/tbody/tr'))
        )
        rows = driver.find_elements(By.XPATH, '/html/body/div/table[1]/tbody/tr')

        print(f"Found {len(rows)} rows for item code {item_code}")

        rows = driver.find_elements(By.XPATH, '//*[@id="contentarea_left"]/div[2]/table[1]/tbody/tr')

        for index, row in enumerate(rows[2:15], start=3):
            try:
                rows = driver.find_elements(By.XPATH, '/html/body/div/table[1]/tbody/tr')
                if len(rows) > index:
                    row = rows[index]
                    detail_link = row.find_element(By.XPATH, '//table[@class="type5"]/tbody/tr[@class="first"]/td[@class="title"]/a')
                    detail_link.click()
                    time.sleep(1)
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.box_type_m.box_type_m3'))
                    )

                    # 데이터 수집
                    # main_text = driver.find_element(By.XPATH, '//*[@class="view_sbj"]').text
                    # title = main_text.split('\n')[0]
                    # stock_name = driver.find_element(By.CSS_SELECTOR, '#contentarea_left .view_sbj > span').text
                    # broker = driver.find_element(By.XPATH, '//*[@class="source"]').text.split('|')[0].strip()
                    # date = driver.find_element(By.XPATH, '//*[@class="source"]').text.split('|')[1].strip()
                    # goal_price = driver.find_element(By.XPATH, '//*[@class="money"]').text
                    # recommendation = driver.find_element(By.XPATH, '//*[@class="coment"]').text
                    # sub_title = driver.find_element(By.XPATH, '//*[@id="contentarea_left"]/div[2]/table/tbody/tr[4]/td/div[1]/p[1]/strong').text
                    # body = driver.find_element(By.XPATH, '//*[@id="contentarea_left"]/div[2]/table/tbody/tr[4]/td/div[1]/p[2]').text
                    # stock_code = item_code

                    # 중복 확인 및 데이터 저장
                    # if not is_duplicate_in_db(cursor, title, date, broker):
                    #     cursor.execute('''
                    #         INSERT INTO stock_analysis (title, stock_name, broker, date, goal_price, recommendation, sub_title, body, url, stock_code)
                    #         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    #     ''', (title, stock_name, broker, date, goal_price, recommendation, sub_title, body, driver.current_url, stock_code))
                    #     conn.commit()

                    # 이전 페이지로 돌아가기
                    driver.back()
                    time.sleep(1)
                else:
                    print(f"Row {index} not found on item code page {item_code}")
                    continue

            except Exception as e:
                print(f"Error occurred: {e}")
                continue

    except Exception as e:
        print(f"Error occurred with item code {item_code}: {e}")
        continue

# 브라우저 닫기
driver.quit()
conn.close()
