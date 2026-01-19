"""
Módulo GIS - Ubicaciones de bosques reales para Forest Guardian RL
Proporciona datos geográficos y coordenadas de bosques reales del mundo
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict
import math

@dataclass
class BosqueReal:
    """Representa un bosque real con coordenadas geográficas"""
    nombre: str
    pais: str
    latitud: float
    longitud: float
    area_km2: float
    densidad: str  # baja, media, alta
    amenazas: List[str]  # tipos de amenazas comunes
    descripcion: str
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario"""
        return {
            'nombre': self.nombre,
            'pais': self.pais,
            'latitud': self.latitud,
            'longitud': self.longitud,
            'area_km2': self.area_km2,
            'densidad': self.densidad,
            'amenazas': self.amenazas,
            'descripcion': self.descripcion
        }

# ============================================================================
# BOSQUES REALES DEL MUNDO
# ============================================================================

BOSQUES_REALES = [
    # AMÉRICA LATINA
    BosqueReal(
        nombre="Amazonas - Perú",
        pais="Perú",
        latitud=-3.4653,
        longitud=-62.2159,
        area_km2=780000,
        densidad="alta",
        amenazas=["sequía", "deforestación", "incendios"],
        descripcion="La región más densa de la selva amazónica peruana con altísima biodiversidad"
    ),
    
    BosqueReal(
        nombre="Pantanal",
        pais="Brasil",
        latitud=-17.8383,
        longitud=-57.0227,
        area_km2=150000,
        densidad="media",
        amenazas=["incendios", "drenaje", "sequía"],
        descripcion="Humedal tropical más grande del mundo con bosques pantanosos"
    ),
    
    BosqueReal(
        nombre="Bosque Atlántico",
        pais="Brasil",
        latitud=-25.2637,
        longitud=-48.6192,
        area_km2=12000,
        densidad="alta",
        amenazas=["fragmentación", "incendios", "urbanización"],
        descripcion="Bosque tropical atlántico con fauna endémica única"
    ),
    
    BosqueReal(
        nombre="Cerro de Pasco",
        pais="Perú",
        latitud=-10.6701,
        longitud=-76.2681,
        area_km2=5000,
        densidad="media",
        amenazas=["minería", "deforestación", "incendios"],
        descripcion="Bosque andino con ecosistemas de transición"
    ),
    
    # AMÉRICA DEL NORTE
    BosqueReal(
        nombre="Bosque Boreal Canadiense",
        pais="Canadá",
        latitud=56.1304,
        longitud=-106.3468,
        area_km2=300000,
        densidad="media",
        amenazas=["cambio climático", "plagas", "incendios"],
        descripcion="Vasto bosque boreal con coníferas y taiga"
    ),
    
    BosqueReal(
        nombre="Sierra Nevada",
        pais="Estados Unidos",
        latitud=37.7694,
        longitud=-119.4179,
        area_km2=20000,
        densidad="media",
        amenazas=["sequía", "incendios", "cambio climático"],
        descripcion="Bosque de coníferas en montañas de California"
    ),
    
    # EUROPA
    BosqueReal(
        nombre="Selva Negra",
        pais="Alemania",
        latitud=48.7758,
        longitud=8.3405,
        area_km2=6000,
        densidad="alta",
        amenazas=["plagas", "sequía", "cambio climático"],
        descripcion="Bosque templado histórico en Baden-Württemberg"
    ),
    
    BosqueReal(
        nombre="Taiga Rusa",
        pais="Rusia",
        latitud=60.0,
        longitud=100.0,
        area_km2=5000000,
        densidad="media",
        amenazas=["incendios", "cambio climático", "plagas"],
        descripcion="Mayor bosque boreal del mundo cubriendo Siberia"
    ),
    
    # ÁFRICA
    BosqueReal(
        nombre="Bosque Congo",
        pais="República Democrática del Congo",
        latitud=-1.0491,
        longitud=24.2155,
        area_km2=2000000,
        densidad="alta",
        amenazas=["deforestación", "incendios", "minería"],
        descripcion="Segundo bosque tropical más grande del mundo"
    ),
    
    BosqueReal(
        nombre="Cercanías Kibale",
        pais="Uganda",
        latitud=0.5544,
        longitud=30.6596,
        area_km2=1300,
        densidad="alta",
        amenazas=["presión demográfica", "incendios", "ganadería"],
        descripcion="Bosque tropical con chimpancés y fauna variada"
    ),
    
    # ASIA
    BosqueReal(
        nombre="Borneo - Sabah",
        pais="Malasia",
        latitud=4.2105,
        longitud=115.2381,
        area_km2=7000,
        densidad="alta",
        amenazas=["deforestación", "incendios", "plantaciones"],
        descripcion="Bosque tropical antiguo con orangutanes"
    ),
    
    BosqueReal(
        nombre="Bosque Tropical Tailandia",
        pais="Tailandia",
        latitud=8.6753,
        longitud=100.9901,
        area_km2=3000,
        densidad="alta",
        amenazas=["deforestación", "incendios", "agricultura"],
        descripcion="Selva tropical con biodiversidad excepcional"
    ),
    
    # OCEANÍA
    BosqueReal(
        nombre="Selva Daintree",
        pais="Australia",
        latitud=-16.2859,
        longitud=145.4293,
        area_km2=1200,
        densidad="alta",
        amenazas=["sequía", "incendios", "cambio climático"],
        descripcion="Una de las selvas tropicales más antiguas del mundo"
    ),
]

# ============================================================================
# ESCENARIOS PREDEFINIDOS
# ============================================================================

ESCENARIOS_REALES = {
    'amazonas_peru': {
        'bosque': BOSQUES_REALES[0],
        'grid_size': 15,
        'fire_spread_prob': 0.15,
        'initial_trees': 0.85,
        'initial_fires': 4,
        'num_agents': 3,
        'description': 'Simulación en selva amazónica densa - Muy desafiante'
    },
    'pantanal': {
        'bosque': BOSQUES_REALES[1],
        'grid_size': 12,
        'fire_spread_prob': 0.2,
        'initial_trees': 0.7,
        'initial_fires': 3,
        'num_agents': 2,
        'description': 'Simulación en humedal tropical - Moderadamente desafiante'
    },
    'sierra_nevada': {
        'bosque': BOSQUES_REALES[5],
        'grid_size': 10,
        'fire_spread_prob': 0.25,
        'initial_trees': 0.65,
        'initial_fires': 3,
        'num_agents': 2,
        'description': 'Simulación en montaña - Condiciones secas'
    },
    'selva_daintree': {
        'bosque': BOSQUES_REALES[12],
        'grid_size': 10,
        'fire_spread_prob': 0.1,
        'initial_trees': 0.9,
        'initial_fires': 2,
        'num_agents': 2,
        'description': 'Simulación en selva antigua australiana - Densa'
    },
    'borneo_sabah': {
        'bosque': BOSQUES_REALES[10],
        'grid_size': 12,
        'fire_spread_prob': 0.18,
        'initial_trees': 0.8,
        'initial_fires': 3,
        'num_agents': 2,
        'description': 'Simulación en bosque tropical de Borneo - Biodiversidad alta'
    },
}

# ============================================================================
# UTILIDADES GEOGRÁFICAS
# ============================================================================

def obtener_bosques_por_pais(pais: str) -> List[BosqueReal]:
    """Obtiene todos los bosques de un país específico"""
    return [b for b in BOSQUES_REALES if b.pais.lower() == pais.lower()]

def obtener_todos_los_paises() -> List[str]:
    """Obtiene lista de todos los países con bosques"""
    return sorted(list(set(b.pais for b in BOSQUES_REALES)))

def calcular_distancia_haversine(
    lat1: float, 
    lon1: float, 
    lat2: float, 
    lon2: float
) -> float:
    """
    Calcula distancia entre dos puntos en km usando fórmula Haversine
    
    Args:
        lat1, lon1: Coordenadas punto 1
        lat2, lon2: Coordenadas punto 2
    
    Returns:
        Distancia en kilómetros
    """
    R = 6371  # Radio de la Tierra en km
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def grid_a_coordenadas(
    bosque: BosqueReal,
    grid_row: int,
    grid_col: int,
    grid_size: int = 10
) -> Tuple[float, float]:
    """
    Convierte coordenadas del grid (0-9) a coordenadas geográficas reales
    
    Args:
        bosque: Objeto BosqueReal con ubicación central
        grid_row: Fila del grid (0-9)
        grid_col: Columna del grid (0-9)
        grid_size: Tamaño del grid (10 por defecto)
    
    Returns:
        Tupla (latitud, longitud)
    """
    # Aproximadamente 1 grado de latitud = 111 km
    # Aproximadamente 1 grado de longitud = 111 * cos(latitud) km
    
    # Área del grid en km (asumiendo ~5km por celda en base a 10x10 = 50km²)
    km_por_celda = 0.5  # Escala: cada celda representa 0.5km
    grados_por_km = 1 / 111.0
    grados_latitud_por_celda = grados_por_km * km_por_celda
    
    # Ajuste para longitud según latitud
    import math
    cos_lat = math.cos(math.radians(bosque.latitud))
    grados_longitud_por_celda = grados_latitud_por_celda / cos_lat if cos_lat != 0 else grados_latitud_por_celda
    
    # Calcular offset desde el centro
    # Centro del grid = (grid_size/2, grid_size/2)
    offset_fila = grid_row - (grid_size / 2)
    offset_col = grid_col - (grid_size / 2)
    
    lat = bosque.latitud - (offset_fila * grados_latitud_por_celda)
    lon = bosque.longitud + (offset_col * grados_longitud_por_celda)
    
    return lat, lon

def coordenadas_a_grid(
    bosque: BosqueReal,
    latitud: float,
    longitud: float,
    grid_size: int = 10
) -> Tuple[int, int]:
    """
    Convierte coordenadas geográficas a coordenadas del grid
    
    Args:
        bosque: Objeto BosqueReal con ubicación central
        latitud: Latitud en grados
        longitud: Longitud en grados
        grid_size: Tamaño del grid
    
    Returns:
        Tupla (row, col) del grid
    """
    km_por_celda = 0.5
    grados_por_km = 1 / 111.0
    grados_latitud_por_celda = grados_por_km * km_por_celda
    
    import math
    cos_lat = math.cos(math.radians(bosque.latitud))
    grados_longitud_por_celda = grados_latitud_por_celda / cos_lat if cos_lat != 0 else grados_latitud_por_celda
    
    # Calcular posición en el grid
    offset_lat = bosque.latitud - latitud
    offset_lon = longitud - bosque.longitud
    
    row = int((grid_size / 2) + (offset_lat / grados_latitud_por_celda))
    col = int((grid_size / 2) + (offset_lon / grados_longitud_por_celda))
    
    # Limitar a límites del grid
    row = max(0, min(row, grid_size - 1))
    col = max(0, min(col, grid_size - 1))
    
    return row, col
