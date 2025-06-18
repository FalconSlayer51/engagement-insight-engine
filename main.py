import json
from fastapi import FastAPI, HTTPException
import joblib
import pandas as pd
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import date, datetime
from event_fomo_score import calculate_event_fomo_score


app = FastAPI()

try:
    resume_model = joblib.load("model/ml_model/models/random_forest_resume.joblib")
    event_model = joblib.load("model/ml_model/models/rf_model_event.joblib")
except FileNotFoundError as e:
    print(f"Warning: Model files not found: {e}")
    resume_model = None
    event_model = None

with open("config.json") as f:
    config = json.load(f)


class Profile(BaseModel):
    resume_uploaded: bool
    goal_tags: List[str]
    karma: int
    projects_added: int
    quiz_history: List[str]
    clubs_joined: List[str]
    buddy_count: int
    
class Activity(BaseModel):
    login_streak: int
    posts_created: int
    buddies_interacted: int
    last_event_attended: Optional[date]
    
class PeerSnapshot(BaseModel):
    batch_avg_projects: int
    batch_resume_uploaded_pct: int
    batch_event_attendance: Dict[str, int]
    buddies_attending_events: List[str]
    
class UserInput(BaseModel):
    user_id: str
    profile: Profile
    activity: Activity
    peer_snapshot: PeerSnapshot
    
@app.post('/analyze-engagement')
async def generate_nudges(userInput: UserInput):
    nudges: List[Dict] = []
    
    rules = config["profile_rules"]
    event_rules = config["event_rules"]
    priorities = config["priority_labels"]
    
    rule_resume_nudge = (
        not userInput.profile.resume_uploaded and
        userInput.peer_snapshot.batch_resume_uploaded_pct >= rules["resume_threshold"] * 100 and
        userInput.profile.projects_added >= rules["projects_avg_threshold"]
    )

    batch_event_attendance_rule = sum(userInput.peer_snapshot.batch_event_attendance.values())
    
    rule_event_nudge = (
        len(userInput.peer_snapshot.buddies_attending_events) > event_rules["buddy_attendance_trigger"] and
        batch_event_attendance_rule > event_rules["batch_attendance_trigger"]
    )
    
    user_data = userInput.dict()
    if user_data['activity']['last_event_attended']:
        user_data['activity']['last_event_attended'] = user_data['activity']['last_event_attended'].strftime('%Y-%m-%d')
    
    model_input = {
        "resume_uploaded": int(userInput.profile.resume_uploaded),
        "karma": userInput.profile.karma,
        "batch_resume_uploaded_pct": userInput.peer_snapshot.batch_resume_uploaded_pct,
        "event_fomo_score": calculate_event_fomo_score(user_data, userInput.peer_snapshot.dict()),
    }
    X_resume = pd.DataFrame([[
        model_input["resume_uploaded"],
        model_input["batch_resume_uploaded_pct"] / 100,
    ]], columns=['resume_uploaded', 'batch_resume_uploaded_pct'])
    
    X_event = pd.DataFrame([[
        model_input["karma"],
        model_input["event_fomo_score"]
    ]], columns=['karma', 'event_fomo_score'])
    

    model_resume_pred = resume_model.predict(X_resume)[0]
    model_event_pred = event_model.predict(X_event)[0]
    print("model_resume_pred: ", model_resume_pred)
    print("model_event_pred: ", model_event_pred)
    print("fomo score: ", model_input["event_fomo_score"])
    
    last_event_date = userInput.activity.last_event_attended
    days_since_event = (datetime.utcnow().date() - last_event_date).days
    
    if rule_resume_nudge or model_resume_pred == 1:
        nudges.append({
            "type": "profile",
            "title": f"{userInput.peer_snapshot.batch_resume_uploaded_pct}% of your peers have uploaded resumes. You haven't yet!",
            "action": "Upload resume now",
            "priority": priorities["resume"]
        })

    if rule_event_nudge or model_event_pred == 1:
        nudges.append({
            "type": "event",
            "title": f"{len(userInput.peer_snapshot.buddies_attending_events)} of your buddies are joining {userInput.peer_snapshot.buddies_attending_events[0]} event",
            "action": "Join the event",
            "priority": priorities["event_fomo"]
        })

    quiz_nudge_trigger_days = config["profile_rules"]["quiz_idle_days"]

    if userInput.activity.last_event_attended:

        if days_since_event >= quiz_nudge_trigger_days:
            nudges.append({
                "type": "quiz",
                "title": f"It's been {('5+' if days_since_event > 5 else days_since_event)} days since your last event. Try a 2-question quiz!",
                "action": "Take quiz now",
                "priority": priorities["quiz"]
            })

    return {
        "user_id": userInput.user_id,
        "nudges": nudges[:3],
        "status": "generated"
    }


@app.get('/health')
def health():
    return {'status': "ok"}

@app.get('/version')
def version():
    return { 'version': '1.0.0'}