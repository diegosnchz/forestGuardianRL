# 🗺️ Integración MongoDB Atlas - Resumen Ejecutivo

## 📦 Archivos Creados

### 1. **upload_geojson_to_atlas.py** (Script Principal)
Script profesional de 450+ líneas para cargar datos GeoJSON a MongoDB Atlas.

**Características:**
- ✅ Conexión segura a MongoDB Atlas con validación
- ✅ Lectura y validación de archivos GeoJSON
- ✅ Transformación automática de features a formato MongoDB
- ✅ Creación de índices geoespaciales 2dsphere
- ✅ Manejo robusto de errores con logging detallado
- ✅ Soporte para FeatureCollection y Feature individual
- ✅ Validación de geometrías (Point, Polygon, LineString, etc.)
- ✅ Metadatos automáticos (timestamp, source, feature_id)
- ✅ Índices adicionales (nombre, tipo) para consultas rápidas
- ✅ Modo de limpieza de colección opcional
- ✅ Estadísticas detalladas post-carga

**Estructura del documento en MongoDB:**
```json
{
  "_id": ObjectId("..."),
  "location": {
    "type": "Polygon",
    "coordinates": [[[-99.2, 19.42], ...]]
  },
  "properties": {
    "nombre": "Bosque de Pinos",
    "tipo": "coniferas",
    "area": 125.5,
    "riesgo_incendio": "alto",
    ...
  },
  "metadata": {
    "uploaded_at": ISODate("2026-01-19T..."),
    "source": "geojson_upload",
    "feature_id": "zona_001"
  },
  "nombre": "Bosque de Pinos",  // Campo raíz para indexación
  "tipo": "coniferas",           // Campo raíz para indexación
  "area": 125.5                  // Campo raíz para indexación
}
```

**Uso:**
```bash
# 1. Configurar MONGODB_URI, GEOJSON_FILE en el script
# 2. Ejecutar
python upload_geojson_to_atlas.py
```

---

### 2. **query_geospatial_examples.py** (Ejemplos de Consultas)
Script educativo con 6 ejemplos completos de consultas geoespaciales.

**Ejemplos incluidos:**
1. **Estadísticas generales**: Total documentos, tipos, riesgos, área total
2. **Zonas cerca de punto** ($near): Encuentra zonas alrededor de drone
3. **Zonas dentro de polígono** ($geoWithin): Área de operación
4. **Zonas de alto riesgo**: Filtrado por propiedades
5. **Respuesta óptima a incendio**: Algoritmo completo de decisión
6. **Búsqueda por tipo**: Zonas protegidas, estaciones, etc.

**Clase ForestGuardianQueries:**
- `find_zones_near_point()`: Búsqueda radial desde punto
- `find_zones_within_polygon()`: Búsqueda dentro de polígono
- `find_high_risk_zones()`: Filtro por nivel de riesgo
- `find_zones_by_type()`: Filtro por tipo de zona
- `find_monitoring_stations_near_fire()`: Estaciones cercanas a incendio
- `calculate_optimal_response_path()`: Cálculo de respuesta con recomendación
- `get_statistics()`: Análisis estadístico completo

**Uso:**
```bash
# 1. Configurar MONGODB_URI en el script
# 2. Ejecutar
python query_geospatial_examples.py
```

---

### 3. **zonas_forestales_ejemplo.geojson** (Datos de Ejemplo)
Archivo GeoJSON completo con 7 features de muestra.

**Contenido:**
- 3 zonas forestales (Polygon):
  - Bosque de Pinos - Zona Norte (125.5 ha, riesgo alto)
  - Bosque Mixto - Zona Sur (87.3 ha, riesgo medio)
  - Reserva Natural - Zona Este (203.8 ha, riesgo bajo)
  
- 3 estaciones de monitoreo (Point):
  - Estación Norte (5 drones, torre vigilancia)
  - Estación Sur (3 drones)
  - Estación Este (4 drones, torre vigilancia)
  
- 1 ruta de patrulla (LineString):
  - Ruta Norte-Sur (5.2 km, 4 patrullas diarias)

**Propiedades incluidas:**
- `nombre`, `tipo`, `area`, `riesgo_incendio`
- `densidad_arboles`, `altitud_promedio`
- `ultima_inspeccion`, `estacion_cercana`
- `capacidad_drones`, `equipamiento` (para estaciones)

---

### 4. **MONGODB_ATLAS_SETUP.md** (Documentación Completa)
Guía exhaustiva de 400+ líneas con todo lo necesario.

**Secciones:**
1. **Prerrequisitos**: Cuenta Atlas, Python 3.8+, archivo GeoJSON
2. **Configuración Atlas**: 
   - Crear cuenta y cluster (M0 gratuito)
   - Database Access (usuario/contraseña)
   - Network Access (whitelist IP)
   - Obtener Connection String
3. **Instalación**: pymongo, requirements.txt
4. **Uso del Script**: Configuración paso a paso
5. **Consultas Geoespaciales**: Ejemplos con pymongo
6. **Integración Forest Guardian**: Código para forest_fire_env.py y train_and_test.py
7. **Troubleshooting**: Soluciones a problemas comunes
8. **Recursos**: Links a documentación oficial

**Código de integración incluido:**
- Método `get_nearby_zones()` para ForestFireEnv
- Método `get_zone_risk_level()` para determinar riesgo
- Actualización de TerminatorAgent con datos geoespaciales

---

### 5. **requirements.txt** (Actualizado)
Agregadas dependencias:
```txt
pymongo>=4.6.0      # Driver MongoDB para Python
requests>=2.31.0    # Ya estaba (para OpenWeatherMap)
```

---

## 🎯 Flujo de Trabajo Completo

### Fase 1: Preparación
```bash
# 1. Obtener URI de MongoDB Atlas
# - Crear cuenta en https://cloud.mongodb.com
# - Crear cluster gratuito M0
# - Configurar usuario y whitelist
# - Copiar URI de conexión

# 2. Preparar archivo GeoJSON
# - Usar zonas_forestales_ejemplo.geojson como plantilla
# - O crear tu propio GeoJSON con geojson.io
```

### Fase 2: Carga de Datos
```bash
# 3. Instalar dependencias
pip install pymongo

# 4. Configurar script
# Editar upload_geojson_to_atlas.py:
MONGODB_URI = "mongodb+srv://user:pass@cluster.mongodb.net/..."
GEOJSON_FILE = "zonas_forestales.geojson"

# 5. Ejecutar carga
python upload_geojson_to_atlas.py

# ✅ Output esperado:
# - Conexión exitosa
# - 7 documentos insertados
# - Índice 2dsphere creado
# - Estadísticas mostradas
```

### Fase 3: Validación
```bash
# 6. Verificar en Atlas UI
# - Ir a Database → Browse Collections
# - Ver mapa_forestal
# - Inspeccionar documentos

# 7. Probar consultas
# Editar query_geospatial_examples.py:
MONGODB_URI = "mongodb+srv://..."

python query_geospatial_examples.py

# ✅ Output: 6 ejemplos con resultados
```

### Fase 4: Integración
```python
# 8. Agregar a forest_fire_env.py
from pymongo import MongoClient

class ForestFireEnv(gym.Env):
    def __init__(self, ..., mongodb_uri=None):
        # ... código existente ...
        if mongodb_uri:
            self.mongo_client = MongoClient(mongodb_uri)
            self.mongo_db = self.mongo_client["forest_guardian"]
    
    def get_nearby_zones(self, position, radius_km=2.0):
        # Convertir grid position a lat/lon
        lat = self.location_lat + (position[0] - self.grid_size/2) * 0.001
        lon = self.location_lon + (position[1] - self.grid_size/2) * 0.001
        
        # Consulta geoespacial
        zones = self.mongo_db["mapa_forestal"].find({
            "location": {
                "$near": {
                    "$geometry": {"type": "Point", "coordinates": [lon, lat]},
                    "$maxDistance": radius_km * 1000
                }
            }
        })
        return list(zones)

# 9. Usar en agentes
class TerminatorAgent:
    def decide(self, obs, agent_pos):
        risk_level = self.env.get_zone_risk_level(agent_pos)
        if risk_level == "alto":
            # Priorizar zona de alto riesgo
            pass
```

---

## 🔍 Consultas Geoespaciales Clave

### 1. Búsqueda por Proximidad ($near)
```python
# Encontrar zonas a menos de 5km del drone
db.mapa_forestal.find({
    "location": {
        "$near": {
            "$geometry": {"type": "Point", "coordinates": [-99.195, 19.415]},
            "$maxDistance": 5000  # metros
        }
    }
})
```

### 2. Búsqueda Dentro de Polígono ($geoWithin)
```python
# Zonas dentro del área de operación
db.mapa_forestal.find({
    "location": {
        "$geoWithin": {
            "$geometry": {
                "type": "Polygon",
                "coordinates": [[[-99.21, 19.40], ...]]
            }
        }
    }
})
```

### 3. Búsqueda por Propiedades
```python
# Zonas de alto riesgo
db.mapa_forestal.find({
    "properties.riesgo_incendio": "alto"
})

# Estaciones operativas
db.mapa_forestal.find({
    "tipo": "estacion",
    "properties.operativa": true
})
```

---

## 📊 Índices Creados Automáticamente

1. **`_id_`**: Índice por defecto de MongoDB
2. **`location_2dsphere`**: Índice geoespacial para consultas $near, $geoWithin
3. **`nombre_index`**: Índice en campo nombre (búsqueda rápida)
4. **`tipo_index`**: Índice en campo tipo (filtrado por categoría)

**Beneficios:**
- Consultas geoespaciales en milisegundos
- Búsquedas por nombre instantáneas
- Filtrado por tipo eficiente
- Escalabilidad a millones de documentos

---

## 🚀 Casos de Uso en Forest Guardian RL

### 1. Detección Inteligente de Incendios
```python
# Determinar severidad basada en zona
fire_position = (10, 15)
zones = env.get_nearby_zones(fire_position, radius_km=0.5)

if zones[0]['properties']['tipo'] == 'protegida':
    priority = "CRITICAL"
elif zones[0]['properties']['riesgo_incendio'] == 'alto':
    priority = "HIGH"
```

### 2. Optimización de Rutas
```python
# Encontrar estación más cercana
stations = db.mapa_forestal.find({
    "tipo": "estacion",
    "location": {"$near": {"$geometry": fire_location}}
}).limit(1)

# Calcular ruta óptima desde estación a incendio
```

### 3. Predicción de Propagación
```python
# Obtener zonas en dirección del viento
wind_direction = env.wind_direction
fire_pos = env.fire_positions[0]

# Calcular punto adelante en dirección del viento
next_lat = fire_lat + np.cos(np.radians(wind_direction)) * 0.01
next_lon = fire_lon + np.sin(np.radians(wind_direction)) * 0.01

# Zonas en riesgo
zones_at_risk = db.mapa_forestal.find({
    "location": {
        "$near": {
            "$geometry": {"type": "Point", "coordinates": [next_lon, next_lat]},
            "$maxDistance": 2000
        }
    }
})
```

### 4. Reentrenamiento Dinámico PPO
```python
# Agregar información geoespacial al observation space
observation = {
    'grid': grid_state,
    'wind': wind_vector,
    'elevation': elevation_map,
    'zone_risk': zone_risk_level,  # NUEVO
    'zone_type': zone_type_encoded  # NUEVO
}

# PPO aprende a priorizar zonas de alto valor
```

---

## ✅ Checklist de Implementación

- [x] Script de carga con validación completa
- [x] Ejemplos de consultas geoespaciales
- [x] Archivo GeoJSON de ejemplo con 7 features
- [x] Documentación exhaustiva (400+ líneas)
- [x] requirements.txt actualizado
- [x] Índices 2dsphere configurados
- [x] Logging y manejo de errores robusto
- [x] Código de integración para ForestFireEnv
- [x] Código de integración para TerminatorAgent
- [ ] Ejecutar carga inicial de datos (requiere configuración Atlas)
- [ ] Validar consultas en Atlas Compass
- [ ] Integrar en forest_fire_env.py (opcional)
- [ ] Reentrenar PPO con features geoespaciales (opcional)

---

## 📈 Próximos Pasos Recomendados

1. **Configuración Inicial** (15 min)
   - Crear cuenta MongoDB Atlas
   - Crear cluster gratuito M0
   - Configurar acceso (usuario + whitelist)

2. **Carga de Datos** (5 min)
   - Ejecutar `upload_geojson_to_atlas.py`
   - Verificar datos en Atlas UI

3. **Pruebas** (10 min)
   - Ejecutar `query_geospatial_examples.py`
   - Revisar resultados de las 6 consultas

4. **Integración Básica** (30 min)
   - Agregar cliente MongoDB a `ForestFireEnv`
   - Implementar `get_nearby_zones()` y `get_zone_risk_level()`
   - Actualizar `TerminatorAgent` con lógica geoespacial

5. **Integración Avanzada** (2-4 horas)
   - Ampliar observation space con datos geoespaciales
   - Reentrenar PPO con nuevas features
   - Evaluar mejora en métricas (fires extinguished, trees saved)

6. **Optimización** (opcional)
   - Agregar caché de consultas frecuentes
   - Implementar actualización de datos en tiempo real
   - Dashboard en Streamlit con mapa interactivo

---

## 🛡️ Seguridad y Mejores Prácticas

1. **Variables de Entorno** (recomendado):
```bash
# .env
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/...
MONGODB_DATABASE=forest_guardian
MONGODB_COLLECTION=mapa_forestal

# Python
from dotenv import load_dotenv
import os

load_dotenv()
uri = os.getenv("MONGODB_URI")
```

2. **Manejo de Contraseñas**:
- ❌ NO commitear URIs con contraseñas a Git
- ✅ Usar `.env` en `.gitignore`
- ✅ Usar secretos de GitHub Actions para CI/CD

3. **Producción**:
- Usar cluster dedicado (no M0 gratuito)
- Configurar replica set para alta disponibilidad
- Implementar backup automático
- Monitorear performance con Atlas Monitoring

---

## 🎓 Recursos de Aprendizaje

- [MongoDB University](https://university.mongodb.com/) - Cursos gratuitos
- [GeoJSON Spec](https://geojson.org/) - Especificación oficial
- [MongoDB Geospatial Queries](https://www.mongodb.com/docs/manual/geospatial-queries/)
- [PyMongo Tutorial](https://pymongo.readthedocs.io/en/stable/tutorial.html)
- [GeoJSON.io](https://geojson.io/) - Editor visual de GeoJSON

---

**Creado por**: Forest Guardian RL Team  
**Fecha**: Enero 2026  
**Versión**: 1.0.0

---

**¿Preguntas?** Consulta [MONGODB_ATLAS_SETUP.md](MONGODB_ATLAS_SETUP.md) para documentación detallada.
