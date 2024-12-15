from __init__ import run_app
from flask_cors import CORS

def create_app():
    app = run_app()
    CORS(app)  # CORS 설정을 앱 생성 후 즉시 적용
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000)
    