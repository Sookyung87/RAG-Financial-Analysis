from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# 브라우저 설정 및 열기
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL 설정 및 이동
url = 'https://finance.naver.com/item/coinfo.naver?code=005930'
driver.get(url)

try:
    # 페이지 로드 상태 확인
    WebDriverWait(driver, 20).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    print("Page loaded completely.")

    # 요소가 특정 텍스트를 가질 때까지 대기
    WebDriverWait(driver, 30).until(
        EC.text_to_be_present_in_element((By.XPATH, '//*[@id="pArea"]/div[1]/div/table/tbody/tr[3]/td/dl/dt[2]/b')))
    print("Target text is present.")

    # 요소 찾기
    element = driver.find_element(By.XPATH, '//*[@id="pArea"]/div[1]/div/table/tbody/tr[3]/td/dl/dt[2]/b')

    # 스크롤 이동
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()

    # 텍스트 추출
    print(f"Extracted text: {element.text}")

except Exception as e:
    print(f"Error occurred: {e}")

finally:
    driver.quit()


