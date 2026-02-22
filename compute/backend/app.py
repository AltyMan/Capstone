from flask import Flask
from routes.habits import habits_bp
from routes.logs import logs_bp
from routes.rules import rules_bp
from routes.users import users_bp
from test_init import *
from db.init_db import init_db

"""
Flask Application Entry Point

INTEGRATION NOTES FOR HABO (Flutter) FRONTEND
-----------------------------------------------
The Habo mobile app expects the Flask server to be accessible at the host/port
configured in `mobile/Habo/lib/repositories/http_habit_repository.dart`
(currently `http://192.168.2.19:5000`).

To fully support Habo, you will need to register additional blueprints:
  - `events_bp` (for habit events/calendar data) - see `HABO_API_SPECIFICATION.md`
  - `categories_bp` (for habit categories) - see `HABO_API_SPECIFICATION.md`

The app also supports CORS if you're testing from a web browser or different
origin. Consider adding Flask-CORS middleware if needed:

    from flask_cors import CORS
    CORS(app)

Current registered blueprints:
  - `/habits` - Basic habit CRUD (partially compatible with Habo)
  - `/logs` - Simple log entries (NOT compatible with Habo events)
  - `/rules` - Scheduling rules (compatible structure, but Habo doesn't use HTTP yet)
  - `/users` - Bulk user data endpoint (not used by Habo)
"""

def create_app() -> Flask:
    
    init_db()
    # habit_test_3()
    
    app = Flask(__name__)
    app.register_blueprint(habits_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(rules_bp)
    app.register_blueprint(users_bp)
    
    # TODO (Habo): Register additional blueprints when implemented:
    # from routes.events import events_bp
    # from routes.categories import categories_bp
    # app.register_blueprint(events_bp)
    # app.register_blueprint(categories_bp)
    
    return app

app = create_app()

@app.get("/")
def home():
    return "One day of singing. Yeah, yeah."

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
