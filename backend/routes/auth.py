from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db_connection


auth = Blueprint("auth", __name__)


# =========================================================
# SIGNUP
# =========================================================
@auth.route("/api/auth/signup", methods=["POST"])
def signup():
    connection = None
    cursor = None

    try:
        # Get JSON data
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "message": "Request body must contain JSON data"
            }), 400

        # Get user information
        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        role_raw = data.get("role", "").strip().lower()

        # -------------------------------------------------
        # Validation
        # -------------------------------------------------

        if not name:
            return jsonify({
                "message": "Name is required"
            }), 400

        if not email:
            return jsonify({
                "message": "Email is required"
            }), 400

        if not password:
            return jsonify({
                "message": "Password is required"
            }), 400

        if not role_raw:
            return jsonify({
                "message": "Role is required"
            }), 400

        # Validate role
        allowed_roles = ["pitcher", "investor"]

        if role_raw not in allowed_roles:
            return jsonify({
                "message": "Role must be either 'pitcher' or 'investor'"
            }), 400

        role = role_raw

        # Basic password validation
        if len(password) < 6:
            return jsonify({
                "message": "Password must be at least 6 characters long"
            }), 400

        # -------------------------------------------------
        # Database connection
        # -------------------------------------------------

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # Check if email already exists
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({
                "message": "An account with this email already exists"
            }), 409

        # -------------------------------------------------
        # Hash password
        # -------------------------------------------------

        password_hash = generate_password_hash(password)

        # -------------------------------------------------
        # Create user
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO users (
                name,
                email,
                password_hash,
                role
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                name,
                email,
                password_hash,
                role
            )
        )

        connection.commit()

        user_id = cursor.lastrowid

        # -------------------------------------------------
        # Create JWT token
        # -------------------------------------------------

        access_token = create_access_token(
            identity=str(user_id)
        )

        # -------------------------------------------------
        # Return response
        # -------------------------------------------------

        return jsonify({
            "message": "Account created successfully",

            "access_token": access_token,

            "user": {
                "user_id": user_id,
                "name": name,
                "email": email,
                "role": role
            }

        }), 201

    except Exception as e:

        # Rollback database changes if something failed
        if connection:
            connection.rollback()

        # Log actual error only on server
        print("Signup error:", e)

        # Don't expose database/internal error to frontend
        return jsonify({
            "message": "Unable to create account. Please try again."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# LOGIN
# =========================================================
@auth.route("/api/auth/login", methods=["POST"])
def login():
    connection = None
    cursor = None

    try:
        # Get JSON data
        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "message": "Request body must contain JSON data"
            }), 400

        # Get login credentials
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        # -------------------------------------------------
        # Validation
        # -------------------------------------------------

        if not email or not password:
            return jsonify({
                "message": "Email and password are required"
            }), 400

        # -------------------------------------------------
        # Database connection
        # -------------------------------------------------

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # Find user
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                user_id,
                name,
                email,
                password_hash,
                role
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        # -------------------------------------------------
        # Check user and password
        # -------------------------------------------------

        if not user:
            return jsonify({
                "message": "Invalid email or password"
            }), 401

        if not check_password_hash(
            user["password_hash"],
            password
        ):
            return jsonify({
                "message": "Invalid email or password"
            }), 401

        # -------------------------------------------------
        # Create JWT
        # -------------------------------------------------

        access_token = create_access_token(
            identity=str(user["user_id"])
        )

        # -------------------------------------------------
        # Return user
        # -------------------------------------------------

        return jsonify({
            "message": "Login successful",

            "access_token": access_token,

            "user": {
                "user_id": user["user_id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }

        }), 200

    except Exception as e:

        # Log real error on backend only
        print("Login error:", e)

        return jsonify({
            "message": "Unable to login. Please try again."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()