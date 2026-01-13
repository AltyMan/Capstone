from flask import Flask
from routes.habits import habits_bp
from test_init import *
from db.sqlite import get_connection
from db.init_db import init_db

def create_app() -> Flask:
    
    init_db()
    habit_test_3()
    
    app = Flask(__name__)
    app.register_blueprint(habits_bp)
    
    return app

app = create_app()

@app.get("/")
def home():
    return "One day of singing. Yeah, yeah."

if __name__ == "__main__":
    app.run(host="192.168.2.19", port=5000)
