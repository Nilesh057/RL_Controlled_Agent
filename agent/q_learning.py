import os
import pickle
import random
import csv
import math

class QLearningAgent:
    def __init__(self, actions, alpha=0.2, gamma=0.9, epsilon=0.2, q_path="data/q_table.pkl"):
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_path = q_path
        self.q = {}
        self.load_q_table(q_path)

    def _ensure_state(self, state):
        if state not in self.q:
            self.q[state] = {a: 0.0 for a in self.actions}

    def select_action(self, state):
        self._ensure_state(state)
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        return max(self.q[state], key=self.q[state].get)

    def update_q_table(self, state, action, reward, next_state):
        """Update Q-table with immediate save for persistence"""
        self._ensure_state(state)
        self._ensure_state(next_state)
        old = self.q[state][action]
        next_max = max(self.q[next_state].values()) if self.q[next_state] else 0.0
        new = old + self.alpha * (reward + self.gamma * next_max - old)
        self.q[state][action] = new
        
        # Auto-save after each update for persistence
        self.save_q_table()
    
    def update_q_with_correction(self, state, wrong_action, correct_action, penalty=-1, bonus=2):
        """Update Q-table when user provides correction"""
        self._ensure_state(state)
        
        # Penalize wrong action
        if wrong_action in self.q[state]:
            self.q[state][wrong_action] += penalty
        
        # Reward correct action
        if correct_action in self.actions:
            self.q[state][correct_action] += bonus
            print(f"✅ Q-table updated: {correct_action} rewarded (+{bonus}), {wrong_action} penalized ({penalty})")
        
        # Save immediately
        self.save_q_table()

    def top_actions(self, state, k=2):
        """Get top k actions for a given state, sorted by Q-value"""
        self._ensure_state(state)
        return sorted(self.q[state].items(), key=lambda kv: kv[1], reverse=True)[:k]
    
    def get_next_best_action(self, state):
        """Get the next best action suggestion (second highest Q-value)"""
        top_actions = self.top_actions(state, k=2)
        if len(top_actions) >= 2:
            return top_actions[1][0]  # Second best action
        elif len(top_actions) == 1:
            return top_actions[0][0]  # Only one action available
        else:
            return random.choice(self.actions)  # Fallback to random
    
    def get_action_confidence(self, state, action):
        """Get confidence score based on Q-value differences and softmax calculations
        Formula: (Q[state, chosen_action] - mean(Q[state, other_actions])) / max_range + softmax
        """
        import math  # Import at the beginning of the method
        
        self._ensure_state(state)
        
        # Get all Q-values for this state
        q_values = list(self.q[state].values())
        action_q = self.q[state].get(action, 0)
        
        if not q_values or len(q_values) <= 1:
            return 0.5  # Neutral confidence for single or no actions
        
        # Method 1: Q-value difference from mean of other actions
        other_actions_q = [q for a, q in self.q[state].items() if a != action]
        if other_actions_q:
            mean_other_q = sum(other_actions_q) / len(other_actions_q)
            max_q = max(q_values)
            min_q = min(q_values)
            max_range = max_q - min_q if max_q != min_q else 1.0
            
            # Enhanced normalized difference confidence
            diff_confidence = (action_q - mean_other_q) / max_range
            # Sigmoid transformation for better distribution
            diff_confidence = 1 / (1 + math.exp(-diff_confidence * 2))  # Sigmoid scaling
        else:
            diff_confidence = 0.5
        
        # Method 2: Softmax-based confidence with temperature scaling
        try:
            temperature = 2.0  # Temperature parameter for softmax
            exp_values = [math.exp(q / temperature) for q in q_values]
            total_exp = sum(exp_values)
            action_exp = math.exp(action_q / temperature)
            softmax_confidence = action_exp / total_exp if total_exp > 0 else 0.5
        except OverflowError:
            # Handle overflow with large Q-values
            softmax_confidence = 0.9 if action_q == max(q_values) else 0.3
        
        # Method 3: Relative ranking confidence 
        sorted_q = sorted(q_values, reverse=True)
        if action_q in sorted_q:
            rank = sorted_q.index(action_q)
            rank_confidence = 1 - (rank / len(sorted_q))
        else:
            rank_confidence = 0.1
        
        # Combine all three methods with weights
        final_confidence = (diff_confidence * 0.4) + (softmax_confidence * 0.4) + (rank_confidence * 0.2)
        
        return round(max(0.1, min(0.99, final_confidence)), 3)  # Clamp between 0.1-0.99
    
    def get_confidence_details(self, state, action):
        """Get detailed confidence breakdown for logging"""
        import math  # Import at the beginning of the method
        
        self._ensure_state(state)
        q_values = list(self.q[state].values())
        action_q = self.q[state].get(action, 0)
        
        if not q_values:
            return {"method_1": 0.5, "method_2": 0.5, "method_3": 0.5, "final": 0.5, "q_values": [], "chosen_q": 0}
        
        # Calculate all three methods
        other_actions_q = [q for a, q in self.q[state].items() if a != action]
        mean_other_q = sum(other_actions_q) / len(other_actions_q) if other_actions_q else 0
        
        # Method 1: Sigmoid difference
        max_q = max(q_values) if q_values else 0
        min_q = min(q_values) if q_values else 0
        max_range = max_q - min_q if max_q != min_q else 1.0
        diff = (action_q - mean_other_q) / max_range
        method_1 = 1 / (1 + math.exp(-diff * 2))
        
        # Method 2: Softmax
        try:
            temperature = 2.0
            exp_values = [math.exp(q / temperature) for q in q_values]
            total_exp = sum(exp_values)
            method_2 = math.exp(action_q / temperature) / total_exp if total_exp > 0 else 0.5
        except OverflowError:
            method_2 = 0.9 if action_q == max_q else 0.3
        
        # Method 3: Ranking
        sorted_q = sorted(q_values, reverse=True)
        if action_q in sorted_q:
            rank = sorted_q.index(action_q)
            method_3 = 1 - (rank / len(sorted_q))
        else:
            method_3 = 0.1
        
        return {
            "q_values": q_values,
            "chosen_q": action_q,
            "mean_other_q": mean_other_q,
            "method_1_sigmoid": round(method_1, 3),
            "method_2_softmax": round(method_2, 3),
            "method_3_ranking": round(method_3, 3),
            "final": self.get_action_confidence(state, action)
        }

    def suggest_followup_task(self, current_state, current_action):
        """Suggest logical follow-up task based on current context, learned patterns, and Q-values"""
        # Enhanced logical task sequences based on real-world workflows
        task_sequences = {
            'open': ['close', 'screenshot', 'mute', 'unmute'],
            'mute': ['unmute', 'play', 'close'],
            'play': ['mute', 'close', 'screenshot'],
            'screenshot': ['open', 'close', 'mute'],
            'close': ['open', 'screenshot'],
            'unmute': ['play', 'mute', 'screenshot'],
            'set_dnd': ['unmute', 'open', 'close']
        }
        
        # Get logical next actions
        logical_next = task_sequences.get(current_action, ['open', 'close', 'screenshot'])
        
        # Create hypothetical follow-up states for Q-value evaluation
        best_followup = None
        best_combined_score = float('-inf')
        
        for next_action in logical_next:
            # Evaluate multiple possible next states
            possible_states = [
                f"{current_state}_completed",  # State after successful completion
                f"after_{current_action}",     # General state after this action
                current_state,                 # Same state (for repeated actions)
                f"{current_action}_context"     # Context-specific state
            ]
            
            # Calculate average Q-value across possible states
            q_scores = []
            for next_state in possible_states:
                self._ensure_state(next_state)
                q_value = self.q[next_state].get(next_action, 0)
                q_scores.append(q_value)
            
            avg_q_score = sum(q_scores) / len(q_scores) if q_scores else 0
            
            # Add logical sequence bonus (prefer early items in sequence)
            sequence_bonus = (len(logical_next) - logical_next.index(next_action)) * 0.1
            
            # Combine Q-value score with logical sequence preference
            combined_score = avg_q_score + sequence_bonus
            
            if combined_score > best_combined_score:
                best_combined_score = combined_score
                best_followup = next_action
        
        # Fallback to highest Q-value action if no good logical sequence found
        if not best_followup or best_combined_score <= 0:
            # Find action with highest Q-value in current state
            self._ensure_state(current_state)
            if self.q[current_state]:
                best_followup = max(self.q[current_state], key=self.q[current_state].get)
            else:
                best_followup = logical_next[0] if logical_next else 'open'
        
        return best_followup
    
    def calculate_followup_reward(self, user_accepted):
        """Calculate bonus reward for follow-up suggestion acceptance"""
        if user_accepted:
            return 1  # Bonus reward for accepted suggestion
        else:
            return 0  # No penalty for rejection

    def save_q_table(self, path=None):
        """Save Q-table with backup and CSV export for analysis"""
        path = path or self.q_path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save binary pickle file
        with open(path, "wb") as f:
            pickle.dump(self.q, f)
        
        # Also save as CSV for human readability
        csv_path = path.replace('.pkl', '.csv')
        try:
            import csv
            with open(csv_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['State', 'Action', 'Q_Value'])
                for state, actions in self.q.items():
                    for action, q_value in actions.items():
                        writer.writerow([state, action, round(q_value, 4)])
        except Exception as e:
            print(f"Warning: Could not save CSV version: {e}")

    def load_q_table(self, path=None):
        """Load Q-table with backup handling"""
        path = path or self.q_path
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    loaded_q = pickle.load(f)
                    self.q = loaded_q
                    print(f"✅ Q-table loaded from {path} with {len(self.q)} states")
            except Exception as e:
                print(f"⚠️  Failed to load Q-table from {path}: {e}")
                print("Starting with fresh Q-table")
                self.q = {}
        else:
            print(f"No existing Q-table found at {path}. Starting fresh.")
            self.q = {}
