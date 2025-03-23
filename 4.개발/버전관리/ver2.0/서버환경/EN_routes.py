from flask import Flask, request, jsonify
import EN_rag as raga
# import llmAnswer
# import rag3 as ragb


#초록색 형식으로 코드를 짜되 너의 코드 이름은 rag2 부분에 적고, ragb는 걍 별명이니 무시해도 됨. 


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
        answer = raga.get_rag_answer(request_question)
        return jsonify(answer)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"오류 발생: {str(e)}"
        }), 500


# @app.route('/rag3', methods=['POST'])
# def rag3():
#    try:
#        data = request.get_json()
#        request_question = data['question']
#            # 주식 관련 질문 처리
#        answer = ragb.get_rag_answer(request_question)
#        return jsonify({
#            'success': True,
#            'answer': answer
#        })

#    except Exception as e:
#        return jsonify({
#            'success': False,
#            'message': f"오류 발생: {str(e)}"
#        }), 500
        
# LLM으로 엔드포인트 설정
# @app.route('/llm', methods=['POST'])
# def rag():
#     try:
#         data = request.get_json()
#         request_question = data['question']
        
#         # LLM을 사용하여 답변 생성
#         answer = llmAnswer.get_llm_answer(request_question)
        
#         return jsonify({
#             'success': True,
#             'answer': answer
#         })
    
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': f"오류 발생: {str(e)}"
#         }), 500
        
# 서버 실행
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)  # 모든 네트워크 인터페이스에서 8000 포트로 실행
