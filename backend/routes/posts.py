from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import get_db_connection


posts_api = Blueprint("posts_api", __name__)


# =========================================================
# CREATE POST
# POST /api/posts
# =========================================================

@posts_api.route("/api/posts", methods=["POST"])
@jwt_required()
def create_post():

    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return {"message": "Post data is required"}, 400

    content = (data.get("content") or "").strip()
    if not content:
        return {"message": "Post content is required"}, 400

    connection = None
    cursor     = None

    try:
        connection = get_db_connection()
        cursor     = connection.cursor(dictionary=True)

        cursor.execute(
            "INSERT INTO posts (user_id, content) VALUES (%s, %s)",
            (current_user_id, content)
        )
        connection.commit()
        post_id = cursor.lastrowid

        cursor.execute(
            "SELECT * FROM posts WHERE post_id = %s",
            (post_id,)
        )
        post = cursor.fetchone()

        return {"message": "Post created successfully", "post": post}, 201

    except Exception as e:
        if connection: connection.rollback()
        print("Create post error:", e)
        return {"message": "Failed to create post", "error": str(e)}, 500

    finally:
        if cursor:     cursor.close()
        if connection: connection.close()


# =========================================================
# GET ALL POSTS (FEED)
# GET /api/posts
# =========================================================

@posts_api.route("/api/posts", methods=["GET"])
@jwt_required()
def get_posts():

    current_user_id = int(get_jwt_identity())

    connection = None
    cursor     = None

    try:
        connection = get_db_connection()
        cursor     = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                p.post_id,
                p.user_id,
                COALESCE(u.name, SUBSTRING_INDEX(u.email,'@',1)) AS author_name,
                u.role  AS author_role,
                p.content,
                p.created_at,
                p.updated_at,
                (SELECT COUNT(*) FROM post_likes pl WHERE pl.post_id = p.post_id) AS likes_count,
                EXISTS(
                    SELECT 1 FROM post_likes pl2
                    WHERE pl2.post_id = p.post_id AND pl2.user_id = %s
                ) AS liked_by_me,
                (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.post_id) AS comments_count
            FROM posts p
            JOIN users u ON u.user_id = p.user_id
            ORDER BY p.created_at DESC
            """,
            (current_user_id,)
        )
        posts = cursor.fetchall()

        return {"message": "Posts retrieved successfully", "posts": posts, "count": len(posts)}, 200

    except Exception as e:
        print("Get posts error:", e)
        return {"message": "Failed to get posts", "error": str(e)}, 500

    finally:
        if cursor:     cursor.close()
        if connection: connection.close()


# =========================================================
# GET MY POSTS
# GET /api/posts/my
# =========================================================

@posts_api.route("/api/posts/my", methods=["GET"])
@jwt_required()
def get_my_posts():

    current_user_id = int(get_jwt_identity())

    connection = None
    cursor     = None

    try:
        connection = get_db_connection()
        cursor     = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT p.*,
                (SELECT COUNT(*) FROM post_likes pl WHERE pl.post_id = p.post_id) AS likes_count,
                (SELECT COUNT(*) FROM comments  c  WHERE c.post_id  = p.post_id) AS comments_count
            FROM posts p
            WHERE p.user_id = %s
            ORDER BY p.created_at DESC
            """,
            (current_user_id,)
        )
        posts = cursor.fetchall()

        return {"message": "Your posts retrieved successfully", "posts": posts, "count": len(posts)}, 200

    except Exception as e:
        print("Get my posts error:", e)
        return {"message": "Failed to get posts", "error": str(e)}, 500

    finally:
        if cursor:     cursor.close()
        if connection: connection.close()


# =========================================================
# UPDATE POST
# PUT /api/posts/<post_id>
# =========================================================

@posts_api.route("/api/posts/<int:post_id>", methods=["PUT"])
@jwt_required()
def update_post(post_id):

    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    content = (data.get("content") or "").strip() if data else ""
    if not content:
        return {"message": "Post content is required"}, 400

    connection = None
    cursor     = None

    try:
        connection = get_db_connection()
        cursor     = connection.cursor(dictionary=True)

        cursor.execute("SELECT user_id FROM posts WHERE post_id = %s", (post_id,))
        post = cursor.fetchone()

        if not post:
            return {"message": "Post not found"}, 404
        if post["user_id"] != current_user_id:
            return {"message": "You can only edit your own posts"}, 403

        cursor.execute(
            "UPDATE posts SET content = %s WHERE post_id = %s",
            (content, post_id)
        )
        connection.commit()

        return {"message": "Post updated successfully"}, 200

    except Exception as e:
        if connection: connection.rollback()
        return {"message": "Failed to update post", "error": str(e)}, 500

    finally:
        if cursor:     cursor.close()
        if connection: connection.close()


# =========================================================
# DELETE POST
# DELETE /api/posts/<post_id>
# =========================================================

@posts_api.route("/api/posts/<int:post_id>", methods=["DELETE"])
@jwt_required()
def delete_post(post_id):

    current_user_id = int(get_jwt_identity())

    connection = None
    cursor     = None

    try:
        connection = get_db_connection()
        cursor     = connection.cursor(dictionary=True)

        cursor.execute("SELECT user_id FROM posts WHERE post_id = %s", (post_id,))
        post = cursor.fetchone()

        if not post:
            return {"message": "Post not found"}, 404
        if post["user_id"] != current_user_id:
            return {"message": "You can only delete your own posts"}, 403

        cursor.execute("DELETE FROM posts WHERE post_id = %s", (post_id,))
        connection.commit()

        return {"message": "Post deleted successfully"}, 200

    except Exception as e:
        if connection: connection.rollback()
        return {"message": "Failed to delete post", "error": str(e)}, 500

    finally:
        if cursor:     cursor.close()
        if connection: connection.close()