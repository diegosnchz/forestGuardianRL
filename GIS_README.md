# Forest Guardian RL - Sistema de Control Autónomo con GIS

## 🌍 Descripción General

**Forest Guardian RL** es un sistema de control autónomo descentralizado para la contención de incendios forestales mediante drones equipados con inteligencia artificial. La aplicación ahora incluye **integración GIS completa** con mapas interactivos de bosques reales del mundo.

### Características Principales

✅ **Simulación de Incendios Forestales** - Entorno de aprendizaje por refuerzo basado en Gymnasium  
✅ **Múltiples Drones Autónomos** - Hasta 3 drones con estrategias independientes  
✅ **Mapas Interactivos GIS** - Folium con 13 bosques reales del mundo  
✅ **Visualización en Tiempo Real** - Dashboards dinámicos con Streamlit  
✅ **Coordenadas Geográficas Reales** - Transformación de grid a lat/lon  
✅ **Heatmaps de Incendios** - Intensidad de fuegos mapeada geográficamente  

---

## 🚀 Instalación y Configuración

### Requisitos Previos

- Python 3.9+
- pip o conda

### Instalación

```bash
# 1. Clonar/descargar el proyecto
cd forestGuardianRL

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la aplicación
streamlit run app.py
```

### Dependencias Principales

```
gymnasium>=0.29.0          # Entorno RL
stable-baselines3>=2.0.0   # Algoritmos de RL
streamlit>=1.28.0          # Web UI
folium>=0.14.0             # Mapas interactivos
plotly>=5.17.0             # Gráficos
numpy, pandas, matplotlib  # Análisis de datos
```

---

## 📁 Estructura del Proyecto

```
forestGuardianRL/
├── app.py                      # Aplicación Streamlit principal
├── forest_fire_env.py          # Entorno base de simulación
├── forest_fire_gis.py          # Extensión GIS del entorno
├── gis_locations.py            # Base de datos de bosques reales
├── gis_visualization.py        # Generador de mapas Folium
├── train_and_test.py           # Agentes y lógica de aprendizaje
├── requirements.txt            # Dependencias Python
└── README.md                   # Este archivo
```

---

## 🎮 Cómo Usar

### Modo: Grid Aleatorio

1. Abre la aplicación: `streamlit run app.py`
2. En la barra lateral, selecciona **"Grid Aleatorio"**
3. Ajusta los parámetros:
   - **Tamaño del Grid** (8-15): Dimensiones del área
   - **Probabilidad de Propagación** (0.0-0.5): Velocidad de fuego
   - **Densidad de Árboles** (0.3-0.9): Cobertura inicial
   - **Número de Drones** (1-3): Unidades autónomas
   - **Focos Iniciales** (1-5): Incendios a combatir
   - **Pasos Máximos** (50-200): Duración de la misión

4. Presiona **"🚀 Iniciar Misión"**
5. Observa la simulación en tiempo real con métricas

### Modo: Bosques Reales (GIS)

1. En la barra lateral, selecciona **"Bosques Reales"**
2. Elige **"Escenarios Predefinidos"** y selecciona uno:
   - 🌳 Amazonas - Perú
   - 🌳 Pantanal - Brasil
   - 🌳 Sierra Nevada - Colombia
   - 🌳 Selva Daintree - Australia
   - 🌳 Borneo - Malasia

   O **"Personalizado"** para ingresar coordenadas propias:
   - Latitud: -90° a +90°
   - Longitud: -180° a +180°

3. Ajusta parámetros ambientales (iguales a Grid Aleatorio)
4. Presiona **"🚀 Iniciar Misión"**
5. **Nuevo**: Visualiza el mapa interactivo con:
   - 🔥 Heatmap de fuegos
   - 📐 Cuadrícula de simulación superpuesta
   - 🚁 Posiciones de drones (iconos azul, naranja, púrpura)
   - 🌲 Árboles salvados (puntos verdes)
   - ℹ️ Información del bosque real

---

## 📊 Módulos GIS Nuevos

### `gis_locations.py`

Define los bosques reales y proporciona utilidades geográficas:

```python
from gis_locations import BOSQUES_REALES, BosqueReal

# Acceder al primer bosque
amazonas = BOSQUES_REALES[0]
print(f"{amazonas.nombre} @ ({amazonas.latitud}, {amazonas.longitud})")

# Listar todos los escenarios predefinidos
from gis_locations import ESCENARIOS_REALES
for nombre, escenario in ESCENARIOS_REALES.items():
    print(f"- {nombre}")
```

**Bosques Disponibles** (13 reales):
1. Amazonas - Perú (-3.4653°, -62.2159°)
2. Pantanal - Brasil (-17.8383°, -57.0227°)
3. Sierra Nevada - Colombia (10.5597°, -73.9045°)
4. Selva Daintree - Australia (-16.2217°, 145.2667°)
5. Borneo - Malasia (4.5353°, 113.0353°)
6. Y 8 más en diferentes continentes...

### `forest_fire_gis.py`

Extiende ForestFireEnv con capacidades geográficas:

```python
from forest_fire_gis import ForestFireGISEnv
from gis_locations import BOSQUES_REALES

# Crear ambiente GIS
bosque = BOSQUES_REALES[0]  # Amazonas
env = ForestFireGISEnv(
    bosque=bosque,
    grid_size=10,
    fire_spread_prob=0.15,
    initial_trees=0.65,
    initial_fires=3,
    num_agents=2
)

# Usar como entorno normal de Gymnasium
obs, info = env.reset()
action = env.action_space.sample()
obs, reward, terminated, truncated, info = env.step(action)

# Nuevos métodos GIS
agent_positions_geo = env.get_agent_geo_positions()  # [(lat, lon), ...]
fires_geo = env.get_fires_geo_positions()            # [(lat, lon), ...]
coverage_km2 = env.get_coverage_area_km2()           # 25.0
bounds = env.get_grid_bounds()                       # {north, south, east, west, ...}
heatmap_data = env.get_heatmap_data()               # [(lat, lon, intensity), ...]
```

### `gis_visualization.py`

Crea mapas interactivos con Folium:

```python
from gis_visualization import MapaForestGuardian

visualizer = MapaForestGuardian(env, zoom_level=12)

# Mapa completo con todos los elementos
mapa = visualizer.crear_mapa_completo(
    incluir_arboles=True,
    incluir_heatmap=True,
    incluir_grid=True,
    incluir_drones=True,
    incluir_info=True
)

# Salvar como HTML
mapa.save('simulacion.html')

# O mostrar en Streamlit
from streamlit_folium import st_folium
st_folium(mapa, width=1000, height=600)
```

---

## 🤖 Agentes y Estrategias

### Dron Azul (ALPHA) - Búsqueda Rápida

- **Objetivo**: Localizar el fuego más cercano
- **Acción**: Dirigirse rápidamente al objetivo
- **Ventaja**: Respuesta inmediata a nuevos focos

### Dron Naranja (BRAVO) - Contención Periférica

- **Objetivo**: Búsqueda de fuegos distantes
- **Acción**: Prevenir propagación en el perímetro
- **Ventaja**: Cobertura de área amplia

### Dron Púrpura (CHARLIE) - Apoyo Estratégico

- **Objetivo**: Soporte táctico
- **Acción**: Protección de áreas críticas
- **Ventaja**: Flexibilidad y redundancia

---

## 📈 Métricas y KPIs

### Disponibles en el Dashboard

| Métrica | Descripción |
|---------|------------|
| 🔥 **Focos Activos** | Número de incendios en tiempo real |
| 🌳 **Árboles Salvados %** | Porcentaje de bosque protegido |
| 💧 **Agua Consumida** | Litros de agua utilizados |
| ⏱️ **Tiempo Transcurrido** | Pasos de simulación ejecutados |
| 📊 **Densidad de Incendios** | Concentración de focos en el área |
| 🚁 **Eficiencia de Drones** | Distancia recorrida vs fuegos extinguidos |

---

## 🔧 Configuración Avanzada

### Variables de Entorno

```bash
# Puerto de Streamlit
export STREAMLIT_SERVER_PORT=8501

# Modo sin headless browser
export STREAMLIT_SERVER_HEADLESS=true
```

### Modificar Bosques

Edita `gis_locations.py` para agregar nuevos bosques:

```python
nuevo_bosque = BosqueReal(
    nombre="Mi Bosque",
    pais="Mi País",
    latitud=0.0,
    longitud=0.0,
    area_km2=1000,
    densidad="media",
    amenazas=["sequía", "incendios"],
    descripcion="Descripción del bosque"
)

BOSQUES_REALES.append(nuevo_bosque)
```

---

## 📚 Referencias y Fórmulas

### Conversión de Coordenadas

Cada celda del grid (10×10) representa 0.5 km de lado:

```
lat_celda = lat_bosque - (row * grados_por_celda)
lon_celda = lon_bosque + (col * grados_por_celda)

donde: grados_por_celda = 0.5 km / (111 km/grado) ≈ 0.0045 grados
```

### Distancia Haversine

```
d = 2R * arcsin(sqrt(sin²((lat2-lat1)/2) + cos(lat1)*cos(lat2)*sin²((lon2-lon1)/2)))
donde: R = 6371 km (radio terrestre)
```

---

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'folium'"

```bash
pip install folium streamlit-folium
```

### Error: "Streamlit radio() got unexpected keyword argument"

**Solución**: Actualiza Streamlit a 1.53.0+:
```bash
pip install --upgrade streamlit
```

### Mapa no se muestra

Asegúrate de tener `streamlit-folium` instalado:
```bash
pip install streamlit-folium
```

### Simulación muy lenta

Reduce el `grid_size` o `max_steps` en los parámetros de la barra lateral.

---

## 📝 Licencia

Este proyecto es de código abierto. Úsalo libremente para investigación y educación.

---

## 👥 Contribuciones

Las contribuciones son bienvenidas. Para cambios significativos, abre un issue primero.

---

## 🎓 Casos de Uso Educativos

1. **Inteligencia Artificial**: Aprendizaje por refuerzo multi-agente
2. **Sistemas Distribuidos**: Coordinación de múltiples robots
3. **Geomática**: Transformaciones de coordenadas y mapeo
4. **Sostenibilidad**: Gestión de incendios forestales reales
5. **Visualización**: Dashboards interactivos con datos geográficos

---

## 📞 Soporte

Para preguntas o problemas, consulta:
- Documentación de [Gymnasium](https://gymnasium.farama.org/)
- Documentación de [Streamlit](https://docs.streamlit.io/)
- Documentación de [Folium](https://folium.readthedocs.io/)

---

**Última actualización**: Enero 2026  
**Versión**: 2.0 (con GIS)
