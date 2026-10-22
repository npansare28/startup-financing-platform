from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import get_db_connection


connections_api = Blueprint("connections_api", __name__)


# =========================================================
# GET MY CONNECTIONS
# GET /api/connections
# =========================================================

@connections_api.route("/api/connections", methods=["GET"])
@jwt_required()
def get_connections():

    current_user_id = int(get_jwt_identity())

    connection = None
    cursor     = None

    try:
        connection = get_db_connection()
        cursor     = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                u.user_id,
                u.name,
                u.email,
                u.role,
                c.created_at AS connected_at
            FROM connections c
            JOIN users u ON (
                CASE
                    WHEN c.sender_id   = %s THEN u.user_id = c.receiver_id
                    WHEN c.receiver_id = %s THEN u.user_id = c.sender_id
                END
            )
            WHERE
                (c.sender_id = %s OR c.receiver_id = %s)
                AND c.status = 'ACCEPTED'
            ORDER BY c.created_at DESC
            """,
            (current_user_id, current_user_id,
             current_user_id, current_user_id)
        )
        connections_list = cursor.fetchall()

        return {
            "message":     "Connections retrieved successfully",
            "connections": connections_list,
            "count":       len(connections_list)
        }, 200

    except Exception as e:
        print("Get connections error:", e)
        return {"message": "Failed to get connections", "error": str(e)}, 500

    finally:
        if cursor:     cursor.close()
        if connection: connection.close()


# =========================================================
# GET MY MUTUAL MATCHES
# GET /api/matches
# =========================================================

@connections_api.route("/api/matches", methods=["GET"])
@jwt_required()
def get_matches():

    current_user_id = int(get_jwt_identity())

    connection = None
    cursor     = None

    try:
        connection = get_db_connection()
        cursor     = connection.cursor(dictionary=True)

        # Mutual RIGHT swipes = matches
        cursor.execute(
            """
            SELECT
                u.user_id,
                u.name,
                u.email,
                u.role,
                s1.created_at AS matched_at
            FROM swipes s1
            JOIN swipes s2
                ON  s1.user_id        = s2.target_user_id
                AND s1.target_user_id = s2.user_id
                AND s2.action         = 'RIGHT'
            JOIN users u ON u.user_id = s1.target_user_id
            WHERE s1.user_id = %s AND s1.action = 'RIGHT'
            ORDER BY s1.created_at DESC
            """,
            (current_user_id,)
        )
        matches = cursor.fetchall()

        return {
            "message": "Matches retrieved successfully",
            "matches": matches,
            "count":   len(matches)
        }, 200

    except Exception as e:
        print("Get matches error:", e)
        return {"message": "Failed to get matches", "error": str(e)}, 500

    finally:
        if cursor:     cursor.close()
        if connection: connection.close()