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

# 브로커 코드 리스트
broker_codes = [56, 21, 57, 18, 15, 64, 78, 39, 66, 16]

# 증권사별로 URL을 변경하며 크롤링
for broker_code in broker_codes:
    url = f'https://finance.naver.com/research/company_list.naver?keyword=&searchType=brokerCode&brokerCode={broker_code}&writeFromDate=&writeToDate=&itemName=&itemCode=&x=7&y=2'
    driver.get(url)

    time.sleep(1)
driver.quit()

