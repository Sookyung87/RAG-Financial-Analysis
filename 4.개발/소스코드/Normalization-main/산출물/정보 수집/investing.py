import pandas as pd
import json

# CSV 파일 경로

csv_file_path = "C:\\Users\\nighc\\Desktop\\investing\\005930.csv"

# CSV 파일 읽기
df = pd.read_csv(csv_file_path)

# DataFrame을 JSON으로 변환
json_output = df.to_json(orient='records', force_ascii=False)

# JSON 파일 저장
json_file_path = "output.json"
with open(json_file_path, "w", encoding="utf-8") as json_file:
    json_file.write(json_output)

print("CSV 파일이 JSON으로 변환되어 저장되었습니다:", json_file_path)
