"""
Módulo GIS para Forest Guardian RL
Extiende ForestFireEnv con soporte de mapas geográficos reales
"""

import numpy as np
from forest_fire_env import ForestFireEnv
from gis_locations import BosqueReal, grid_a_coordenadas, coordenadas_a_grid
from typing import List, Tuple, Dict
import math

class ForestFireGISEnv(ForestFireEnv):
    """
    Extensión de ForestFireEnv con soporte para ubicaciones geográficas reales
    Mapea el grid 10x10 a coordenadas geográficas usando Haversine
    """
    
    def __init__(
        self,
        bosque: BosqueReal,
        grid_size: int = 10,
        fire_spread_prob: float = 0.1,
        initial_trees: float = 0.6,
        initial_fires: int = 3,
        num_agents: int = 2
    ):
        """
        Inicializa entorno GIS
        
        Args:
            bosque: Objeto BosqueReal con ubicación
            grid_size: Tamaño del grid (hereda de ForestFireEnv)
            fire_spread_prob: Probabilidad de propagación
            initial_trees: Densidad inicial de árboles
            initial_fires: Número de fuegos iniciales
            num_agents: Número de drones
        """
        # Inicializar clase padre
        super().__init__(
            grid_size=grid_size,
            fire_spread_prob=fire_spread_prob,
            initial_trees=initial_trees,
            initial_fires=initial_fires,
            num_agents=num_agents
        )
        
        # Guardar información geográfica
        self.bosque = bosque
        self.km_por_celda = 0.5  # Cada celda = 0.5 km
        
        # Precalcular factores de conversión
        self._calculate_conversion_factors()
        
        # Histórico de posiciones geográficas
        self.agent_geo_positions = []
        self.fire_locations_geo = []
    
    def _calculate_conversion_factors(self):
        """Calcula los factores para convertir entre grid y coordenadas geográficas"""
        # Grados de latitud por km (constante)
        self.grados_latitud_por_km = 1 / 111.0
        
        # Grados de latitud por celda
        self.grados_latitud_por_celda = self.grados_latitud_por_km * self.km_por_celda
        
        # Ajuste para longitud según latitud
        cos_lat = math.cos(math.radians(self.bosque.latitud))
        self.grados_longitud_por_celda = (
            self.grados_latitud_por_celda / cos_lat 
            if cos_lat != 0 
            else self.grados_latitud_por_celda
        )
    
    def grid_to_geo(self, grid_row: int, grid_col: int) -> Tuple[float, float]:
        """Convierte coordenadas grid a geográficas"""
        offset_fila = grid_row - (self.grid_size / 2)
        offset_col = grid_col - (self.grid_size / 2)
        
        lat = self.bosque.latitud - (offset_fila * self.grados_latitud_por_celda)
        lon = self.bosque.longitud + (offset_col * self.grados_longitud_por_celda)
        
        return lat, lon
    
    def geo_to_grid(self, latitud: float, longitud: float) -> Tuple[int, int]:
        """Convierte coordenadas geográficas a grid"""
        offset_lat = self.bosque.latitud - latitud
        offset_lon = longitud - self.bosque.longitud
        
        row = int((self.grid_size / 2) + (offset_lat / self.grados_latitud_por_celda))
        col = int((self.grid_size / 2) + (offset_lon / self.grados_longitud_por_celda))
        
        # Limitar a límites del grid
        row = max(0, min(row, self.grid_size - 1))
        col = max(0, min(col, self.grid_size - 1))
        
        return row, col
    
    def get_agent_geo_positions(self) -> List[Tuple[float, float]]:
        """Retorna posiciones geográficas de los agentes"""
        return [self.grid_to_geo(pos[0], pos[1]) for pos in self.agent_positions]
    
    def get_fires_geo_positions(self) -> List[Tuple[float, float]]:
        """Retorna posiciones geográficas de los fuegos"""
        fires = np.argwhere(self.grid == 2)
        return [self.grid_to_geo(f[0], f[1]) for f in fires]
    
    def get_trees_geo_positions(self) -> List[Tuple[float, float]]:
        """Retorna posiciones geográficas de los árboles"""
        trees = np.argwhere(self.grid == 1)
        return [self.grid_to_geo(t[0], t[1]) for t in trees]
    
    def get_grid_bounds(self) -> Dict[str, float]:
        """Retorna los límites geográficos del grid"""
        # Coordenadas de las esquinas del grid
        top_left = self.grid_to_geo(0, 0)
        top_right = self.grid_to_geo(0, self.grid_size - 1)
        bottom_left = self.grid_to_geo(self.grid_size - 1, 0)
        bottom_right = self.grid_to_geo(self.grid_size - 1, self.grid_size - 1)
        
        return {
            'north': max(top_left[0], top_right[0]),
            'south': min(bottom_left[0], bottom_right[0]),
            'east': max(top_right[1], bottom_right[1]),
            'west': min(top_left[1], bottom_left[1]),
            'center_lat': self.bosque.latitud,
            'center_lon': self.bosque.longitud
        }
    
    def get_grid_center(self) -> Tuple[float, float]:
        """Retorna el centro geográfico del grid"""
        return self.bosque.latitud, self.bosque.longitud
    
    def get_coverage_area_km2(self) -> float:
        """Calcula el área cubierta por el grid en km²"""
        # Grid size x size, cada celda = km_por_celda²
        return (self.grid_size * self.km_por_celda) ** 2
    
    def get_heatmap_data(self) -> List[Tuple[float, float, float]]:
        """
        Retorna datos para heatmap: [(lat, lon, intensity), ...]
        La intensidad es 1.0 para fuego, 0.0 para vacío
        """
        heatmap_data = []
        
        # Fuegos con intensidad máxima
        for fire_lat, fire_lon in self.get_fires_geo_positions():
            heatmap_data.append((fire_lat, fire_lon, 1.0))
        
        # Árboles salvados con intensidad baja-media
        for tree_lat, tree_lon in self.get_trees_geo_positions():
            heatmap_data.append((tree_lat, tree_lon, 0.3))
        
        return heatmap_data
    
    def get_mission_summary(self) -> Dict:
        """Retorna resumen de la misión con datos geográficos"""
        bounds = self.get_grid_bounds()
        
        return {
            'bosque': self.bosque.nombre,
            'pais': self.bosque.pais,
            'area_simulada_km2': self.get_coverage_area_km2(),
            'area_total_bosque_km2': self.bosque.area_km2,
            'coordenada_central': self.get_grid_center(),
            'limites_grid': bounds,
            'agentes_geo': self.get_agent_geo_positions(),
            'fuegos_geo': self.get_fires_geo_positions(),
            'arboles_geo': self.get_trees_geo_positions(),
            'densidad_bosque': self.bosque.densidad,
            'amenazas': self.bosque.amenazas
        }
