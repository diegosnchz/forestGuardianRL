import gymnasium as gym
from gymnasium import spaces
import numpy as np
import time
from numba import jit, int32, float32
import xarray as xr

# --- CONFIGURATION ---
GRID_SIZE = 50   # Expanded scale for "Industrial" logic
N_CHANNELS = 4   # 0: Terrain, 1: Humidity, 2: Fire, 3: Agents
MAX_STEPS = 500

# Constants for channels
CH_TERRAIN = 0
CH_HUMIDITY = 1
CH_FIRE = 2
CH_AGENTS = 3

# --- NUMBA KERNEL (THE PHYSICS ENGINE) ---
@jit(nopython=True, cache=True)
def physics_step(state_grid, actions, agent_positions, fire_spread_prob, wind_dir):
    """
    Simulates one step of the environment dynamics.
    Optimized with Numba for high-performance computing.
    
    state_grid: (C, H, W) float32 numpy array
    actions: (N,) int array of agent actions
    agent_positions: (N, 2) int array
    fire_spread_prob: float
    wind_dir: (2,) float vector (dx, dy) effect
    """
    C, H, W = state_grid.shape
    num_agents = len(actions)
    
    # 1. AGENT DYNAMICS
    # Clean old positions
    for i in range(num_agents):
        r, c = agent_positions[i]
        state_grid[CH_AGENTS, r, c] = 0.0
        
    for i in range(num_agents):
        action = actions[i]
        r, c = agent_positions[i]
        
        # 0: Up, 1: Down, 2: Left, 3: Right, 4: Stay/Suppress
        dr, dc = 0, 0
        if action == 0: dr = -1
        elif action == 1: dr = 1
        elif action == 2: dc = -1
        elif action == 3: dc = 1
        
        nr, nc = r + dr, c + dc
        
        # Boundary checks
        if 0 <= nr < H and 0 <= nc < W:
            # Collision check (naive for performance: last one wins/overwrites or we check grid)
            # Just move
            agent_positions[i] = (nr, nc)
            
            # Action 5: Suppress Fire
            if action == 5:
                 # Suppress 3x3 area
                 r_min = max(0, nr-1)
                 r_max = min(H, nr+2)
                 c_min = max(0, nc-1)
                 c_max = min(W, nc+2)
                 state_grid[CH_FIRE, r_min:r_max, c_min:c_max] = 0.0

    # Write new positions
    for i in range(num_agents):
        r, c = agent_positions[i]
        state_grid[CH_AGENTS, r, c] = 1.0

    # 2. FIRE DYNAMICS (Cellular Automaton with Wind & Terrain)
    # We need a copy to update synchronously
    fire_grid = state_grid[CH_FIRE].copy()
    terrain_grid = state_grid[CH_TERRAIN]
    humidity_grid = state_grid[CH_HUMIDITY]
    
    # Iterate over grid (this loop is fast in Numba)
    for r in range(H):
        for c in range(W):
            if state_grid[CH_FIRE, r, c] > 0.1:
                # Fire exists here, check spread
                
                # Dynamic Spread Probability
                # Slope effect: Fire moves faster uphill (Higher Terrain)
                # Wind effect
                
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        if dr == 0 and dc == 0: continue
                        
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < H and 0 <= nc < W:
                            if state_grid[CH_FIRE, nr, nc] < 0.1: # Not burning yet
                                
                                # Base prob
                                prob = fire_spread_prob
                                
                                # Humidity Modifier (Higher humidity = lower prob)
                                prob *= (1.0 - humidity_grid[nr, nc])
                                
                                # Terrain Modifier (Uphill spread)
                                slope = terrain_grid[nr, nc] - terrain_grid[r, c]
                                if slope > 0: prob *= (1.0 + slope * 2.0)
                                
                                # Wind Modifier (Directional bias)
                                # Dot product of direction and wind
                                v_norm = np.sqrt(dr*dr + dc*dc)
                                dir_r = dr / v_norm
                                dir_c = dc / v_norm
                                wind_factor = dir_r * wind_dir[0] + dir_c * wind_dir[1]
                                prob *= (1.0 + wind_factor)
                                
                                if np.random.random() < prob:
                                    fire_grid[nr, nc] = 1.0
                                    
    state_grid[CH_FIRE] = fire_grid
    
    # Calculate Reward metrics immediately
    trees_burned = np.sum(fire_grid)
    return state_grid, agent_positions, trees_burned

class ForestGuardianEnv(gym.Env):
    """
    The High-Performance Industrial Environment.
    Wraps Xarray+Numba logic in a standard Gym API.
    """
    metadata = {'render_modes': ['human', 'rgb_array']}

    def __init__(self, grid_size=GRID_SIZE, num_agents=2):
        super(ForestGuardianEnv, self).__init__()
        
        self.grid_size = grid_size
        self.num_agents = num_agents
        
        # Action Space: 4 moves + 1 wait + 1 suppress
        self.action_space = spaces.MultiDiscrete([6] * num_agents)
        
        # Observation Space: Multi-channel Grid
        self.observation_space = spaces.Box(
            low=0, high=1, 
            shape=(N_CHANNELS, grid_size, grid_size), 
            dtype=np.float32
        )
        
        self.state = None
        self.agent_positions = None
        self.steps = 0
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # Initialize Xarray Dataset for complex state management (Metadata)
        # But we perform operations on the underlying numpy array for speed
        
        # 1. Terrain (Perlin noise-ish or simple gradient)
        # Creating a simple mountain in the center
        x = np.linspace(-1, 1, self.grid_size)
        y = np.linspace(-1, 1, self.grid_size)
        X, Y = np.meshgrid(x, y)
        terrain = np.exp(-(X**2 + Y**2)/0.5) # Gaussian hill
        
        # 2. Humidity (Random pockets)
        humidity = np.random.rand(self.grid_size, self.grid_size) * 0.5 + 0.2
        
        # 3. Fire (Start in random corners)
        fire = np.zeros((self.grid_size, self.grid_size), dtype=np.float32)
        start_fires = 3
        for _ in range(start_fires):
            fr, fc = np.random.randint(0, self.grid_size, size=2)
            fire[fr, fc] = 1.0
            
        # 4. Agents
        agents = np.zeros((self.grid_size, self.grid_size), dtype=np.float32)
        self.agent_positions = np.zeros((self.num_agents, 2), dtype=np.int32)
        for i in range(self.num_agents):
            self.agent_positions[i] = [0, i] # Start at top left
            agents[0, i] = 1.0
            
        # Combine into (C, H, W)
        self.np_state = np.stack([terrain, humidity, fire, agents]).astype(np.float32)
        
        self.steps = 0
        return self.np_state, {}

    def step(self, actions):
        self.steps += 1
        
        # Constants for simulation
        spread_prob = 0.05
        wind = np.array([0.2, 0.5]) # Wind blowing South-East
        
        prev_fire_sum = np.sum(self.np_state[CH_FIRE])
        
        # --- THE NUMBA CALL ---
        self.np_state, self.agent_positions, current_fire_sum = physics_step(
            self.np_state, 
            np.array(actions, dtype=np.int32), 
            self.agent_positions,
            spread_prob, 
            wind
        )
        # ----------------------
        
        # Reward Calculation
        # Penalty for fire existing (Global)
        fire_penalty = -current_fire_sum * 0.1
        
        # Reward for suppressing (Difference in fire)
        # If fire grew less than expected or shrank?
        # Simple Logic: Maximize trees preserved (which is minimize fire sum)
        
        reward = fire_penalty
        
        terminated = False
        truncated = False
        if self.steps >= MAX_STEPS:
            truncated = True
        
        # Termination: Fire out or All burned
        if current_fire_sum == 0:
            reward += 1000 # Mission Accomplished
            terminated = True
        elif current_fire_sum > (self.grid_size**2 * 0.8):
            reward -= 1000 # Forest Lost
            terminated = True
            
        info = {
            "fire_intensity": current_fire_sum,
            "trees_lost_pct": (current_fire_sum / (self.grid_size**2)) * 100
        }
        
        return self.np_state, reward, terminated, truncated, info

    def render(self):
        # Needed for debug, implementing simple matplotlib
        pass

if __name__ == "__main__":
    # Quick Test
    env = ForestGuardianEnv()
    obs, _ = env.reset()
    print("State Shape:", obs.shape)
    
    t0 = time.time()
    for _ in range(100):
        actions = [1, 2] # Dummy actions
        obs, r, term, trunc, info = env.step(actions)
        if term: break
    print(f"100 Steps Time: {time.time()-t0:.4f}s")
