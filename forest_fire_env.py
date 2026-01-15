import gymnasium as gym
from gymnasium import spaces
import numpy as np
import matplotlib.pyplot as plt


class ForestFireEnv(gym.Env):
    """
    Custom Gymnasium environment for forest fire management.
    
    Grid: 10x10
    States: 0=Empty, 1=Tree, 2=Fire, 3=Agent
    Actions: 0-3=Move (up, down, left, right), 4=Cut tree, 5=Extinguish fire, 6=Wait
    """
    
    metadata = {'render_modes': ['human', 'rgb_array']}
    
    def __init__(self, grid_size=10, fire_spread_prob=0.3, initial_trees=0.6, initial_fires=3):
        super(ForestFireEnv, self).__init__()
        
        self.grid_size = grid_size
        self.fire_spread_prob = fire_spread_prob
        self.initial_trees = initial_trees
        self.initial_fires = initial_fires
        
        # Action space: 7 discrete actions
        # 0: Move up, 1: Move down, 2: Move left, 3: Move right
        # 4: Cut tree, 5: Extinguish fire, 6: Wait
        self.action_space = spaces.Discrete(7)
        
        # Observation space: grid_size x grid_size grid with values 0-3
        self.observation_space = spaces.Box(
            low=0, high=3, shape=(grid_size, grid_size), dtype=np.int32
        )
        
        # Initialize state variables
        self.grid = None
        self.agent_pos = None
        self.initial_tree_count = 0
        self.step_count = 0
        
    def reset(self, seed=None, options=None):
        """Reset the environment to initial state."""
        super().reset(seed=seed)
        
        # Initialize grid with empty cells
        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=np.int32)
        
        # Place trees randomly
        tree_mask = self.np_random.random((self.grid_size, self.grid_size)) < self.initial_trees
        self.grid[tree_mask] = 1
        self.initial_tree_count = np.sum(self.grid == 1)
        
        # Place agent in a random empty or tree position
        empty_or_tree_positions = np.argwhere(self.grid <= 1)
        if len(empty_or_tree_positions) > 0:
            agent_idx = self.np_random.integers(0, len(empty_or_tree_positions))
            self.agent_pos = tuple(empty_or_tree_positions[agent_idx])
        else:
            self.agent_pos = (0, 0)
        
        # Place initial fires randomly on trees (not where agent is)
        tree_positions = np.argwhere(self.grid == 1)
        tree_positions = [tuple(pos) for pos in tree_positions if tuple(pos) != self.agent_pos]
        
        if len(tree_positions) >= self.initial_fires:
            fire_indices = self.np_random.choice(len(tree_positions), self.initial_fires, replace=False)
            for idx in fire_indices:
                fire_pos = tree_positions[idx]
                self.grid[fire_pos] = 2
        
        self.step_count = 0
        
        return self._get_obs(), {}
    
    def _get_obs(self):
        """Get current observation (grid with agent marked)."""
        obs = self.grid.copy()
        obs[self.agent_pos] = 3  # Mark agent position
        return obs
    
    def step(self, action):
        """Execute one step in the environment."""
        self.step_count += 1
        reward = 0
        terminated = False
        truncated = False
        
        # Save agent's current position
        current_pos = self.agent_pos
        
        # Execute action
        if action == 0:  # Move up
            new_pos = (max(0, self.agent_pos[0] - 1), self.agent_pos[1])
            self.agent_pos = new_pos
        elif action == 1:  # Move down
            new_pos = (min(self.grid_size - 1, self.agent_pos[0] + 1), self.agent_pos[1])
            self.agent_pos = new_pos
        elif action == 2:  # Move left
            new_pos = (self.agent_pos[0], max(0, self.agent_pos[1] - 1))
            self.agent_pos = new_pos
        elif action == 3:  # Move right
            new_pos = (self.agent_pos[0], min(self.grid_size - 1, self.agent_pos[1] + 1))
            self.agent_pos = new_pos
        elif action == 4:  # Cut tree
            if self.grid[self.agent_pos] == 1:
                self.grid[self.agent_pos] = 0
                reward += 1  # Small reward for cutting
        elif action == 5:  # Extinguish fire
            if self.grid[self.agent_pos] == 2:
                self.grid[self.agent_pos] = 0
                reward += 10  # Big reward for extinguishing fire
        elif action == 6:  # Wait
            pass
        
        # Fire spread phase (stochastic)
        fire_positions = np.argwhere(self.grid == 2)
        new_fires = []
        
        for fire_pos in fire_positions:
            row, col = fire_pos
            # Check all 4 neighbors
            neighbors = [
                (row - 1, col), (row + 1, col),
                (row, col - 1), (row, col + 1)
            ]
            
            for neighbor in neighbors:
                n_row, n_col = neighbor
                # Check if neighbor is within bounds
                if 0 <= n_row < self.grid_size and 0 <= n_col < self.grid_size:
                    # Fire spreads to trees with probability
                    if self.grid[n_row, n_col] == 1:
                        if self.np_random.random() < self.fire_spread_prob:
                            new_fires.append((n_row, n_col))
        
        # Apply new fires
        for fire_pos in new_fires:
            self.grid[fire_pos] = 2
        
        # Burn out fires (trees on fire become empty after spreading)
        for fire_pos in fire_positions:
            if self.grid[tuple(fire_pos)] == 2:  # Still on fire
                self.grid[tuple(fire_pos)] = 0  # Burned out
        
        # Calculate penalty for active fires
        active_fires = np.sum(self.grid == 2)
        reward -= 0.1 * active_fires
        
        # Check termination conditions
        remaining_trees = np.sum(self.grid == 1)
        
        # Forest destroyed: lost more than 80% of trees
        if self.initial_tree_count > 0:
            destruction_ratio = 1 - (remaining_trees / self.initial_tree_count)
            if destruction_ratio >= 0.8:
                reward -= 100
                terminated = True
        
        # Episode ends if no more fires (success) or max steps
        if active_fires == 0 and len(fire_positions) > 0:
            # All fires extinguished
            reward += 50  # Bonus for clearing all fires
            terminated = True
        
        # Truncate after too many steps
        if self.step_count >= 200:
            truncated = True
        
        return self._get_obs(), reward, terminated, truncated, {}
    
    def render(self, mode='human'):
        """Render the environment."""
        if mode == 'human':
            print(f"\nStep: {self.step_count}")
            print(f"Agent position: {self.agent_pos}")
            
            # Create a visual representation
            visual = self.grid.copy()
            visual[self.agent_pos] = 3
            
            symbols = {0: '·', 1: '🌲', 2: '🔥', 3: '🤖'}
            for row in visual:
                print(' '.join([symbols.get(cell, str(cell)) for cell in row]))
            
            print(f"Trees: {np.sum(self.grid == 1)}, Fires: {np.sum(self.grid == 2)}")
        
        return None
    
    def render_matplotlib(self, ax=None):
        """Render the environment using matplotlib."""
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))
        
        # Create color map
        # 0=Empty (white), 1=Tree (green), 2=Fire (red), 3=Agent (blue)
        display_grid = self.grid.copy()
        display_grid[self.agent_pos] = 3
        
        colors = np.zeros((self.grid_size, self.grid_size, 3))
        colors[display_grid == 0] = [1, 1, 1]      # White for empty
        colors[display_grid == 1] = [0, 0.7, 0]    # Green for trees
        colors[display_grid == 2] = [1, 0, 0]      # Red for fire
        colors[display_grid == 3] = [0, 0, 1]      # Blue for agent
        
        ax.imshow(colors, interpolation='nearest')
        ax.grid(True, which='both', color='black', linewidth=0.5)
        ax.set_xticks(np.arange(-0.5, self.grid_size, 1))
        ax.set_yticks(np.arange(-0.5, self.grid_size, 1))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_title(f'Step: {self.step_count} | Trees: {np.sum(self.grid == 1)} | Fires: {np.sum(self.grid == 2)}')
        
        return ax
