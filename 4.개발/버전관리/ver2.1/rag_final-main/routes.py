from flask import Flask, request, jsonify
import change_prompt as ragc

app = Flask(__name__)

@app.route('/prompt_rag', methods=['POST'])
def prompt_rag():
    try:
        data = request.get_json()
        request_question = data['question']
        return ragc.get_rag_answer(request_question)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"오류 발생: {str(e)}"
        }), 500

@app.route('/test', methods=['POST'])
def test():
    try:
        return jsonify({
            'Similarity': 'doc1: 삼성전자 뉴스\n유사도: 0.72\ndoc2: 삼성전자 공시\n유사도: 0.73\ndoc3: LG 뉴스\n유사도: 0.74\ndoc4: LG 공시\n유사도: 0.75\ndoc5: 하이닉스 뉴스\n유사도: 0.78',
            'Prompt': '이것은 프롬프트이다. 이것은 프롬프트이다. ...',
            'RAG': 'RAG 답변입니다.',
            'LLM': 'LLM 답변입니다.',
            'success': True
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"오류 발생: {str(e)}"
        }), 500

# 서버 실행
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)