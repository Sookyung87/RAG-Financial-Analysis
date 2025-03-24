from flask import Flask, request, jsonify
import rag as raga
import EN_rag as ragb
import llm as llma
import change_prompt as ragc
import deepl
# import llmAnswer
# import rag3 as ragb


#초록색 형식으로 코드를 짜되 너의 코드 이름은 rag2 부분에 적고, ragb는 걍 별명이니 무시해도 됨. 

# auth_key는 번역기 api 키
auth_key = "2fc705ba-7ffd-48ba-b3a1-78c2b24bd0d9:fx"
translator = deepl.Translator(auth_key=auth_key)

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



@app.route('/prompt_rag', methods=['POST'])
def prompt_rag():
    try:
        data = request.get_json()
        request_question = data['question']
            # 주식 관련 질문 처리
        answer = ragc.get_rag_answer(request_question)
        return jsonify(answer)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"오류 발생: {str(e)}"
        }), 500




@app.route('/translate_rag', methods=['POST'])
def translate_rag():
    try:
        data = request.get_json()
        request_question = data['question']
        question_en = translator.translate_text(request_question, target_lang="EN-US").text
            # 주식 관련 질문 처리
        answer = ragb.get_rag_answer(question_en)
        return jsonify(answer)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"오류 발생: {str(e)}"
        }), 500


@app.route('/llm', methods=['POST'])
def llm():
    try:
        data = request.get_json()
        request_question = data['question']
            # 주식 관련 질문 처리
        answer = llma.get_llm_answer(request_question)
        return jsonify({
            'answer' : answer,
            'doc1' : {'link' : None, 'score' : None, 'title' : None},
            'doc2' : {'link' : None, 'score' : None, 'title' : None},
            'doc3' : {'link' : None, 'score' : None, 'title' : None},
            'doc4' : {'link' : None, 'score' : None, 'title' : None},
            'doc5' : {'link' : None, 'score' : None, 'title' : None}})
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"오류 발생: {str(e)}"
        }), 500


@app.route('/test', methods=['POST'])
def test():
    try:
        data = request.get_json()
        request_question = data['question']
            # 주식 관련 질문 처리
        return jsonify({'answer': '테스트용 답변입니다', 
                        'doc1': {'link': 'https://test1.com', 'score': 1.00, 'title': '테스트 기사제목1'}, 
                        'doc2': {'link': 'https://test2.com', 'score': 2.22, 'title': '테스트 기사제목2'}, 
                        'doc3': {'link': 'https://test3.com', 'score': 3.33, 'title': '테스트 기사제목3'}, 
                        'doc4': {'link': 'https://test4.com', 'score': 4.44, 'title': '테스트 기사제목4'}, 
                        'doc5': {'link': 'https://test5.com', 'score': 5.55, 'title': '테스트 기사제목5'}})
            
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
