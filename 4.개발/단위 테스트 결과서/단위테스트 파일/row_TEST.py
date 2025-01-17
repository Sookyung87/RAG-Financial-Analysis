from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys


# stdout 인코딩을 UTF-8로 설정
sys.stdout.reconfigure(encoding='utf-8')

# 브라우저 설정 및 열기
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


url = f'https://finance.naver.com/research/company_list.naver?keyword=&searchType=brokerCode&brokerCode={56}&writeFromDate=&writeToDate=&itemName=&itemCode=&x=7&y=2'
driver.get(url)

# 페이지 로드 대기
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.type_1')))

rows = driver.find_elements(By.XPATH, '//*[@id="contentarea_left"]/div[2]/table[1]/tbody/tr')


for index, row in enumerate(rows[2:15], start=3):
    try:
            # 각 row 안에서 상대적 경로로 링크 찾기

            rows = driver.find_elements(By.XPATH, '//*[@id="contentarea_left"]/div[2]/table[1]/tbody/tr')
            row = rows[index]

            detail_link = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2) a')
            detail_link.click()

            time.sleep(1)
            driver.back()

    except Exception as e:
        print(f"Error occurred: {e}")
        continue
