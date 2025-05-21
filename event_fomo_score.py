from datetime import datetime
import math

def calculate_event_fomo_score(user_data, peer_snapshot):
    """
    Calculate the event FOMO (Fear of Missing Out) score for a user.
    
    Args:
        user_data (dict): User's profile and activity data
        peer_snapshot (dict): Peer snapshot data containing batch and buddy information
        
    Returns:
        float: Event FOMO score between 0 and 1
    """
    # Constants
    BUDDY_WEIGHT = 0.4
    BATCH_WEIGHT = 0.3
    TIME_WEIGHT = 0.3
    MAX_DAYS_SINCE_EVENT = 90  # Maximum days to consider for time decay
    
    # 1. Calculate buddy factor (0 to 1)
    buddy_score = 0
    if user_data['profile']['buddy_count'] > 0:
        buddies_attending = len(peer_snapshot['buddies_attending_events'])
        buddy_score = min(buddies_attending / user_data['profile']['buddy_count'], 1.0)
    
    # 2. Calculate batch attendance factor (0 to 1)
    batch_scores = []
    for event, attendance in peer_snapshot['batch_event_attendance'].items():
        # Normalize attendance score (0-1) based on batch_attendance_trigger
        normalized_score = min(attendance / 10, 1.0)  # 10 is batch_attendance_trigger
        batch_scores.append(normalized_score)
    
    batch_score = sum(batch_scores) / len(batch_scores) if batch_scores else 0
    
    # 3. Calculate time decay factor (0 to 1)
    last_event_date = datetime.strptime(user_data['activity']['last_event_attended'], '%Y-%m-%d')
    days_since_event = (datetime.now() - last_event_date).days
    time_score = min(days_since_event / MAX_DAYS_SINCE_EVENT, 1.0)
    
    # 4. Calculate final weighted score
    fomo_score = (
        BUDDY_WEIGHT * buddy_score +
        BATCH_WEIGHT * batch_score +
        TIME_WEIGHT * time_score
    )
    
    # 5. Apply sigmoid function to get a smooth 0-1 score
    fomo_score = 1 / (1 + math.exp(-5 * (fomo_score - 0.5)))
    
    return round(fomo_score, 2)

def get_event_fomo_insights(user_data, peer_snapshot):
    """
    Generate insights about the user's event FOMO score.
    
    Args:
        user_data (dict): User's profile and activity data
        peer_snapshot (dict): Peer snapshot data
        
    Returns:
        dict: Insights about the user's event FOMO
    """
    fomo_score = calculate_event_fomo_score(user_data, peer_snapshot)
    
    insights = {
        'score': fomo_score,
        'level': 'low' if fomo_score < 0.3 else 'medium' if fomo_score < 0.7 else 'high',
        'factors': {
            'buddy_attendance': len(peer_snapshot['buddies_attending_events']),
            'total_buddies': user_data['profile']['buddy_count'],
            'days_since_last_event': (datetime.now() - datetime.strptime(user_data['activity']['last_event_attended'], '%Y-%m-%d')).days,
            'batch_attendance': peer_snapshot['batch_event_attendance']
        },
        'recommendations': []
    }
    
    # Generate recommendations based on score and factors
    if fomo_score > 0.7:
        insights['recommendations'].append("High FOMO detected! Consider attending upcoming events to stay connected with your peers.")
    elif fomo_score > 0.3:
        insights['recommendations'].append("Moderate FOMO level. Keep an eye on event announcements to maintain engagement.")
    
    if len(peer_snapshot['buddies_attending_events']) > 0:
        insights['recommendations'].append(f"Your buddies are attending: {', '.join(peer_snapshot['buddies_attending_events'])}")
    
    return insights 