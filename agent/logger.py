import csv
import os
import random
from datetime import datetime

def log_episode_enhanced(log_path, task_id, intent, action, reward, feedback, suggestion, confidence, 
                        followup_task=None, followup_accepted=False, followup_reward=0, q_details=None):
    """Enhanced logging with all 12 required fields plus detailed confidence breakdown"""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    file_exists = os.path.isfile(log_path)
    
    timestamp = datetime.now().isoformat(timespec="seconds")
    
    # Ensure confidence is properly calculated (not random)
    if confidence is None:
        confidence = 0.5  # Default if not provided
    else:
        confidence = round(float(confidence), 3)
    
    # Calculate total reward including bonuses
    total_reward = reward + followup_reward
    
    # Extract Q-value details if provided
    if q_details:
        q_value_diff = q_details.get('method_1_sigmoid', 0)
        softmax_conf = q_details.get('method_2_softmax', 0.5) 
        ranking_conf = q_details.get('method_3_ranking', 0.5)
        chosen_q = q_details.get('chosen_q', 0)
        mean_other_q = q_details.get('mean_other_q', 0)
    else:
        q_value_diff = 0
        softmax_conf = confidence
        ranking_conf = confidence
        chosen_q = 0
        mean_other_q = 0
    
    with open(log_path, "a", newline="") as f:
        w = csv.writer(f)
        if not file_exists:
            # All 15+ required fields for comprehensive logging
            w.writerow([
                "Task_ID", "Parsed_Intent", "Action_Taken", "Base_Reward", "Total_Reward",
                "Timestamp", "Confidence_Score", "User_Feedback", "Suggested_Correct_Action", 
                "Sigmoid_Confidence", "Softmax_Confidence", "Ranking_Confidence", "Follow_up_Task", "Follow_up_Accepted", 
                "Follow_up_Reward", "Chosen_Q_Value", "Mean_Other_Q_Values"
            ])
        w.writerow([
            task_id, intent, action, reward, total_reward, timestamp, confidence, 
            feedback, suggestion or "", q_value_diff, softmax_conf, ranking_conf, followup_task or "", 
            followup_accepted, followup_reward, chosen_q, mean_other_q
        ])

def log_episode(log_path, task_id, intent, action, reward, feedback, suggestion, confidence=None):
    """Backward compatibility wrapper for enhanced logging"""
    log_episode_enhanced(log_path, task_id, intent, action, reward, feedback, suggestion, confidence)

def create_comprehensive_task_log(file_path, num_entries=35):
    """Create comprehensive task log with 35+ realistic entries spanning multiple task types"""
    import random
    from datetime import datetime, timedelta
    
    # Expanded task categories with more realistic scenarios
    communication_tasks = [
        "check email notifications", "reply to urgent message", "join video conference", 
        "send WhatsApp message", "check Slack updates", "answer phone call",
        "review meeting invite", "update status message", "check Discord notifications"
    ]
    
    media_tasks = [
        "play music", "pause video", "take screenshot", "record screen", "play podcast", 
        "adjust volume", "mute system audio", "unmute microphone", "take photo", 
        "edit video clip", "play white noise", "stop music playback"
    ]
    
    productivity_tasks = [
        "open calendar app", "set reminder", "create new document", "open file manager", 
        "open calculator", "set timer for work", "open notepad", "backup files", 
        "organize desktop", "open presentation software", "launch code editor"
    ]
    
    system_tasks = [
        "set do not disturb", "close browser tabs", "restart application", 
        "check system updates", "clear cache", "open system preferences", 
        "monitor CPU usage", "close all applications", "check disk space"
    ]
    
    all_tasks = communication_tasks + media_tasks + productivity_tasks + system_tasks
    
    # Generate timestamps over the past week for realistic distribution
    start_time = datetime.now() - timedelta(days=7)
    
    with open(file_path, 'w') as f:
        for i in range(num_entries):
            task = random.choice(all_tasks)
            # Realistic time progression with some clustering during work hours
            if i < 15:  # Morning tasks
                base_hour = 9
            elif i < 25:  # Afternoon tasks
                base_hour = 14
            else:  # Evening tasks
                base_hour = 19
            
            day_offset = i // 8  # Spread across multiple days
            hour_variation = random.randint(-2, 3)
            minute_variation = random.randint(0, 59)
            
            current_time = start_time + timedelta(
                days=day_offset, 
                hours=base_hour + hour_variation, 
                minutes=minute_variation
            )
            time_str = current_time.strftime("%I:%M %p")
            f.write(f"{time_str} - {task.title()}\n")
    
    print(f"✅ Created comprehensive task log with {num_entries} diverse entries at {file_path}")
    print(f"   📊 Task categories: Communication, Media, Productivity, System")
    print(f"   ⏰ Time span: 7 days with realistic clustering")

def log_total_reward(episode, total_reward, episode_log_path):
    """Log total reward for an episode"""
    os.makedirs(os.path.dirname(episode_log_path), exist_ok=True)
    file_exists = os.path.isfile(episode_log_path)
    timestamp = datetime.now().isoformat(timespec="seconds")
    
    with open(episode_log_path, "a", newline="") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow(["Episode", "Total Reward", "Timestamp"])
        w.writerow([episode, total_reward, timestamp])
