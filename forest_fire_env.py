import gymnasium as gym
from gymnasium import spaces
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import ListedColormap

class ForestFireEnv(gym.Env):
    metadata = {'render_modes': ['human', 'rgb_array']}
    
    def __init__(self, grid_size=20, fire_spread_prob=0.1, initial_trees=0.5, initial_fires=3, num_agents=1):
        super(ForestFireEnv, self).__init__()
        
        self.grid_size = grid_size
        self.fire_spread_prob = 0.1  # Fuego lento (10%)
        self.initial_trees = initial_trees
        self.initial_fires = initial_fires
        self.num_agents = num_agents
        
        self.water_tanks = [10] * num_agents
        self.max_water = 10
        self.river_row = 0
        
        self.action_space = spaces.Discrete(7)
        self.observation_space = spaces.Box(
            low=0, high=4, shape=(grid_size, grid_size), dtype=np.int32
        )
        
        self.grid = None
        self.agent_positions = []
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=np.int32)
        
        tree_mask = self.np_random.random((self.grid_size, self.grid_size)) < self.initial_trees
        self.grid[tree_mask] = 1
        self.grid[self.river_row, :] = 0 
        
        # Posicionar agentes (esquinas opuestas)
        if self.num_agents == 1:
            self.agent_positions = [(self.grid_size//2, self.grid_size//2)]
        else:
            self.agent_positions = [(0, 0), (self.grid_size-1, self.grid_size-1)]
            
        # Posicionar fuego
        valid_fires = []
        attempts = 0
        while len(valid_fires) < self.initial_fires and attempts < 100:
            r, c = self.np_random.integers(1, self.grid_size, size=2)
            if self.grid[r,c] == 1 and (r,c) not in self.agent_positions:
                self.grid[r,c] = 2
                valid_fires.append((r,c))
            attempts += 1
            
        self.water_tanks = [self.max_water] * self.num_agents
        return self._get_obs(), {}
    
    def _get_obs(self):
        obs = self.grid.copy()
        for i, pos in enumerate(self.agent_positions):
            val = 3 if i == 0 else 4 # 3=Azul, 4=Naranja
            obs[pos] = val
        return obs
    
    def step(self, actions):
        if not isinstance(actions, list) and not isinstance(actions, np.ndarray):
            actions = [actions]
        
        if len(actions) < self.num_agents:
            actions = actions * self.num_agents 
            
        total_reward = 0
        terminated = False
        truncated = False
        
        # 1. Acciones Agentes
        for i, action in enumerate(actions):
            r, c = self.agent_positions[i]
            
            # Movimiento
            if action == 0: r = max(0, r-1)
            elif action == 1: r = min(self.grid_size-1, r+1)
            elif action == 2: c = max(0, c-1)
            elif action == 3: c = min(self.grid_size-1, c+1)
            
            self.agent_positions[i] = (r, c)
            
            # Talar
            if action == 4:
                if self.grid[r,c] == 1: 
                    self.grid[r,c] = 0
                    total_reward += 0.5
            
            # Apagar
            elif action == 5:
                if self.water_tanks[i] > 0:
                    extinguished = False
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            nr, nc = r+dr, c+dc
                            if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                                if self.grid[nr,nc] == 2:
                                    self.grid[nr,nc] = 0
                                    extinguished = True
                    if extinguished:
                        self.water_tanks[i] -= 1
                        total_reward += 5.0
            
            # Recargar
            elif action == 6:
                if r == self.river_row:
                    self.water_tanks[i] = self.max_water
        
        # 2. Expansión Fuego
        new_fires = []
        fire_positions = np.argwhere(self.grid == 2)
        
        for fr, fc in fire_positions:
            neighbors = [(fr-1,fc), (fr+1,fc), (fr,fc-1), (fr,fc+1)]
            for nr, nc in neighbors:
                if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                    if self.grid[nr,nc] == 1:
                        if self.np_random.random() < self.fire_spread_prob:
                            new_fires.append((nr,nc))
        
        for nf in new_fires:
            self.grid[nf] = 2
            
        # Recompensas
        active_fires = np.sum(self.grid == 2)
        trees_left = np.sum(self.grid == 1)
        
        total_reward -= (active_fires * 0.1)
        
        if active_fires == 0:
            total_reward += 50
            terminated = True
        elif trees_left == 0:
            total_reward -= 50
            terminated = True
            
        return self._get_obs(), total_reward, terminated, truncated, {}

    def render_animation(self, frames, filename='simulation.gif', fps=5):
        print(f"   --> Procesando GIF '{filename}' con {len(frames)} frames...")
        try:
            fig, ax = plt.subplots(figsize=(6, 6))
            # Mapa de colores: 0=Blanco, 1=Verde, 2=Rojo, 3=Azul, 4=Naranja
            cmap = ListedColormap(['white', 'green', 'red', 'blue', 'orange'])
            
            im = ax.imshow(frames[0], cmap=cmap, vmin=0, vmax=4)
            ax.set_xticks([]); ax.set_yticks([])
            title = ax.set_title("Inicio")
            
            def update(i):
                im.set_data(frames[i])
                title.set_text(f"Paso {i}")
                return im, title
                
            anim = FuncAnimation(fig, update, frames=len(frames), interval=200, blit=False)
            
            # Usamos PillowWriter explícitamente
            writer = PillowWriter(fps=fps)
            anim.save(filename, writer=writer)
            plt.close()
            print(f"   --> ¡ÉXITO! GIF guardado en: {filename}")
        except Exception as e:
            print(f"   --> ERROR generando GIF: {e}")