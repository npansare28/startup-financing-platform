from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import get_db_connection

users = Blueprint("users", __name__)


# =========================================================
# OTHER USER PROFILE
# GET /api/users/<user_id>
# =========================================================

@users.route("/api/users/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user_profile(user_id):
    connection = None
    cursor = None

    try:
        # Get the currently logged-in user
        current_user_id = get_jwt_identity()

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # Get basic user information
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                user_id,
                name,
                email,
                role,
                created_at
            FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "message": "User not found"
            }), 404

        # -------------------------------------------------
        # Create profile
        # -------------------------------------------------

        profile = dict(user)

        # -------------------------------------------------
        # Pitcher profile
        # -------------------------------------------------

        if user["role"] == "PITCHER":

            cursor.execute(
                """
                SELECT
                    startup_name,
                    industry,
                    description,
                    stage,
                    funding_required,
                    location,
                    website,
                    founded_year,
                    team_size,
                    revenue,
                    traction
                FROM pitcher_profiles
                WHERE user_id = %s
                """,
                (user_id,)
            )

            pitcher = cursor.fetchone()

            if pitcher:
                profile.update(pitcher)

        # -------------------------------------------------
        # Investor profile
        # -------------------------------------------------

        elif user["role"] == "INVESTOR":

            cursor.execute(
                """
                SELECT
                    investor_id,
                    investor_name,
                    investor_type,
                    description,
                    location,
                    min_investment,
                    max_investment,
                    website
                FROM investor_profiles
                WHERE user_id = %s
                """,
                (user_id,)
            )

            investor = cursor.fetchone()

            if investor:

                inv_id = investor.pop("investor_id", None)

                profile.update(investor)

                # -----------------------------------------
                # Investor industries
                # -----------------------------------------

                if inv_id:

                    cursor.execute(
                        """
                        SELECT industry
                        FROM investor_industries
                        WHERE investor_id = %s
                        """,
                        (inv_id,)
                    )

                    profile["industries"] = [
                        row["industry"]
                        for row in cursor.fetchall()
                    ]

                    # -------------------------------------
                    # Investor preferred stages
                    # -------------------------------------

                    cursor.execute(
                        """
                        SELECT stage
                        FROM investor_stages
                        WHERE investor_id = %s
                        """,
                        (inv_id,)
                    )

                    profile["preferred_stages"] = [
                        row["stage"]
                        for row in cursor.fetchall()
                    ]

        # -------------------------------------------------
        # Remove email when viewing another user's profile
        # -------------------------------------------------

        if str(current_user_id) != str(user_id):
            profile.pop("email", None)

        # -------------------------------------------------
        # Return profile
        # -------------------------------------------------

        return jsonify({
            "message": "User profile retrieved successfully",
            "user": profile,
            "profile": profile
        }), 200

    except Exception as e:

        # Log actual error on backend only
        print("User profile error:", e)

        # Do not expose database/internal errors
        return jsonify({
            "message": "Failed to load profile. Please try again."
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()