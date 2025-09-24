import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def plot_rewards(rewards, output_path="data/learning_curve.png"):
    """Enhanced reward plotting with better visualization"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Main learning curve
    episodes = range(1, len(rewards) + 1)
    ax1.plot(episodes, rewards, marker="o", linewidth=2, markersize=8, color='#2E86AB')
    ax1.fill_between(episodes, rewards, alpha=0.3, color='#2E86AB')
    ax1.set_title("🤖 RL Agent Learning Curve", fontsize=16, fontweight='bold')
    ax1.set_xlabel("Episode Number", fontsize=12)
    ax1.set_ylabel("Total Reward", fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(episodes)
    
    # Add trend line if more than 2 episodes
    if len(rewards) > 2:
        z = np.polyfit(episodes, rewards, 1)
        p = np.poly1d(z)
        ax1.plot(episodes, p(episodes), "--", alpha=0.8, color='red', label=f'Trend (slope: {z[0]:.1f})')
        ax1.legend()
    
    # Reward distribution/statistics
    ax2.bar(episodes, rewards, color=['green' if r > 0 else 'red' if r < 0 else 'gray' for r in rewards], alpha=0.7)
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    ax2.set_title("📊 Episode Reward Distribution", fontsize=14, fontweight='bold')
    ax2.set_xlabel("Episode Number", fontsize=12)
    ax2.set_ylabel("Reward", fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(episodes)
    
    # Add statistics text
    if rewards:
        avg_reward = np.mean(rewards)
        max_reward = max(rewards)
        min_reward = min(rewards)
        
        stats_text = f"📈 Stats:\nAvg: {avg_reward:.1f}\nMax: {max_reward}\nMin: {min_reward}"
        ax2.text(0.02, 0.98, stats_text, transform=ax2.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"💾 Saved enhanced reward chart to: {output_path}")

def create_performance_dashboard(task_log_path, output_path="data/dashboard.png"):
    """Create a comprehensive performance dashboard"""
    try:
        import pandas as pd
        
        # Read task log data
        df = pd.read_csv(task_log_path)
        
        # Create dashboard with multiple subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Reward over time with confidence overlay
        task_numbers = range(len(df))
        ax1.plot(task_numbers, df['Total_Reward'], marker='o', label='Total Reward', linewidth=2)
        if 'Confidence_Score' in df.columns:
            ax1_twin = ax1.twinx()
            ax1_twin.plot(task_numbers, df['Confidence_Score'], '--', color='orange', alpha=0.7, label='Confidence')
            ax1_twin.set_ylabel('Confidence Score', color='orange')
            ax1_twin.legend(loc='upper right')
        ax1.set_title('🎯 Reward & Confidence Progression')
        ax1.set_xlabel('Task Number')
        ax1.set_ylabel('Total Reward')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # 2. Action frequency
        action_counts = df['Action_Taken'].value_counts()
        ax2.pie(action_counts.values, labels=action_counts.index, autopct='%1.1f%%', startangle=90)
        ax2.set_title('🔄 Action Distribution')
        
        # 3. Feedback distribution with follow-up acceptance
        feedback_data = []
        if 'User_Feedback' in df.columns:
            positive = len(df[df['User_Feedback'].str.contains('👍', na=False)])
            negative = len(df[df['User_Feedback'].str.contains('👎', na=False)])
            feedback_data = [positive, negative]
            labels = ['👍 Positive', '👎 Negative']
            colors = ['green', 'red']
        else:
            feedback_data = [1, 1]  # Default data if no feedback column
            labels = ['No Data', 'Available']
            colors = ['gray', 'lightgray']
        
        ax3.bar(labels, feedback_data, color=colors, alpha=0.7)
        ax3.set_title('📝 Feedback Distribution')
        ax3.set_ylabel('Count')
        
        # 4. Learning trend by confidence and Q-value differences
        if 'Q_Value_Difference' in df.columns and 'Confidence_Score' in df.columns:
            scatter = ax4.scatter(df['Q_Value_Difference'], df['Confidence_Score'], 
                                c=df['Total_Reward'], cmap='RdYlGn', alpha=0.6, s=50)
            ax4.set_xlabel('Q-Value Difference')
            ax4.set_ylabel('Confidence Score')
            ax4.set_title('🧠 Q-Value vs Confidence (Color = Reward)')
            plt.colorbar(scatter, ax=ax4, label='Total Reward')
        else:
            # Fallback: show average reward by intent
            intent_rewards = df.groupby('Parsed_Intent')['Total_Reward'].mean() if 'Total_Reward' in df.columns else pd.Series([1])
            ax4.barh(range(len(intent_rewards)), intent_rewards.values)
            ax4.set_yticks(range(len(intent_rewards)))
            ax4.set_yticklabels(intent_rewards.index if len(intent_rewards) > 1 else ['Sample'])
            ax4.set_title('🧠 Average Reward by Intent')
            ax4.set_xlabel('Average Reward')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"📊 Saved performance dashboard to: {output_path}")
        
    except ImportError:
        print("⚠️ pandas not available for dashboard creation")
    except Exception as e:
        print(f"⚠️ Error creating dashboard: {e}")

def plot_confidence_analysis(task_log_path, output_path="data/confidence_analysis.png"):
    """Create detailed confidence score analysis visualization"""
    try:
        import pandas as pd
        
        df = pd.read_csv(task_log_path)
        
        if 'Confidence_Score' not in df.columns:
            print("⚠️ No confidence data available for analysis")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Confidence distribution
        ax1.hist(df['Confidence_Score'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.axvline(df['Confidence_Score'].mean(), color='red', linestyle='--', 
                   label=f'Mean: {df["Confidence_Score"].mean():.3f}')
        ax1.set_title('📊 Confidence Score Distribution')
        ax1.set_xlabel('Confidence Score')
        ax1.set_ylabel('Frequency')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Confidence vs Reward correlation
        if 'Total_Reward' in df.columns:
            ax2.scatter(df['Confidence_Score'], df['Total_Reward'], alpha=0.6, s=30)
            
            # Add correlation line
            z = np.polyfit(df['Confidence_Score'], df['Total_Reward'], 1)
            p = np.poly1d(z)
            ax2.plot(df['Confidence_Score'], p(df['Confidence_Score']), "r--", alpha=0.8)
            
            # Calculate correlation
            correlation = df['Confidence_Score'].corr(df['Total_Reward'])
            ax2.set_title(f'🔗 Confidence vs Reward (r={correlation:.3f})')
            ax2.set_xlabel('Confidence Score')
            ax2.set_ylabel('Total Reward')
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"🎯 Saved confidence analysis to: {output_path}")
        
    except Exception as e:
        print(f"⚠️ Error creating confidence analysis: {e}")
