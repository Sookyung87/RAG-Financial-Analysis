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


url = f'https://finance.naver.com/research/company_read.naver?nid=77650&page=1'
driver.get(url)


# 요소를 찾는 각 부분에 try-except 추가
try:
    stock_name = driver.find_element(By.CSS_SELECTOR, '#contentarea_left .view_sbj > span').text

except Exception as e:
    print(f"Error occurred while getting stock_name: {e}")
    stock_name = "정보 없음"  # 기본값 설정

try:
    # 제목
    main_text = driver.find_element(By.XPATH, '//*[@class="view_sbj"]').text
    # 제목
    title = main_text.split('\n')[0]  

except Exception as e:
    print(f"Error occurred while getting title: {e}")
    title = "정보 없음"  # 기본값 설정

try:
    # 증권사
    broker = driver.find_element(By.XPATH, '//*[@class="source"]').text.split('|')[0].strip()

except Exception as e:
    print(f"Error occurred while getting broker: {e}")
    broker = "정보 없음"  

try:
    # 날짜
    date = date = driver.find_element(By.XPATH, '//*[@class="source"]').text.split('|')[1].strip()
except Exception as e:
    print(f"Error occurred while getting date: {e}")
    date = "정보 없음"  # 기본값 설정

try:
    # 목표가
    goal_price = driver.find_element(By.XPATH, '//*[@class="money"]').text
except Exception as e:
    print(f"Error occurred while getting goal_price: {e}")
    goal_price = "정보 없음"  # 기본값 설정

try:
    # 투자 의견
    Recommendation = driver.find_element(By.XPATH, '//*[@class="coment"]').text
except Exception as e:
    print(f"Error occurred while getting Recommendation: {e}")
    Recommendation = "정보 없음"  # 기본값 설정

try:
    # 부제
    sub_title = driver.find_element(By.XPATH, '//*[@id="contentarea_left"]/div[2]/table/tbody/tr[4]/td/div[1]/p[1]/strong').text
except Exception as e:
    print(f"Error occurred while getting sub_title: {e}")
    sub_title = "정보 없음"  # 기본값 설정

try:
    # 본문
    body = driver.find_element(By.XPATH, '//*[@id="contentarea_left"]/div[2]/table/tbody/tr[4]/td/div[1]/p[2]').text
except Exception as e:
    print(f"Error occurred while getting body: {e}")
    body = "정보 없음"  # 기본값 설정

# 결과 출력
print(f'종목명: {stock_name} \n제목: {title} \n증권사: {broker} \n작성일: {date} \n목표가: {goal_price} \n투자 의견: {Recommendation} \n부제: {sub_title} \n본문: {body}')



# 브라우저 닫기
driver.quit()
