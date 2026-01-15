import gymnasium as gym
from gymnasium import spaces
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import ListedColormap
import os

class ForestFireEnv(gym.Env):
    metadata = {'render_modes': ['human', 'rgb_array']}
    
    def __init__(self, grid_size=10, fire_spread_prob=0.1, initial_trees=0.6, initial_fires=2, num_agents=2):
        super(ForestFireEnv, self).__init__()
        
        # GRID 10x10
        self.grid_size = 10 
        self.fire_spread_prob = 0.1
        self.initial_trees = initial_trees
        self.initial_fires = initial_fires
        self.num_agents = num_agents
        
        # AGUA INFINITA
        self.water_tanks = [999] * num_agents
        self.max_water = 999
        self.river_row = 0
        
        self.action_space = spaces.Discrete(7)
        self.observation_space = spaces.Box(low=0, high=4, shape=(grid_size, grid_size), dtype=np.int32)
        
        self.grid = None
        self.agent_positions = []
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=np.int32)
        
        # Árboles
        tree_mask = self.np_random.random((self.grid_size, self.grid_size)) < self.initial_trees
        self.grid[tree_mask] = 1
        
        # AGENTES EN ESQUINAS OPUESTAS
        self.agent_positions = [(0, 0), (self.grid_size-1, self.grid_size-1)]
        
        # FUEGO MASIVO EN EL CENTRO (3x3)
        # Esto asegura que tengan algo que apagar sí o sí
        center = self.grid_size // 2
        for r in range(center-1, center+2):
            for c in range(center-1, center+2):
                if 0 <= r < self.grid_size and 0 <= c < self.grid_size:
                    self.grid[r,c] = 2
            
        return self._get_obs(), {}
    
    def _get_obs(self):
        obs = self.grid.copy()
        for i, pos in enumerate(self.agent_positions):
            val = 3 if i == 0 else 4
            if 0 <= pos[0] < self.grid_size and 0 <= pos[1] < self.grid_size:
                 obs[pos] = val
        return obs
    
    def step(self, actions):
        if not isinstance(actions, list) and not isinstance(actions, np.ndarray):
            actions = [actions]
        
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
            
            # Acción 5: APAGAR (Radio 3x3)
            if action == 5:
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r+dr, c+dc
                        if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                            if self.grid[nr,nc] == 2:
                                self.grid[nr,nc] = 0 # Fuego apagado
        
        # 2. Expansión Fuego (Muy lenta)
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
            
        if np.sum(self.grid == 2) == 0: terminated = True
            
        return self._get_obs(), 0, terminated, truncated, {}

    def render_animation(self, frames, filename='simulation.gif', fps=5):
        # RUTA ESPECÍFICA DEL USUARIO
        base_dir = r"C:\Users\diego\Downloads\forestGuardianRL\GIF"
        
        # Crear carpeta si no existe
        if not os.path.exists(base_dir):
            try:
                os.makedirs(base_dir)
            except:
                base_dir = "." # Fallback si falla la ruta
        
        full_path = os.path.join(base_dir, filename)
        
        print(f"   --> Generando GIF en: {full_path} ...")
        
        fig, ax = plt.subplots(figsize=(5, 5))
        # Blanco, Verde, Rojo, Azul, Naranja
        cmap = ListedColormap(['white', 'green', 'red', 'blue', 'orange'])
        
        im = ax.imshow(frames[0], cmap=cmap, vmin=0, vmax=4)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title("Forest Guardian Demo")
        
        def update(i):
            im.set_data(frames[i])
            return im,
            
        anim = FuncAnimation(fig, update, frames=len(frames), interval=200, blit=True)
        try:
            writer = PillowWriter(fps=fps)
            anim.save(full_path, writer=writer)
            print(f"   --> ¡GIF GUARDADO EXITOSAMENTE!")
            print(f"   --> Ruta: {full_path}")
        except Exception as e:
            print(f"ERROR GUARDANDO GIF: {e}")
        finally:
            plt.close()