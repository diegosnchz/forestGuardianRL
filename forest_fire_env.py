import gymnasium as gym
from gymnasium import spaces
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import ListedColormap
import os
import requests
from typing import Tuple, Dict, Optional

class ForestFireEnv(gym.Env):
    """
    Entorno de incendios forestales mejorado con física realista.
    
    Mejoras v2.0:
    - Sistema de viento (dirección y velocidad) que afecta propagación
    - Integración con API de clima real
    - Tercer agente con estrategia de cortafuegos
    - Sistema de elevación del terreno
    - Compatibilidad estricta con Gymnasium para PPO
    """
    metadata = {'render_modes': ['human', 'rgb_array']}
    
    def __init__(
        self, 
        grid_size=10, 
        fire_spread_prob=0.1, 
        initial_trees=0.6, 
        initial_fires=3, 
        num_agents=3,  # CAMBIO: ahora 3 por defecto
        use_real_weather=False,
        location_lat=None,
        location_lon=None,
        api_key=None
    ):
        super(ForestFireEnv, self).__init__()
        
        # Parámetros básicos
        self.grid_size = grid_size
        self.base_fire_spread_prob = fire_spread_prob
        self.initial_trees = initial_trees
        self.initial_fires = initial_fires
        self.num_agents = num_agents
        
        # Sistema de clima real
        self.use_real_weather = use_real_weather
        self.location_lat = location_lat
        self.location_lon = location_lon
        self.api_key = api_key
        
        # Parámetros de viento (dirección en grados, velocidad en km/h)
        self.wind_direction = 0.0  # 0° = Norte, 90° = Este, 180° = Sur, 270° = Oeste
        self.wind_speed = 5.0      # km/h
        
        # Agua infinita
        self.water_tanks = [999] * num_agents
        self.max_water = 999
        self.river_row = 0
        
        # Espacios de acción y observación
        # Acciones: 0=Arriba, 1=Abajo, 2=Izq, 3=Der, 4=Idle, 5=Apagar, 6=Cortafuegos
        self.action_space = spaces.Discrete(7)
        
        # Observación: Grid + Viento + Elevación
        # Grid: (grid_size, grid_size) con valores 0-5
        # Viento: [dirección_normalizada, velocidad_normalizada]
        # Elevación: (grid_size, grid_size) con valores 0-1
        self.observation_space = spaces.Dict({
            'grid': spaces.Box(low=0, high=5, shape=(grid_size, grid_size), dtype=np.int32),
            'wind': spaces.Box(low=0.0, high=1.0, shape=(2,), dtype=np.float32),
            'elevation': spaces.Box(low=0.0, high=1.0, shape=(grid_size, grid_size), dtype=np.float32)
        })
        
        # Estado del entorno
        self.grid = None
        self.elevation = None  # Mapa de elevación (0-1)
        self.agent_positions = []
        self.steps_count = 0
    
    def _fetch_real_weather(self) -> Dict:
        """
        Obtiene datos de clima real usando OpenWeatherMap API.
        
        Returns:
            Diccionario con wind_speed (km/h) y wind_direction (grados)
        """
        if not self.use_real_weather or not self.api_key:
            return {'wind_speed': 5.0, 'wind_direction': 0.0}
        
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': self.location_lat or 0,
                'lon': self.location_lon or 0,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                wind_speed = data.get('wind', {}).get('speed', 5.0) * 3.6  # m/s a km/h
                wind_direction = data.get('wind', {}).get('deg', 0.0)
                
                print(f"✓ Clima real obtenido: Viento {wind_speed:.1f} km/h desde {wind_direction:.0f}°")
                return {
                    'wind_speed': wind_speed,
                    'wind_direction': wind_direction
                }
        except Exception as e:
            print(f"⚠ No se pudo obtener clima real: {e}")
        
        # Fallback a valores por defecto
        return {'wind_speed': 5.0, 'wind_direction': 0.0}
    
    def _generate_elevation_map(self) -> np.ndarray:
        """
        Genera un mapa de elevación del terreno usando ruido Perlin simplificado.
        
        Returns:
            Array (grid_size, grid_size) con valores 0-1
        """
        # Generar elevación usando interpolación bilineal con puntos aleatorios
        elevation = np.zeros((self.grid_size, self.grid_size))
        
        # Crear puntos de control aleatorios
        n_points = 5
        control_points = []
        for _ in range(n_points):
            x = self.np_random.integers(0, self.grid_size)
            y = self.np_random.integers(0, self.grid_size)
            height = self.np_random.random()
            control_points.append((x, y, height))
        
        # Interpolación con distancia inversa ponderada
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                total_weight = 0
                weighted_sum = 0
                
                for px, py, h in control_points:
                    distance = np.sqrt((i - px)**2 + (j - py)**2) + 0.1
                    weight = 1 / distance**2
                    weighted_sum += weight * h
                    total_weight += weight
                
                elevation[i, j] = weighted_sum / total_weight
        
        # Normalizar a rango 0-1
        elevation = (elevation - elevation.min()) / (elevation.max() - elevation.min() + 1e-6)
        
        return elevation.astype(np.float32)
    
    def _calculate_fire_spread_probability(
        self, 
        from_pos: Tuple[int, int], 
        to_pos: Tuple[int, int]
    ) -> float:
        """
        Calcula la probabilidad de propagación del fuego considerando viento y elevación.
        
        Args:
            from_pos: Posición origen del fuego (row, col)
            to_pos: Posición destino (row, col)
        
        Returns:
            Probabilidad ajustada (0-1)
        """
        base_prob = self.base_fire_spread_prob
        
        # 1. Factor de viento vectorial
        # Calcular dirección del movimiento del fuego
        dr = to_pos[0] - from_pos[0]  # Positivo = Sur
        dc = to_pos[1] - from_pos[1]  # Positivo = Este
        
        # Convertir a ángulo (0° = Norte, sentido horario)
        fire_direction = np.degrees(np.arctan2(dc, -dr)) % 360
        
        # Diferencia angular entre dirección del viento y dirección del fuego
        angle_diff = abs(fire_direction - self.wind_direction)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        
        # Factor de viento: máximo cuando fuego va en dirección del viento
        wind_factor = 1.0 + (self.wind_speed / 20.0) * (1 - angle_diff / 180.0)
        wind_factor = np.clip(wind_factor, 0.5, 3.0)
        
        # 2. Factor de elevación
        # Fuego sube más fácilmente cuesta arriba
        elev_from = self.elevation[from_pos[0], from_pos[1]]
        elev_to = self.elevation[to_pos[0], to_pos[1]]
        elev_diff = elev_to - elev_from
        
        if elev_diff > 0:  # Cuesta arriba
            elevation_factor = 1.0 + elev_diff * 2.0
        else:  # Cuesta abajo
            elevation_factor = 1.0 + elev_diff * 0.5
        
        elevation_factor = np.clip(elevation_factor, 0.3, 2.0)
        
        # Probabilidad final
        final_prob = base_prob * wind_factor * elevation_factor
        return np.clip(final_prob, 0.0, 1.0)
        
    def reset(self, seed=None, options=None):
        """Reset del entorno con nuevas características."""
        super().reset(seed=seed)
        
        self.steps_count = 0
        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=np.int32)
        
        # Generar mapa de elevación
        self.elevation = self._generate_elevation_map()
        
        # Obtener clima real o generar aleatorio
        if self.use_real_weather:
            weather = self._fetch_real_weather()
            self.wind_speed = weather['wind_speed']
            self.wind_direction = weather['wind_direction']
        else:
            # Viento aleatorio
            self.wind_speed = self.np_random.uniform(0, 20)  # 0-20 km/h
            self.wind_direction = self.np_random.uniform(0, 360)  # 0-360 grados
        
        # 1. Generar Árboles (evitando zonas muy elevadas)
        tree_mask = self.np_random.random((self.grid_size, self.grid_size)) < self.initial_trees
        # Reducir árboles en zonas altas (terreno rocoso)
        high_elevation_mask = self.elevation > 0.8
        tree_mask[high_elevation_mask] = False
        self.grid[tree_mask] = 1
        
        # 2. Colocar Agentes (separados)
        self.agent_positions = []
        attempts = 0
        while len(self.agent_positions) < self.num_agents and attempts < 100:
            r = self.np_random.integers(0, self.grid_size)
            c = self.np_random.integers(0, self.grid_size)
            
            if (r, c) not in self.agent_positions:
                self.agent_positions.append((r, c))
            attempts += 1
        
        # Rellenar con posiciones por defecto si no se pudo colocar todos
        while len(self.agent_positions) < self.num_agents:
            self.agent_positions.append((0, len(self.agent_positions)))
            
        # 3. Colocar Fuegos
        fires_placed = 0
        attempts = 0
        while fires_placed < self.initial_fires and attempts < 200:
            r = self.np_random.integers(1, self.grid_size - 1)
            c = self.np_random.integers(1, self.grid_size - 1)
            
            if self.grid[r, c] == 1 and (r, c) not in self.agent_positions:
                self.grid[r, c] = 2
                fires_placed += 1
            attempts += 1
            
        return self._get_obs(), {}
    
    def _get_obs(self) -> Dict:
        """
        Obtiene la observación completa del entorno.
        
        Returns:
            Diccionario con grid, wind y elevation
        """
        obs_grid = self.grid.copy()
        
        # Marcar posiciones de agentes en el grid
        for i, pos in enumerate(self.agent_positions):
            if 0 <= pos[0] < self.grid_size and 0 <= pos[1] < self.grid_size:
                # Agente 1: 3, Agente 2: 4, Agente 3: 5
                obs_grid[pos[0], pos[1]] = 3 + i
        
        # Normalizar viento para observación
        wind_obs = np.array([
            self.wind_direction / 360.0,  # Normalizar 0-1
            self.wind_speed / 50.0        # Normalizar 0-1 (asumiendo max 50 km/h)
        ], dtype=np.float32)
        
        return {
            'grid': obs_grid,
            'wind': wind_obs,
            'elevation': self.elevation
        }
    
    def step(self, actions):
        """
        Ejecuta un paso de simulación con acciones mejoradas.
        
        Acciones:
        0: Arriba, 1: Abajo, 2: Izquierda, 3: Derecha
        4: Idle (no hacer nada)
        5: Apagar fuego (radio 3x3)
        6: Cortafuegos - NUEVO (elimina árboles para crear barrera)
        
        Args:
            actions: Lista de acciones para cada agente
        
        Returns:
            observation, reward, terminated, truncated, info
        """
        if not isinstance(actions, (list, np.ndarray)):
            actions = [actions]
        
        self.steps_count += 1
        terminated = False
        truncated = False
        reward = 0
        
        # 1. EJECUTAR ACCIONES DE LOS AGENTES
        for i, action in enumerate(actions[:self.num_agents]):
            r, c = self.agent_positions[i]
            old_r, old_c = r, c
            
            # Movimiento propuesto
            if action == 0:    # Arriba
                r = max(0, r - 1)
            elif action == 1:  # Abajo
                r = min(self.grid_size - 1, r + 1)
            elif action == 2:  # Izquierda
                c = max(0, c - 1)
            elif action == 3:  # Derecha
                c = min(self.grid_size - 1, c + 1)
            elif action == 4:  # Idle
                pass
            
            # FÍSICA DE COLISIONES - Verificar si hay otro agente
            collision = False
            for j, other_pos in enumerate(self.agent_positions):
                if i != j and (r, c) == other_pos:
                    collision = True
                    break
            
            if collision:
                # No mover si hay colisión
                r, c = old_r, old_c
            
            # Actualizar posición
            self.agent_positions[i] = (r, c)
            
            # ACCIÓN 5: APAGAR FUEGO (Radio 3x3)
            if action == 5:
                fires_extinguished = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                            if self.grid[nr, nc] == 2:
                                self.grid[nr, nc] = 0  # Apagar fuego
                                fires_extinguished += 1
                                reward += 10  # Recompensa por apagar fuego
            
            # ACCIÓN 6: CORTAFUEGOS (NUEVO - UNIDAD GAMMA)
            # Elimina árboles sanos para crear barrera contra el fuego
            if action == 6:
                trees_removed = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                            if self.grid[nr, nc] == 1:  # Si hay árbol sano
                                self.grid[nr, nc] = 0  # Eliminar árbol
                                trees_removed += 1
                                reward -= 1  # Penalización menor por sacrificar árboles
        
        # 2. PROPAGACIÓN DEL FUEGO CON FÍSICA MEJORADA
        new_fires = []
        fire_positions = np.argwhere(self.grid == 2)
        
        for fr, fc in fire_positions:
            # Vecinos en 4 direcciones
            neighbors = [
                (fr - 1, fc),  # Norte
                (fr + 1, fc),  # Sur
                (fr, fc - 1),  # Oeste
                (fr, fc + 1)   # Este
            ]
            
            for nr, nc in neighbors:
                if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                    if self.grid[nr, nc] == 1:  # Si hay árbol
                        # Calcular probabilidad con viento y elevación
                        spread_prob = self._calculate_fire_spread_probability(
                            (fr, fc), (nr, nc)
                        )
                        
                        if self.np_random.random() < spread_prob:
                            new_fires.append((nr, nc))
                            reward -= 5  # Penalización por propagación
        
        # Aplicar nuevos fuegos
        for nf_r, nf_c in new_fires:
            self.grid[nf_r, nf_c] = 2
        
        # 3. CONDICIONES DE TERMINACIÓN
        active_fires = np.sum(self.grid == 2)
        
        if active_fires == 0:
            terminated = True
            reward += 100  # Gran recompensa por extinguir todos los fuegos
        
        # Recompensa por árboles salvados
        trees_remaining = np.sum(self.grid == 1)
        reward += trees_remaining * 0.1
        
        # Info adicional
        info = {
            'active_fires': int(active_fires),
            'trees_remaining': int(trees_remaining),
            'wind_speed': float(self.wind_speed),
            'wind_direction': float(self.wind_direction),
            'steps': self.steps_count
        }
            
        return self._get_obs(), reward, terminated, truncated, info

    def render_animation(self, frames, filename='simulation.gif', fps=5):
        """
        Genera animación GIF de la simulación.
        Ahora con soporte para 3 agentes (azul, naranja, púrpura).
        """
        # Crear carpeta GIF en directorio actual
        base_dir = "GIF"
        
        if not os.path.exists(base_dir):
            try:
                os.makedirs(base_dir)
            except:
                base_dir = "." 
        
        full_path = os.path.join(base_dir, filename)
        
        print(f"   --> Generando GIF en: {full_path} ...")
        
        fig, ax = plt.subplots(figsize=(6, 6))
        
        # Colormap actualizado: 0=blanco, 1=verde, 2=rojo, 3=azul, 4=naranja, 5=púrpura
        cmap = ListedColormap(['white', 'green', 'red', 'blue', 'orange', 'purple'])
        
        # Extraer solo el grid si frames tiene observaciones complejas
        if isinstance(frames[0], dict):
            grid_frames = [f['grid'] for f in frames]
        else:
            grid_frames = frames
        
        im = ax.imshow(grid_frames[0], cmap=cmap, vmin=0, vmax=5)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title("Forest Guardian RL v2.0 - Multi-Agent")
        
        # Leyenda
        legend_elements = [
            plt.Rectangle((0, 0), 1, 1, fc='green', label='Árbol'),
            plt.Rectangle((0, 0), 1, 1, fc='red', label='Fuego'),
            plt.Rectangle((0, 0), 1, 1, fc='blue', label='Dron ALPHA'),
            plt.Rectangle((0, 0), 1, 1, fc='orange', label='Dron BRAVO'),
            plt.Rectangle((0, 0), 1, 1, fc='purple', label='Dron GAMMA')
        ]
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
        
        def update(i):
            im.set_data(grid_frames[i])
            ax.set_title(f"Forest Guardian RL v2.0 - Paso {i}")
            return im,
            
        anim = FuncAnimation(fig, update, frames=len(grid_frames), interval=200, blit=True)
        
        try:
            writer = PillowWriter(fps=fps)
            anim.save(full_path, writer=writer)
            print(f"   --> ¡GIF GUARDADO EXITOSAMENTE!")
        except Exception as e:
            print(f"ERROR GUARDANDO GIF: {e}")
        finally:
            plt.close()
    
    def get_wind_info(self) -> Dict:
        """
        Retorna información del viento actual.
        
        Returns:
            Diccionario con speed (km/h) y direction (grados)
        """
        return {
            'speed': self.wind_speed,
            'direction': self.wind_direction,
            'direction_name': self._wind_direction_name()
        }
    
    def _wind_direction_name(self) -> str:
        """Convierte grados a nombre de dirección cardinal."""
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        idx = int((self.wind_direction + 22.5) / 45) % 8
        return directions[idx]
    
    def get_elevation_at(self, row: int, col: int) -> float:
        """Obtiene la elevación en una posición específica."""
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            return float(self.elevation[row, col])
        return 0.0