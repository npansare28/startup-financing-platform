from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from database import get_db_connection


profile_api = Blueprint("profile_api", __name__)


# =========================================================
# GET MY PROFILE
# GET /api/profile
# =========================================================

@profile_api.route("/api/profile", methods=["GET"])
@profile_api.route("/api/profile/me", methods=["GET"])
@jwt_required()
def get_profile():

    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Base user information
        cursor.execute(
            """
            SELECT user_id, name, email, role, created_at
            FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:
            return {"message": "User not found"}, 404

        profile = dict(user)

        # -------------------------------------------------
        # PITCHER PROFILE
        # -------------------------------------------------

        if role == "PITCHER":

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
        # INVESTOR PROFILE
        # -------------------------------------------------

        elif role == "INVESTOR":

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

                # Investor industries
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

                    # Investor preferred stages
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

        return {
            "message": "Profile retrieved successfully",
            "profile": profile,
            "user": profile
        }, 200

    except Exception as e:

        print("Get profile error:", e)

        return {
            "message": "Failed to load profile. Please try again."
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# RECORD PROFILE VIEW
# POST /api/profile-views/<viewed_user_id>
# =========================================================

@profile_api.route(
    "/api/profile-views/<int:viewed_user_id>",
    methods=["POST"]
)
@jwt_required()
def record_profile_view(viewed_user_id):

    viewer_id = int(get_jwt_identity())

    connection = None
    cursor = None

    try:

        # -------------------------------------------------
        # Don't count viewing your own profile
        # -------------------------------------------------

        if viewer_id == viewed_user_id:
            return {
                "message": "Own profile view is not counted"
            }, 200

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # Check whether the viewed user exists
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE user_id = %s
            """,
            (viewed_user_id,)
        )

        viewed_user = cursor.fetchone()

        if not viewed_user:
            return {
                "message": "User not found"
            }, 404

        # -------------------------------------------------
        # Record profile view
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO profile_views (
                viewer_id,
                viewed_id
            )
            VALUES (%s, %s)
            """,
            (
                viewer_id,
                viewed_user_id
            )
        )

        connection.commit()

        return {
            "message": "Profile view recorded"
        }, 201

    except Exception as e:

        if connection:
            connection.rollback()

        print("Record profile view error:", e)

        return {
            "message": "Unable to record profile view"
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# GET MY PROFILE VIEW COUNT
# GET /api/profile-views
# =========================================================

@profile_api.route(
    "/api/profile-views",
    methods=["GET"]
)
@jwt_required()
def get_profile_views():

    user_id = int(get_jwt_identity())

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT COUNT(*) AS count
            FROM profile_views
            WHERE viewed_id = %s
            """,
            (user_id,)
        )

        result = cursor.fetchone()

        view_count = result["count"] if result else 0

        return {
            "count": view_count
        }, 200

    except Exception as e:

        print("Get profile views error:", e)

        return {
            "message": "Unable to load profile views"
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# UPDATE MY PROFILE
# PUT /api/profile
# =========================================================

def _clean_str(val):

    if val is None:
        return None

    val = str(val).strip()

    return val if val else None


def _clean_num(val):

    if val is None or val == "":
        return None

    try:

        if isinstance(val, str):

            val = (
                val
                .replace("₹", "")
                .replace("$", "")
                .replace(",", "")
                .strip()
            )

            if not val:
                return None

        return float(val)

    except (ValueError, TypeError):

        return None


def _clean_int(val):

    if val is None or val == "":
        return None

    try:

        if isinstance(val, str):

            val = val.replace(",", "").strip()

            if not val:
                return None

        return int(float(val))

    except (ValueError, TypeError):

        return None


@profile_api.route("/api/profile", methods=["PUT"])
@jwt_required()
def update_profile():

    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")

    data = request.get_json()

    if not data:
        return {
            "message": "Profile data is required"
        }, 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # Update name
        # -------------------------------------------------

        if data.get("name") is not None:

            clean_name = _clean_str(data.get("name"))

            if clean_name:

                cursor.execute(
                    """
                    UPDATE users
                    SET name = %s
                    WHERE user_id = %s
                    """,
                    (
                        clean_name,
                        user_id
                    )
                )

        # -------------------------------------------------
        # PITCHER
        # -------------------------------------------------

        if role == "PITCHER":

            cursor.execute(
                """
                SELECT pitcher_id
                FROM pitcher_profiles
                WHERE user_id = %s
                """,
                (user_id,)
            )

            exists = cursor.fetchone()

            vals = {
                "startup_name": _clean_str(
                    data.get("startup_name")
                ),
                "industry": _clean_str(
                    data.get("industry")
                ),
                "description": _clean_str(
                    data.get("description")
                ),
                "stage": _clean_str(
                    data.get("stage")
                ),
                "funding_required": _clean_num(
                    data.get("funding_required")
                ),
                "location": _clean_str(
                    data.get("location")
                ),
                "website": _clean_str(
                    data.get("website")
                ),
                "founded_year": _clean_int(
                    data.get("founded_year")
                ),
                "team_size": _clean_int(
                    data.get("team_size")
                ),
                "revenue": _clean_num(
                    data.get("revenue")
                ),
                "traction": _clean_str(
                    data.get("traction")
                ),
            }

            if exists:

                cursor.execute(
                    """
                    UPDATE pitcher_profiles
                    SET
                        startup_name=%s,
                        industry=%s,
                        description=%s,
                        stage=%s,
                        funding_required=%s,
                        location=%s,
                        website=%s,
                        founded_year=%s,
                        team_size=%s,
                        revenue=%s,
                        traction=%s
                    WHERE user_id=%s
                    """,
                    (
                        *vals.values(),
                        user_id
                    )
                )

            else:

                cursor.execute(
                    """
                    INSERT INTO pitcher_profiles
                    (
                        user_id,
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
                    )
                    VALUES
                    (
                        %s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s
                    )
                    """,
                    (
                        user_id,
                        *vals.values()
                    )
                )

        # -------------------------------------------------
        # INVESTOR
        # -------------------------------------------------

        elif role == "INVESTOR":

            cursor.execute(
                """
                SELECT investor_id
                FROM investor_profiles
                WHERE user_id = %s
                """,
                (user_id,)
            )

            row = cursor.fetchone()

            inv_vals = {
                "investor_name": _clean_str(
                    data.get("investor_name")
                ),
                "investor_type": _clean_str(
                    data.get("investor_type")
                ),
                "description": _clean_str(
                    data.get("description")
                ),
                "location": _clean_str(
                    data.get("location")
                ),
                "min_investment": _clean_num(
                    data.get("min_investment")
                ),
                "max_investment": _clean_num(
                    data.get("max_investment")
                ),
                "website": _clean_str(
                    data.get("website")
                ),
            }

            if row:

                investor_id = row["investor_id"]

                cursor.execute(
                    """
                    UPDATE investor_profiles
                    SET
                        investor_name=%s,
                        investor_type=%s,
                        description=%s,
                        location=%s,
                        min_investment=%s,
                        max_investment=%s,
                        website=%s
                    WHERE user_id=%s
                    """,
                    (
                        *inv_vals.values(),
                        user_id
                    )
                )

            else:

                cursor.execute(
                    """
                    INSERT INTO investor_profiles
                    (
                        user_id,
                        investor_name,
                        investor_type,
                        description,
                        location,
                        min_investment,
                        max_investment,
                        website
                    )
                    VALUES
                    (
                        %s,%s,%s,%s,
                        %s,%s,%s,%s
                    )
                    """,
                    (
                        user_id,
                        *inv_vals.values()
                    )
                )

                investor_id = cursor.lastrowid

            # -------------------------------------------------
            # Update industries
            # -------------------------------------------------

            if "industries" in data:

                cursor.execute(
                    """
                    DELETE FROM investor_industries
                    WHERE investor_id = %s
                    """,
                    (investor_id,)
                )

                for industry in data["industries"] or []:

                    clean_industry = _clean_str(industry)

                    if clean_industry:

                        cursor.execute(
                            """
                            INSERT INTO investor_industries
                            (
                                investor_id,
                                industry
                            )
                            VALUES (%s, %s)
                            """,
                            (
                                investor_id,
                                clean_industry
                            )
                        )

            # -------------------------------------------------
            # Update preferred stages
            # -------------------------------------------------

            if "preferred_stages" in data:

                cursor.execute(
                    """
                    DELETE FROM investor_stages
                    WHERE investor_id = %s
                    """,
                    (investor_id,)
                )

                for stage in data["preferred_stages"] or []:

                    clean_stage = _clean_str(stage)

                    if clean_stage:

                        cursor.execute(
                            """
                            INSERT INTO investor_stages
                            (
                                investor_id,
                                stage
                            )
                            VALUES (%s, %s)
                            """,
                            (
                                investor_id,
                                clean_stage
                            )
                        )

        connection.commit()

        return {
            "message": "Profile updated successfully"
        }, 200

    except Exception as e:

        if connection:
            connection.rollback()

        print("Update profile error:", e)

        return {
            "message": "Failed to update profile. Please try again."
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()