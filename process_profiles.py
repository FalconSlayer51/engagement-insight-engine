import json
import pandas as pd
from datetime import datetime
from event_fomo_score import calculate_event_fomo_score

with open("simulated_profiles.json", "r") as f:
    json_data = json.load(f)

processed_data = []
for entry in json_data:
    profile = entry.get("profile", {})
    peer_snapshot = entry.get("peer_snapshot", {})
    activity = entry.get("activity", {})

    resume_uploaded = profile.get("resume_uploaded", False)
    karma = profile.get("karma", 0)
    batch_resume_uploaded_pct = peer_snapshot.get("batch_resume_uploaded_pct", 0)

    try:
        fomo_score = calculate_event_fomo_score(entry, peer_snapshot)
    except Exception as e:
        print(f"Skipping entry due to error: {e}")
        continue

    # Label rules
    should_nudge_resume = int(not resume_uploaded and batch_resume_uploaded_pct > 80)
    should_nudge_event = int(fomo_score >= 0.5)

    processed_data.append({
        "resume_uploaded": int(resume_uploaded),
        "karma": karma,
        "batch_resume_uploaded_pct": batch_resume_uploaded_pct,
        "event_fomo_score": fomo_score,
        "should_nudge_resume": should_nudge_resume,
        "should_nudge_event": should_nudge_event
    })

df = pd.DataFrame(processed_data)
df.to_csv("processed_fomo_dataset.csv", index=False)
print("✅ CSV 'processed_fomo_dataset.csv' generated.")
