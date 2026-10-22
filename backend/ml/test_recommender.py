from recommender import compatibility_score, rank_investors


pitcher = {
    "startup_name": "FinTechPay",
    "industry": "FinTech",
    "stage": "Seed",
    "funding_required": 5000000,
    "location": "Pune",
    "description": "Digital payments platform for small businesses",
    "traction": "10000 users",
}

investors = [
    {
        "user_id": 101,
        "investor_name": "Investor A",
        "investor_type": "Angel",
        "location": "Pune",
        "min_investment": 2000000,
        "max_investment": 10000000,
        "industries": ["FinTech", "SaaS"],
        "preferred_stages": ["Seed", "Series A"],
        "description": "Invests in fintech and software startups",
    },
    {
        "user_id": 102,
        "investor_name": "Investor B",
        "investor_type": "VC",
        "location": "Mumbai",
        "min_investment": 20000000,
        "max_investment": 100000000,
        "industries": ["Healthcare"],
        "preferred_stages": ["Series B"],
        "description": "Healthcare technology venture capital",
    },
]

score, features = compatibility_score(pitcher, investors[0])

print("Single pair test")
print("Score:", score)
print("Features:", features)
print()

print("Ranked investors")
for item in rank_investors(pitcher, investors):
    print(
        item["investor_name"],
        "=>",
        item["compatibility_score"],
        item["compatibility_features"],
    )
