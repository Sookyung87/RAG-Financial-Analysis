from flask import request, jsonify
import user_service as us
import price_service as price
import analyze_service as analyze
import get_goal_price as ggp
import rag_answer as raga
from question_classify import question_type
from rag_answer import PineconeManager, NLPProcessor
from werkzeug.exceptions import BadRequest
import json


from DB_structure import Chat
from __init__ import db

#이수경 - 인자값에 정의 해줘야돼서 코드 추가했음
# Flask 앱 초기화 부분에 추가
API_KEY = "pcsk_1jdim_KL9H4gTcBXzBVr7z6j11yHHtm5QJo7f3zwQhLsvd4rroVuYUC7VBSNdmDUdB8RG"
INDEX_NAME = "stock-research"

pinecone_manager = PineconeManager(API_KEY, INDEX_NAME)
nlp_processor = NLPProcessor()


def setup_routes(app):

    @app.route('/')
    def mainpage():
        return jsonify({
            'API name': 'Stock Analysis RAG API',
            'version': '1.0',
            'endpoint': '-'
        })
    
    @app.route('/check_userid', methods=['POST'])
    def check_userid():
        data = request.get_json()

        request_id = data['id']
        return us.find_userid(request_id)
        

    @app.route('/rag', methods=['POST'])
    def rag():
        try: 
            data = request.get_json()

            request_id = data['id']
            request_pw = data['pw']
            request_question = data['question']

            if us.auth_userid(request_id, request_pw) == False:
                return jsonify({
                    'success' : False,
                    'system' : '아이디나 비밀번호가 잘못되었습니다.',

                })
        

            new_chat = Chat()
            new_chat.username = request_id
            new_chat.question = request_question


            # 1. 주식의 가격을 묻는 질문
            # 2. 주식의 미래 가격 추측을 묻는 질문
            # 3. 주식 종목 분석 질문
            # 4. 주식과 관련된 그 외의 질문
            # 5. 주식과 관련없는 질문
            type = question_type(request_question)
            if type == '1':
                answer = price.get_stock_price(request_question)
                new_chat.answer = json.dumps(answer)
                db.session.add(new_chat)
                db.session.commit()
                return jsonify(answer)

            elif type == '2' :
                stock_code = analyze.get_stock_code(request_question)
                answer = ggp.query_stock_data(request_question, stock_code)
                new_chat.answer = json.dumps(answer)
                db.session.add(new_chat)
                db.session.commit()
                return jsonify(answer)

            elif type == '3' :
                answer = analyze.get_stock_analyze(request_question)
                new_chat.answer = json.dumps(answer)
                db.session.add(new_chat)
                db.session.commit()
                return jsonify(answer)
           
            elif type == '4':
                try:
                    # `pinecone_manager`와 `nlp_processor`를 전달
                    answer = raga.generate_answer_with_context(
                        request_question, pinecone_manager, nlp_processor
                    )

                    if not answer["success"]:
                        new_chat.answer = answer["message"]
                        db.session.add(new_chat)
                        db.session.commit()
                        return jsonify(answer)

                    new_chat.answer = json.dumps(answer["answer"])
                    db.session.add(new_chat)
                    db.session.commit()

                    response_data = {
                        "1.success": True,
                        "2.context": answer["context"],
                        "3.similarity": answer["similarity"],
                        "4.RAGanswer": answer["answer"],
                        "5.LLManswer" : answer["answer2"]

                    }
                    return jsonify(response_data)

                except Exception as e:
                    return jsonify({
                        "success": False,
                        "message": f"RAG 처리 중 오류 발생: {str(e)}"
                    }), 500

            elif type == '5':
                return jsonify({
                    'success' : True,
                    'message' : '증권 관련 질문을 입력해주세요.'
                })
            
            return jsonify({
                'success' : False,
                'message' : '질문 분석 오류. 질문을 다시 입력해주세요.'
            })
        
        except BadRequest:
            # JSON 파싱 실패 시 처리
            return jsonify({
                'success': False,
                'message': '요청 데이터가 잘못된 JSON 형식입니다.'
            }), 400

        except Exception as e:
            # 기타 예외 처리
            return jsonify({
                'success': False,
                'message': f'서버 내부 오류: {str(e)}'
            }), 500