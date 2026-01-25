import numpy as np
import random
from numba_env import CELL_FIRE, CELL_TREE, CELL_EMPTY, CELL_BURNT

class XAIAssistant:
    def __init__(self):
        self.history = []
        self.context = {}
        
    def welcome_message(self):
        return """
        **👋 Welcome to ForestGuardian Command Center!**
        
        I am your AI Tactical Advisor. My job is to explain what the autonomous drone agents are thinking.
        
        **What you are seeing:**
        - 🌲 **Green**: Healthy Forest
        - 🔥 **Red (Pastel)**: Active Fire (Requires Extinguishing)
        - 🟫 **Brown**: Burnt Areas (Lost resources)
        - 🔵 **Blue Dots**: Your AI Agents
        
        **Tip:** Ask me "Why did Agent 0 move left?" or "What is the fire status?"
        """
        
    def analyze_step(self, obs, agents_prev, agents_curr, rewards):
        """
        Analyzes the transition from step T to T+1 to generate explanations.
        """
        self.context['obs'] = obs
        self.context['agents'] = agents_curr
        
        # Simple heuristic analysis for prototype
        # In a real system, this would use SHAP values from the RL model
        
        analysis = []
        grid = obs['grid']
        
        # Check for extinguishing events
        for i, (prev, curr) in enumerate(zip(agents_prev, agents_curr)):
            if np.array_equal(prev, curr):
                # Agent didn't move -> Likely extinguished or blocked
                r, c = curr
                # Check 3x3 for fire
                local_grid = grid[max(0,r-1):min(grid.shape[0],r+2), max(0,c-1):min(grid.shape[1],c+2)]
                if np.any(local_grid == CELL_FIRE):
                    analysis.append(f"**Agent {i}** is holding position to **CONTAIN FIRE** at sector {curr}.")
                
        if len(analysis) > 0:
            return "\n".join(analysis)
        return None

    def query(self, user_text, current_state):
        """
        Responds to user questions based on current simulation state.
        """
        user_text = user_text.lower()
        
        if "hello" in user_text or "hi" in user_text:
            return "Systems Online. Ready to analyze tactical patterns. How can I assist?"
            
        if "why" in user_text and "agent" in user_text:
            # Fake XAI logic for demo
            agent_idx = 0 if "0" in user_text else 1
            return f"**Analysis for Agent {agent_idx}:**\nModel detected high-value cluster of trees at risk. Movement vector aligns with gradient of fire intensity. Confidence: 89%."
            
        if "status" in user_text:
            grid = current_state['grid']
            fires = np.sum(grid == CELL_FIRE)
            trees = np.sum(grid == CELL_TREE)
            return f"**Current Situation Report:**\n- Active Fires: {fires}\n- Remaining Forest: {trees} units\n- Threat Level: {'CRITICAL' if fires > 10 else 'MODERATE'}"
            
        if "help" in user_text:
            return "Try asking: 'Why did agent 0 stop?', 'What is the fire status?', or 'Explain the strategy'."
            
        return "I am processing that request... (My XAI module is currently limited to tactical analysis. Try asking about agent actions or fire status.)"
