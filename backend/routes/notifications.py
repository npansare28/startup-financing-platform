from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import get_db_connection


notifications_api = Blueprint("notifications_api", __name__)


# =========================================================
# GET MY NOTIFICATIONS
# GET /api/notifications
# =========================================================

@notifications_api.route("/api/notifications", methods=["GET"])
@jwt_required()
def get_notifications():

    current_user_id = int(get_jwt_identity())

    connection = None
    cursor     = None

    try:
        connection = get_db_connection()
        cursor     = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                n.notification_id,
                n.user_id,
                n.type,
                n.message,
                n.is_read,
                n.created_at,
                n.sender_id,
                COALESCE(u.name, SUBSTRING_INDEX(u.email,'@',1)) AS sender_name
            FROM notifications n
            LEFT JOIN users u ON u.user_id = n.sender_id
            WHERE n.user_id = %s
            ORDER BY n.created_at DESC
            """,
            (current_user_id,)
        )
        notifications = cursor.fetchall()

        unread_count = sum(
            1 for n in notifications if not n.get("is_read", False)
        )

        return {
            "message":       "Notifications retrieved successfully",
            "notifications": notifications,
            "count":         len(notifications),
            "unread_count":  unread_count
        }, 200

    except Exception as e:
        print("Get notifications error:", e)
        return {"message": "Failed to get notifications", "error": str(e)}, 500

    finally:
        if cursor:     cursor.close()
        if connection: connection.close()


# =========================================================
# MARK ONE NOTIFICATION AS READ
# PUT /api/notifications/<notification_id>/read
# =========================================================

@notifications_api.route(
    "/api/notifications/<int:notification_id>/read",
    methods=["PUT"]
)
@jwt_required()
def mark_notification_read(notification_id):

    current_user_id = int(get_jwt_identity())

    connection = None
    cursor     = None

    try:
        connection = get_db_connection()
        cursor     = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT notification_id FROM notifications WHERE notification_id = %s AND user_id = %s",
            (notification_id, current_user_id)
        )
        if not cursor.fetchone():
            return {"message": "Notification not found"}, 404

        cursor.execute(
            "UPDATE notifications SET is_read = TRUE WHERE notification_id = %s AND user_id = %s",
            (notification_id, current_user_id)
        )
        connection.commit()

        return {"message": "Notification marked as read"}, 200

    except Exception as e:
        if connection: connection.rollback()
        print("Mark read error:", e)
        return {"message": "Failed to mark notification as read", "error": str(e)}, 500

    finally:
        if cursor:     cursor.close()
        if connection: connection.close()


# =========================================================
# MARK ALL NOTIFICATIONS AS READ
# PUT /api/notifications/read-all
# =========================================================

@notifications_api.route("/api/notifications/read-all", methods=["PUT"])
@jwt_required()
def mark_all_notifications_read():

    current_user_id = int(get_jwt_identity())

    connection = None
    cursor     = None

    try:
        connection = get_db_connection()
        cursor     = connection.cursor(dictionary=True)

        cursor.execute(
            "UPDATE notifications SET is_read = TRUE WHERE user_id = %s",
            (current_user_id,)
        )
        connection.commit()

        return {"message": "All notifications marked as read"}, 200

    except Exception as e:
        if connection: connection.rollback()
        print("Mark all read error:", e)
        return {"message": "Failed to mark all notifications as read", "error": str(e)}, 500

    finally:
        if cursor:     cursor.close()
        if connection: connection.close()


# =========================================================
# DELETE A NOTIFICATION
# DELETE /api/notifications/<notification_id>
# =========================================================

@notifications_api.route(
    "/api/notifications/<int:notification_id>",
    methods=["DELETE"]
)
@jwt_required()
def delete_notification(notification_id):

    current_user_id = int(get_jwt_identity())

    connection = None
    cursor     = None

    try:
        connection = get_db_connection()
        cursor     = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT notification_id FROM notifications WHERE notification_id = %s AND user_id = %s",
            (notification_id, current_user_id)
        )
        if not cursor.fetchone():
            return {"message": "Notification not found"}, 404

        cursor.execute(
            "DELETE FROM notifications WHERE notification_id = %s AND user_id = %s",
            (notification_id, current_user_id)
        )
        connection.commit()

        return {"message": "Notification deleted successfully"}, 200

    except Exception as e:
        if connection: connection.rollback()
        print("Delete notification error:", e)
        return {"message": "Failed to delete notification", "error": str(e)}, 500

    finally:
        if cursor:     cursor.close()
        if connection: connection.close()