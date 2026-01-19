# ✅ Modelo de Rothermel - Checklist de Verificación

## 🎯 Requisitos Previos

- [ ] Python 3.8+ instalado
- [ ] Dependencias básicas instaladas: `pip install -r requirements.txt`
- [ ] `numpy`, `gymnasium` funcionando correctamente

---

## 🧪 Test Rápido de Funcionalidad

### 1. Verificar Sintaxis

```bash
python -m py_compile forest_fire_env.py
```

**Esperado:** Sin errores ✅

---

### 2. Ejecutar Suite de Tests

```bash
python test_rothermel_model.py
```

**Esperado:** 4/5 tests pasando (1 omitido si no hay MongoDB) ✅

**Tests que deben pasar:**
- ✅ test_wind_directional_propagation
- ✅ test_fuel_moisture_effect
- ✅ test_slope_effect
- ✅ test_rothermel_probability_calculation
- ⚠️ test_mongodb_updates (omitido sin URI)
- ✅ test_fuel_moisture_stats

---

### 3. Test Básico de Entorno

```python
from forest_fire_env import ForestFireEnv
import numpy as np

# Crear entorno
env = ForestFireEnv(grid_size=30)
obs, _ = env.reset()

print("✅ Entorno creado correctamente")

# Verificar fuel_moisture existe
assert env.fuel_moisture is not None
assert env.fuel_moisture.shape == (30, 30)
print(f"✅ Mapa de humedad generado: {env.fuel_moisture.shape}")

# Verificar rango de valores
assert np.all(env.fuel_moisture >= 5.0)
assert np.all(env.fuel_moisture <= 35.0)
print(f"✅ Humedad en rango válido: {env.fuel_moisture.min():.1f}% - {env.fuel_moisture.max():.1f}%")

# Verificar viento
print(f"✅ Viento: {env.wind_speed:.1f} km/h desde {env.wind_direction:.0f}°")

# Verificar elevación
assert env.elevation is not None
print(f"✅ Elevación generada: min={env.elevation.min():.2f}, max={env.elevation.max():.2f}")

# Test de propagación
env.grid[15, 15] = 2  # Colocar fuego
from_pos = (15, 15)
to_pos = (14, 15)  # Norte

prob = env._calculate_fire_spread_probability(from_pos, to_pos)
assert 0.0 <= prob <= 1.0
print(f"✅ Probabilidad de propagación calculada: {prob:.4f}")

# Estadísticas de humedad
stats = env.get_fuel_moisture_stats()
assert 'mean' in stats
assert 'min' in stats
assert 'max' in stats
print(f"✅ Estadísticas de humedad: media={stats['mean']:.1f}%")

print("\n🎉 ¡TODOS LOS TESTS BÁSICOS PASARON!")
```

**Guardar como:** `test_rothermel_basic.py`

```bash
python test_rothermel_basic.py
```

---

### 4. Test de Propagación Direccional

```python
from forest_fire_env import ForestFireEnv
import numpy as np

env = ForestFireEnv(grid_size=25, fire_spread_prob=0.15)
env.reset()

# Configurar viento fuerte hacia el Este
env.wind_speed = 20.0
env.wind_direction = 90.0  # Este

print(f"Viento: {env.wind_speed} km/h hacia {env.wind_direction}°")

# Limpiar y colocar árboles
env.grid[:, :] = 0
for i in range(10, 16):
    for j in range(10, 20):
        env.grid[i, j] = 1  # Árboles

# Fuego en el centro
env.grid[13, 12] = 2

initial_fires = np.sum(env.grid == 2)
print(f"Fuegos iniciales: {initial_fires}")

# Simular 20 pasos
for _ in range(20):
    env.step([4, 4, 4])  # Idle

# Analizar propagación
fire_positions = np.argwhere(env.grid == 2)
if len(fire_positions) > 1:
    mean_col = np.mean(fire_positions[:, 1])
    print(f"Columna media del fuego: {mean_col:.1f}")
    
    if mean_col > 13:
        print("✅ Fuego se propagó a favor del viento (hacia el Este)")
    else:
        print("⚠️ Propagación no claramente direccional (puede ser variabilidad aleatoria)")
else:
    print("⚠️ Fuego no se propagó")
```

**Esperado:** Fuego se propaga hacia el Este ✅

---

### 5. Test de Humedad

```python
from forest_fire_env import ForestFireEnv
import numpy as np

# Caso A: Seco
env_dry = ForestFireEnv(grid_size=20)
env_dry.reset()
env_dry.fuel_moisture[:, :] = 5.0  # Muy seco

env_dry.grid[:, :] = 1
env_dry.grid[10, 10] = 2

for _ in range(30):
    env_dry.step([4, 4, 4])

fires_dry = np.sum(env_dry.grid == 2)
print(f"Fuegos con combustible seco (5%): {fires_dry}")

# Caso B: Húmedo
env_wet = ForestFireEnv(grid_size=20)
env_wet.reset()
env_wet.fuel_moisture[:, :] = 30.0  # Húmedo

env_wet.grid[:, :] = 1
env_wet.grid[10, 10] = 2

for _ in range(30):
    env_wet.step([4, 4, 4])

fires_wet = np.sum(env_wet.grid == 2)
print(f"Fuegos con combustible húmedo (30%): {fires_wet}")

ratio = fires_dry / (fires_wet + 1)
print(f"Ratio: {ratio:.1f}x")

if ratio > 3:
    print("✅ Humedad afecta significativamente la propagación")
else:
    print("⚠️ Efecto de humedad menor al esperado")
```

**Esperado:** Ratio > 3x ✅

---

## 🛰️ Test de MongoDB Atlas (Opcional)

### Configurar URI

```bash
export MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/"
```

O en Python:

```python
import os
os.environ['MONGODB_URI'] = "mongodb+srv://..."
```

### Test de Conexión

```python
from forest_fire_env import ForestFireEnv

env = ForestFireEnv(grid_size=20)
env.reset()

if env.mongodb_enabled:
    print("✅ MongoDB conectado")
    print(f"   Collection: {env.mongodb_collection.name}")
else:
    print("⚠️ MongoDB no configurado")
```

### Test de Actualización

```python
from forest_fire_env import ForestFireEnv

env = ForestFireEnv(grid_size=15)
env.reset()

if env.mongodb_enabled:
    # Contar documentos antes
    count_before = env.mongodb_collection.count_documents({})
    
    # Mover agentes
    for _ in range(5):
        env.step([0, 1, 2])  # Movimientos variados
    
    # Contar después
    count_after = env.mongodb_collection.count_documents({})
    
    updates = count_after - count_before
    print(f"Actualizaciones generadas: {updates}")
    
    if updates > 0:
        print("✅ Asimilación UAV funcionando")
    else:
        print("⚠️ No se guardaron actualizaciones")
else:
    print("⚠️ MongoDB no configurado - test omitido")
```

---

## 📊 Verificación de Métricas

### Rango de Valores Esperados

| Métrica | Rango Esperado | Verificación |
|---------|---------------|--------------|
| Humedad del combustible | 5-35% | [ ] |
| Elevación | 0-1 | [ ] |
| Viento (velocidad) | 0-20 km/h | [ ] |
| Viento (dirección) | 0-360° | [ ] |
| Probabilidad base | 0.1 (10%) | [ ] |
| Probabilidad mínima | ~0.01-0.05 | [ ] |
| Probabilidad máxima | ~0.5-1.0 | [ ] |
| Rango dinámico | >10x | [ ] |

### Verificación Manual

```python
from forest_fire_env import ForestFireEnv

env = ForestFireEnv()
env.reset()

# Humedad
stats = env.get_fuel_moisture_stats()
print(f"Humedad: {stats['min']:.1f}% - {stats['max']:.1f}% (media: {stats['mean']:.1f}%)")
assert 5 <= stats['min'] <= 35
assert 5 <= stats['max'] <= 35

# Viento
wind = env.get_wind_info()
print(f"Viento: {wind['speed']:.1f} km/h {wind['direction_name']} ({wind['direction']:.0f}°)")
assert 0 <= wind['speed'] <= 50
assert 0 <= wind['direction'] < 360

# Elevación
print(f"Elevación: {env.elevation.min():.2f} - {env.elevation.max():.2f}")
assert 0 <= env.elevation.min() <= 1
assert 0 <= env.elevation.max() <= 1

print("✅ Todas las métricas en rangos válidos")
```

---

## 🎨 Integración con Streamlit

### Test de Compatibilidad

```bash
streamlit run app.py
```

**Verificar:**
- [ ] Aplicación inicia sin errores
- [ ] Puede iniciar simulación
- [ ] No hay excepciones en terminal
- [ ] GIF se genera correctamente
- [ ] Métricas se actualizan

**Si hay errores:**
1. Verificar que `forest_fire_env.py` está en el directorio
2. Verificar imports en `app.py`
3. Revisar logs en terminal

---

## 📝 Troubleshooting

### Error: "AttributeError: 'ForestFireEnv' object has no attribute 'fuel_moisture'"

**Causa:** Entorno no inicializado con `reset()`

**Solución:**
```python
env = ForestFireEnv()
obs, _ = env.reset()  # Importante!
```

### Error: "ValueError: setting an array element with a sequence"

**Causa:** Tipo de datos incorrecto en fuel_moisture

**Solución:** Ya corregido en implementación (usa `.astype(np.float32)`)

### Warning: "MongoDB URI no configurado"

**Causa:** Variable de entorno `MONGODB_URI` no establecida

**Solución (opcional):**
```bash
export MONGODB_URI="mongodb+srv://..."
```

Si no necesitas asimilación UAV, puedes ignorar este warning.

### Tests fallan esporádicamente

**Causa:** Propagación estocástica del fuego

**Solución:** Ejecutar tests varias veces o ajustar umbrales en `test_rothermel_model.py`

---

## ✅ Checklist Final

- [ ] ✅ `forest_fire_env.py` compila sin errores
- [ ] ✅ Tests básicos pasan (4/5)
- [ ] ✅ Entorno se puede crear y resetear
- [ ] ✅ Humedad está en rango 5-35%
- [ ] ✅ Viento se genera correctamente
- [ ] ✅ Probabilidad de propagación es dinámica
- [ ] ✅ Propagación direccional funciona
- [ ] ✅ Efecto de humedad es significativo (>3x)
- [ ] ✅ Streamlit app funciona correctamente
- [ ] ⚠️ MongoDB conectado (opcional)

---

## 🎓 Verificación Avanzada

### Test de Sensibilidad Paramétrica

```python
import numpy as np
from forest_fire_env import ForestFireEnv

# Variar viento
for wind_speed in [0, 5, 10, 20]:
    env = ForestFireEnv()
    env.reset()
    env.wind_speed = wind_speed
    
    prob = env._calculate_fire_spread_probability((10, 10), (9, 10))
    print(f"Viento {wind_speed:2d} km/h → P = {prob:.4f}")

# Variar humedad
for moisture in [5, 15, 25, 35]:
    env = ForestFireEnv()
    env.reset()
    env.fuel_moisture[:, :] = moisture
    
    prob = env._calculate_fire_spread_probability((10, 10), (9, 10))
    print(f"Humedad {moisture:2d}% → P = {prob:.4f}")
```

**Esperado:** 
- Probabilidad aumenta con mayor viento
- Probabilidad disminuye con mayor humedad

---

## 📞 Soporte

Si algún test falla:

1. Ejecuta `python test_rothermel_model.py` para diagnosticar
2. Revisa [ROTHERMEL_MODEL_README.md](ROTHERMEL_MODEL_README.md)
3. Verifica versiones: `pip show numpy gymnasium`
4. Reporta issue con output completo de tests

---

**Estado del sistema:** [ ] 🟢 FUNCIONANDO | [ ] 🟡 PARCIAL | [ ] 🔴 ERRORES

**Fecha de verificación:** ________________  
**Verificado por:** ________________
