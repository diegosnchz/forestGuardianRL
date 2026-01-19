# 📝 Mission Logger - Sistema de Historial de Misiones

## 🎯 Descripción General

El **Mission Logger** es un sistema de persistencia que almacena automáticamente los resultados de cada simulación en **MongoDB Atlas**, incluyendo:

- ✅ Métricas de rendimiento (KPIs)
- ✅ Historial completo de decisiones XAI paso a paso
- ✅ Configuración utilizada (agentes, tamaño de grid, probabilidades)
- ✅ Snapshot final del grid en formato GeoJSON
- ✅ Estadísticas por agente (distancias, confianza, acciones)

Esto permite:
- 📊 Analizar tendencias en el rendimiento
- 🔍 Comparar diferentes configuraciones de agentes
- 🏆 Identificar las mejores estrategias
- 🗺️ Revisar el historial de decisiones XAI

---

## 🏗️ Arquitectura

### Componentes

```
┌─────────────────────────────────────────────────────┐
│                    app.py (Streamlit)                │
│  ┌──────────────────────────────────────────────┐  │
│  │  Tab 7: "📜 Historial de Misiones"           │  │
│  │  ├─ 🕐 Recientes                             │  │
│  │  ├─ 🏆 Mejores                               │  │
│  │  ├─ 🔍 Buscar                                │  │
│  │  └─ 📊 Estadísticas                          │  │
│  └──────────────────────────────────────────────┘  │
│                        ↓                             │
│  ┌──────────────────────────────────────────────┐  │
│  │  mission_logger.py (MissionLogger)           │  │
│  │  ├─ save_mission()                           │  │
│  │  ├─ get_recent_missions()                    │  │
│  │  ├─ get_top_missions()                       │  │
│  │  ├─ compare_missions()                       │  │
│  │  └─ get_statistics()                         │  │
│  └──────────────────────────────────────────────┘  │
│                        ↓                             │
└─────────────────────────────────────────────────────┘
                         ↓
        ┌────────────────────────────────┐
        │   MongoDB Atlas Collection     │
        │      "mission_logs"            │
        │                                │
        │  {                             │
        │    mission_id: UUID,           │
        │    timestamp: ISO,             │
        │    kpis: {...},                │
        │    xai_log: [{...}],           │
        │    final_snapshot: GeoJSON     │
        │  }                             │
        └────────────────────────────────┘
```

---

## 📦 Esquema de Documento MongoDB

Cada misión se guarda como un documento con la siguiente estructura:

```json
{
  "_id": "ObjectId generado por MongoDB",
  
  "mission_id": "550e8400-e29b-41d4-a716-446655440000",
  
  "timestamp": "2026-01-17T10:30:45.123456",
  
  "geo_zone": "Bosque de Chapultepec",
  
  "geojson_file": "bosques/chapultepec.geojson",
  
  "configuration": {
    "grid_size": 50,
    "num_agents": 2,
    "fire_prob": 0.1,
    "tree_density": 0.3,
    "initial_fires": 5,
    "max_steps": 150
  },
  
  "kpis": {
    "kpi_survival_rate": 85.5,
    "trees_saved_pct": 85.5,
    "fires_extinguished": 12,
    "water_consumed": 48,
    "steps_taken": 142,
    "mission_success": true
  },
  
  "xai_log": [
    {
      "step": 1,
      "agent_id": "Alpha",
      "position": [10, 15],
      "action_name": "move_and_extinguish",
      "target_position": [12, 18],
      "distance_to_target": 3.6,
      "explanation": "Detectado fuego crítico en (12, 18) con 2 árboles adyacentes",
      "tactical_reasoning": "Prioridad alta: fuego amenaza múltiples árboles",
      "importance_scores": {
        "fire_proximity": 0.85,
        "tree_density": 0.70,
        "water_availability": 0.60
      },
      "confidence": 0.92
    },
    // ... más decisiones
  ],
  
  "agent_stats": {
    "Alpha": {
      "decisions": 71,
      "avg_confidence": 0.87,
      "avg_distance": 4.2,
      "actions": {
        "move_and_extinguish": 45,
        "refill_water": 15,
        "move": 11
      }
    },
    "Bravo": {
      "decisions": 71,
      "avg_confidence": 0.82,
      "avg_distance": 8.5,
      "actions": {
        "move_and_extinguish": 38,
        "refill_water": 18,
        "move": 15
      }
    }
  },
  
  "final_snapshot": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [10, 15]
        },
        "properties": {
          "cell_type": "tree",
          "value": 1
        }
      },
      // ... más features
    ]
  }
}
```

---

## 🚀 Instalación y Configuración

### 1. Instalar dependencias

```bash
pip install pymongo
```

### 2. Configurar MongoDB Atlas

1. Crea una cuenta en [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Crea un cluster gratuito (M0)
3. Crea un usuario de base de datos
4. Whitelist tu IP (o usa 0.0.0.0/0 para desarrollo)
5. Obtén tu connection string:

```
mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
```

### 3. Configurar en Streamlit

En la **sidebar de app.py**:

1. Expande "🗺️ MongoDB Atlas (Opcional)"
2. Pega tu URI de MongoDB Atlas
3. Marca "Habilitar historial de misiones"
4. Verifica que aparezca "✅ Mission Logger conectado"

---

## 💻 Uso Programático

### Ejemplo básico

```python
from mission_logger import MissionLogger, save_mission_summary

# Inicializar
logger = MissionLogger(uri="mongodb+srv://...")
logger.connect()

# Guardar una misión
mission_id = save_mission_summary(
    mission_logger=logger,
    geo_zone="Bosque de Chapultepec",
    geojson_file="bosques/chapultepec.geojson",
    configuration={
        "grid_size": 50,
        "num_agents": 2,
        "fire_prob": 0.1
    },
    initial_trees=2000,
    final_trees=1710,
    fires_extinguished=12,
    water_consumed=48,
    steps_taken=142,
    xai_decisions=[...],  # Lista de AgentDecision objects
    final_grid=np.array(...)  # Grid final
)

print(f"Misión guardada: {mission_id}")
```

### Consultar misiones

```python
# Últimas 10 misiones
recent = logger.get_recent_missions(limit=10)

# Top 5 misiones por supervivencia
top = logger.get_top_missions(limit=5)

# Misiones de una zona específica
zone_missions = logger.get_missions_by_zone("Chapultepec", limit=20)

# Obtener una misión específica
mission = logger.get_mission_by_id("550e8400-e29b-41d4-a716-446655440000")

# Comparar misiones
comparison = logger.compare_missions([
    "mission_id_1",
    "mission_id_2",
    "mission_id_3"
])

# Estadísticas globales
stats = logger.get_statistics()
print(f"Total misiones: {stats['total_missions']}")
print(f"Supervivencia promedio: {stats['avg_survival_rate']:.1f}%")
```

---

## 🎨 Interfaz de Usuario (Tab 7)

### 🕐 Recientes

- **Tabla** de las últimas N misiones
- **Selector** de cantidad (5-50)
- **Detalles** al hacer clic:
  - Métricas principales (supervivencia, fuegos, agua, pasos)
  - Configuración utilizada
  - Estadísticas por agente
  - Historial XAI completo

### 🏆 Mejores

- **Ranking** de las mejores misiones por tasa de supervivencia
- **Gráfico de barras** interactivo
- **Tabla** con detalles de cada top mission
- Código de colores: verde (éxito), amarillo (parcial)

### 🔍 Buscar

- **Filtros**:
  - Por zona geográfica
  - Supervivencia mínima (slider)
- **Resultados** en tabla
- **Export** a CSV (futuro)

### 📊 Estadísticas

- **Métricas globales**:
  - Total de misiones
  - Supervivencia promedio
  - Mejor resultado
  - Pasos promedio
  
- **Gráficos**:
  - Tendencia temporal de supervivencia
  - Distribución por zona (pie chart)
  - Supervivencia promedio por zona (bar chart)
  
- **Acciones administrativas**:
  - Limpiar base de datos (⚠️ peligroso)

---

## 📋 API Reference

### `class MissionLogger`

#### `__init__(uri, database_name="forestguardian")`
Inicializa el logger con URI de MongoDB.

**Parámetros:**
- `uri` (str): Connection string de MongoDB Atlas
- `database_name` (str): Nombre de la base de datos (default: "forestguardian")

#### `connect() -> bool`
Conecta a MongoDB y crea índices.

**Returns:**
- `bool`: True si la conexión fue exitosa

#### `save_mission(...) -> str`
Guarda una misión completa en MongoDB.

**Parámetros:**
- `geo_zone` (str): Nombre de la zona geográfica
- `geojson_file` (str): Ruta del archivo GeoJSON
- `configuration` (dict): Configuración de la simulación
- `kpis` (dict): Métricas de rendimiento
- `xai_log` (list): Historial de decisiones XAI
- `agent_stats` (dict): Estadísticas por agente
- `final_grid` (np.array): Grid final del entorno

**Returns:**
- `str`: UUID de la misión guardada

#### `get_recent_missions(limit=10) -> list`
Obtiene las misiones más recientes.

**Parámetros:**
- `limit` (int): Número de misiones a retornar

**Returns:**
- `list[dict]`: Lista de documentos de misiones

#### `get_top_missions(limit=10) -> list`
Obtiene las mejores misiones por supervivencia.

**Parámetros:**
- `limit` (int): Número de misiones a retornar

**Returns:**
- `list[dict]`: Lista de documentos ordenados por kpi_survival_rate DESC

#### `get_missions_by_zone(geo_zone, limit=10) -> list`
Obtiene misiones de una zona específica.

**Parámetros:**
- `geo_zone` (str): Nombre de la zona
- `limit` (int): Número de misiones a retornar

**Returns:**
- `list[dict]`: Lista de documentos de esa zona

#### `get_mission_by_id(mission_id) -> dict`
Obtiene una misión por su UUID.

**Parámetros:**
- `mission_id` (str): UUID de la misión

**Returns:**
- `dict`: Documento de la misión o None

#### `compare_missions(mission_ids) -> dict`
Compara múltiples misiones.

**Parámetros:**
- `mission_ids` (list[str]): Lista de UUIDs a comparar

**Returns:**
```python
{
    "missions": [...],  # Documentos completos
    "comparison": {
        "best_survival": {...},
        "worst_survival": {...},
        "avg_survival_rate": float,
        "avg_fires_extinguished": float,
        "avg_water_consumed": float,
        "avg_steps": float
    }
}
```

#### `get_statistics() -> dict`
Obtiene estadísticas globales.

**Returns:**
```python
{
    "total_missions": int,
    "avg_survival_rate": float,
    "max_survival_rate": float,
    "min_survival_rate": float,
    "avg_steps": float
}
```

#### `delete_mission(mission_id) -> bool`
Elimina una misión.

**Parámetros:**
- `mission_id` (str): UUID de la misión

**Returns:**
- `bool`: True si se eliminó exitosamente

#### `clear_all_missions() -> bool`
⚠️ **PELIGROSO**: Elimina TODAS las misiones.

**Returns:**
- `bool`: True si se eliminaron todas

---

### Función helper: `save_mission_summary()`

```python
def save_mission_summary(
    mission_logger: MissionLogger,
    geo_zone: str,
    geojson_file: str,
    configuration: dict,
    initial_trees: int,
    final_trees: int,
    fires_extinguished: int,
    water_consumed: int,
    steps_taken: int,
    xai_decisions: list,
    final_grid: np.ndarray
) -> str
```

Wrapper conveniente para guardar misiones. Calcula automáticamente:
- `kpi_survival_rate`
- `trees_saved_pct`
- `mission_success` (>50% supervivencia)
- Convierte XAI decisions a formato dict
- Calcula estadísticas por agente

**Returns:**
- `str`: UUID de la misión guardada

---

## 🔍 Índices MongoDB

Para optimizar las consultas, se crean automáticamente estos índices:

```python
# 1. Consultas de misiones recientes
{"timestamp": -1}

# 2. Filtros por zona
{"geo_zone": 1}

# 3. Top misiones por supervivencia
{"kpis.kpi_survival_rate": -1}

# 4. Consultas complejas (zona + tiempo)
{"geo_zone": 1, "timestamp": -1}
```

---

## 🧪 Testing

Ejecuta los tests del Mission Logger:

```bash
python -c "
from mission_logger import MissionLogger
import numpy as np

logger = MissionLogger(uri='mongodb+srv://...')
if logger.connect():
    print('✅ Conexión exitosa')
    
    # Test save
    mission_id = logger.save_mission(
        geo_zone='Test Zone',
        geojson_file='test.geojson',
        configuration={'grid_size': 30},
        kpis={'kpi_survival_rate': 75.0, 'mission_success': True},
        xai_log=[],
        agent_stats={},
        final_grid=np.zeros((30, 30))
    )
    
    print(f'✅ Misión guardada: {mission_id}')
    
    # Test retrieve
    mission = logger.get_mission_by_id(mission_id)
    print(f'✅ Misión recuperada: {mission[\"geo_zone\"]}')
    
    # Clean up
    logger.delete_mission(mission_id)
    print('✅ Misión eliminada')
else:
    print('❌ Error de conexión')
"
```

---

## 🛠️ Troubleshooting

### Error: "pymongo not installed"

```bash
pip install pymongo
```

### Error: "Connection timeout"

- Verifica que tu IP esté en la whitelist de MongoDB Atlas
- Prueba con `0.0.0.0/0` (solo para desarrollo)
- Verifica que el cluster esté activo

### Error: "Authentication failed"

- Verifica username y password en la URI
- Asegúrate de URL-encode caracteres especiales:
  - `@` → `%40`
  - `#` → `%23`
  - `$` → `%24`

### Error: "Database not found"

- No te preocupes, MongoDB Atlas crea automáticamente la base de datos al insertar el primer documento

### No aparece "Mission Logger conectado"

1. Verifica que pymongo esté instalado
2. Verifica la URI de MongoDB
3. Revisa los logs en la terminal de Streamlit
4. Asegúrate de que el checkbox esté marcado

---

## 📈 Casos de Uso

### 1. Optimización de Agentes

**Problema**: ¿Qué configuración de agentes es más efectiva?

**Solución**:
1. Ejecuta múltiples misiones con diferentes configuraciones
2. Ve a Tab 7 → "🏆 Mejores"
3. Analiza las top 10 misiones
4. Identifica patrones en la configuración

### 2. Análisis de Zonas

**Problema**: ¿Qué zonas son más difíciles?

**Solución**:
1. Ve a Tab 7 → "📊 Estadísticas"
2. Revisa "Supervivencia Promedio por Zona"
3. Identifica zonas con menor supervivencia
4. Ajusta parámetros específicos para esas zonas

### 3. Debugging de Decisiones

**Problema**: ¿Por qué falló una misión?

**Solución**:
1. Ve a Tab 7 → "🕐 Recientes"
2. Selecciona la misión fallida
3. Expande "🧠 Historial XAI"
4. Analiza decisión por decisión
5. Identifica dónde el agente tomó decisiones subóptimas

### 4. Comparación A/B

**Problema**: ¿Estrategia A o B es mejor?

**Solución**:
1. Ejecuta 5 misiones con estrategia A
2. Ejecuta 5 misiones con estrategia B
3. Usa `compare_missions()` para analizar diferencias
4. Compara avg_survival_rate y avg_steps

---

## 🔮 Roadmap Futuro

### Versión 2.0
- [ ] Export a CSV/Excel
- [ ] Filtros avanzados (rango de fechas, múltiples zonas)
- [ ] Gráficos de comparación de XAI decisions
- [ ] Replay de misión desde MongoDB
- [ ] Anotaciones manuales en misiones

### Versión 3.0
- [ ] Machine Learning: predecir éxito basado en configuración
- [ ] Recomendador de configuraciones óptimas
- [ ] Dashboard en tiempo real (WebSocket)
- [ ] Multi-tenancy (usuarios separados)

---

## 📞 Soporte

Si encuentras algún problema:

1. Verifica que todos los requisitos estén instalados
2. Revisa los logs en la terminal
3. Consulta la sección de Troubleshooting
4. Abre un issue en el repositorio

---

## 📄 Licencia

Este sistema es parte del proyecto Forest Guardian RL y sigue la misma licencia del proyecto principal.

---

**Última actualización**: 2026-01-17  
**Versión**: 1.0.0  
**Autor**: Forest Guardian RL Team
