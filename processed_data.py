import json
import pandas as pd
from datetime import datetime
import math

# ---- FOMO Score Function ----
def calculate_event_fomo_score(user_data, peer_snapshot):
    BUDDY_WEIGHT = 0.4
    BATCH_WEIGHT = 0.3
    TIME_WEIGHT = 0.3
    MAX_DAYS_SINCE_EVENT = 90

    buddy_score = 0
    if user_data['profile']['buddy_count'] > 0:
        buddies_attending = len(peer_snapshot['buddies_attending_events'])
        buddy_score = min(buddies_attending / user_data['profile']['buddy_count'], 1.0)

    batch_scores = []
    for event, attendance in peer_snapshot['batch_event_attendance'].items():
        normalized_score = min(attendance / 10, 1.0)
        batch_scores.append(normalized_score)
    batch_score = sum(batch_scores) / len(batch_scores) if batch_scores else 0

    last_event_date = datetime.strptime(user_data['activity']['last_event_attended'], '%Y-%m-%d')
    days_since_event = (datetime.now() - last_event_date).days
    time_score = min(days_since_event / MAX_DAYS_SINCE_EVENT, 1.0)

    fomo_score = (
        BUDDY_WEIGHT * buddy_score +
        BATCH_WEIGHT * batch_score +
        TIME_WEIGHT * time_score
    )
    fomo_score = 1 / (1 + math.exp(-5 * (fomo_score - 0.5)))

    return round(fomo_score, 2)

# ---- Load JSON ----
with open("simulated_profiles.json", "r") as f:
    json_data = json.load(f)

# For this example, use a single peer snapshot for all users
with open("peer_snapshot.json", "r") as f:
    peer_snapshots = json.load(f)
peer_snapshot = peer_snapshots[0]  # You can also match based on user_id if needed

# ---- Process Data ----
processed_data = []

for entry in json_data:
    profile = entry.get("profile", {})
    activity = entry.get("activity", {})

    resume_uploaded = profile.get("resume_uploaded", False)
    karma = profile.get("karma", 0)
    projects_added = profile.get("projects_added", 0)
    login_streak = activity.get("login_streak", 0)
    posts_created = activity.get("posts_created", 0)
    quizzes_taken = len(profile.get("quiz_history", []))
    clubs_joined = len(profile.get("clubs_joined", []))
    buddies_interacted = activity.get("buddies_interacted", 0)
    batch_resume_uploaded_pct = peer_snapshot.get("batch_resume_uploaded_pct", 0)

    # Calculate FOMO score
    try:
        fomo_score = calculate_event_fomo_score(entry, peer_snapshot)
    except Exception as e:
        print(f"Skipping entry due to error: {e}")
        continue

    # Labels
    should_nudge_resume = int(not resume_uploaded and batch_resume_uploaded_pct > 80)
    should_nudge_event = int(fomo_score >= 0.5)

    # --- NEW: Quiz nudge label ---
    try:
        last_quiz_date = datetime.strptime(activity["last_quiz_taken"], "%Y-%m-%d")
        days_since_quiz = (datetime.now() - last_quiz_date).days
        should_nudge_quiz = int(days_since_quiz > 30)
    except Exception:
        should_nudge_quiz = 1  # if date missing or malformed, assume quiz is overdue

    processed_data.append({
        "resume_uploaded": int(resume_uploaded),
        "karma": karma,
        "projects_added": projects_added,
        "login_streak": login_streak,
        "posts_created": posts_created,
        "quizzes_taken": quizzes_taken,
        "clubs_joined": clubs_joined,
        "buddies_interacted": buddies_interacted,
        "batch_resume_uploaded_pct": batch_resume_uploaded_pct,
        "event_fomo_score": fomo_score,
        "should_nudge_resume": should_nudge_resume,
        "should_nudge_event": should_nudge_event,
        "should_nudge_quiz": should_nudge_quiz 
    })

# ---- Save to CSV ----
df = pd.DataFrame(processed_data)
df.to_csv("processed_fomo_dataset.csv", index=False)
print("✅ CSV 'processed_fomo_dataset.csv' generated successfully.")(
