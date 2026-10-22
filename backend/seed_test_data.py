"""Populate the existing sample users/profiles plus realistic test interactions.

Run from the backend directory:
    python seed_test_data.py

All test users use password: password123
This script is safe to run repeatedly; it avoids duplicate rows where the schema
has unique constraints and only adds missing test interactions.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db_connection
from seed_data import seed as seed_base_data


PITCHER_EMAILS = [
    "aarav@finflow.io",
    "priya@medpulse.health",
    "rohan@greengrid.energy",
    "kavita@cybervault.io",
    "sneha@eduspark.in",
]

INVESTOR_EMAILS = [
    "vikram@elevationcapital.vc",
    "ananya@blueharbor.in",
    "rajesh@nexusalpha.fund",
    "meera@titanangels.com",
]


def get_user_ids(cursor, emails):
    ids = {}
    for email in emails:
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        row = cursor.fetchone()
        if not row:
            raise RuntimeError(f"Missing seeded user: {email}")
        ids[email] = row["user_id"]
    return ids


def add_swipe(cursor, user_id, target_user_id, action):
    cursor.execute(
        """
        INSERT IGNORE INTO swipes (user_id, target_user_id, action)
        VALUES (%s, %s, %s)
        """,
        (user_id, target_user_id, action),
    )


def add_connection(cursor, user_a, user_b):
    sender_id, receiver_id = sorted((user_a, user_b))
    cursor.execute(
        """
        INSERT IGNORE INTO connections (sender_id, receiver_id, status)
        VALUES (%s, %s, 'ACCEPTED')
        """,
        (sender_id, receiver_id),
    )


def add_notification(cursor, user_id, notification_type, message, sender_id):
    cursor.execute(
        """
        INSERT INTO notifications (user_id, type, message, sender_id)
        SELECT %s, %s, %s, %s
        WHERE NOT EXISTS (
            SELECT 1 FROM notifications
            WHERE user_id = %s
              AND type = %s
              AND message = %s
              AND sender_id = %s
        )
        """,
        (
            user_id,
            notification_type,
            message,
            sender_id,
            user_id,
            notification_type,
            message,
            sender_id,
        ),
    )


def add_profile_view(cursor, viewer_id, viewed_id):
    cursor.execute(
        """
        INSERT INTO profile_views (viewer_id, viewed_id)
        SELECT %s, %s
        WHERE NOT EXISTS (
            SELECT 1 FROM profile_views
            WHERE viewer_id = %s AND viewed_id = %s
        )
        """,
        (viewer_id, viewed_id, viewer_id, viewed_id),
    )


def seed_interactions():
    # First create the base sample users, profiles, and posts.
    seed_base_data()

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        pitchers = get_user_ids(cursor, PITCHER_EMAILS)
        investors = get_user_ids(cursor, INVESTOR_EMAILS)

        # ---------------------------------------------------------
        # Mutual RIGHT swipes -> matches/connections/notifications
        # ---------------------------------------------------------
        matches = [
            (pitchers["aarav@finflow.io"], investors["vikram@elevationcapital.vc"]),
            (pitchers["priya@medpulse.health"], investors["ananya@blueharbor.in"]),
            (pitchers["kavita@cybervault.io"], investors["vikram@elevationcapital.vc"]),
            (pitchers["sneha@eduspark.in"], investors["meera@titanangels.com"]),
        ]

        for pitcher_id, investor_id in matches:
            add_swipe(cursor, pitcher_id, investor_id, "RIGHT")
            add_swipe(cursor, investor_id, pitcher_id, "RIGHT")
            add_connection(cursor, pitcher_id, investor_id)
            add_notification(
                cursor,
                pitcher_id,
                "MATCH",
                "You have a new match!",
                investor_id,
            )
            add_notification(
                cursor,
                investor_id,
                "MATCH",
                "You have a new match!",
                pitcher_id,
            )

        # ---------------------------------------------------------
        # LEFT swipes so recommendations also have varied history.
        # ---------------------------------------------------------
        left_swipes = [
            (pitchers["aarav@finflow.io"], investors["rajesh@nexusalpha.fund"]),
            (pitchers["priya@medpulse.health"], investors["rajesh@nexusalpha.fund"]),
            (investors["ananya@blueharbor.in"], pitchers["kavita@cybervault.io"]),
            (investors["meera@titanangels.com"], pitchers["rohan@greengrid.energy"]),
        ]

        for user_id, target_id in left_swipes:
            add_swipe(cursor, user_id, target_id, "LEFT")

        # ---------------------------------------------------------
        # Profile views
        # ---------------------------------------------------------
        views = [
            (investors["vikram@elevationcapital.vc"], pitchers["aarav@finflow.io"]),
            (investors["ananya@blueharbor.in"], pitchers["priya@medpulse.health"]),
            (pitchers["sneha@eduspark.in"], investors["meera@titanangels.com"]),
            (pitchers["kavita@cybervault.io"], investors["vikram@elevationcapital.vc"]),
            (investors["rajesh@nexusalpha.fund"], pitchers["rohan@greengrid.energy"]),
        ]

        for viewer_id, viewed_id in views:
            add_profile_view(cursor, viewer_id, viewed_id)

        # ---------------------------------------------------------
        # A few interaction notifications for realistic testing.
        # ---------------------------------------------------------
        add_notification(
            cursor,
            pitchers["aarav@finflow.io"],
            "PROFILE_VIEW",
            "Vikramaditya Singhania viewed your profile.",
            investors["vikram@elevationcapital.vc"],
        )
        add_notification(
            cursor,
            pitchers["priya@medpulse.health"],
            "PROFILE_VIEW",
            "Ananya Sen viewed your profile.",
            investors["ananya@blueharbor.in"],
        )
        add_notification(
            cursor,
            investors["meera@titanangels.com"],
            "PROFILE_VIEW",
            "Sneha Patel viewed your profile.",
            pitchers["sneha@eduspark.in"],
        )

        # ---------------------------------------------------------
        # A few post likes/comments if the tables are available.
        # ---------------------------------------------------------
        cursor.execute("SELECT post_id, user_id FROM posts ORDER BY post_id LIMIT 3")
        posts = cursor.fetchall()

        for post in posts:
            # Choose a user different from the author.
            candidates = list(pitchers.values()) + list(investors.values())
            liker = next((uid for uid in candidates if uid != post["user_id"]), None)
            if liker:
                cursor.execute(
                    """
                    INSERT IGNORE INTO post_likes (post_id, user_id)
                    VALUES (%s, %s)
                    """,
                    (post["post_id"], liker),
                )
                cursor.execute(
                    """
                    INSERT INTO comments (post_id, user_id, comment_text)
                    SELECT %s, %s, %s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM comments
                        WHERE post_id = %s AND user_id = %s AND comment_text = %s
                    )
                    """,
                    (
                        post["post_id"],
                        liker,
                        "Great milestone! Looking forward to seeing how this grows.",
                        post["post_id"],
                        liker,
                        "Great milestone! Looking forward to seeing how this grows.",
                    ),
                )

        connection.commit()

        print("\nTest data is ready!")
        print("----------------------------------------")
        print("Test login password: password123")
        print("Pitchers:")
        for email in PITCHER_EMAILS:
            print(f"  - {email}")
        print("Investors:")
        for email in INVESTOR_EMAILS:
            print(f"  - {email}")
        print("\nCreated test interactions:")
        print("  - Mutual matches / connections")
        print("  - LEFT and RIGHT swipes")
        print("  - Profile views")
        print("  - Match/profile-view notifications")
        print("  - Post likes and comments")

    except Exception as e:
        if connection:
            connection.rollback()
        print("Test data seeding failed:", e)
        raise

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


if __name__ == "__main__":
    seed_interactions()
