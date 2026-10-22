import sys
import os
from werkzeug.security import generate_password_hash

# Ensure backend root in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import get_db_connection

def seed():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    default_password_hash = generate_password_hash("password123")

    print("Seeding database with sample users, profiles, and posts...")

    # Ensure user 1 has a profile if it's a PITCHER
    cur.execute("SELECT user_id, role, name FROM users WHERE user_id = 1")
    u1 = cur.fetchone()
    if u1:
        if not u1.get("name"):
            cur.execute("UPDATE users SET name = 'Nikhil (Founder)' WHERE user_id = 1")
        cur.execute("SELECT pitcher_id FROM pitcher_profiles WHERE user_id = 1")
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO pitcher_profiles
                    (user_id, startup_name, industry, description, stage,
                     funding_required, location, website, founded_year, team_size, revenue, traction)
                VALUES (1, 'ApexScale AI', 'AI & Machine Learning',
                        'Autonomous agent infrastructure for enterprise workflows and multi-modal automation.',
                        'Seed', 35000000.00, 'Bangalore, India', 'https://apexscale.ai', 2024, 8, 12000000.00,
                        '15 Enterprise pilots, $120k ARR, 45% MoM growth')
            """)

    # Sample Founders / Pitchers
    pitchers = [
        {
            "name": "Aarav Sharma",
            "email": "aarav@finflow.io",
            "role": "PITCHER",
            "profile": {
                "startup_name": "FinFlow AI",
                "industry": "FinTech",
                "description": "Next-generation automated cross-border treasury management and liquidity optimization for high-growth tech companies.",
                "stage": "Seed",
                "funding_required": 25000000.00,
                "location": "Bangalore, India",
                "website": "https://finflow.io",
                "founded_year": 2023,
                "team_size": 12,
                "revenue": 18000000.00,
                "traction": "80+ corporate customers, $2.1M monthly transaction volume, 3x YoY revenue growth"
            }
        },
        {
            "name": "Priya Nair",
            "email": "priya@medpulse.health",
            "role": "PITCHER",
            "profile": {
                "startup_name": "MedPulse Health",
                "industry": "HealthTech",
                "description": "AI-powered clinical triage and remote vital monitoring platform enabling proactive chronic care delivery.",
                "stage": "Series A",
                "funding_required": 60000000.00,
                "location": "Mumbai, India",
                "website": "https://medpulse.health",
                "founded_year": 2022,
                "team_size": 22,
                "revenue": 45000000.00,
                "traction": "Deployed in 45 hospital networks, 180,000 active patient monitoring sessions, ISO 13485 certified"
            }
        },
        {
            "name": "Rohan Verma",
            "email": "rohan@greengrid.energy",
            "role": "PITCHER",
            "profile": {
                "startup_name": "GreenGrid CleanTech",
                "industry": "CleanTech",
                "description": "Decentralized battery energy storage systems (BESS) and microgrid management software for commercial and industrial complexes.",
                "stage": "Pre-Seed",
                "funding_required": 15000000.00,
                "location": "Delhi NCR, India",
                "website": "https://greengrid.energy",
                "founded_year": 2024,
                "team_size": 6,
                "revenue": 3500000.00,
                "traction": "4 commercial pilots operating at 99.4% uptime; signed Letters of Intent worth ₹4.8 Cr"
            }
        },
        {
            "name": "Kavita Rao",
            "email": "kavita@cybervault.io",
            "role": "PITCHER",
            "profile": {
                "startup_name": "CyberVault Security",
                "industry": "Cybersecurity",
                "description": "Zero-trust API security mesh preventing data exfiltration and credential leaks for cloud-native microservices.",
                "stage": "Seed",
                "funding_required": 30000000.00,
                "location": "Hyderabad, India",
                "website": "https://cybervault.io",
                "founded_year": 2023,
                "team_size": 9,
                "revenue": 22000000.00,
                "traction": "Securing 450M+ API requests daily across banking and e-commerce leaders in APAC"
            }
        },
        {
            "name": "Sneha Patel",
            "email": "sneha@eduspark.in",
            "role": "PITCHER",
            "profile": {
                "startup_name": "EduSpark Learning",
                "industry": "EdTech",
                "description": "Adaptive gamified STEM learning platform for K-12 students with personalized AI learning paths in regional languages.",
                "stage": "Seed",
                "funding_required": 20000000.00,
                "location": "Pune, India",
                "website": "https://eduspark.in",
                "founded_year": 2023,
                "team_size": 15,
                "revenue": 14000000.00,
                "traction": "250,000 registered students, 42 school district partnerships, 88% term renewal rate"
            }
        }
    ]

    for p in pitchers:
        cur.execute("SELECT user_id FROM users WHERE email = %s", (p["email"],))
        existing = cur.fetchone()
        if not existing:
            cur.execute("""
                INSERT INTO users (name, email, password_hash, role)
                VALUES (%s, %s, %s, %s)
            """, (p["name"], p["email"], default_password_hash, p["role"]))
            user_id = cur.lastrowid
        else:
            user_id = existing["user_id"]
            cur.execute("UPDATE users SET name = %s WHERE user_id = %s", (p["name"], user_id))

        cur.execute("SELECT pitcher_id FROM pitcher_profiles WHERE user_id = %s", (user_id,))
        if not cur.fetchone():
            prof = p["profile"]
            cur.execute("""
                INSERT INTO pitcher_profiles
                    (user_id, startup_name, industry, description, stage,
                     funding_required, location, website, founded_year, team_size, revenue, traction)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id, prof["startup_name"], prof["industry"], prof["description"],
                prof["stage"], prof["funding_required"], prof["location"], prof["website"],
                prof["founded_year"], prof["team_size"], prof["revenue"], prof["traction"]
            ))

    # Sample Investors
    investors = [
        {
            "name": "Vikramaditya Singhania",
            "email": "vikram@elevationcapital.vc",
            "role": "INVESTOR",
            "profile": {
                "investor_name": "Elevation Ventures",
                "investor_type": "VC",
                "description": "Early-stage venture capital firm investing in ambitious tech founders transforming finance, B2B SaaS, and artificial intelligence in India and Southeast Asia.",
                "location": "Mumbai, India",
                "min_investment": 10000000.00,
                "max_investment": 150000000.00,
                "website": "https://elevationventures.example.com",
                "industries": ["FinTech", "AI & Machine Learning", "B2B SaaS", "Cybersecurity"],
                "stages": ["Seed", "Series A"]
            }
        },
        {
            "name": "Ananya Sen",
            "email": "ananya@blueharbor.in",
            "role": "INVESTOR",
            "profile": {
                "investor_name": "BlueHarbor Angel Syndicate",
                "investor_type": "Angel",
                "description": "Operator-led syndicate backing founders building high-impact healthcare, climate solutions, and deep tech with patient capital and go-to-market mentorship.",
                "location": "Bangalore, India",
                "min_investment": 2500000.00,
                "max_investment": 25000000.00,
                "website": "https://blueharbor.example.com",
                "industries": ["HealthTech", "CleanTech", "EdTech"],
                "stages": ["Idea", "Pre-Seed", "Seed"]
            }
        },
        {
            "name": "Rajesh Kulkarni",
            "email": "rajesh@nexusalpha.fund",
            "role": "INVESTOR",
            "profile": {
                "investor_name": "Nexus Alpha Family Office",
                "investor_type": "Family Office",
                "description": "Multi-stage institutional family office investing growth capital in sustainable infrastructure, clean energy, and market-leading enterprise software.",
                "location": "Bangalore, India",
                "min_investment": 50000000.00,
                "max_investment": 500000000.00,
                "website": "https://nexusalpha.example.com",
                "industries": ["CleanTech", "Enterprise Software", "FinTech"],
                "stages": ["Series A", "Series B+"]
            }
        },
        {
            "name": "Meera Krishnan",
            "email": "meera@titanangels.com",
            "role": "INVESTOR",
            "profile": {
                "investor_name": "Titan Seed Fund",
                "investor_type": "Syndicate",
                "description": "Early stage institutional micro-fund empowering mission-driven founders with hands-on product strategy, network introductions, and institutional follow-on rounds.",
                "location": "Delhi NCR, India",
                "min_investment": 5000000.00,
                "max_investment": 50000000.00,
                "website": "https://titanangels.example.com",
                "industries": ["EdTech", "FinTech", "AI & Machine Learning", "HealthTech"],
                "stages": ["Pre-Seed", "Seed", "Series A"]
            }
        }
    ]

    for inv in investors:
        cur.execute("SELECT user_id FROM users WHERE email = %s", (inv["email"],))
        existing = cur.fetchone()
        if not existing:
            cur.execute("""
                INSERT INTO users (name, email, password_hash, role)
                VALUES (%s, %s, %s, %s)
            """, (inv["name"], inv["email"], default_password_hash, inv["role"]))
            user_id = cur.lastrowid
        else:
            user_id = existing["user_id"]
            cur.execute("UPDATE users SET name = %s WHERE user_id = %s", (inv["name"], user_id))

        cur.execute("SELECT investor_id FROM investor_profiles WHERE user_id = %s", (user_id,))
        inv_row = cur.fetchone()
        prof = inv["profile"]
        if not inv_row:
            cur.execute("""
                INSERT INTO investor_profiles
                    (user_id, investor_name, investor_type, description, location,
                     min_investment, max_investment, website)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id, prof["investor_name"], prof["investor_type"], prof["description"],
                prof["location"], prof["min_investment"], prof["max_investment"], prof["website"]
            ))
            investor_id = cur.lastrowid
        else:
            investor_id = inv_row["investor_id"]

        # Industries
        cur.execute("DELETE FROM investor_industries WHERE investor_id = %s", (investor_id,))
        for ind in prof["industries"]:
            cur.execute("INSERT INTO investor_industries (investor_id, industry) VALUES (%s, %s)", (investor_id, ind))

        # Stages
        cur.execute("DELETE FROM investor_stages WHERE investor_id = %s", (investor_id,))
        for stg in prof["stages"]:
            cur.execute("INSERT INTO investor_stages (investor_id, stage) VALUES (%s, %s)", (investor_id, stg))

    # Seed initial community posts if none exist
    cur.execute("SELECT COUNT(*) AS cnt FROM posts")
    post_count = cur.fetchone()["cnt"]
    if post_count == 0:
        cur.execute("SELECT user_id, email, role, name FROM users WHERE email IN ('aarav@finflow.io', 'vikram@elevationcapital.vc', 'priya@medpulse.health')")
        sample_authors = {r["email"]: r["user_id"] for r in cur.fetchall()}

        posts_data = [
            (
                sample_authors.get("aarav@finflow.io", 1),
                "Excited to share that FinFlow AI just crossed $2.1M in monthly processed cross-border volume! Our autonomous treasury engine is cutting cross-currency transaction latency from 48h to under 3 minutes. Currently opening our Seed round to accelerate APAC expansion! 🚀"
            ),
            (
                sample_authors.get("vikram@elevationcapital.vc", 1),
                "At Elevation Ventures, we are actively looking to deploy ₹100M+ across early-stage AI agent infrastructure and cross-border FinTech. If you are building high-conviction software with early customer love, my DMs and matching queue are open!"
            ),
            (
                sample_authors.get("priya@medpulse.health", 1),
                "Milestone update: MedPulse Health has officially achieved ISO 13485 medical device quality certification! Now deployed in 45 hospital networks across India. Looking to connect with healthcare-focused syndicates and strategic Series A leads."
            )
        ]

        for uid, content in posts_data:
            if uid:
                cur.execute("INSERT INTO posts (user_id, content) VALUES (%s, %s)", (uid, content))

    conn.commit()
    print("Database seeding completed successfully!")
    cur.close()
    conn.close()

if __name__ == "__main__":
    seed()
