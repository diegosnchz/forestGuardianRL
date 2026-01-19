# 🔥 Modelo de Rothermel - Implementación en Forest Guardian RL

## 🎯 Descripción General

Se ha integrado el **Modelo de Rothermel** en `forest_fire_env.py` para simular la propagación de incendios forestales con física realista basada en investigación científica.

El modelo de Rothermel es el estándar internacional para predecir la velocidad y dirección de propagación de incendios forestales, desarrollado por Richard C. Rothermel en 1972 para el U.S. Forest Service.

---

## 📐 Fundamentos del Modelo de Rothermel

El modelo calcula la **tasa de propagación** del fuego basándose en tres factores principales:

```
R = R₀ × φw × φs × ηM

Donde:
R  = Tasa de propagación resultante
R₀ = Tasa de propagación base
φw = Factor de viento
φs = Factor de pendiente (slope)
ηM = Factor de humedad del combustible
```

---

## 🔧 Implementación en Forest Guardian RL

### 1. **Humedad del Combustible (Fuel Moisture Content)**

**Variable:** `self.fuel_moisture` - Mapa 2D con valores 5-35%

**Generación:**
```python
def _generate_fuel_moisture_map(self) -> np.ndarray:
    # Humedad base varía con elevación
    moisture = base_fuel_moisture + elevation * 15.0
    
    # Variabilidad espacial (ruido aleatorio ±5%)
    noise = np.random.uniform(-5, 5, size=(grid_size, grid_size))
    moisture += noise
    
    # Rango realista: 5-35%
    return np.clip(moisture, 5.0, 35.0)
```

**Interpretación:**
- **5-10%**: Combustible muy seco (alta propagación)
- **15-20%**: Combustible normal
- **25-35%**: Combustible húmedo (baja propagación)

**Factor en Rothermel:**
```python
# Decaimiento exponencial
moisture_factor = exp(-0.08 * (moisture - 5.0))

# FMC = 5%  → factor ≈ 1.0  (muy seco)
# FMC = 15% → factor ≈ 0.45 (normal)
# FMC = 30% → factor ≈ 0.11 (húmedo)
```

---

### 2. **Factor de Viento Vectorial (φw)**

**Variables:**
- `self.wind_speed` (0-20 km/h)
- `self.wind_direction` (0-360°)

**Cálculo Vectorial:**
```python
# Dirección del movimiento del fuego
fire_direction = arctan2(dc, -dr) % 360

# Alineación con el viento (-1 a +1)
alignment = 1 - |fire_direction - wind_direction| / 180

# Factor con exponente 1.5 (Rothermel estándar)
wind_multiplier = (wind_speed / 10.0)^1.5
wind_factor = 1.0 + wind_multiplier * alignment
```

**Comportamiento:**
- **A favor del viento (alignment = +1.0)**: Multiplica hasta **4x**
- **Perpendicular (alignment = 0.0)**: Factor ≈ 1.0
- **Contra el viento (alignment = -1.0)**: Reduce hasta **0.3x**

**Ejemplo Numérico:**
```
Viento: 15 km/h desde 90° (Este)
Fuego se propaga hacia 90° (Este):
  → alignment = 1.0
  → wind_multiplier = (15/10)^1.5 = 1.84
  → wind_factor = 1.0 + 1.84 * 1.0 = 2.84x

Fuego se propaga hacia 270° (Oeste):
  → alignment = -1.0
  → wind_factor = 1.0 + 1.84 * (-1.0) = -0.84 → clamp a 0.3x
```

---

### 3. **Factor de Pendiente (φs)**

**Variable:** `self.elevation` - Mapa 2D con valores 0-1

**Cálculo de Pendiente:**
```python
slope = elevation[to] - elevation[from]

if slope > 0:  # Cuesta arriba
    elevation_factor = 1.0 + slope * 3.5
else:  # Cuesta abajo
    elevation_factor = 1.0 + slope * 0.3
```

**Comportamiento:**
- **Cuesta arriba**: Efecto **muy fuerte** (multiplica hasta 3.5x)
- **Cuesta abajo**: Efecto **moderado** (reduce hasta 0.7x)
- **Terreno plano**: Factor = 1.0

**Justificación Física:**
- El fuego **precalienta** el combustible cuesta arriba
- Las llamas se inclinan hacia arriba por convección
- Efecto documentado en incendios reales (Crown fires)

---

### 4. **Probabilidad Final de Propagación**

```python
def _calculate_fire_spread_probability(from_pos, to_pos) -> float:
    """
    MODELO DE ROTHERMEL SIMPLIFICADO
    """
    base_prob = 0.1  # Probabilidad base
    
    # 1. Factor de viento vectorial
    wind_factor = calculate_wind_factor(...)  # 0.3 - 4.0
    
    # 2. Factor de elevación
    elevation_factor = calculate_slope_factor(...)  # 0.2 - 3.0
    
    # 3. Factor de humedad
    moisture_factor = exp(-0.08 * (moisture - 5.0))  # 0.1 - 1.0
    
    # Probabilidad combinada
    final_prob = base_prob * wind_factor * elevation_factor * moisture_factor
    
    return clip(final_prob, 0.0, 1.0)
```

**Ejemplos de Escenarios:**

| Condiciones | Cálculo | Prob. Final |
|------------|---------|-------------|
| **Peor caso:** Viento fuerte (4x), cuesta arriba (2.5x), seco (1.0) | 0.1 × 4 × 2.5 × 1.0 | **1.0 (100%)** |
| **Caso normal:** Sin viento (1x), plano (1x), normal (0.45) | 0.1 × 1 × 1 × 0.45 | **0.045 (4.5%)** |
| **Mejor caso:** Contra viento (0.3x), cuesta abajo (0.7x), húmedo (0.11) | 0.1 × 0.3 × 0.7 × 0.11 | **0.0023 (0.23%)** |

---

## 🛰️ Asimilación de Datos UAV en MongoDB Atlas

### Actualización de Humedad en Tiempo Real

Cuando un dron se mueve, actualiza la humedad del combustible en MongoDB Atlas:

```python
def _update_fuel_moisture_mongodb(row, col, agent_id):
    """
    ASIMILACIÓN DE DATOS UAV:
    Simula medición de humedad por sensores del dron.
    """
    # Medición con variación ±2%
    measured_moisture = current_moisture + random(-2.0, 2.0)
    
    # Actualizar localmente
    fuel_moisture[row, col] = measured_moisture
    
    # Documento para MongoDB
    document = {
        'timestamp': datetime.utcnow().isoformat(),
        'step': steps_count,
        'agent_id': 'ALPHA' | 'BRAVO' | 'GAMMA',
        'position': {'row': row, 'col': col},
        'fuel_moisture': {
            'value': measured_moisture,
            'unit': 'percent',
            'previous_value': current_moisture
        },
        'environmental_data': {
            'elevation': elevation[row, col],
            'wind_speed': wind_speed,
            'wind_direction': wind_direction,
            'cell_state': grid[row, col]
        }
    }
    
    # Insertar en colección 'fuel_moisture_updates'
    mongodb_collection.insert_one(document)
```

### Esquema de Documento MongoDB

```json
{
  "_id": "ObjectId(...)",
  "timestamp": "2026-01-19T10:30:45.123456",
  "step": 42,
  "agent_id": "ALPHA",
  "position": {
    "row": 15,
    "col": 23
  },
  "fuel_moisture": {
    "value": 18.3,
    "unit": "percent",
    "previous_value": 17.8
  },
  "environmental_data": {
    "elevation": 0.65,
    "wind_speed": 12.5,
    "wind_direction": 135.0,
    "cell_state": 1
  },
  "metadata": {
    "grid_size": 50,
    "update_number": 127
  }
}
```

### Colección en MongoDB Atlas

**Database:** `forestguardian`  
**Collection:** `fuel_moisture_updates`

**Índices Recomendados:**
```javascript
// Consultas por timestamp
db.fuel_moisture_updates.createIndex({ "timestamp": -1 })

// Consultas por posición
db.fuel_moisture_updates.createIndex({ "position.row": 1, "position.col": 1 })

// Consultas por agente
db.fuel_moisture_updates.createIndex({ "agent_id": 1, "step": 1 })
```

---

## 🚀 Uso en Streamlit

### Configurar MongoDB URI

En la sidebar de `app.py`:

1. Expande "🗺️ MongoDB Atlas (Opcional)"
2. Pega tu URI de MongoDB Atlas
3. La conexión se establece automáticamente en `ForestFireEnv`

### Verificar Actualizaciones

```python
# Durante la simulación
env = ForestFireEnv()
obs, _ = env.reset()

# Ejecutar pasos
for step in range(100):
    obs, reward, done, _, info = env.step(actions)
    
    # Estadísticas de humedad
    moisture_stats = env.get_fuel_moisture_stats()
    print(f"Actualizaciones: {moisture_stats['updates_count']}")
    print(f"Humedad promedio: {moisture_stats['mean']:.1f}%")
```

### Consultar Datos en MongoDB

```python
from pymongo import MongoClient

client = MongoClient("mongodb+srv://...")
db = client['forestguardian']
collection = db['fuel_moisture_updates']

# Últimas 10 actualizaciones
recent = collection.find().sort('timestamp', -1).limit(10)

for update in recent:
    print(f"Agente {update['agent_id']}: Humedad {update['fuel_moisture']['value']:.1f}%")

# Agregación por agente
pipeline = [
    {'$group': {
        '_id': '$agent_id',
        'avg_moisture': {'$avg': '$fuel_moisture.value'},
        'count': {'$sum': 1}
    }}
]
stats = collection.aggregate(pipeline)
```

---

## 📊 Visualización de Humedad

### Mapa de Calor en Streamlit

```python
import plotly.graph_objects as go

def plot_fuel_moisture_heatmap(fuel_moisture):
    fig = go.Figure(data=go.Heatmap(
        z=fuel_moisture,
        colorscale='RdYlGn_r',  # Rojo (seco) → Verde (húmedo)
        colorbar=dict(title='Humedad (%)')
    ))
    
    fig.update_layout(
        title='Mapa de Humedad del Combustible',
        xaxis_title='Columna',
        yaxis_title='Fila'
    )
    
    return fig

# En Streamlit
st.plotly_chart(plot_fuel_moisture_heatmap(env.fuel_moisture))
```

### Series Temporales de Actualizaciones

```python
# Consultar historial de una celda
cell_history = collection.find({
    'position.row': 15,
    'position.col': 23
}).sort('step', 1)

steps = []
moisture_values = []

for doc in cell_history:
    steps.append(doc['step'])
    moisture_values.append(doc['fuel_moisture']['value'])

# Gráfico
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=steps,
    y=moisture_values,
    mode='lines+markers',
    name='Humedad'
))
fig.update_layout(
    title='Evolución de Humedad en Celda (15, 23)',
    xaxis_title='Paso',
    yaxis_title='Humedad (%)'
)
```

---

## 🧪 Validación del Modelo

### Test 1: Propagación con Viento

```python
env = ForestFireEnv(grid_size=20)
env.reset()

# Configurar viento fuerte hacia el Este
env.wind_speed = 20.0
env.wind_direction = 90.0

# Colocar fuego en centro
env.grid[10, 10] = 2

# Simular 50 pasos
for _ in range(50):
    env.step([4, 4, 4])  # Todos los agentes idle

# Verificar: fuego debe propagarse hacia el Este
fire_positions = np.argwhere(env.grid == 2)
assert np.mean(fire_positions[:, 1]) > 10, "Fuego no se propagó hacia el viento"
```

### Test 2: Efecto de Humedad

```python
# Caso A: Combustible seco
env_dry = ForestFireEnv()
env_dry.reset()
env_dry.fuel_moisture[:, :] = 5.0  # Muy seco

# Caso B: Combustible húmedo
env_wet = ForestFireEnv()
env_wet.reset()
env_wet.fuel_moisture[:, :] = 30.0  # Muy húmedo

# Simular ambos
fires_dry = count_fires_after_50_steps(env_dry)
fires_wet = count_fires_after_50_steps(env_wet)

assert fires_dry > fires_wet * 3, "Humedad no afecta propagación"
```

### Test 3: Asimilación MongoDB

```python
env = ForestFireEnv()
env.reset()

# Mover agente Alpha
env.agent_positions[0] = (5, 5)
env.step([3, 4, 4])  # Alpha mueve derecha

# Verificar inserción en MongoDB
updates = collection.find({'agent_id': 'ALPHA'}).count()
assert updates > 0, "No se guardaron actualizaciones en MongoDB"
```

---

## 📖 Referencias Científicas

1. **Rothermel, R.C. (1972)**  
   *A mathematical model for predicting fire spread in wildland fuels*  
   USDA Forest Service Research Paper INT-115

2. **Finney, M.A. (1998)**  
   *FARSITE: Fire Area Simulator - Model Development and Evaluation*  
   USDA Forest Service Research Paper RMRS-RP-4

3. **Albini, F.A. (1976)**  
   *Estimating Wildfire Behavior and Effects*  
   USDA Forest Service General Technical Report INT-30

4. **Sullivan, A.L. (2009)**  
   *Wildland surface fire spread modelling, 1990-2007*  
   International Journal of Wildland Fire, 18(4):349-368

---

## 🔮 Mejoras Futuras

### v2.1 (Próxima Versión)
- [ ] Tipos de combustible (hierba, arbustos, bosque denso)
- [ ] Humedad atmosférica (afecta humedad del combustible)
- [ ] Temperatura ambiente (acelera secado)
- [ ] Radiación solar (varía con hora del día)

### v3.0 (Largo Plazo)
- [ ] Crown fire (fuego de copas)
- [ ] Spotting (focos secundarios por brasas volantes)
- [ ] Firebrands (propagación a larga distancia)
- [ ] Modelos de combustible Albini/Scott-Burgan

---

## 📞 Soporte

**¿Preguntas sobre el modelo de Rothermel?**

1. Revisa la documentación de USFS: https://www.fs.usda.gov/
2. Paper original: https://www.fs.fed.us/rm/pubs_int/int_rp115.pdf
3. Abre un issue en el repositorio

---

**Última actualización:** 2026-01-19  
**Versión:** 2.0.0  
**Autor:** Forest Guardian RL Team  
**Basado en:** Modelo de Rothermel (USDA Forest Service, 1972)
