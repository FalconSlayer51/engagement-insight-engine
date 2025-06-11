import os
import sys
from pathlib import Path
import json
from unittest.mock import patch, mock_open
import pytest

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# Mock config data
mock_config = {
    "profile_rules": {
        "resume_threshold": 0.7,
        "projects_avg_threshold": 2,
        "quiz_idle_days": 7
    },
    "event_rules": {
        "buddy_attendance_trigger": 2,
        "batch_attendance_trigger": 10
    },
    "priority_labels": {
        "resume": "high",
        "project": "medium",
        "quiz": "low",
        "event_fomo": "medium"
    }
}

# Mock model data
mock_model_data = b"mock model data"

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables and configurations"""
    # Mock file operations
    with patch('builtins.open', mock_open(read_data=json.dumps(mock_config))) as mock_file:
        with patch('joblib.load', return_value=None) as mock_load:
            yield 