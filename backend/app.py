import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

load_dotenv()

from routes.auth import auth
from routes.profile import profile_api
from routes.matching import matching_api
from routes.search import search_api
from routes.connections import connections_api
from routes.posts import posts_api
from routes.interactions import interactions_api
from routes.notifications import notifications_api
from routes.users import users


app = Flask(__name__)
CORS(app)


# =====================================================
# JWT CONFIGURATION
# =====================================================

jwt_secret = os.getenv("JWT_SECRET_KEY")

if not jwt_secret:
    raise RuntimeError("JWT_SECRET_KEY is not configured")

app.config["JWT_SECRET_KEY"] = jwt_secret

jwt = JWTManager(app)


# =====================================================
# REGISTER BLUEPRINTS
# =====================================================

app.register_blueprint(auth)
app.register_blueprint(profile_api)
app.register_blueprint(matching_api)
app.register_blueprint(search_api)
app.register_blueprint(connections_api)
app.register_blueprint(posts_api)
app.register_blueprint(interactions_api)
app.register_blueprint(notifications_api)
app.register_blueprint(users)


# =====================================================
# HOME ROUTE
# =====================================================

@app.route("/")
def home():
    return "Startup Financing Platform Backend is Running!"


# =====================================================
# BASIC API TEST
# =====================================================

@app.route("/api/test")
def test_api():
    return {
        "message": "API is working!",
        "project": "Startup Financing Platform"
    }


# =====================================================
# START SERVER
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)