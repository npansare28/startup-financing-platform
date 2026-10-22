from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from database import get_db_connection


search_api = Blueprint("search_api", __name__)


# =========================================================
# SEARCH PROFILES
# GET /api/search
# =========================================================

@search_api.route("/api/search", methods=["GET"])
@jwt_required()
def search_profiles():

    current_user_id = int(get_jwt_identity())
    claims          = get_jwt()
    role            = claims.get("role")

    if role not in ("PITCHER", "INVESTOR"):
        return {"message": "Invalid user role"}, 400

    target_role = "INVESTOR" if role == "PITCHER" else "PITCHER"

    # Query params
    query      = request.args.get("query",    "").strip()
    industry   = request.args.get("industry", "").strip()
    location   = request.args.get("location", "").strip()
    stage      = request.args.get("stage",    "").strip()

    try:
        min_inv = float(request.args["min_investment"]) if request.args.get("min_investment") else None
        max_inv = float(request.args["max_investment"]) if request.args.get("max_investment") else None
    except ValueError:
        return {"message": "Investment values must be numbers"}, 400

    connection = None
    cursor     = None

    try:
        connection = get_db_connection()
        cursor     = connection.cursor(dictionary=True)

        # -----------------------------------------------
        # Search INVESTORS (when current user is PITCHER)
        # -----------------------------------------------
        if target_role == "INVESTOR":
            sql = """
                SELECT
                    u.user_id,
                    COALESCE(u.name, SUBSTRING_INDEX(u.email,'@',1)) AS name,
                    u.email, u.role,
                    ip.investor_name, ip.investor_type, ip.description,
                    ip.location, ip.min_investment, ip.max_investment, ip.website
                FROM users u
                LEFT JOIN investor_profiles ip ON ip.user_id = u.user_id
                WHERE u.role = 'INVESTOR'
                  AND u.user_id != %s
            """
            params = [current_user_id]

            if query:
                sql += """
                  AND (
                    LOWER(u.email) LIKE %s
                    OR LOWER(ip.investor_name) LIKE %s
                    OR LOWER(ip.description) LIKE %s
                    OR LOWER(ip.location) LIKE %s
                  )
                """
                like = f"%{query.lower()}%"
                params += [like, like, like, like]

            if location:
                sql += " AND LOWER(ip.location) LIKE %s"
                params.append(f"%{location.lower()}%")

            if min_inv is not None:
                sql += " AND ip.max_investment >= %s"
                params.append(min_inv)

            if max_inv is not None:
                sql += " AND ip.min_investment <= %s"
                params.append(max_inv)

            cursor.execute(sql, params)
            results = cursor.fetchall()

            # Industry filter (post-query via investor_industries)
            if industry:
                filtered = []
                for r in results:
                    cursor.execute(
                        """
                        SELECT industry FROM investor_industries ii
                        JOIN investor_profiles ip ON ip.investor_id = ii.investor_id
                        WHERE ip.user_id = %s
                        """,
                        (r["user_id"],)
                    )
                    industries = [x["industry"].lower() for x in cursor.fetchall()]
                    if any(industry.lower() in ind for ind in industries):
                        filtered.append(r)
                results = filtered

            # Stage filter
            if stage:
                filtered = []
                for r in results:
                    cursor.execute(
                        """
                        SELECT stage FROM investor_stages ist
                        JOIN investor_profiles ip ON ip.investor_id = ist.investor_id
                        WHERE ip.user_id = %s
                        """,
                        (r["user_id"],)
                    )
                    stages = [x["stage"].lower() for x in cursor.fetchall()]
                    if stage.lower() in stages:
                        filtered.append(r)
                results = filtered

        # -----------------------------------------------
        # Search PITCHERS (when current user is INVESTOR)
        # -----------------------------------------------
        else:
            sql = """
                SELECT
                    u.user_id,
                    COALESCE(u.name, SUBSTRING_INDEX(u.email,'@',1)) AS name,
                    u.email, u.role,
                    pp.startup_name, pp.industry, pp.description,
                    pp.stage, pp.funding_required, pp.location,
                    pp.website, pp.founded_year, pp.team_size,
                    pp.revenue, pp.traction
                FROM users u
                LEFT JOIN pitcher_profiles pp ON pp.user_id = u.user_id
                WHERE u.role = 'PITCHER'
                  AND u.user_id != %s
            """
            params = [current_user_id]

            if query:
                sql += """
                  AND (
                    LOWER(u.email) LIKE %s
                    OR LOWER(pp.startup_name) LIKE %s
                    OR LOWER(pp.description) LIKE %s
                    OR LOWER(pp.industry) LIKE %s
                    OR LOWER(pp.location) LIKE %s
                  )
                """
                like = f"%{query.lower()}%"
                params += [like, like, like, like, like]

            if industry:
                sql += " AND LOWER(pp.industry) LIKE %s"
                params.append(f"%{industry.lower()}%")

            if location:
                sql += " AND LOWER(pp.location) LIKE %s"
                params.append(f"%{location.lower()}%")

            if stage:
                sql += " AND LOWER(pp.stage) = %s"
                params.append(stage.lower())

            if min_inv is not None:
                sql += " AND pp.funding_required >= %s"
                params.append(min_inv)

            if max_inv is not None:
                sql += " AND pp.funding_required <= %s"
                params.append(max_inv)

            cursor.execute(sql, params)
            results = cursor.fetchall()

        return {
            "message": "Search completed successfully",
            "results": results,
            "count":   len(results)
        }, 200

    except Exception as e:
        print("Search error:", e)
        return {"message": "Search failed", "error": str(e)}, 500

    finally:
        if cursor:     cursor.close()
        if connection: connection.close()