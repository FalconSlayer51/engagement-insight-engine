from datetime import date
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# Create mock models
mock_resume_model = MagicMock()
mock_resume_model.predict.return_value = [1]  # Always predict 1 for testing
mock_event_model = MagicMock()
mock_event_model.predict.return_value = [1]  # Always predict 1 for testing

# Import app after setting up mocks
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_version_endpoint():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": "1.0.0"}

def test_resume_nudge():
    test_data = {
        "user_id": "stu_7023",
        "profile": {
            "resume_uploaded": False,
            "goal_tags": ["UI/UX", "AI"],
            "karma": 386,
            "projects_added": 0,
            "quiz_history": ["sql"],
            "clubs_joined": [],
            "buddy_count": 0
        },
        "activity": {
            "login_streak": 1,
            "posts_created": 0,
            "buddies_interacted": 3,
            "last_event_attended": "2025-03-07"
        },
        "peer_snapshot": {
            "batch_avg_projects": 3,
            "batch_resume_uploaded_pct": 80,  # Above 70% threshold
            "batch_event_attendance": {
                "startup-meetup": 5,
                "coding-contest": 11,
                "tech-talk": 4
            },
            "buddies_attending_events": ["tech-talk", "coding-contest", "startup-meetup"]
        }
    }
    
    # Set mock model predictions
    mock_resume_model.predict.return_value = [1]
    mock_event_model.predict.return_value = [0]
    
    response = client.post("/analyze-engagement", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "stu_7023"
    assert len(data["nudges"]) > 0
    resume_nudge = next((n for n in data["nudges"] if n["type"] == "profile"), None)
    assert resume_nudge is not None
    assert "resume" in resume_nudge["title"].lower()
    assert resume_nudge["priority"] == "high"

def test_event_nudge():
    test_data = {
        "user_id": "stu_7023",
        "profile": {
            "resume_uploaded": True,
            "goal_tags": ["UI/UX", "AI"],
            "karma": 386,
            "projects_added": 0,
            "quiz_history": ["sql"],
            "clubs_joined": [],
            "buddy_count": 0
        },
        "activity": {
            "login_streak": 1,
            "posts_created": 0,
            "buddies_interacted": 3,
            "last_event_attended": "2024-01-01"  # Old event date
        },
        "peer_snapshot": {
            "batch_avg_projects": 3,
            "batch_resume_uploaded_pct": 70,
            "batch_event_attendance": {
                "startup-meetup": 5,
                "coding-contest": 11,
                "tech-talk": 4
            },
            "buddies_attending_events": ["tech-talk", "coding-contest", "startup-meetup"]
        }
    }
    
    # Set mock model predictions
    mock_resume_model.predict.return_value = [0]
    mock_event_model.predict.return_value = [1]
    
    response = client.post("/analyze-engagement", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "stu_7023"
    assert len(data["nudges"]) > 0
    event_nudge = next((n for n in data["nudges"] if n["type"] == "event"), None)
    assert event_nudge is not None
    assert "event" in event_nudge["title"].lower()
    assert event_nudge["priority"] == "medium"

def test_quiz_nudge():
    test_data = {
        "user_id": "stu_7023",
        "profile": {
            "resume_uploaded": True,
            "goal_tags": ["UI/UX", "AI"],
            "karma": 386,
            "projects_added": 0,
            "quiz_history": ["sql"],
            "clubs_joined": [],
            "buddy_count": 0
        },
        "activity": {
            "login_streak": 1,
            "posts_created": 0,
            "buddies_interacted": 3,
            "last_event_attended": "2025-03-07"
        },
        "peer_snapshot": {
            "batch_avg_projects": 3,
            "batch_resume_uploaded_pct": 70,
            "batch_event_attendance": {
                "startup-meetup": 5,
                "coding-contest": 11,
                "tech-talk": 4
            },
            "buddies_attending_events": ["tech-talk", "coding-contest", "startup-meetup"]
        }
    }
    
    # Set mock model predictions
    mock_resume_model.predict.return_value = [0]
    mock_event_model.predict.return_value = [0]
    
    response = client.post("/analyze-engagement", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "stu_7023"
    assert len(data["nudges"]) > 0
    quiz_nudge = next((n for n in data["nudges"] if n["type"] == "quiz"), None)
    assert quiz_nudge is not None
    assert "quiz" in quiz_nudge["title"].lower()
    assert quiz_nudge["priority"] == "low"

def test_multiple_nudges():
    test_data = {
        "user_id": "stu_7023",
        "profile": {
            "resume_uploaded": False,
            "goal_tags": ["UI/UX", "AI"],
            "karma": 386,
            "projects_added": 0,
            "quiz_history": ["sql"],
            "clubs_joined": [],
            "buddy_count": 0
        },
        "activity": {
            "login_streak": 1,
            "posts_created": 0,
            "buddies_interacted": 3,
            "last_event_attended": "2024-01-01"  # Old event date
        },
        "peer_snapshot": {
            "batch_avg_projects": 3,
            "batch_resume_uploaded_pct": 81,  # Above 70% threshold
            "batch_event_attendance": {
                "startup-meetup": 5,
                "coding-contest": 11,
                "tech-talk": 4
            },
            "buddies_attending_events": ["tech-talk", "coding-contest", "startup-meetup"]
        }
    }
    
    # Set mock model predictions
    mock_resume_model.predict.return_value = [1]
    mock_event_model.predict.return_value = [1]
    
    response = client.post("/analyze-engagement", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "stu_7023"
    assert len(data["nudges"]) > 0
    assert len(data["nudges"]) <= 3  # Maximum 3 nudges
    
    # Check that we have all types of nudges
    nudge_types = {n["type"] for n in data["nudges"]}
    assert "profile" in nudge_types or "event" in nudge_types or "quiz" in nudge_types

def test_no_nudges():
    test_data = {
        "user_id": "stu_7023",
        "profile": {
            "resume_uploaded": True,
            "goal_tags": ["UI/UX", "AI"],
            "karma": 386,
            "projects_added": 3,
            "quiz_history": ["sql", "python", "java"],
            "clubs_joined": ["coding-club"],
            "buddy_count": 5
        },
        "activity": {
            "login_streak": 7,
            "posts_created": 5,
            "buddies_interacted": 10,
            "last_event_attended": date.today().strftime("%Y-%m-%d")
        },
        "peer_snapshot": {
            "batch_avg_projects": 3,
            "batch_resume_uploaded_pct": 70,
            "batch_event_attendance": {
                "startup-meetup": 1,
                "coding-contest": 1,
                "tech-talk": 1
            },
            "buddies_attending_events": ["tech-talk", "coding-contest", "startup-meetup"]
        }
    }
    
    # Set mock model predictions
    mock_resume_model.predict.return_value = [0]
    mock_event_model.predict.return_value = [0]
    
    response = client.post("/analyze-engagement", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "stu_7023"
    assert len(data["nudges"]) == 0  # No nudges for highly engaged user
