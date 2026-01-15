# 🔧 Detalles Técnicos de Implementación

## 1. Modificaciones a forest_fire_env.py

### 1.1 Inicialización con Zona del Río

```python
def __init__(self, grid_size=10, fire_spread_prob=0.5, initial_trees=0.6, initial_fires=3):
    # ...
    # River zone: Row 0 is a water source (River/Base)
    self.river_row = 0  # ← Fila 0 es la zona del río
```

**Impacto:**
- Define dónde está la fuente de agua
- Facilita navegación (el agente sabe: si row==0, hay agua)

---

### 1.2 Reset con Zona del Río Limpia

```python
def reset(self, seed=None, options=None):
    # ...
    # Clear river zone (row 0) from trees to make it accessible
    self.grid[self.river_row, :] = 0  # ← Limpia la fila 0
    
    # Ahora place_fires sabe que la fila 0 es segura
```

**Impacto:**
- La fila 0 nunca tiene árboles, es siempre segura
- El agente puede llegar al río sin obstáculos
- Estrategia clara: cuando tengas miedo, corre al río

---

### 1.3 Acción Wait Mejorada

```python
elif action == 6:  # Wait
    if self.agent_pos[0] == self.river_row:
        # En el río: recarga completa e instantánea
        self.water_tank = self.max_water  # De 0 a 10 en 1 paso!
        reward += 2  # Bonificación por llegar al agua
    else:
        # En otro lugar: recarga lenta
        self.water_tank = min(self.water_tank + 2, self.max_water)
```

**Impacto:**
- **Costo-Beneficio claro:** Ir al río es rápido pero implica abandona área de fuegos
- **Estrategia emergente:** El agente aprende a equilibrar:
  - Apagar fuegos (consumir agua)
  - Recargar agua (ir al río)

---

## 2. Arquitectura de train_and_test.py

### 2.1 Clase OperarioAgent (Rule-based)

**Estructura:**
```python
class OperarioAgent:
    def decide_action(obs, agent_pos, water_level, max_water):
        # Examina la observación
        # Evalúa reglas en orden de prioridad
        # Retorna (action, reason) o (None, reason)
```

**Lógica de Decisión (Orden Crítico):**

| Prioridad | Condición | Acción | Razón |
|-----------|-----------|--------|-------|
| 1️⃣ **CRÍTICA** | En río + agua < máx | WAIT (6) | Recargar agua |
| 2️⃣ **CRÍTICA** | Fuego adyacente + agua > 0 | EXTINGUISH (5) | Combatir fuego |
| 3️⃣ **ALTA** | Sin agua + hay fuego | MOVE_UP (0) | Huir al río |
| 4️⃣ **MEDIA** | Árbol adyacente + fuego + agua baja | CUT (4) | Crear cortafuegos |
| 5️⃣ **BAJA** | Ninguna de arriba | None | Dejar al Navegador |

**Ventaja del Orden:**
- Si estoy en el río sin agua máxima → NO me distraeré apagando fuegos, me recargaré
- Si tengo agua y hay fuego adyacente → COMBATIR ES PRIORITARIO
- Si no tengo agua pero hay fuego → HUIR es mejor que quedarse

**Implementación del Operario:**
```python
# Detectar fuego adyacente
neighbors = [(row-1,col), (row+1,col), (row,col-1), (row,col+1)]
for n_row, n_col in neighbors:
    if grid[n_row, n_col] == 2:  # 2 = Fire
        adjacent_fire = True
        fire_count_nearby += 1

# Aplicar reglas en orden
if row == 0 and water_level < max_water:
    return 6, "Recargando agua en el río"
    
if adjacent_fire and water_level > 0:
    return 5, f"Extinguiendo fuego ({fire_count_nearby} fires)"
    
if water_level == 0 and fire_count_nearby > 0:
    return 0, "Sin agua! Navegando al río"

# ... más reglas ...

# Si nada aplica
return None, "No hay amenaza - Navegante toma control"
```

---

### 2.2 Clase NavegadorAgent (PPO Neural)

**Wrapper alrededor del modelo entrenado:**
```python
class NavegadorAgent:
    def __init__(self, model):
        self.model = model  # Modelo PPO guardado
    
    def decide_action(self, obs):
        action, _states = self.model.predict(obs, deterministic=True)
        return action
```

**Características:**
- Usa el modelo PPO ya entrenado
- Determinístico (`deterministic=True`) para reproducibilidad en tests
- Simple: solo predice la acción

**Qué ha Aprendido:**
Después de 50,000 timesteps, el modelo ha aprendido patrones como:
- "Acércate a los fuegos para extinguirlos"
- "Si estás perdido, ve hacia arriba (río)"
- "Rodea los árboles cuando puedas"
- "Mantente en movimiento para explorar"

---

### 2.3 Clase ForestGuardianManager (Coordinador)

**Flujo Principal:**
```python
def decide_action(obs, agent_pos, water_level, max_water):
    # Paso 1: Consultar Operario
    action, reason = self.operario.decide_action(...)
    
    if action is not None:
        # El Operario tiene una decisión → usar
        self.operario_actions += 1
        return action, "Operario (Rule-based)", reason
    
    else:
        # El Operario no tiene regla → usar Navegador
        action = self.navegador.decide_action(obs)
        self.navegador_actions += 1
        return action, "Navegador (PPO)", "Strategic movement"
```

**Estadísticas que Rastrea:**
```python
self.operario_actions       # Cuántas decisiones tomó Operario
self.navegador_actions      # Cuántas decisiones tomó Navegador
self.operario_action_history    # Qué decidió cada vez
self.navegador_action_history   # Qué hizo Navegador cada vez
```

**Método de Reporte:**
```python
def print_statistics(self):
    total = self.operario_actions + self.navegador_actions
    operario_pct = (self.operario_actions / total) * 100
    
    # Imprime en formato visual
    print(f"Operario: {self.operario_actions} ({operario_pct:.1f}%)")
    print(f"Navegador: {self.navegador_actions} ({100-operario_pct:.1f}%)")
```

---

## 3. Flujo Completo de Entrenamiento y Prueba

### Fase 1: Entrenamiento del Navegador (50,000 timesteps)

```
1. Crear ForestFireEnv
   ├─ Grid: 10x10
   ├─ Fila 0: Zona del río (sin árboles)
   ├─ Filas 1-9: Bosque con árboles y fuegos
   └─ Sistema de agua: 0-10 unidades

2. Crear modelo PPO
   ├─ Policy: "MlpPolicy" (Red Neuronal Simple)
   ├─ Learning Rate: 3e-4
   ├─ Pasos por actualización: 2048
   └─ Épocas de entrenamiento: 10

3. Entrenar 50,000 timesteps
   ├─ El modelo ve miles de estados del bosque
   ├─ Aprende qué acciones generan más recompensa
   ├─ Gradualmente mejora su estrategia
   └─ Se guarda como ppo_forest_fire.zip

Tiempo aprox: 5-10 minutos (dependiendo del hardware)
```

### Fase 2: Evaluación con Manager Jerárquico

```
Para cada episodio de prueba (3 total):

Loop Principal:
┌─────────────────────────────────────────────┐
│ 1. Observar estado actual (grid 10x10)      │
│ 2. Llamar ForestGuardianManager              │
│    ├─ OperarioAgent evalúa reglas           │
│    └─ NavegadorAgent (si necesario)         │
│ 3. Ejecutar acción elegida                  │
│ 4. Fuego se propaga (50% chance)            │
│ 5. Registrar recompensa                     │
│ 6. Contar pasos (termina en 200 o victoria) │
└─────────────────────────────────────────────┘

Recopila:
- Total de recompensa por episodio
- Longitud (pasos) de cada episodio
- Porcentaje de uso Operario vs Navegador
- Árboles y fuegos restantes
```

---

## 4. Métricas y KPIs

### 4.1 Recompensa (Reward)

```python
reward = 0

# Durante ejecución de acción
reward += 1        # Si corta un árbol
reward += 10       # Si extingue un fuego
reward -= 1        # Si intenta extinguir sin agua
reward += 2        # Si recarga en el río

# Después de que el fuego se propaga
reward -= 0.1 * active_fires  # Penalidad por cada fuego activo

# Eventos terminales
reward += 50       # Todos los fuegos extinguidos
reward -= 100      # 80%+ del bosque destruido
```

**Objetivo:** Maximizar recompensa total

---

### 4.2 Episodio (Episode)

**Termina cuando:**
1. ✅ Todos los fuegos se extinguen → `reward += 50`
2. ❌ 80%+ de árboles quemados → `reward -= 100`
3. ⏱️ 200 pasos ejecutados → `truncated = True`

**Métrica:** `episode_length` (cuántos pasos tardó)
- Menos pasos = más eficiente
- Pero debe ser suficiente para ganar

---

### 4.3 Uso del Operario

```python
operario_usage = (operario_actions / total_actions) * 100
```

**Interpretación:**
- **0-20%:** Pocos fuegos, navegador hace la mayoría
- **30-50%:** Balance saludable (situaciones variadas)
- **70-100%:** Muchos fuegos (Operario constantemente ocupado)

---

## 5. Flujo de Decisión Visualizado

```
┌─────────────────────────────────────────┐
│ Estado Actual del Entorno               │
│ (Grid 10x10, agua, posición)            │
└──────────────┬──────────────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │ ForestGuardianManager │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │ Operario.decide()    │
    │ (evalúa reglas)      │
    └──────┬───────────────┘
           │
           ├─ ¿Hay regla? 
           │    YES ──────┐
           │              ▼
           │    ┌─────────────────────┐
           │    │ return (action, msg) │
           │    │  Operario controla  │
           │    └────────┬────────────┘
           │             │
           NO            │
           │             │
           ▼             │
    ┌──────────────────────────┐
    │ Navegador.decide(obs)    │
    │ (usa modelo PPO)         │
    │ return (action)          │
    │ Navegador controla       │
    └──────┬───────────────────┘
           │
           └────────┬────────────┘
                    │
                    ▼
         ┌─────────────────────┐
         │ Manager retorna:    │
         │ (action, agent_name,│
         │  reason)            │
         └────────┬────────────┘
                  │
                  ▼
       ┌────────────────────┐
       │ Ejecutar en Entorno │
       │ (env.step(action)) │
       └────────────────────┘
```

---

## 6. Ejemplo de Ejecución Paso a Paso

### Escenario: Agent in Danger

```
Estado Inicial:
┌─────────────────────────┐
│ Agent: (5, 5)           │
│ Water: 2/10             │
│ Fuego adyacente: SÍ     │
└─────────────────────────┘

Paso 1: Manager llama Operario
├─ Detecta: fire at (5,6) [derecha]
├─ Evalúa: adjacent_fire=True, water_level=2
├─ Regla 2 aplica: "Si fuego adyacente + agua → EXTINGUISH"
└─ Retorna: (5, "Extinguir fuego")

Paso 2: Manager ejecuta acción 5 (EXTINGUISH)
├─ Fuego en (5,6) se extingue ✓
├─ Water: 2 → 1
└─ Reward: +10

Paso 3: Fuego se propaga
├─ Fuego original (4,5) intenta propagarse
├─ Prob 50%, digamos que se propaga a (3,5)
└─ Ahora hay fuego en (3,5) (no adyacente)

Paso 4: Manager llama Operario
├─ Detecta: sin fuego adyacente
├─ Water: 1 > 0 pero no amenaza inmediata
├─ Regla 2: NO aplica (sin fuego adyacente)
├─ Regla 3: NO aplica (water > 0)
├─ Ninguna regla aplica → return None
└─ Manager cede control al NAVEGADOR

Paso 5: Manager llama Navegador
├─ Observa: Grid con fuego en (3,5)
├─ PPO recomienda: acción 0 (MOVE_UP)
└─ Retorna: 0

Paso 6: Manager ejecuta acción 0 (MOVE_UP)
├─ Agent: (5,5) → (4,5)
├─ Reward: pequeño penalty por fuego cercano -0.1
└─ Estado actualizado
```

**Estadísticas después de estos pasos:**
```
operario_actions: 1  (un paso con Operario)
navegador_actions: 1  (un paso con Navegador)
```

---

## 7. Ventajas Técnicas de esta Arquitectura

### Computacionales
```
PPO Puro:
- Predice en CADA paso (red neuronal)
- 50,000 timesteps × 1 predicción = 50k

Jerárquico:
- 30% Reglas (muy rápido)
- 70% Predicciones (red neuronal)
- 50,000 × 0.7 = 35k predicciones (30% más rápido!)
```

### Robustez
```
PPO Puro:
- Si el modelo predice "EXTINGUISH" sin agua → desperdicio
- Si predice "MOVE AWAY" estando en río → mal entrenado

Jerárquico:
- Operario GARANTIZA: "Si agua=0, nunca EXTINGUISH"
- Operario GARANTIZA: "Si en río, recargará agua"
```

### Mantenibilidad
```
PPO Puro:
- Para cambiar "cómo se extinguen fuegos" → reentrenar todo

Jerárquico:
- Para cambiar "cómo se extinguen fuegos" → editar regla en Operario
- Rápido, no requiere reentrenamiento
```

---

## 8. Cómo Debuggear

### Ver qué hace cada agente:

```python
# En test_agent, cada 10 pasos:
if steps % 10 == 0:
    action, agent_name, reason = manager.decide_action(...)
    print(f"Step {steps}: {agent_name} → {reason}")
    
# Output:
# Step 10: Operario (Rule-based System) → Extinguiendo fuego (2 fires)
# Step 20: Navegador (PPO Neural Network) → Strategic movement
# Step 30: Operario (Rule-based System) → Recargando agua en el río
```

### Analizar decisiones después del episodio:

```python
print("Todas las decisiones del Operario:")
for i, decision in enumerate(manager.operario_action_history):
    print(f"  {i}: {decision}")

print("\nTodas las decisiones del Navegador:")
for i, decision in enumerate(manager.navegador_action_history):
    print(f"  {i}: {decision}")
```

---

## 9. Extensiones Futuras

### Easy: Agregar nueva regla al Operario
```python
# En OperarioAgent.decide_action():
# Regla 5 (nueva): Si 3+ árboles adyacentes → CUT
if tree_count_nearby >= 3:
    return 4, "Creando barrera de seguridad"
```

### Medium: Agregar sub-agente especializado
```python
class BomberoAgent:  # Experto en fuegos grandes
    def decide_action(self, obs, fire_count):
        if fire_count >= 5:
            return ...  # estrategia específica

# En Manager:
action1 = self.operario.decide_action(...)
if action1: return action1

action2 = self.bombero.decide_action(...)  # NUEVO
if action2: return action2

action3 = self.navegador.decide_action(...)
return action3
```

### Hard: Entrenar Navegador Especializado
```python
# Navegador para movimiento
self.nav_movement = PPO(...)
self.nav_movement.learn(50000)

# Navegador para combate
self.nav_combat = PPO(...)
self.nav_combat.learn(50000)

# Manager elige el correcto
if water_level > 5:  # Tengo agua
    return self.nav_combat.predict(obs)
else:
    return self.nav_movement.predict(obs)
```

---

**¡Ahora entiendes cómo funciona cada pieza! 🧩**
