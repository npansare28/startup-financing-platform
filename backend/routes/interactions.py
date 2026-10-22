from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import get_db_connection


interactions_api = Blueprint("interactions_api", __name__)


# =========================================================
# LIKE A POST
# POST /api/posts/<post_id>/like
# =========================================================

@interactions_api.route("/api/posts/<int:post_id>/like", methods=["POST"])
@jwt_required()
def like_post(post_id):

    current_user_id = int(get_jwt_identity())

    connection = None
    cursor     = None

    try:
        connection = get_db_connection()
        cursor     = connection.cursor(dictionary=True)

        cursor.execute("SELECT post_id FROM posts WHERE post_id = %s", (post_id,))
        if not cursor.fetchone():
            return {"message": "Post not found"}, 404

        cursor.execute(
            "SELECT like_id FROM post_likes WHERE post_id = %s AND user_id = %s",
            (post_id, current_user_id)
        )
        if cursor.fetchone():
            return {"message": "You have already liked this post"}, 400

        cursor.execute(
            "INSERT INTO post_likes (post_id, user_id) VALUES (%s, %s)",
            (post_id, current_user_id)
        )
        connection.commit()

        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM post_likes WHERE post_id = %s",
            (post_id,)
        )
        likes_count = cursor.fetchone()["cnt"]

        return {"message": "Post liked successfully", "post_id": post_id, "likes_count": likes_count}, 200

    except Exception as e:
        if connection: connection.rollback()
        return {"message": "Failed to like post", "error": str(e)}, 500

    finally:
        if cursor:     cursor.close()
        if connection: connection.close()


# =========================================================
# UNLIKE A POST
# DELETE /api/posts/<post_id>/like
# =========================================================

@interactions_api.route("/api/posts/<int:post_id>/like", methods=["DELETE"])
@jwt_required()
def unlike_post(post_id):

    current_user_id = int(get_jwt_identity())

    connection = None
    cursor     = None

    try:
        connection = get_db_connection()
        cursor     = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT like_id FROM post_likes WHERE post_id = %s AND user_id = %s",
            (post_id, current_user_id)
        )
        if not cursor.fetchone():
            return {"message": "You have not liked this post"}, 400

        cursor.execute(
            "DELETE FROM post_likes WHERE post_id = %s AND user_id = %s",
            (post_id, current_user_id)
        )
        connection.commit()

        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM post_likes WHERE post_id = %s",
            (post_id,)
        )
        likes_count = cursor.fetchone()["cnt"]

        return {"message": "Post unliked successfully", "post_id": post_id, "likes_count": likes_count}, 200

    except Exception as e:
        if connection: connection.rollback()
        return {"message": "Failed to unlike post", "error": str(e)}, 500

    finally:
        if cursor:     cursor.close()
        if connection: connection.close()


# =========================================================
# ADD COMMENT
# POST /api/posts/<post_id>/comments
# =========================================================

@interactions_api.route("/api/posts/<int:post_id>/comments", methods=["POST"])
@jwt_required()
def add_comment(post_id):

    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    content = (data.get("content") or "").strip() if data else ""
    if not content:
        return {"message": "Comment content is required"}, 400

    connection = None
    cursor     = None

    try:
        connection = get_db_connection()
        cursor     = connection.cursor(dictionary=True)

        cursor.execute("SELECT post_id FROM posts WHERE post_id = %s", (post_id,))
        if not cursor.fetchone():
            return {"message": "Post not found"}, 404

        cursor.execute(
            "INSERT INTO comments (post_id, user_id, comment_text) VALUES (%s, %s, %s)",
            (post_id, current_user_id, content)
        )
        connection.commit()
        comment_id = cursor.lastrowid

        cursor.execute(
            """
            SELECT c.comment_id, c.post_id, c.user_id,
                   COALESCE(u.name, SUBSTRING_INDEX(u.email,'@',1)) AS author_name,
                   c.comment_text, c.created_at
            FROM comments c
            JOIN users u ON u.user_id = c.user_id
            WHERE c.comment_id = %s
            """,
            (comment_id,)
        )
        comment = cursor.fetchone()

        return {"message": "Comment added successfully", "comment": comment}, 201

    except Exception as e:
        if connection: connection.rollback()
        return {"message": "Failed to add comment", "error": str(e)}, 500

    finally:
        if cursor:     cursor.close()
        if connection: connection.close()


# =========================================================
# GET COMMENTS FOR A POST
# GET /api/posts/<post_id>/comments
# =========================================================

@interactions_api.route("/api/posts/<int:post_id>/comments", methods=["GET"])
@jwt_required()
def get_comments(post_id):

    connection = None
    cursor     = None

    try:
        connection = get_db_connection()
        cursor     = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT c.comment_id, c.post_id, c.user_id,
                   COALESCE(u.name, SUBSTRING_INDEX(u.email,'@',1)) AS author_name,
                   c.comment_text, c.created_at
            FROM comments c
            JOIN users u ON u.user_id = c.user_id
            WHERE c.post_id = %s
            ORDER BY c.created_at ASC
            """,
            (post_id,)
        )
        comments = cursor.fetchall()

        return {"message": "Comments retrieved successfully", "comments": comments, "count": len(comments)}, 200

    except Exception as e:
        return {"message": "Failed to get comments", "error": str(e)}, 500

    finally:
        if cursor:     cursor.close()
        if connection: connection.close()


# =========================================================
# DELETE COMMENT
# DELETE /api/posts/<post_id>/comments/<comment_id>
# =========================================================

@interactions_api.route("/api/posts/<int:post_id>/comments/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(post_id, comment_id):

    current_user_id = int(get_jwt_identity())

    connection = None
    cursor     = None

    try:
        connection = get_db_connection()
        cursor     = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT user_id FROM comments WHERE comment_id = %s AND post_id = %s",
            (comment_id, post_id)
        )
        comment = cursor.fetchone()

        if not comment:
            return {"message": "Comment not found"}, 404
        if comment["user_id"] != current_user_id:
            return {"message": "You can only delete your own comments"}, 403

        cursor.execute("DELETE FROM comments WHERE comment_id = %s", (comment_id,))
        connection.commit()

        return {"message": "Comment deleted successfully"}, 200

    except Exception as e:
        if connection: connection.rollback()
        return {"message": "Failed to delete comment", "error": str(e)}, 500

    finally:
        if cursor:     cursor.close()
        if connection: connection.close()