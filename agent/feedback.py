def get_feedback():
    """Enhanced feedback system with clear 👍/👎 interface and real-time feedback loop"""
    print("\n" + "="*50)
    print("   USER FEEDBACK REQUIRED")
    print("="*50)
    print("Was the agent's action correct?")
    print("👍 = Correct action (type: 1, y, yes, or 👍)")
    print("👎 = Incorrect action (type: 2, n, no, or 👎)")
    print("-"*50)
    
    while True:
        fb = input("Your feedback: ").strip().lower()
        
        # Positive feedback options
        if fb in ("1", "y", "yes", "👍", "correct", "good", "right"):
            print("✅ Positive feedback recorded!")
            return "👍", None
        
        # Negative feedback options
        elif fb in ("2", "n", "no", "👎", "incorrect", "wrong", "bad"):
            print("❌ Negative feedback recorded.")
            print("💡 What action should have been taken?")
            correction = input("Enter the correct action: ").strip()
            if correction:
                print(f"📝 Correction recorded: {correction}")
                return "👎", correction
            else:
                print("⚠️ No correction provided")
                return "👎", None
        
        # Invalid input
        else:
            print("⚠️  Invalid input! Please use:")
            print("   • 👍, 1, y, yes for correct")
            print("   • 👎, 2, n, no for incorrect")
            continue

def get_feedback_with_correction(agent, state, action):
    """Enhanced feedback system with follow-up suggestions and Q-table correction"""
    print("\n" + "="*50)
    print("   USER FEEDBACK REQUIRED")
    print("="*50)
    print(f"Agent's action for '{state}': {action}")
    print("Was this action correct?")
    print("👍 = Correct action (type: 1, y, yes, or 👍)")
    print("👎 = Incorrect action (type: 2, n, no, or 👎)")
    print("-"*50)
    
    # Get initial feedback
    feedback, correction = None, None
    while feedback is None:
        fb = input("Your feedback: ").strip().lower()
        
        if fb in ("1", "y", "yes", "👍", "correct", "good", "right"):
            print("✅ Positive feedback recorded!")
            feedback = "👍"
        elif fb in ("2", "n", "no", "👎", "incorrect", "wrong", "bad"):
            print("❌ Negative feedback recorded.")
            print("💡 CORRECTION REQUIRED: What action should have been taken?")
            print(f"   Available actions: {', '.join(agent.actions)}")
            
            # Mandatory correction prompt with validation
            while not correction:
                correction = input("Enter the correct action: ").strip().lower()
                if correction in agent.actions:
                    print(f"📝 Correction recorded: {correction}")
                    # Update Q-table with correction immediately
                    if hasattr(agent, 'update_q_with_correction'):
                        agent.update_q_with_correction(state, action, correction)
                    print(f"✅ Q-table updated with correction (+1 bonus reward)")
                    break
                elif correction:
                    print(f"⚠️ Invalid action '{correction}'. Choose from: {', '.join(agent.actions)}")
                    correction = None
                else:
                    print("⚠️ Correction cannot be empty. Please provide the correct action.")
            
            feedback = "👎"
        else:
            print("⚠️  Invalid input! Please use 👍 or 👎")
            continue
    
    # Generate follow-up suggestion for successful tasks
    followup_task = None
    followup_accepted = False
    followup_reward = 0
    
    if feedback == "👍" and hasattr(agent, 'suggest_followup_task'):
        followup_action = agent.suggest_followup_task(state, action)
        followup_task = f"{followup_action} (logical next step after {action})"
        
        print(f"\n🚀 Follow-up suggestion: {followup_task}")
        print("This suggestion is based on learned task sequences and Q-values.")
        
        accept_input = input("Would you like to try this follow-up task? (y/n): ").strip().lower()
        
        if accept_input in ('y', 'yes', '1', 'ok', 'sure'):
            followup_accepted = True
            followup_reward = agent.calculate_followup_reward(True)
            print(f"✅ Follow-up accepted! Bonus reward: +{followup_reward}")
        else:
            followup_accepted = False
            followup_reward = 0  # No penalty for declining
            print("📝 Follow-up declined - no penalty applied.")
    
    # Provide correction bonus reward
    correction_reward = 1 if correction else 0
    total_followup_reward = followup_reward + correction_reward
    
    return feedback, correction, followup_task, followup_accepted, total_followup_reward

def get_confidence_score():
    """Get confidence score from user for action evaluation"""
    while True:
        try:
            confidence = input("Rate agent confidence (1-10, or press Enter for auto): ").strip()
            if not confidence:
                import random
                return round(random.uniform(0.5, 1.0), 2)
            
            score = float(confidence)
            if 1 <= score <= 10:
                return score / 10  # Normalize to 0-1 range
            else:
                print("⚠️  Please enter a number between 1-10")
        except ValueError:
            print("⚠️  Please enter a valid number")
