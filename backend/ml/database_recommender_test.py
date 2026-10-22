import sys
import os

# Allow Python to find database.py from the backend folder
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from database import get_db_connection
from recommender import rank_investors


# =========================================================
# GET PITCHER PROFILE
# =========================================================

def get_pitcher_profile(cursor, user_id):

    cursor.execute(
        """
        SELECT
            u.user_id,
            u.name,
            u.email,
            u.role,
            p.startup_name,
            p.industry,
            p.description,
            p.stage,
            p.funding_required,
            p.location,
            p.website,
            p.founded_year,
            p.team_size,
            p.revenue,
            p.traction
        FROM users u
        JOIN pitcher_profiles p
            ON p.user_id = u.user_id
        WHERE u.user_id = %s
        """,
        (user_id,)
    )

    return cursor.fetchone()


# =========================================================
# GET ALL INVESTORS
# =========================================================

def get_investors(cursor):

    cursor.execute(
        """
        SELECT
            u.user_id,
            u.name,
            u.email,
            u.role,
            i.investor_id,
            i.investor_name,
            i.investor_type,
            i.description,
            i.location,
            i.min_investment,
            i.max_investment,
            i.website
        FROM users u
        JOIN investor_profiles i
            ON i.user_id = u.user_id
        WHERE u.role = 'INVESTOR'
        """
    )

    investors = cursor.fetchall()

    # Get industries and preferred stages
    for investor in investors:

        investor_id = investor["investor_id"]

        # -----------------------------------------
        # Investor industries
        # -----------------------------------------

        cursor.execute(
            """
            SELECT industry
            FROM investor_industries
            WHERE investor_id = %s
            """,
            (investor_id,)
        )

        investor["industries"] = [
            row["industry"]
            for row in cursor.fetchall()
        ]

        # -----------------------------------------
        # Investor stages
        # -----------------------------------------

        cursor.execute(
            """
            SELECT stage
            FROM investor_stages
            WHERE investor_id = %s
            """,
            (investor_id,)
        )

        investor["preferred_stages"] = [
            row["stage"]
            for row in cursor.fetchall()
        ]

    return investors


# =========================================================
# MAIN
# =========================================================

def main():

    connection = None
    cursor = None

    try:

        # -----------------------------------------
        # Connect to MySQL
        # -----------------------------------------

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        # -----------------------------------------
        # Find one pitcher
        # -----------------------------------------

        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE role = 'PITCHER'
            LIMIT 1
            """
        )

        pitcher_user = cursor.fetchone()

        if not pitcher_user:

            print(
                "No pitcher users found in database."
            )

            return

        # -----------------------------------------
        # Get pitcher profile
        # -----------------------------------------

        pitcher = get_pitcher_profile(
            cursor,
            pitcher_user["user_id"]
        )

        if not pitcher:

            print(
                "Pitcher profile not found."
            )

            return

        # -----------------------------------------
        # Display pitcher
        # -----------------------------------------

        print("\n====================================")
        print("REAL DATABASE ML TEST")
        print("====================================")

        print("\nTest Pitcher:")

        print(
            "Name:",
            pitcher["startup_name"]
            or pitcher["name"]
        )

        print(
            "Industry:",
            pitcher["industry"]
        )

        print(
            "Stage:",
            pitcher["stage"]
        )

        print(
            "Funding:",
            pitcher["funding_required"]
        )

        print(
            "Location:",
            pitcher["location"]
        )

        # -----------------------------------------
        # Get investors
        # -----------------------------------------

        investors = get_investors(cursor)

        if not investors:

            print(
                "\nNo investors found in database."
            )

            return

        print(
            "\nInvestors found:",
            len(investors)
        )

        # -----------------------------------------
        # Run ML recommendation
        # -----------------------------------------

        ranked = rank_investors(
            pitcher,
            investors
        )

        # -----------------------------------------
        # Display results
        # -----------------------------------------

        print("\n====================================")
        print("ML RECOMMENDATIONS")
        print("====================================")

        for index, result in enumerate(
            ranked,
            start=1
        ):

            print(
                f"\n{index}. Result:"
            )

            print(result)

        print("\n====================================")
        print("TEST COMPLETED")
        print("====================================")

    except Exception as e:

        print(
            "\nERROR:",
            e
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# START PROGRAM
# =========================================================

if __name__ == "__main__":
    main()