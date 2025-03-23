from flask import Flask, request, jsonify
import text_embedding_ada_002.text_embedding_ada_002 as raga


app = Flask(__name__)

@app.route('/')
def mainpage():
    return jsonify({
        'API name': 'Stock Analysis RAG API',
        'version': '1.0',
        'endpoint': '-'
    })
    
@app.route('/rag', methods=['POST'])
def rag():
    try:
        data = request.get_json()
        request_question = data['question']
            # 주식 관련 질문 처리
        re_docs = raga.top_5_docs(request_question)
        answer = raga.get_rag_answer(request_question)
        return jsonify({
            'success': True,
            'answer': answer,
            'reference_docs' : re_docs
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"오류 발생: {str(e)}"
        }), 500
        
# 서버 실행
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)  # 모든 네트워크 인터페이스에서 8000 포트로 실행
