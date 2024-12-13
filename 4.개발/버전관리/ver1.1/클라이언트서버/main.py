from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query_stock', methods=['POST'])
def query_stock():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        password = data.get('password')
        message = data.get('message')

        # RAG API 호출
        api_url = "http://localhost:8000/rag"
        request_data = {
            "id": user_id,
            "pw": password,
            "question": message
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        api_response = requests.post(
            api_url,
            json=request_data,
            headers=headers,
            timeout=30,  # 30초로 타임아웃 설정
            verify=False  # SSL 인증서 검증 비활성화
        )

        if api_response.status_code == 200:
            response_data = api_response.json()
            return jsonify({"success": True, "data": response_data})
        else:
            return jsonify({
                "success": False, 
                "error": f"API 서버 응답 오류 (상태 코드: {api_response.status_code})"
            }), 500

    except requests.exceptions.ConnectionError:
        return jsonify({
            "success": False,
            "error": "RAG API 서버에 연결할 수 없습니다. API 서버가 실행 중인지 확인해주세요."
        }), 500
    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "API 요청 시간이 초과되었습니다. 잠시 후 다시 시도해주세요."
        }), 500
    except Exception:
        return jsonify({
            "success": False,
            "error": "예상치 못한 오류가 발생했습니다."
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
