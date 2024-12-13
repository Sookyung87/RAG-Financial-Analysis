import json
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import uuid  # UUID 모듈 추가

# 원하는 디렉토리 경로 (환경에 맞춰 수정)
new_directory = "C:\\Users\\nighc\\Desktop\\Crawl"

# 작업 디렉토리 변경
os.chdir(new_directory)

# 변경된 작업 디렉토리 확인
print("Working directory:", os.getcwd())

# stdout 인코딩을 UTF-8로 설정
sys.stdout.reconfigure(encoding='utf-8')

# JSON 파일 경로
json_file_path = 'CrawlData.json'

# 기존 파일이 있다면 로드하고, 없다면 빈 리스트로 시작
if os.path.exists(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
else:
    data = []

# 데이터 중복 확인 함수
def is_duplicate(data_list, new_data):
    for existing_data in data_list:
        if (
            existing_data["title"] == new_data["title"]
            and existing_data["date"] == new_data["date"]
            and existing_data["broker"] == new_data["broker"]
        ):
            return True
    return False

# 브라우저 설정 및 열기
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 브로커 코드 리스트
item_codes = ["005930", "000660", "373220", "207940", "005380", "000270", "068270", "105560", "035420", "055550"]

# 증권사별로 URL을 변경하며 크롤링
for item_code in item_codes:
    try:
        url = f'https://finance.naver.com/research/company_list.naver?keyword=&brokerCode=&writeFromDate=&writeToDate=&searchType=itemCode&itemName=%BB%EF%BC%BA%C0%FC%C0%DA&itemCode={item_code}&x=39&y=24  '
        driver.get(url)

        # 페이지 로드 대기
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.type_1')))
        rows = driver.find_elements(By.XPATH, '//*[@id="contentarea_left"]/div[2]/table[1]/tbody/tr')

        for index, row in enumerate(rows[2:15], start=3):
            try:
                rows = driver.find_elements(By.XPATH, '//*[@id="contentarea_left"]/div[2]/table[1]/tbody/tr')
                if len(rows) > index:
                    row = rows[index]
                    detail_link = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2) a')
                    detail_link.click()
                    time.sleep(1)
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.box_type_m.box_type_m3'))
                    )

                    # 데이터 수집
                    main_text = driver.find_element(By.XPATH, '//*[@class="view_sbj"]').text
                    title = main_text.split('\n')[0]
                    stock_name = driver.find_element(By.CSS_SELECTOR, '#contentarea_left .view_sbj > span').text
                    broker = driver.find_element(By.XPATH, '//*[@class="source"]').text.split('|')[0].strip()
                    date = driver.find_element(By.XPATH, '//*[@class="source"]').text.split('|')[1].strip()
                    goal_price = driver.find_element(By.XPATH, '//*[@class="money"]').text
                    recommendation = driver.find_element(By.XPATH, '//*[@class="coment"]').text
                    sub_title = driver.find_element(By.XPATH, '//*[@id="contentarea_left"]/div[2]/table/tbody/tr[4]/td/div[1]/p[1]/strong').text
                    body = driver.find_element(By.XPATH, '//*[@id="contentarea_left"]/div[2]/table/tbody/tr[4]/td/div[1]/p[2]').text
                    

                    # 데이터를 딕셔너리 형태로 변환하고 ID 및 URL 추가
                    stock_data = {
                        "id": str(uuid.uuid4()),  # 고유한 ID 생성
                        "title": title,
                        "stock_name": stock_name,
                        "broker": broker,
                        "date": date,
                        "goal_price": goal_price,
                        "recommendation": recommendation,
                        "sub_title": sub_title,
                        "body": body,
                        "url": driver.current_url,  # 현재 페이지의 URL 추가
                        "stock_code" : item_code
                    }

                    # 중복 여부 확인 후 추가
                    if not is_duplicate(data, stock_data):
                        data.append(stock_data)

                    # 이전 페이지로 돌아가기
                    driver.back()
                    time.sleep(1)
                else:
                    print(f"Row {index} not found on item code page {item_code}")
                    continue

            except Exception as e:
                print(f"Error occurred: {e}")
                continue

        # 각 브로커 코드가 끝날 때 JSON 파일 저장
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"Error occurred with item code {item_code}: {e}")
        # JSON 파일 저장
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        continue

# 브라우저 닫기
driver.quit()
