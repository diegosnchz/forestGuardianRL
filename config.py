"""
Módulo de configuración para Forest Guardian RL
Define constantes y configuraciones globales para la aplicación
"""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class EnvironmentConfig:
    """Configuración del entorno ForestFireEnv"""
    grid_size: int = 10
    fire_spread_prob: float = 0.1
    initial_trees: float = 0.6
    initial_fires: int = 3
    num_agents: int = 2
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return {
            'grid_size': self.grid_size,
            'fire_spread_prob': self.fire_spread_prob,
            'initial_trees': self.initial_trees,
            'initial_fires': self.initial_fires,
            'num_agents': self.num_agents
        }

# Configuración predeterminada
DEFAULT_CONFIG = EnvironmentConfig()

# Rangos válidos para validación
CONFIG_RANGES = {
    'grid_size': (8, 15),
    'fire_spread_prob': (0.0, 0.5),
    'initial_trees': (0.3, 0.9),
    'initial_fires': (1, 5),
    'num_agents': (1, 3),
    'max_steps': (50, 200)
}

# Configuraciones predefinidas para demos rápidas
DEMO_CONFIGS = {
    'facil': EnvironmentConfig(
        grid_size=10,
        fire_spread_prob=0.05,
        initial_trees=0.8,
        initial_fires=2,
        num_agents=2
    ),
    'normal': EnvironmentConfig(
        grid_size=10,
        fire_spread_prob=0.1,
        initial_trees=0.6,
        initial_fires=3,
        num_agents=2
    ),
    'dificil': EnvironmentConfig(
        grid_size=12,
        fire_spread_prob=0.2,
        initial_trees=0.5,
        initial_fires=4,
        num_agents=2
    ),
    'extremo': EnvironmentConfig(
        grid_size=15,
        fire_spread_prob=0.3,
        initial_trees=0.4,
        initial_fires=5,
        num_agents=3
    )
}

# Textos y descripción
APP_TITLE = "Forest Guardian RL - Centro de Control de Misión"
APP_DESCRIPTION = """
Sistema Autónomo de Control de Incendios Forestales

Visualiza en tiempo real cómo los drones equipados con IA contienen incendios forestales
usando estrategias de búsqueda y fuego coordinadas.
"""

AGENT_DESCRIPTIONS = {
    1: "Dron Azul (ALPHA) - Búsqueda de Proximidad",
    2: "Dron Naranja (BRAVO) - Contención Periférica",
    3: "Dron Púrpura (CHARLIE) - Apoyo Estratégico"
}

CELL_DESCRIPTIONS = {
    0: "Celda vacía",
    1: "Árbol / Vegetación",
    2: "Fuego activo",
    3: "Dron 1 (Azul)",
    4: "Dron 2 (Naranja)"
}

# Themas de colores
COLORS = {
    'empty': '#ffffff',
    'tree': '#00aa00',
    'fire': '#ff0000',
    'agent1': '#0066ff',
    'agent2': '#ff9900',
    'agent3': '#9966ff',
    'primary': '#667eea',
    'success': '#00aa00',
    'danger': '#ff0000',
    'warning': '#ffaa00',
    'info': '#0066ff'
}

# Mensajes de estado
MISSION_MESSAGES = {
    'idle': "👈 Ajusta los parámetros en el panel izquierdo y presiona '🚀 Iniciar Misión' para comenzar",
    'running': "🚀 Misión iniciada - Drones desplegados",
    'success': "✅ Misión completada - Todos los fuegos extinguidos",
    'timeout': "⏱️ Misión completada por tiempo máximo",
    'failed': "❌ Misión fallida - Propagación no contenida"
}
