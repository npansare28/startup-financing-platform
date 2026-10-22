from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import get_db_connection

# =========================================================
# ML RECOMMENDATION ENGINE
# =========================================================

import sys
import os

ML_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "ml"
)

if ML_PATH not in sys.path:
    sys.path.append(ML_PATH)

from recommender import rank_investors, rank_pitchers


matching_api = Blueprint("matching_api", __name__)


# =========================================================
# HELPER
# =========================================================

def _build_profile(
    user_row,
    pitcher_row=None,
    investor_row=None,
    industries=None,
    stages=None
):
    """
    Merge user + role-specific profile into one dictionary.
    """

    email = user_row.get("email") or ""

    name = user_row.get("name")

    if not name:
        name = email.split("@")[0] if email else "User"

    profile = {
        "user_id": user_row["user_id"],
        "name": name,
        "email": email,
        "role": user_row["role"],
    }

    if pitcher_row:
        profile.update({
            key: value
            for key, value in pitcher_row.items()
            if value is not None
        })

    if investor_row:
        profile.update({
            key: value
            for key, value in investor_row.items()
            if value is not None
        })

    if industries is not None:
        profile["industries"] = industries

    if stages is not None:
        profile["preferred_stages"] = stages

    return profile


# =========================================================
# GET MATCHING / RECOMMENDATIONS
# =========================================================

@matching_api.route("/api/matching", methods=["GET"])
@matching_api.route("/api/recommendations", methods=["GET"])
@jwt_required()
def get_matching_profiles():

    current_user_id = int(get_jwt_identity())

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # Get current user
        # IMPORTANT: email is included
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                user_id,
                name,
                email,
                role
            FROM users
            WHERE user_id = %s
            """,
            (current_user_id,)
        )

        current_user = cursor.fetchone()

        if not current_user:
            return {
                "message": "User not found"
            }, 404

        role = current_user["role"]

        if role not in ("PITCHER", "INVESTOR"):
            return {
                "message": "Invalid user role"
            }, 400

        # -------------------------------------------------
        # Opposite role
        # -------------------------------------------------

        target_role = (
            "INVESTOR"
            if role == "PITCHER"
            else "PITCHER"
        )

        # -------------------------------------------------
        # Build current user's profile
        # -------------------------------------------------

        current_user_profile = _build_profile(
            current_user
        )

        # =================================================
        # CURRENT USER = PITCHER
        # =================================================

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
                (current_user_id,)
            )

            current_pitcher = cursor.fetchone()

            if current_pitcher:

                current_user_profile = _build_profile(
                    current_user,
                    pitcher_row=current_pitcher
                )

        # =================================================
        # CURRENT USER = INVESTOR
        # =================================================

        else:

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
                (current_user_id,)
            )

            current_investor = cursor.fetchone() or {}

            current_investor_id = current_investor.get(
                "investor_id"
            )

            # Do not modify the original dictionary
            current_investor_data = {
                key: value
                for key, value in current_investor.items()
                if key != "investor_id"
            }

            industries = []
            stages = []

            if current_investor_id:

                # Investor industries
                cursor.execute(
                    """
                    SELECT industry
                    FROM investor_industries
                    WHERE investor_id = %s
                    """,
                    (current_investor_id,)
                )

                industries = [
                    row["industry"]
                    for row in cursor.fetchall()
                ]

                # Investor stages
                cursor.execute(
                    """
                    SELECT stage
                    FROM investor_stages
                    WHERE investor_id = %s
                    """,
                    (current_investor_id,)
                )

                stages = [
                    row["stage"]
                    for row in cursor.fetchall()
                ]

            current_user_profile = _build_profile(
                current_user,
                investor_row=current_investor_data,
                industries=industries,
                stages=stages
            )

        # =================================================
        # GET USERS ALREADY SWIPED
        # =================================================

        cursor.execute(
            """
            SELECT target_user_id
            FROM swipes
            WHERE user_id = %s
            """,
            (current_user_id,)
        )

        swiped_ids = {
            row["target_user_id"]
            for row in cursor.fetchall()
        }

        # Never recommend yourself
        swiped_ids.add(current_user_id)

        # =================================================
        # GET CANDIDATE USERS
        # =================================================

        cursor.execute(
            """
            SELECT
                user_id,
                name,
                email,
                role
            FROM users
            WHERE role = %s
            """,
            (target_role,)
        )

        candidates = cursor.fetchall()

        profiles = []

        # =================================================
        # BUILD CANDIDATE PROFILES
        # =================================================

        for user in candidates:

            if user["user_id"] in swiped_ids:
                continue

            uid = user["user_id"]

            # =================================================
            # CANDIDATE = PITCHER
            # =================================================

            if target_role == "PITCHER":

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
                    (uid,)
                )

                pitcher = cursor.fetchone()

                profile = _build_profile(
                    user,
                    pitcher_row=pitcher
                )

            # =================================================
            # CANDIDATE = INVESTOR
            # =================================================

            else:

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
                    (uid,)
                )

                investor = cursor.fetchone() or {}

                investor_id = investor.get(
                    "investor_id"
                )

                investor_data = {
                    key: value
                    for key, value in investor.items()
                    if key != "investor_id"
                }

                industries = []
                stages = []

                if investor_id:

                    # Investor industries
                    cursor.execute(
                        """
                        SELECT industry
                        FROM investor_industries
                        WHERE investor_id = %s
                        """,
                        (investor_id,)
                    )

                    industries = [
                        row["industry"]
                        for row in cursor.fetchall()
                    ]

                    # Investor stages
                    cursor.execute(
                        """
                        SELECT stage
                        FROM investor_stages
                        WHERE investor_id = %s
                        """,
                        (investor_id,)
                    )

                    stages = [
                        row["stage"]
                        for row in cursor.fetchall()
                    ]

                profile = _build_profile(
                    user,
                    investor_row=investor_data,
                    industries=industries,
                    stages=stages
                )

            profiles.append(profile)

        # =================================================
        # ML RANKING
        # =================================================

        if role == "PITCHER":

            profiles = rank_investors(
                current_user_profile,
                profiles
            )

        else:

            profiles = rank_pitchers(
                current_user_profile,
                profiles
            )

        return {
            "message": "Matching profiles retrieved successfully",
            "profiles": profiles
        }, 200

    except Exception as e:

        print("Matching error:", repr(e))

        return {
            "message": "Failed to get matching profiles"
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# SWIPE ON A PROFILE
# POST /api/matching/swipe
# =========================================================

@matching_api.route("/api/matching/swipe", methods=["POST"])
@jwt_required()
def swipe_profile():

    current_user_id = int(get_jwt_identity())

    data = request.get_json()

    if not data:
        return {
            "message": "Swipe data is required"
        }, 400

    target_user_id = data.get("target_user_id")
    action = data.get("action", "").upper()

    if not target_user_id or action not in ("LEFT", "RIGHT"):
        return {
            "message": "target_user_id and action (LEFT/RIGHT) are required"
        }, 400

    target_user_id = int(target_user_id)

    if target_user_id == current_user_id:
        return {
            "message": "You cannot swipe on yourself"
        }, 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # Get current user's role
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                user_id,
                role
            FROM users
            WHERE user_id = %s
            """,
            (current_user_id,)
        )

        current_user = cursor.fetchone()

        if not current_user:
            return {
                "message": "Current user not found"
            }, 404

        role = current_user["role"]

        if role not in ("PITCHER", "INVESTOR"):
            return {
                "message": "Invalid user role"
            }, 400

        # -------------------------------------------------
        # Verify TARGET user
        # IMPORTANT:
        # target_user_id, NOT current_user_id
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                user_id,
                name,
                email,
                role
            FROM users
            WHERE user_id = %s
            """,
            (target_user_id,)
        )

        target = cursor.fetchone()

        if not target:
            return {
                "message": "Target user not found"
            }, 404

        # -------------------------------------------------
        # Only opposite role
        # -------------------------------------------------

        if target["role"] == role:
            return {
                "message": "You can only swipe on the opposite user type"
            }, 400

        # -------------------------------------------------
        # Insert swipe
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT IGNORE INTO swipes
            (user_id, target_user_id, action)
            VALUES (%s, %s, %s)
            """,
            (
                current_user_id,
                target_user_id,
                action
            )
        )

        matched = False

        # =================================================
        # RIGHT SWIPE
        # =================================================

        if action == "RIGHT":

            # -------------------------------------------------
            # Check whether target already RIGHT-swiped current
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT swipe_id
                FROM swipes
                WHERE user_id = %s
                  AND target_user_id = %s
                  AND action = 'RIGHT'
                """,
                (
                    target_user_id,
                    current_user_id
                )
            )

            mutual_right = cursor.fetchone()

            # =================================================
            # MUTUAL MATCH
            # =================================================

            if mutual_right:

                matched = True

                sender_id = min(
                    current_user_id,
                    target_user_id
                )

                receiver_id = max(
                    current_user_id,
                    target_user_id
                )

                # -------------------------------------------------
                # Create connection
                # -------------------------------------------------

                cursor.execute(
                    """
                    INSERT IGNORE INTO connections
                    (sender_id, receiver_id, status)
                    VALUES (%s, %s, 'ACCEPTED')
                    """,
                    (
                        sender_id,
                        receiver_id
                    )
                )

                # -------------------------------------------------
                # Match notification - current user
                # -------------------------------------------------

                cursor.execute(
                    """
                    INSERT INTO notifications
                    (user_id, type, message, sender_id)
                    VALUES (
                        %s,
                        'MATCH',
                        'You have a new match!',
                        %s
                    )
                    """,
                    (
                        current_user_id,
                        target_user_id
                    )
                )

                # -------------------------------------------------
                # Match notification - target user
                # -------------------------------------------------

                cursor.execute(
                    """
                    INSERT INTO notifications
                    (user_id, type, message, sender_id)
                    VALUES (
                        %s,
                        'MATCH',
                        'You have a new match!',
                        %s
                    )
                    """,
                    (
                        target_user_id,
                        current_user_id
                    )
                )

            else:

                # =================================================
                # INTEREST NOTIFICATION
                # =================================================
                # User showed interest but no mutual match yet.
                #
                # If your notifications.type column supports
                # 'INTEREST', this will notify the target user.
                # =================================================

                try:

                    cursor.execute(
                        """
                        SELECT notification_id
                        FROM notifications
                        WHERE user_id = %s
                          AND sender_id = %s
                          AND type = 'INTEREST'
                        LIMIT 1
                        """,
                        (
                            target_user_id,
                            current_user_id
                        )
                    )

                    existing_interest = cursor.fetchone()

                    if not existing_interest:

                        cursor.execute(
                            """
                            INSERT INTO notifications
                            (user_id, type, message, sender_id)
                            VALUES (
                                %s,
                                'INTEREST',
                                'Someone is interested in you!',
                                %s
                            )
                            """,
                            (
                                target_user_id,
                                current_user_id
                            )
                        )

                except Exception as interest_error:

                    # Don't destroy a valid swipe if the
                    # INTEREST notification type isn't supported.
                    print(
                        "Interest notification error:",
                        repr(interest_error)
                    )

        # -------------------------------------------------
        # Save everything
        # -------------------------------------------------

        connection.commit()

        return {
            "message": "Swipe recorded successfully",
            "action": action,
            "matched": matched
        }, 201

    except Exception as e:

        if connection:
            connection.rollback()

        print("Swipe error:", repr(e))

        return {
            "message": "Swipe failed"
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# GET MY RIGHT SWIPES / INTERESTS
# GET /api/interests
# =========================================================

@matching_api.route("/api/interests", methods=["GET"])
@jwt_required()
def get_interests():

    current_user_id = int(get_jwt_identity())

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                u.user_id,
                u.name,
                u.email,
                u.role
            FROM swipes s
            JOIN users u
                ON u.user_id = s.target_user_id
            WHERE s.user_id = %s
              AND s.action = 'RIGHT'
            ORDER BY s.created_at DESC
            """,
            (current_user_id,)
        )

        profiles = cursor.fetchall()

        return {
            "message": "Interests retrieved successfully",
            "profiles": profiles,
            "count": len(profiles)
        }, 200

    except Exception as e:

        print("Interests error:", repr(e))

        return {
            "message": "Failed to get interests"
        }, 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()