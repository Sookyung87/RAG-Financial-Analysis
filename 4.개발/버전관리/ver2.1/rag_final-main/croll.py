import feedparser
from bs4 import BeautifulSoup
from trafilatura import fetch_url, extract
import pandas as pd
import sqlite3
from datetime import datetime
import deepl  # pip install deepl

print("🚀 프로그램이 시작되었습니다.")

# ✅ DeepL API 키 설정
auth_key = "d2a4f978-1f8e-43b7-87f8-ff0d97c66fcd:fx"
translator = deepl.Translator(auth_key)

# ✅ 매일경제 RSS 주소
rss_url = "https://www.mk.co.kr/rss/50200011/"

# ✅ DB 연결 시도
try:
    conn = sqlite3.connect('RAG_sample_data.db')
    cursor = conn.cursor()
    print("✅ DB 연결 성공")
except Exception as e:
    print(f"❌ DB 연결 실패: {e}")

# ✅ 기존 링크 수집
cursor.execute('SELECT "링크" FROM news')
existing_links = set(row[0] for row in cursor.fetchall())

# ✅ RSS 파싱
feed = feedparser.parse(rss_url)
print(f"📰 RSS 항목 수: {len(feed.entries)}개")

# ✅ 뉴스 수집
title_list = []
contents_list = []
link_list = []

for entry in feed.entries:
    url = entry.link
    if url in existing_links:
        continue

    html = fetch_url(url)
    if html is None:
        continue

    soup = BeautifulSoup(html, 'html.parser')
    if soup.title is None:
        continue

    title = soup.title.string.strip().replace('\n', ' ').strip()
    text = extract(html)
    if not text:
        continue

    try:
        parsed_date = datetime(*entry.published_parsed[:6])
        formatted_date = parsed_date.strftime("%Y.%m.%d")
    except:
        formatted_date = datetime.now().strftime("%Y.%m.%d")

    full_content = f"입력 {formatted_date}.\n{text}"

    title_list.append(title)
    contents_list.append(full_content)
    link_list.append(url)

# ✅ 새 뉴스 저장
if title_list:
    df = pd.DataFrame({
        '제목': title_list,
        '내용': contents_list,
        '링크': link_list
    })
    df.to_sql('news', conn, if_exists='append', index=False)
    print(f"✅ 새 뉴스 {len(df)}건 저장 완료.")
else:
    print("ℹ️ 저장할 새 뉴스가 없습니다.")

# ✅ 영어내용 컬럼이 없을 경우 추가
try:
    cursor.execute("ALTER TABLE news ADD COLUMN 영어내용 TEXT")
except sqlite3.OperationalError:
    pass  # 이미 있을 경우 무시

# ✅ 번역 대상 개수 확인
cursor.execute('SELECT COUNT(*) FROM news WHERE 영어제목 IS NULL OR 영어제목 = "" OR 영어내용 IS NULL OR 영어내용 = ""')
target_count = cursor.fetchone()[0]
print(f"🔍 번역 대상 뉴스 개수: {target_count}")

# ✅ 번역 대상 조회
cursor.execute('SELECT id, 제목, 내용 FROM news WHERE 영어제목 IS NULL OR 영어제목 = "" OR 영어내용 IS NULL OR 영어내용 = ""')
rows = cursor.fetchall()

if not rows:
    print("ℹ️ 번역할 뉴스가 없습니다.")
else:
    for row in rows:
        news_id, title_ko, content_ko = row
        print(f"\n[→] 번역 시도: id={news_id}, 제목 길이: {len(title_ko)}, 내용 길이: {len(content_ko)}")

        try:
            title_en = translator.translate_text(title_ko, source_lang="KO", target_lang="EN-US").text
            content_en = translator.translate_text(content_ko, source_lang="KO", target_lang="EN-US").text

            cursor.execute('''
                UPDATE news
                SET 영어제목 = ?, 영어내용 = ?
                WHERE id = ?
            ''', (title_en, content_en, news_id))

            print(f"[✅] 번역 성공: id={news_id}")

        except Exception as e:
            print(f"[❌] 번역 실패: id={news_id}, 에러: {e}")

# ✅ DB 저장 및 종료
conn.commit()
conn.close()
print("\n🏁 전체 작업 완료")
