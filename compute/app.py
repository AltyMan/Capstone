from flask import Flask
from routes.habits import habits_bp
from test_init import *

app = Flask(__name__)
app.register_blueprint(habits_bp)

@app.get("/")
def home():
    return "One day of singing. Yeah, yeah."

habit_test_2()
if __name__ == "__main__":
    app.run(host="192.168.2.19", port=5000)
