# 🌲 Forest Guardian RL - Arquitectura Jerárquica MineRL-Inspired

## 📋 Descripción General

Este proyecto implementa una **Arquitectura de Aprendizaje Jerárquico** inspirada en el proyecto **MineRL Diamond** de Minecraft. En lugar de un único agente monolítico, tenemos múltiples sub-agentes especializados coordinados por un controlador jerárquico.

---

## 🏗️ Componentes de la Arquitectura

### 1. **Operario Agent** (Sub-Agente Basado en Reglas)
**Tipo:** Sistema Hard-coded / Rule-based

**Responsabilidades:**
- Detectar situaciones críticas (fuego adyacente, sin agua, etc.)
- Tomar decisiones inmediatas y confiables basadas en reglas

**Reglas Implementadas:**
```
1. Si estoy en el río (fila 0) y no tengo agua máxima → ESPERAR (recargar)
2. Si hay fuego adyacente y tengo agua → EXTINGUIR FUEGO
3. Si no tengo agua y hay fuego → NAVEGAR AL RÍO
4. Si hay árbol adyacente + fuego + agua baja → CORTAR ÁRBOL (cortafuegos)
5. Si no hay amenaza inmediata → CEDER CONTROL AL NAVEGADOR
```

**Ventajas:**
- ✅ Decisiones instantáneas y predecibles
- ✅ Manejo robusto de emergencias
- ✅ No requiere entrenamiento
- ✅ Fácil de debuggear y entender

---

### 2. **Navegador Agent** (Sub-Agente PPO Neural)
**Tipo:** Red Neuronal (Proximal Policy Optimization)

**Responsabilidades:**
- Aprender navegación estratégica
- Explorar el entorno
- Moverse hacia objetivos (fuegos, río, etc.)
- Mantener comportamiento flexible y adaptativo

**Lo que aprende:**
- Cómo navegar eficientemente hacia fuegos
- Cómo llegar al río para recargar agua
- Cuándo es seguro acercarse a los árboles
- Estrategias para sobrevivir épocas de fuego intenso

**Ventajas:**
- ✅ Aprende patrones complejos
- ✅ Se adapta a diferentes escenarios
- ✅ Mejora continuamente durante el entrenamiento
- ✅ Complementa las limitaciones del Operario

---

### 3. **ForestGuardianManager** (Controlador Jerárquico)
**Tipo:** Coordinador de decisiones

**Flujo de Control:**
```
1. Recibe estado del entorno (observación)
2. Consulta al OPERARIO: ¿Hay situación crítica?
   ├─ SI → OPERARIO toma control
   └─ NO → Consulta al NAVEGADOR
3. NAVEGADOR actúa para movimiento estratégico
4. Ejecuta acción en el entorno
5. Recolecta estadísticas de uso
```

**Estadísticas que Recolecta:**
- Porcentaje de acciones del Operario vs Navegador
- Historial de decisiones
- Métricas de rendimiento por episodio

---

## 📊 Cómo Funciona: Ejemplo Práctico

### Escenario 1: Crisis de Agua
```
Estado: Agent sin agua, fuego adyacente, alejado del río

1. OPERARIO: "¡Sin agua y hay fuego! Navegar al río"
   → Retorna acción: MOVE_UP (hacia fila 0)
2. MANAGER ejecuta MOVE_UP
3. Agent se acerca al río
```

### Escenario 2: En el Río
```
Estado: Agent en fila 0, agua < máximo

1. OPERARIO: "Estoy en el río, debo recargar"
   → Retorna acción: WAIT (recargar)
2. MANAGER ejecuta WAIT
3. water_tank aumenta a máximo
```

### Escenario 3: Exploración Tranquila
```
Estado: Agent con agua, sin fuego cercano, necesita movimiento estratégico

1. OPERARIO: "Ninguna amenaza inmediata"
   → Retorna: None
2. MANAGER: "Llamar al NAVEGADOR"
   → NAVEGADOR usa PPO para decidir movimiento
3. MANAGER ejecuta acción del NAVEGADOR
4. Agent se mueve estratégicamente
```

---

## 🔄 Mejoras respecto a Enfoque Monolítico

| Aspecto | PPO Puro | Jerárquico |
|--------|----------|-----------|
| **Velocidad** | Lento (RL es lento) | Rápido (reglas inmediatas) |
| **Confiabilidad** | Variable | Alta (reglas garantizadas) |
| **Complejidad** | Simple conceptualmente | Complejo pero modular |
| **Explicabilidad** | Caja negra | Explicable (decisiones del Operario claras) |
| **Escalabilidad** | Difícil agregar comportamientos | Fácil agregar más sub-agentes |
| **Tasa de Aprendizaje** | Buena | Mejor (menos casos críticos) |

---

## 🌊 Mejoras al Entorno (forest_fire_env.py)

### Zona del Río (River Zone)
- **Ubicación:** Fila 0
- **Propiedades:** Sin árboles, agua infinita
- **Beneficio:** Punto seguro para recargar agua
- **Recarga en Río:**
  - Cuando haces `WAIT` en fila 0 → `water_tank = max_water` (recarga completa)
  - Cuando haces `WAIT` en otro lugar → `water_tank += 2` (recarga lenta)

### Gestión de Agua Mejorada
```python
# Acción: Extinguish Fire
if water_tank > 0:
    extinguish_fire()
    water_tank -= 1
else:
    penalty = -1  # Aprender a no desperdiciar
    
# Acción: Wait (en río)
if agent_pos[0] == 0:
    water_tank = max_water  # Recarga instantánea
    reward += 2
```

---

## 📈 Entrenamiento y Pruebas

### Fase 1: Entrenamiento del Navegador
```
- Timesteps: 50,000
- Algoritmo: PPO
- Entorno: ForestFireEnv con sistema de agua
- Output: ppo_forest_fire.zip (modelo guardado)
```

### Fase 2: Evaluación Jerárquica
```
- 3 episodios de prueba
- Usa ForestGuardianManager para coordinar agentes
- Mide:
  * Recompensa media
  * Longitud de episodio
  * Porcentaje de uso del Operario
```

### Fase 3: Visualización
```
- Renderiza 6 frames clave de un episodio
- Muestra decisiones del Manager
- Genera: forest_fire_hierarchical_visualization.png
```

---

## 💡 Cómo Extender la Arquitectura

### Agregar un Tercer Sub-Agente (Ejemplo: Bombero Especialista)

```python
class BomberoAgent:
    """Especialista en apagar fuegos grandes"""
    def decide_action(self, obs, fire_positions):
        # Lógica especializada para fuegos extensos
        pass

# En ForestGuardianManager.decide_action():
action1, reason1 = self.operario.decide_action(...)
if action1 is not None:
    return action1
    
action2, reason2 = self.bombero.decide_action(...)
if action2 is not None:
    return action2
    
action3 = self.navegador.decide_action(...)  # Fallback
return action3
```

### Entrenar Múltiples Navegadores Especializados

```python
# Navegador para movimiento
self.nav_movement = NavegadorAgent(model_movement)

# Navegador para combate
self.nav_combat = NavegadorAgent(model_combat)

# Manager elige cuál usar según contexto
```

---

## 🎯 Conceptos Clave (Comparación con MineRL)

### MineRL Diamond (Minecraft)
```
High-level Planner
    ↓
Craftier (Basado en reglas)
    ↓
Miner (Red Neuronal)
    ↓
Ejecutar acciones
```

### Forest Guardian (Nuestro Proyecto)
```
ForestGuardianManager
    ├─ Operario (Reglas - similar a Craftier)
    └─ Navegador (PPO - similar a Miner)
        ↓
Ejecutar acciones
```

---

## 📊 Interpretación de Resultados

### Estadísticas del Manager

```
Total de acciones: 450
  - Operario (Reglas):  180 (40.0%)
  - Navegador (PPO):    270 (60.0%)
```

**Interpretación:**
- El Operario manejó el 40% de decisiones (crisis + recargas)
- El Navegador tuvo el 60% (exploración y movimiento)
- **Balance saludable:** No todos los pasos son emergencias

---

## 🚀 Próximas Mejoras Posibles

1. **Agentes Especializados Adicionales:**
   - Cortador de Cortafuegos (tree-cutting specialist)
   - Predictor de Propagación (fire spread prediction)

2. **Aprendizaje Jerárquico Mejorado:**
   - El Navegador aprende a cumplir objetivos del Operario
   - Transfer learning entre agentes

3. **Comunicación Inter-Agentes:**
   - Operario informa necesidades al Navegador
   - Navegador retroalimenta sobre oportunidades

4. **Meta-learning:**
   - Manager aprende cuándo delegar a cada agente

---

## 🔍 Debugging y Análisis

### Ver Decisiones en Detalle
```
El sistema imprime en cada paso:
- Qué agente decidió (Operario o Navegador)
- Razón de la decisión
- Estado del agua
- Recompensa acumulada
```

### Analizar Historial
```python
manager.operario_action_history  # Ver todas las decisiones del Operario
manager.navegador_action_history  # Ver todas las del Navegador
```

---

## 📝 Conclusión

La arquitectura jerárquica combina lo mejor de ambos mundos:
- **Confiabilidad** del rule-based (Operario)
- **Flexibilidad** del deep learning (Navegador)

Esto es especialmente poderoso para problemas donde:
✅ Hay estados críticos predecibles (agua, fuego cercano)
✅ Necesitas comportamiento robusto y explicable
✅ El aprendizaje RL es lento o inestable
✅ Quieres escalar a múltiples especializaciones

---

**¡Bienvenido a la era del Hierarchical RL! 🎓🔥💧**
