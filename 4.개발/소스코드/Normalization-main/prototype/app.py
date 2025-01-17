import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from chat_request import send_openai_request
from openai import OpenAI

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    api_key = db.Column(db.String(255))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ChatMessage(db.Model): # ChatMessage 클래스 형식 정의
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

@login_manager.user_loader # 클라이언트가 로그인을 했을 때 리다이렉트 등 화면 이동을 해도 로그인 상태를 유지할 수 있게끔 하는 코드 
def load_user(user_id):
    return User.query.get(int(user_id)) # 세션에서 user_id 변수값을 불러오고, 이와 같은 값의 객체를 User 테이블에서 찾아서 반환한다.

@app.route('/') # 기본 경로('/')에 접속했을 때 
def index():
    return render_template('index.html') # index.html를 리턴한다.

@app.route('/chat', methods=['POST']) # /chat 경로로 POST 요청(채팅 입력 후 엔터)이 왔을 때
def chat():
    if not current_user.is_authenticated: #만약 현재 사용자가 로그인되어있지 않다면
        return jsonify({'error': '채팅을 시작하려면 로그인이 필요합니다.'}), 401 # HTTP 상태코드 401를 반환하고 json 형식으로 '채팅을 시작하려면 로그인이 필요합니다.'라는 에러 메시지를 반환한다.

    user_message = request.json['message'] # user_message 변수에 클라이언트한테 전달받은 json 데이터의 message 부분을 저장한다.
    try: # 예외 처리 기술로 try문 안의 코드를 실행한다. 오류가 없다면 except 부분은 무시한다.
        if current_user.api_key: # 만약 current_user 객체의 api_key 속성에 값이 들어있다면 
            api_key = current_user.api_key # api_key 변수에 위의 속성 값을 넣는다.
        else: # 그렇지 않다면 (current_user 객체의 api_key 속성에 값이 없다면)
            return jsonify({'error': 'OpenAI API 키가 설정되지 않았습니다. 설정 페이지에서 API 키를 먼저 설정해주세요.'}), 401 # HTTP 상태코드 401를 반환하고 json 형식으로 'OpenAI API 키가 설정되지 않았습니다. 설정 페이지에서 API 키를 먼저 설정해주세요.'라는 에러 메시지를 반환한다.

        bot_response = send_openai_request(user_message, api_key) # bot_response 변수에 openai api의 응답을 저장한다. 

        chat_message = ChatMessage(user_id=current_user.id, message=user_message, response=bot_response)
        db.session.add(chat_message) # chat_message 변수값을 db에 추가한다.
        db.session.commit() # 데이터베이스에 변경사항을 커밋한다.
        return jsonify({'response': bot_response}) # json 데이터로 "response"키에 bot_response 변수 값을 반환한다.
    except Exception as e: #만약 try문에서 오류가 발생했다면 발생한 예외를 변수 e에 저장하고
        app.logger.error(f"Error in chat request: {str(e)}") # 발생한 오류를 string 형으로 "Error in chat request : " 와 함께 서버 로그에 기록한다.
        return jsonify({'error': str(e)}), 500 # json 데이터로 'error' : 발생한 예외 (string형) 값을 반환하고 HTTP 상태코드 500을 반환한다.

@app.route('/chat_history')
@login_required # 로그인 상태가 요구되며 로그인하지 않았을 시 로그인 페이지로 리다이렉트 한다.
def chat_history():
    messages = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.timestamp).all()
    return jsonify([{'message': msg.message, 'response': msg.response} for msg in messages])

@app.route('/set_api_key', methods=['POST'])
@login_required # 로그인 상태가 요구되며 로그인하지 않았을 시 로그인 페이지로 리다이렉트 한다.
def set_api_key():
    api_key = request.json['api_key'] # 전달받은 json 데이터의 'api_key' 값을 api_key 변수에 저장한다.
    try: # 예외 처리 기술로 try문 안의 코드를 실행한다. 오류가 없다면 except 부분은 무시한다.
        current_user.api_key = api_key # 현재 로그인된 유저의 api_key 속성에 api_key 변수를 저장한다. 
        db.session.commit() # 데이터베이스에 변경사항을 커밋한다.
        return jsonify({'success': True}) # json 데이터로 'success' : True를 반환한다.
    except Exception as e: # 만약 오류가 발생하면 예외를 변수 e에 저장하고
        app.logger.error(f"Error setting API key: {str(e)}") # 변수 e를 string 형으로 "Error setting API key: " 와 함께 서버 로그에 기록한다.
        return jsonify({'success': False, 'error': str(e)}), 500 # json 데이터로 'success' : False, 'error' : 변수 e(string형 예외상황) 을 반환하고, HTTP 상태코드 500을 반환한다.

@app.route('/register', methods=['GET', 'POST']) # /register 경로로 POST 요청(회원가입정보 입력)이 왔을 때
def register():
    if request.method == 'POST': # 만약 클라이언트로부터 POST가 왔다면
        username = request.form.get('username') # username 변수에 전달받은 아이디 부분을 저장한다.
        password = request.form.get('password') # password 변수에 전달받은 비밀번호 부분을 저장한다.
        confirm_password = request.form.get('confirm_password') # confirm_password 변수에 전달받은 비밀번호 확인 부분을 저장한다.
        api_key = request.form.get('api_key') # api_key 변수에 전달받은 API 키 부분을 저장한다.
        
        if not api_key: # 만약 api_key 변수가 None 이라면 (입력값이 없다면)
            flash('API 키를 입력해주세요.', 'error') # 'API 키를 입력해주세요.'라는 에러 알람을 띄운다.
            return redirect(url_for('register')) # register() 함수와 연결된 URL을 리다이렉트한다.
        
        if password != confirm_password: # 만약 password 변수가 confirm_password 변수와 다르다면 
            flash('비밀번호가 일치하지 않습니다.') # '비밀번호가 일치하지 않습니다.'라는 알람을 띄운다.
            return redirect(url_for('register')) # register() 함수와 연결된 URL을 리다이렉트한다.

        
        user = User.query.filter_by(username=username).first() # User테이블의 username 속성과 username 변수를 비교하여 중복값이 존재하면 그 값을 user변수에 넣고 db검색을 종료한다.
        if user: # 만약 user 변수에 값이 들어있으면 (= 중복되는 username이 있으면)
            flash('이미 존재하는 사용자 이름입니다.') # '이미 존재하는 사용자 이름입니다.'라는 알람을 띄운다. 
            return redirect(url_for('register')) # register() 함수와 연결된 URL을 리다이렉트한다.

        
        new_user = User(username=username, api_key=api_key) # 입력받은 Username, api_key 를 사용해 새로운 User객체 new_user를 만든다.
        new_user.set_password(password) # password 값을 해쉬값으로 암호화하여 new_user 객체에 저장한다.
        db.session.add(new_user) # new_user 객체를 db에 추가한다.
        db.session.commit() # 데이터베이스에 변경사항을 커밋한다.
        
        flash('회원가입이 완료되었습니다. 로그인해주세요.') # '회원가입이 완료되었습니다. 로그인해주세요.' 알람을 띄운다.
        return redirect(url_for('login')) # login() 함수와 연결된 URL을 리다이렉트한다.
    
    return render_template('register.html') # register.html을 리턴한다.

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': # 클라이언트가 로그인 폼을 제출했다면
        username = request.form.get('username') # username 변수에 전달받은 아이디 부분을 저장한다.
        password = request.form.get('password') # password 변수에 전달받은 비밀번호 부분을 저장한다.
        
        user = User.query.filter_by(username=username).first() # User테이블의 username 속성과 username 변수를 비교하여 중복값이 존재하면 그 값을 user변수에 넣고 db검색을 종료한다.
        if user and user.check_password(password): # 만약 user 변수 값이 존재하고 + 입력된 비밀번호와 db의 비밀번호 해쉬값이 같다면 
            login_user(user) # user 계정으로 로그인한다.
            return redirect(url_for('index')) # index() 함수와 연결된 URL을 리다이렉트한다.
        else: # 그렇지 않으면 (if 조건 중 하나라도 충족하지 못하면)
            flash('잘못된 사용자 이름 또는 비밀번호입니다.') # '잘못된 사용자 이름 또는 비밀번호입니다.' 알람을 표시한다.
            return redirect(url_for('login')) # login() 함수와 연결된 URL을 리다이렉트한다.
    
    return render_template('login.html') # login.html를 리턴한다.

@app.route('/logout')
@login_required # 로그인 상태가 요구되며 로그인하지 않았을 시 로그인 페이지로 리다이렉트 한다.
def logout():
    logout_user() # 로그아웃한다.
    return redirect(url_for('index')) # index() 함수와 연결된 URL을 리다이렉트한다.

@app.route('/check_username', methods=['POST'])
def check_username():
    username = request.json['username'] # 클라이언트가 보낸 json 데이터에서 'username' 부분을 username 변수에 저장한다.
    user = User.query.filter_by(username=username).first() # User테이블의 username 속성과 username 변수를 비교하여 중복값이 존재하면 그 값을 user변수에 넣고 db검색을 종료한다.
    return jsonify({'available': user is None}) # user변수에 값이 없다면 json 데이터로 'available' : True 를 반환하고, 값이 있다면 'available' : False 를 반환한다.

@app.route('/settings') # 설정창 ('/settings')에 접속했을 때 
@login_required # 로그인 상태가 요구되며 로그인하지 않았을 시 로그인 페이지로 리다이렉트 한다.
def settings():
    return render_template('settings.html') # settings.html를 리턴한다.

@app.route('/update_api_key', methods=['POST'])
@login_required # 로그인 상태가 요구되며 로그인하지 않았을 시 로그인 페이지로 리다이렉트 한다.
def update_api_key():
    api_key = request.form.get('api_key') # api 키 입력 창에 입력한 값을 api_key변수에 넣는다.
    if not api_key: # 만약 api_key 변수가 비어있으면
        flash('API 키를 입력해주세요.', 'error') # 'API 키를 입력해주세요.' 경고문을 출력한다.
    else: # 그렇지 않으면 (=변수에 값이 있으면)
        current_user.api_key = api_key # current_user 객체의 api_key 속성에 api_key 값을 넣는다.
        db.session.commit() # 데이터베이스에 변경사항을 커밋한다.
        flash('API 키가 성공적으로 업데이트되었습니다.', 'success') # 'API 키가 성공적으로 업데이트되었습니다.' 성공 문구를 출력한다.
    return redirect(url_for('settings')) # 이후에 /settings 페이지로 리다이렉트한다. 

with app.app_context(): # main.py 실행 시 context를 생성한다. (context란 프로그램 실행에 필요한 준비과정을 말함) 
    db.create_all() # 테이블이 존재하지 않으면 테이블을 새로 생성한다. 이후 with문을 종료한다.

if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5000) 
