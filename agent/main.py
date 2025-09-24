# agent/main.py

from agent.q_learning import QLearningAgent
from agent.logger import log_episode_enhanced, log_total_reward, create_comprehensive_task_log
from agent.feedback import get_feedback_with_correction, get_confidence_score
from agent.visualizer import plot_rewards, create_performance_dashboard, plot_confidence_analysis
import os
import time
from datetime import datetime

def print_banner():
    """Print a nice banner for the RL Agent"""
    print("\n" + "="*60)
    print("    🤖 REINFORCEMENT LEARNING CONTROLLED AGENT 🤖")
    print("="*60)
    print("  Learning from user feedback to improve task execution")
    print("-"*60)

def display_task_info(episode, task_index, task, action, next_best=None):
    """Display task information in a structured format"""
    print(f"\n📋 TASK {task_index} (Episode {episode})")
    print("-"*40)
    print(f"Task: {task}")
    print(f"🎯 Agent's Action: {action}")
    if next_best:
        print(f"💡 Next Best Option: {next_best}")
    print("-"*40)

def main():
    """Main function to run the RL agent with comprehensive logging, feedback, and persistence"""
    print_banner()
    
    # File paths
    task_log_path = os.path.join("data", "comprehensive_task_log.csv")
    episode_log_path = os.path.join("data", "episode_log.csv")
    chart_path = os.path.join("data", "learning_curve.png")
    dashboard_path = os.path.join("data", "performance_dashboard.png")
    confidence_path = os.path.join("data", "confidence_analysis.png")
    task_file_path = os.path.join("data", "task_log.txt")
    
    # Create comprehensive task log if not exists
    if not os.path.exists(task_file_path):
        print("📅 Creating comprehensive task log with 35+ realistic entries...")
        create_comprehensive_task_log(task_file_path, 35)
    
    # Load tasks from file
    try:
        with open(task_file_path, "r") as f:
            task_list = [line.strip().split(" - ")[1] for line in f.readlines() if " - " in line]
    except FileNotFoundError:
        print(f"⚠️  Task file not found: {task_file_path}")
        return
    
    print(f"📋 Loaded {len(task_list)} tasks for training")
    
    # Initialize agent with persistence
    agent = QLearningAgent(actions=["open", "mute", "play", "unmute", "close", "screenshot", "set_dnd"])
    total_rewards = []
    
    # Load previous learning progress
    try:
        import pandas as pd
        if os.path.exists(episode_log_path):
            episode_df = pd.read_csv(episode_log_path)
            if not episode_df.empty:
                total_rewards = episode_df['Total_Reward'].tolist()
                print(f"🔄 Resumed learning from {len(total_rewards)} previous episodes")
    except Exception as e:
        print(f"🆕 Starting fresh learning session")
    
    # Run multiple episodes for meaningful learning
    num_episodes = 6  # Increased for better learning demonstration
    start_episode = len(total_rewards) + 1
    
    for episode in range(start_episode, start_episode + num_episodes):
        print(f"\n🏁 Starting Episode {episode}")
        print("="*60)
        total_reward = 0
        start_time = time.time()
        
        # Shuffle tasks for diversity
        import random
        episode_tasks = task_list.copy()
        random.shuffle(episode_tasks)
        
        # Use first 8 tasks per episode for focused training
        for task_index, task in enumerate(episode_tasks[:8], 1):
            # Parse intent from task
            parsed_intent = task.lower().split()[0] if task else "open"
            
            # Get agent's action and confidence with detailed analysis
            action = agent.select_action(parsed_intent)
            confidence = agent.get_action_confidence(parsed_intent, action)
            confidence_details = agent.get_confidence_details(parsed_intent, action)
            next_best = agent.get_next_best_action(parsed_intent)
            
            # Display task information with enhanced details
            print(f"\n📋 TASK {task_index} (Episode {episode})")
            print("-"*40)
            print(f"Task: {task}")
            print(f"🎯 Agent's Action: {action}")
            print(f"📈 Confidence Score: {confidence:.3f}")
            print(f"💡 Next Best Option: {next_best}")
            print(f"🧠 Q-Value Details: Chosen={confidence_details.get('chosen_q', 0):.2f}, Mean Others={confidence_details.get('mean_other_q', 0):.2f}")
            print("-"*40)
            
            # Get enhanced user feedback with correction and follow-up
            feedback, correction, followup_task, followup_accepted, followup_reward = get_feedback_with_correction(agent, parsed_intent, action)
            task_id = f"{episode}-{task_index}"
            
            # Enhanced reward logic based on feedback
            if feedback == "👍":
                base_reward = 2
                feedback_text = "👍 Correct"
            elif feedback == "👎":
                base_reward = -2
                feedback_text = "👎 Incorrect"
            else:
                base_reward = 0
                feedback_text = "Neutral"
            
            # Calculate total reward including followup bonus
            total_task_reward = base_reward + followup_reward
            
            # Update Q-table with base reward
            agent.update_q_table(parsed_intent, action, base_reward, parsed_intent)
            
            # Enhanced structured logging with all required fields
            log_episode_enhanced(
                log_path=task_log_path,
                task_id=task_id,
                intent=parsed_intent,
                action=action,
                reward=base_reward,
                feedback=feedback_text,
                suggestion=correction or "",
                confidence=confidence,
                followup_task=followup_task,
                followup_accepted=followup_accepted,
                followup_reward=followup_reward,
                q_details=confidence_details
            )
            
            total_reward += total_task_reward
            print(f"🏆 Episode {episode} Reward so far: {total_reward} (Task: {total_task_reward})")
            
            # Small delay for better UX
            time.sleep(0.5)
        
        # Log episode summary
        episode_duration = time.time() - start_time
        log_total_reward(episode, total_reward, episode_log_path)
        total_rewards.append(total_reward)
        
        print(f"\n✅ Episode {episode} Complete!")
        print(f"Total Reward: {total_reward}")
        print(f"Duration: {episode_duration:.1f} seconds")
        print("="*60)
        
        # Generate visualizations after each episode
        plot_rewards(total_rewards, chart_path)
        if os.path.exists(task_log_path):
            create_performance_dashboard(task_log_path, dashboard_path)
            plot_confidence_analysis(task_log_path, confidence_path)
    
    # Save Q-table (already auto-saved after each update)
    agent.save_q_table("data/final_q_table.pkl")
    
    # Final comprehensive summary
    print(f"\n🎉 Training Complete!")
    print(f"Episodes Completed: {len(total_rewards)}")
    print(f"Average Reward: {sum(total_rewards)/len(total_rewards):.1f}")
    print(f"Best Episode: {max(total_rewards)} (Episode {total_rewards.index(max(total_rewards)) + 1})")
    print(f"Improvement: {total_rewards[-1] - total_rewards[0] if len(total_rewards) > 1 else 0}")
    print(f"\n📁 Generated Files:")
    print(f"  • Learning curve: {chart_path}")
    print(f"  • Performance dashboard: {dashboard_path}")
    print(f"  • Confidence analysis: {confidence_path}")
    print(f"  • Detailed logs: {task_log_path}")
    print(f"  • Q-table persistence: data/final_q_table.pkl & .csv")
    
if __name__ == "__main__":
    main()
