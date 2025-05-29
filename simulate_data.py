import json
import random
from datetime import datetime, timedelta

goal_tags_pool = ["GRE", "CAT", "GATE", "data science", "web dev", "AI", "UI/UX"]
quiz_pool = ["aptitude", "python", "dsa", "ml", "java", "sql"]
clubs_pool = ["coding", "robotics", "arts", "ml-club"]
event_pool = ["startup-meetup", "coding-contest", "tech-talk"]

def random_date_within(days_ago):
    return (datetime.today() - timedelta(days=random.randint(0, days_ago))).strftime("%Y-%m-%d")

def simulate_user(user_id):
    return {
        "user_id": user_id,
        "profile": {
            "resume_uploaded": random.choice([True, False]),
            "goal_tags": random.sample(goal_tags_pool, k=2),
            "karma": random.randint(50, 500),
            "projects_added": random.randint(0, 5),
            "quiz_history": random.sample(quiz_pool, k=random.randint(0, 3)),
            "clubs_joined": random.sample(clubs_pool, k=random.randint(0, 2)),
            "buddy_count": random.randint(0, 5)
        },
        "activity": {
            "login_streak": random.randint(0, 10),
            "posts_created": random.randint(0, 3),
            "buddies_interacted": random.randint(0, 5),
            "last_event_attended": random_date_within(90)
        },
        "peer_snapshot": simulate_peer_snapshot()
    }

def simulate_peer_snapshot():
    return {
        "batch_avg_projects": random.randint(1, 4),
        "batch_resume_uploaded_pct": random.randint(60, 95),
        "batch_event_attendance": {
            event: random.randint(3, 12) for event in event_pool
        },
        "buddies_attending_events": random.sample(event_pool, k=random.randint(1, len(event_pool)))
    }

# Generate 2000 users and 3 peer snapshots
users = [simulate_user(f"stu_{7023+i}") for i in range(10000)]
#peer_snapshots = [simulate_peer_snapshot() for i in range(10)]

# Save to JSON files
with open("simulated_profiles.json", "w") as f:
    json.dump(users, f, indent=2)

# with open("peer_snapshot.json", "w") as f:
#     json.dump(peer_snapshots, f, indent=2)

print("✅ Simulated data generated successfully!")
