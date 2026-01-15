import gymnasium as gym
from gymnasium import spaces
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation


class ForestFireEnv(gym.Env):
    """
    Custom Gymnasium environment for forest fire management.
    
    Grid: 10x10
    States: 0=Empty/Burned, 1=Tree, 2=Fire, 3=Agent1, 4=Agent2 (optional)
    Actions: 0-3=Move (up, down, left, right), 4=Cut tree, 5=Extinguish fire, 6=Wait
    """
    
    metadata = {'render_modes': ['human', 'rgb_array']}
    
    def __init__(self, grid_size=10, fire_spread_prob=0.6, initial_trees=0.6, initial_fires=5, num_agents=1):
        super(ForestFireEnv, self).__init__()
        
        self.grid_size = grid_size
        self.fire_spread_prob = fire_spread_prob
        self.initial_trees = initial_trees
        self.initial_fires = initial_fires
        
        # Water management system
        self.water_tank = 10
        self.max_water = 10
        
        # River zone: Row 0 is a water source (River/Base)
        # Agent can refill water faster here
        self.river_row = 0
        
        # Number of agents (for visualization bonus)
        self.num_agents = max(1, int(num_agents))
        self.agent_positions = []  # list of (row, col) when num_agents > 1
        
        # Action space: 7 discrete actions
        # 0: Move up, 1: Move down, 2: Move left, 3: Move right
        # 4: Cut tree, 5: Extinguish fire, 6: Wait
        self.action_space = spaces.Discrete(7)
        
        # Observation space values:
        # 0=Empty/Burned, 1=Tree, 2=Fire, 3=Agent1, 4=Agent2 (if enabled)
        self.observation_space = spaces.Box(
            low=0, high=4, shape=(grid_size, grid_size), dtype=np.int32
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
        
        # Place agent(s)
        if self.num_agents == 1:
            empty_or_tree_positions = np.argwhere(self.grid <= 1)
            if len(empty_or_tree_positions) > 0:
                agent_idx = self.np_random.integers(0, len(empty_or_tree_positions))
                self.agent_pos = tuple(empty_or_tree_positions[agent_idx])
            else:
                self.agent_pos = (0, 0)
            self.agent_positions = [self.agent_pos]
        else:
            # Two agents starting at opposite corners for visual contrast
            self.agent_positions = [(0, 0), (self.grid_size - 1, self.grid_size - 1)]
            self.agent_pos = self.agent_positions[0]  # backward compatibility
        
        # Clear river zone (row 0) from trees to make it accessible for water refills
        self.grid[self.river_row, :] = 0
        
        # Place initial fires randomly on trees (not where agent is, and not in river zone)
        tree_positions = np.argwhere(self.grid == 1)
        # avoid placing fire on any agent position
        agent_set = set(self.agent_positions)
        tree_positions = [tuple(pos) for pos in tree_positions if tuple(pos) not in agent_set]
        
        if len(tree_positions) >= self.initial_fires:
            fire_indices = self.np_random.choice(len(tree_positions), self.initial_fires, replace=False)
            for idx in fire_indices:
                fire_pos = tree_positions[idx]
                self.grid[fire_pos] = 2
        
        # Reset water tank
        self.water_tank = self.max_water
        self.step_count = 0
        
        return self._get_obs(), {}
    
    def _get_obs(self):
        """Get current observation (grid with agent(s) marked)."""
        obs = self.grid.copy()
        if self.num_agents == 1:
            obs[self.agent_pos] = 3  # Mark single agent
        else:
            a1 = self.agent_positions[0]
            a2 = self.agent_positions[1]
            obs[a1] = 3
            obs[a2] = 4
        return obs
    
    def step(self, action):
        """Execute one step in the environment."""
        self.step_count += 1
        reward = 0
        terminated = False
        truncated = False
        
        # Execute action (supports single or multi-agent, synchronized actions)
        def move(pos, action_id):
            r, c = pos
            if action_id == 0:  # up
                return (max(0, r - 1), c)
            if action_id == 1:  # down
                return (min(self.grid_size - 1, r + 1), c)
            if action_id == 2:  # left
                return (r, max(0, c - 1))
            if action_id == 3:  # right
                return (r, min(self.grid_size - 1, c + 1))
            return (r, c)
        
        # Movement
        if action in [0, 1, 2, 3]:
            if self.num_agents == 1:
                self.agent_pos = move(self.agent_pos, action)
                self.agent_positions[0] = self.agent_pos
            else:
                self.agent_positions = [move(p, action) for p in self.agent_positions]
                self.agent_pos = self.agent_positions[0]  # keep primary
        
        # Cut tree
        elif action == 4:
            positions = self.agent_positions if self.num_agents > 1 else [self.agent_pos]
            for p in positions:
                if self.grid[p] == 1:
                    self.grid[p] = 0
                    reward += 1
        
        # Extinguish fire
        elif action == 5:
            positions = self.agent_positions if self.num_agents > 1 else [self.agent_pos]
            extinguishes = 0
            for p in positions:
                if self.water_tank > 0 and self.grid[p] == 2:
                    self.grid[p] = 0
                    self.water_tank = max(0, self.water_tank - 1)
                    reward += 10
                    extinguishes += 1
            if extinguishes == 0:
                reward -= 1  # penalty for invalid extinguish
        
        # Wait / Recharge
        elif action == 6:
            positions = self.agent_positions if self.num_agents > 1 else [self.agent_pos]
            # Faster recovery if any agent is on river row
            if any(p[0] == self.river_row for p in positions):
                if self.water_tank < self.max_water:
                    reward += 2
                self.water_tank = self.max_water
            else:
                self.water_tank = min(self.water_tank + 2, self.max_water)
        
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
        
        # Burn out old fires first (before applying new ones)
        # This ensures fires persist for at least one step
        for fire_pos in fire_positions:
            self.grid[tuple(fire_pos)] = 0  # Burned out
        
        # Apply new fires after burning out old ones
        for fire_pos in new_fires:
            self.grid[fire_pos] = 2
        
        # Calculate penalty for active fires (new fires that just spread)
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
        
        # Episode ends if no more fires and there were fires at the start of this step
        if active_fires == 0 and len(fire_positions) > 0:
            # All fires extinguished (either by agent or burned out with no spread)
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
            print(f"Water level: {self.water_tank}/{self.max_water}")
            
            # Create a visual representation
            visual = self.grid.copy()
            if self.num_agents == 1:
                visual[self.agent_pos] = 3
            else:
                a1, a2 = self.agent_positions
                visual[a1] = 3
                visual[a2] = 4
            
            symbols = {0: '·', 1: '🌲', 2: '🔥', 3: 'A', 4: 'B'}
            for row in visual:
                print(' '.join([symbols.get(cell, str(cell)) for cell in row]))
            
            print(f"Trees: {np.sum(self.grid == 1)}, Fires: {np.sum(self.grid == 2)}")
        
        return None
    
    def render_matplotlib(self, ax=None, agent_acting=None):
        """Render the environment using matplotlib.
        
        Args:
            ax: matplotlib axis
            agent_acting: 'navegador' or 'operario' to highlight active agent
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))
        
        from matplotlib.colors import ListedColormap
        
        # Create color map: white, green, red, blue, orange
        # 0=Empty/Burned (white), 1=Tree (green), 2=Fire (red), 3=Navegador (blue), 4=Operario (orange)
        display_grid = self.grid.copy()
        if self.num_agents == 1:
            display_grid[self.agent_pos] = 3
        else:
            a1, a2 = self.agent_positions
            display_grid[a1] = 3
            display_grid[a2] = 4
        
        cmap = ListedColormap(['white', 'green', 'red', 'blue', 'orange'])
        colors = cmap(display_grid)
        
        ax.imshow(display_grid, interpolation='nearest', cmap=cmap, vmin=0, vmax=4)
        ax.grid(True, which='both', color='gray', linewidth=0.5, alpha=0.3)
        ax.set_xticks(np.arange(-0.5, self.grid_size, 1))
        ax.set_yticks(np.arange(-0.5, self.grid_size, 1))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        
        title = f'Step: {self.step_count} | Trees: {np.sum(self.grid == 1)} | Fires: {np.sum(self.grid == 2)} | Water: {self.water_tank}/{self.max_water}'
        if agent_acting:
            title = f'{title}\nActing: {agent_acting.upper()}'
        ax.set_title(title)
        
        return ax

    def render_animation(self, frames, agent_labels=None, filename='forest_fire_animation.gif', fps=5):
        """Create and save an animation (GIF or MP4) from a list of grid frames.

        Args:
            frames: list of np.ndarray grids over time
            agent_labels: list of agent names per frame (e.g., ['navegador', 'operario', ...])
            filename: output file path, .gif or .mp4
            fps: frames per second
        """
        from matplotlib.colors import ListedColormap
        
        fig, ax = plt.subplots(figsize=(7, 7))
        cmap = ListedColormap(['white', 'green', 'red', 'blue', 'orange'])

        im = ax.imshow(frames[0], interpolation='nearest', cmap=cmap, vmin=0, vmax=4)
        ax.grid(True, which='both', color='gray', linewidth=0.5, alpha=0.3)
        ax.set_xticks(np.arange(-0.5, self.grid_size, 1))
        ax.set_yticks(np.arange(-0.5, self.grid_size, 1))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        title_text = ax.set_title('Forest Fire - Step 0')

        def update(i):
            im.set_data(frames[i])
            label = ''
            if agent_labels and i < len(agent_labels):
                label = f' | Acting: {agent_labels[i].upper()}'
            title_text.set_text(f'Forest Fire - Step {i}{label}')
            return [im, title_text]

        anim = animation.FuncAnimation(fig, update, frames=len(frames), interval=1000//max(1, fps), blit=True)

        try:
            if filename.endswith('.mp4'):
                writer = animation.FFMpegWriter(fps=fps)
                anim.save(filename, writer=writer)
            else:
                writer = animation.PillowWriter(fps=fps)
                anim.save(filename, writer=writer)
            print(f"Animation saved to '{filename}'")
        except Exception as e:
            # Fallback to GIF if MP4 fails
            print(f"Failed to save animation to {filename}: {e}\nAttempting GIF fallback...")
            try:
                gif_name = filename.rsplit('.', 1)[0] + '.gif'
                writer = animation.PillowWriter(fps=fps)
                anim.save(gif_name, writer=writer)
                print(f"Animation saved to '{gif_name}'")
            except Exception as e2:
                print(f"Failed to save GIF animation: {e2}")
        finally:
            plt.close(fig)
