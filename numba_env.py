import numpy as np
import gymnasium as gym
from gymnasium import spaces
from numba import jit
import networkx as nx

# --- CONSTANTS ---
CELL_EMPTY = 0
CELL_TREE = 1
CELL_FIRE = 2
CELL_BURNT = 3

# Actions
ACTION_NONE = 0
ACTION_UP = 1
ACTION_DOWN = 2
ACTION_LEFT = 3
ACTION_RIGHT = 4
ACTION_EXTINGUISH = 5

@jit(nopython=True)
def _fast_fire_spread(grid, p_fire, p_burnout):
    """
    Simulates Cellular Automata fire spread with persistence.
    """
    rows, cols = grid.shape
    new_grid = grid.copy()
    
    for r in range(rows):
        for c in range(cols):
            cell = grid[r, c]
            
            if cell == CELL_FIRE:
                # With p_burnout, it becomes burnt
                if np.random.random() < p_burnout:
                    new_grid[r, c] = CELL_BURNT
                
                # Try to spread to neighbors regardless if it burned out this step 
                # (to ensure at least one spread attempt)
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if grid[nr, nc] == CELL_TREE:
                            if np.random.random() < p_fire:
                                new_grid[nr, nc] = CELL_FIRE
                            
    return new_grid

@jit(nopython=True)
def _get_agent_obs_grid(grid, agent_pos, view_radius):
    """
    Extracts a local grid observation for an agent.
    Pads with 0 if out of bounds.
    """
    r, c = agent_pos
    rows, cols = grid.shape
    size = 2 * view_radius + 1
    obs = np.zeros((size, size), dtype=np.int8)
    
    r_start = r - view_radius
    c_start = c - view_radius
    
    for i in range(size):
        for j in range(size):
            cur_r = r_start + i
            cur_c = c_start + j
            if 0 <= cur_r < rows and 0 <= cur_c < cols:
                obs[i, j] = grid[cur_r, cur_c]
                
    return obs

class ForestFireMAEnv(gym.Env):
    """
    Multi-Agent Forest Fire Environment.
    
    State:
        - Grid: HxW numpy array (Integers)
        - Agents: List of (row, col) positions
    
    Action Space (Per Agent):
        - 0: None
        - 1: Up
        - 2: Down
        - 3: Left
        - 4: Right
        - 5: Extinguish (3x3 area center)
    """
    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self, grid_size=32, n_agents=2, view_radius=4):
        super(ForestFireMAEnv, self).__init__()
        
        self.grid_size = grid_size
        self.n_agents = n_agents
        self.view_radius = view_radius
        
        # Grid dimensions
        self.rows = grid_size
        self.cols = grid_size
        
        # Define Action Space (Discrete per agent)
        # Note: In standard Gym, we often flatten this or use MultiDiscrete.
        # Here we simulate independent choices.
        self.action_space = spaces.MultiDiscrete([6] * n_agents)
        
        # Observation Space: Needs to accommodate Graph + Grid info.
        # For simplicity in Gym check compliance, we use a Dict.
        # global_grid: The full map (channel 0: static/fire)
        # agent_positions: Linear list
        self.observation_space = spaces.Dict({
            "grid": spaces.Box(low=0, high=2, shape=(self.rows, self.cols), dtype=np.int8),
            "agents": spaces.Box(low=0, high=grid_size, shape=(n_agents, 2), dtype=np.int32)
        })
        
        self.grid = None
        self.agents = None
        
        # Physics Params
        self.p_fire = 0.12 # Balanced spread
        self.p_burnout = 0.02 # Fires last longer before dying on their own
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # 1. Initialize Grid (Balanced Forest)
        # 70% trees, 30% empty
        self.grid = np.random.choice([CELL_EMPTY, CELL_TREE], 
                                     size=(self.rows, self.cols), 
                                     p=[0.3, 0.7]).astype(np.int8)
        
        # 2. Start some fires (Ensure num_fires are started on trees)
        num_fires = 8 # Significant but manageable outbreak
        started = 0
        tries = 0
        while started < num_fires and tries < 100:
            idx = np.random.randint(0, self.rows * self.cols)
            r, c = divmod(idx, self.cols)
            if self.grid[r, c] == CELL_TREE:
                self.grid[r, c] = CELL_FIRE
                started += 1
            tries += 1
            
        # 3. Spawn Agents (Randomly across the map to avoid stacking)
        self.agents = []
        for i in range(self.n_agents):
            r = np.random.randint(0, self.rows)
            c = np.random.randint(0, self.cols)
            self.agents.append(np.array([r, c]))
            
        self.agents = np.array(self.agents, dtype=np.int32)
        
        return self._get_obs(), {}

    def step(self, actions):
        """
        actions: List/Array of ints, one per agent.
        """
        rewards = np.zeros(self.n_agents)
        initial_trees = np.sum(self.grid == CELL_TREE)
        
        # 1. Apply Agent Actions
        for i, action in enumerate(actions):
            r, c = self.agents[i]
            
            if action == ACTION_UP:
                r = max(0, r - 1)
            elif action == ACTION_DOWN:
                r = min(self.rows - 1, r + 1)
            elif action == ACTION_LEFT:
                c = max(0, c - 1)
            elif action == ACTION_RIGHT:
                c = min(self.cols - 1, c + 1)
            elif action == ACTION_EXTINGUISH:
                # Extinguish 3x3 area around agent
                # Reward for putting out fire?
                extinguished_count = self._apply_extinguish(r, c)
                rewards[i] += extinguished_count * 5.0 # High reward for executing task
                
            self.agents[i] = [r, c]
            
        # 2. Physics Step (Fire Spread)
        trees_before_spread = np.sum(self.grid == CELL_TREE)
        self.grid = _fast_fire_spread(self.grid, self.p_fire, self.p_burnout)
        trees_after_spread = np.sum(self.grid == CELL_TREE)
        
        # Global Penalty for lost trees
        burnt_trees = trees_before_spread - trees_after_spread
        global_penalty = burnt_trees * -1.0
        
        # Add global penalty to all agents (Cooperative)
        rewards += global_penalty
        
        terminated = False # Endless for now, or defined by steps
        truncated = False
        
        # Calculate forest health
        total_cells = self.rows * self.cols
        current_trees = trees_after_spread
        health_pct = (current_trees / total_cells) * 100.0
        
        info = {
            "burnt_last_step": burnt_trees,
            "forest_health": health_pct
        }
        
        return self._get_obs(), rewards, terminated, truncated, info

    def _apply_extinguish(self, r, c):
        """
        Extinguishes fires in 3x3 radius.
        Returns number of fires put out.
        """
        count = 0
        r_start = max(0, r - 1)
        r_end = min(self.rows, r + 2)
        c_start = max(0, c - 1)
        c_end = min(self.cols, c + 2)
        
        for i in range(r_start, r_end):
            for j in range(c_start, c_end):
                if self.grid[i, j] == CELL_FIRE:
                    if np.random.random() < 0.3: # 30% success rate per step
                        self.grid[i, j] = CELL_EMPTY 
                        count += 1
        return count

    def _get_obs(self):
        return {
            "grid": self.grid.copy(),
            "agents": self.agents.copy()
        }

    def get_graph_data(self):
        """
        Helper to generate graph data for GAT agents.
        Nodes: Agents
        Edges: Agents within communication radius (e.g., 10 cells)
        """
        n = self.n_agents
        adj = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.linalg.norm(self.agents[i] - self.agents[j])
                if dist < 10.0: # Communication radius
                    adj[i, j] = 1
                    adj[j, i] = 1
            adj[i, i] = 1 # Self-loop
            
        return adj
