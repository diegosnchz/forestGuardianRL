# 🧠 Sistema XAI (Explainable AI) - Forest Guardian RL

## Descripción General

El sistema **XAI (Explainable AI)** de Forest Guardian RL proporciona interpretabilidad completa de las decisiones tomadas por los agentes autónomos (ALPHA y BRAVO). En lugar de ser una "caja negra", ahora puedes entender **por qué** cada agente toma cada acción, **qué factores** influyen más, y **cómo** se distribuye la atención en el mapa.

### Componentes Principales

```
XAI System (Sistema de Inteligencia Explicable)
├── 🎯 Decisiones (AgentDecision)
│   └── Captura contexto completo de cada decisión
├── 🗺️ Mapas de Atención (Attention Maps)
│   └── Visualización de qué influye más en cada decisión
├── 📊 Importancia de Atributos (Importance Scores)
│   └── Cuantificación de influencia de cada factor
├── ⚔️ Razonamiento Táctico (Tactical Reasoning)
│   └── Justificación role-específica para cada decisión
└── 📈 Historiales y Análisis (History & Analytics)
    └── Seguimiento y comparación multi-agente
```

---

## 1. Conceptos Fundamentales

### 1.1 AgentDecision (Decisión del Agente)

Cada decisión captura:

```python
@dataclass
class AgentDecision:
    timestamp: datetime          # Cuándo se tomó
    agent_id: str               # Identificador único (ALPHA, BRAVO)
    agent_role: str             # Rol táctico (nearest, farthest)
    position: Tuple[int, int]   # Posición actual del agente
    action: int                 # Código de acción (0-6)
    action_name: str            # Nombre descriptivo ("Mover Arriba", etc.)
    grid_state: np.ndarray      # Estado del entorno
    explanation: str            # Explicación textual
    tactical_reasoning: str     # Razonamiento táctico
    attention_map: np.ndarray   # Mapa de atención (matriz 0-1)
    importance_scores: Dict     # Importancia de cada factor
    alternative_actions: List   # Alternativas consideradas
    confidence: float           # Confianza en la decisión (0-1)
    distance_to_target: float   # Distancia al objetivo
    water_level: int            # Agua disponible en tanque
```

### 1.2 Roles de Agentes

| Rol | Agente | Estrategia | Objetivo |
|-----|--------|-----------|----------|
| **nearest** | ALPHA 🔵 | Respuesta Rápida | Minimizar tiempo de respuesta |
| **farthest** | BRAVO 🟠 | Contención Periférica | Prevenir propagación en perímetro |

### 1.3 Acciones Disponibles

```
0: Mover Arriba ⬆️
1: Mover Abajo ⬇️
2: Mover Izquierda ⬅️
3: Mover Derecha ➡️
4: Idle (Esperar) ⏸️
5: Apagar Fuego (radio 3x3) 🚒
6: Construir Cortafuegos 🔥
```

---

## 2. Sistema de Importancia de Atributos

### 2.1 Factores Analizados

El sistema XAI evalúa **8 factores clave** que influyen en las decisiones:

#### **1. Proximidad al Fuego** (proximidad_fuego)
- **Peso**: Variable (alto para ALPHA, bajo para BRAVO)
- **Descripción**: Distancia en celdas al fuego más cercano
- **Rango**: 0-100 (normalizado por tamaño del grid)
- **Fórmula**: `1.0 - (min_distance / max_distance)`

#### **2. Cantidad de Fuegos** (cantidad_fuegos)
- **Peso**: Moderado
- **Descripción**: Número total de focos activos
- **Rango**: 0-100 (normalizado)
- **Fórmula**: `num_fires / max_possible_fires`

#### **3. Cobertura Periférica** (cobertura_perimetral)
- **Peso**: Alto para BRAVO, bajo para ALPHA
- **Descripción**: Máxima distancia al perímetro (solo BRAVO)
- **Rango**: 0-1
- **Fórmula**: Análisis de posiciones en borde

#### **4. Árboles en Riesgo** (arboles_en_riesgo)
- **Peso**: Moderado-alto
- **Descripción**: Árboles adyacentes a fuegos
- **Rango**: 0-100
- **Fórmula**: Conteo ponderado por proximidad

#### **5. Densidad Local de Árboles** (densidad_arboles_local)
- **Peso**: Bajo-moderado
- **Descripción**: Cantidad de árboles en radio 3
- **Rango**: 0-1
- **Fórmula**: `trees_in_radius / max_possible`

#### **6. Centralidad del Agente** (centralidad)
- **Peso**: Bajo
- **Descripción**: Qué tan alejado está del centro
- **Rango**: 0-1
- **Fórmula**: Distancia euclidiana al centro normalizada

#### **7. Influencia del Viento** (influencia_viento)
- **Peso**: Moderado (si está disponible)
- **Descripción**: Magnitud del vector de viento
- **Rango**: 0-1
- **Fórmula**: `vector_magnitude / max_wind`

#### **8. Factor de Elevación** (factor_elevacion)
- **Peso**: Bajo (si está disponible)
- **Descripción**: Promedio de elevación en radio
- **Rango**: 0-1
- **Fórmula**: Normalización de altura

### 2.2 Visualización de Importancia

```
Importancia de Atributos - ALPHA
═════════════════════════════════════════════════════════════════

Proximidad Fuego        ██████████ 85.2%
Cantidad Fuegos         ██████░░░░ 62.5%
Arboles En Riesgo       ████░░░░░░ 48.3%
Densidad Arboles       ███░░░░░░░ 32.1%
Centralidad            ██░░░░░░░░ 15.7%
Influencia Viento      ░░░░░░░░░░  0.0%
Factor Elevacion       ░░░░░░░░░░  0.0%
```

---

## 3. Mapas de Atención (Attention Maps)

Los **mapas de atención** muestran visualmente dónde se concentra la "atención" del agente.

### 3.1 Cómo se Generan

```python
# Matriz de atención (0-1)
attention_map = np.zeros((grid_size, grid_size))

# 1. Posición del agente: MÁXIMA atención (1.0)
attention_map[agent_r, agent_c] = 1.0

# 2. Posición del fuego objetivo: atención alta (0.9)
attention_map[fire_r, fire_c] = 0.9

# 3. Camino entre agente y fuego: atención gradual (0.1-0.5)
for cell in path:
    attention_map[cell] = 0.1 + (0.4 * proximity_to_target)

# 4. GAMMA (cortafuegos): atención en árboles cerca de fuegos (0.6)
for tree in trees_near_fires:
    attention_map[tree_r, tree_c] = 0.6
```

### 3.2 Interpretación Visual

```
Mapa de Atención - ALPHA
════════════════════════════════════════════════════════════════

Rojo Oscuro (1.0)    ▓▓▓   Máxima atención - Posición del agente
Rojo Brillante (0.9) ░░░   Objetivo principal - Fuego a extinguir
Naranja (0.5)        ░░░   Ruta estratégica
Amarillo (0.2)       ░░░   Área de influencia
Blanco (0.0)         ░░░   Zona no relevante
```

### 3.3 Caso de Uso: Entendiendo una Decisión

```
Decisión: ALPHA - Mover Abajo

📊 Mapa de Atención:
   - Máxima atención en fuego a 2 celdas sur
   - Ruta clara hacia el objetivo
   - Árboles en riesgo detectados

💡 Interpretación:
   "El agente ve claramente el fuego abajo y se mueve directo"

⚔️ Razonamiento Táctico ALPHA:
   "Respuesta Rápida - Amenaza inmediata a 2 celdas"
```

---

## 4. Razonamiento Táctico Role-Específico

### 4.1 ALPHA - Respuesta Rápida (Nearest)

**Doctrina Operacional:**
- ✅ Minimizar tiempo de respuesta
- ✅ Priorizar amenazas inmediatas
- ✅ Supresión directa de fuegos

**Patrones de Decisión:**
```
CONDICIÓN                    ACCIÓN ESPERADA
════════════════════════════════════════════════════════════════
Fuego a <3 celdas           Movimiento directo hacia fuego
Fuego cercano + árboles     Apagar si es accesible
En posición de apagar        Extinguir incendio (acción 5)
Fuego lejano                 Buscar fuego más cercano
```

**Ejemplo de Explicación ALPHA:**
```
🔵 TÁCTICA ALPHA - RESPUESTA RÁPIDA

Doctrina Operacional:
• Minimizar tiempo de respuesta
• Priorizar amenazas inmediatas
• Supresión directa de fuegos

Estado: 🏃 Aproximación rápida
ETA: 2 movimientos

Análisis: Fuego detectado a 2 celdas al sur
Acción: Mover Abajo para aproximarse rápidamente
```

### 4.2 BRAVO - Contención Periférica (Farthest)

**Doctrina Operacional:**
- ✅ Prevenir propagación en perímetro
- ✅ Proteger áreas aún no afectadas
- ✅ Crear defensa en profundidad

**Patrones de Decisión:**
```
CONDICIÓN                    ACCIÓN ESPERADA
════════════════════════════════════════════════════════════════
Fuego cercano pero ALPHA    Ignorar (dejar a ALPHA)
Fuego en perímetro          Aproximarse a defender
Múltiples fuegos lejanos    Analizar patrón de propagación
Riesgo de expansión         Cortafuegos preventivo
```

**Ejemplo de Explicación BRAVO:**
```
🟠 TÁCTICA BRAVO - CONTENCIÓN PERIFÉRICA

Doctrina Operacional:
• Prevenir propagación en perímetro
• Proteger áreas aún no afectadas
• Crear defensa en profundidad

Estado: 🛡️ Vigilancia del perímetro
Posición Estratégica: Esquina NE (máxima cobertura)

Análisis: ALPHA maneja fuego cercano
Acción: Patrullar perímetro y preparar defensa
```

---

## 5. Cómo Usar el Sistema XAI

### 5.1 En Streamlit (Aplicación Web)

#### **Pestaña 6: Explicabilidad IA (XAI)**

```
🧠 Explicabilidad IA (XAI) - Análisis de Decisiones
└── Selectores
    ├── Agente (ALPHA / BRAVO)
    └── Paso de Simulación
    
└── Sub-pestañas
    ├── 📊 Última Decisión
    │   ├── Razonamiento Táctico Completo
    │   ├── Importancia de Atributos (gráfico)
    │   └── Alternativas Consideradas
    │
    ├── 📈 Evolución Temporal
    │   ├── Timeline de Distancia/Confianza/Agua
    │   ├── Distribución de Acciones
    │   ├── Scatter: Confianza vs Distancia
    │   └── Heatmap de Importancia Evolutiva
    │
    ├── 🗺️ Mapas de Atención por Paso
    │   ├── Slider para seleccionar paso
    │   ├── Visualización de Atención
    │   ├── Explicación de la Decisión
    │   └── Razonamiento Táctico Detallado
    │
    └── 📉 Análisis Estadístico Multi-Agente
        ├── Comparación de Agentes
        ├── Métricas Globales
        ├── Historial Tabular
        └── Exportación a JSON
```

### 5.2 En Código Python

#### **Inicializar el Explainer**

```python
from xai_explainer import XAIExplainer

# Crear explainer para grid 10x10
explainer = XAIExplainer(grid_size=10, enable_mongodb=False)
```

#### **Generar Explicación de Decisión**

```python
# Después de que ALPHA toma una decisión
decision = explainer.explain_decision(
    agent_id="ALPHA",
    agent_role="nearest",
    position=(5, 5),           # Posición actual
    action=1,                  # Código de acción
    grid_state=obs,            # Estado del entorno
    obs={'step': step},        # Observaciones extras
    water_level=env.water_tanks[0]  # Agua disponible
)

# Acceder a los datos
print(decision.explanation)          # Texto explicativo
print(decision.tactical_reasoning)   # Razonamiento táctico
print(decision.importance_scores)    # Factores de importancia
print(decision.confidence)           # Confianza (0-1)
```

#### **Visualizar Mapas de Atención**

```python
from xai_visualization import create_attention_heatmap
import matplotlib.pyplot as plt

# Crear y mostrar mapa
fig = create_attention_heatmap(
    attention_map=decision.attention_map,
    grid_state=decision.grid_state,
    agent_position=decision.position,
    title="Análisis de Atención ALPHA"
)

plt.show()
```

#### **Generar Gráficos de Importancia**

```python
from xai_visualization import create_importance_chart

fig = create_importance_chart(
    importance_scores=decision.importance_scores,
    title="Factores de Decisión"
)

fig.show()
```

#### **Analizar Múltiples Decisiones**

```python
from xai_visualization import (
    create_decision_timeline,
    create_action_distribution_chart,
    create_multi_agent_comparison
)

# Timeline de distancia al objetivo
fig_timeline = create_decision_timeline(
    decisions=agent_decisions,
    metric='distance_to_target'
)

# Distribución de acciones
fig_actions = create_action_distribution_chart(agent_decisions)

# Comparación multi-agente
fig_comparison = create_multi_agent_comparison({
    'ALPHA': alpha_decisions,
    'BRAVO': bravo_decisions
})
```

#### **Exportar Reportes**

```python
from xai_visualization import export_decision_report

# Exportar una decisión
export_decision_report(decision, "reporte_alpha_paso_42.html")

# Exportar historial completo
explainer.export_history("historial_completo.json")
```

### 5.3 En train_and_test.py (Integración Completa)

```python
from xai_explainer import XAIExplainer

def make_the_magic(conf):
    """
    Función principal con integración XAI
    """
    # ... código existente ...
    
    # Inicializar explainer
    xai_explainer = XAIExplainer(grid_size=conf['grid_size'], enable_mongodb=False)
    
    # En el loop principal de simulación
    while not done:
        # Decisiones de agentes
        action_blue = agent_blue.decide(obs, positions[0])
        action_orange = agent_orange.decide(obs, positions[1])
        
        # GENERAR EXPLICACIONES XAI (nuevo)
        decision_blue = xai_explainer.explain_decision(
            agent_id="ALPHA",
            agent_role="nearest",
            position=positions[0],
            action=action_blue,
            grid_state=obs.copy(),
            obs={'step': step},
            water_level=water_tanks[0]
        )
        
        decision_orange = xai_explainer.explain_decision(
            agent_id="BRAVO",
            agent_role="farthest",
            position=positions[1],
            action=action_orange,
            grid_state=obs.copy(),
            obs={'step': step},
            water_level=water_tanks[1]
        )
        
        # Guardar decisiones para análisis posterior
        all_decisions.append(decision_blue)
        all_decisions.append(decision_orange)
        
        # Ejecutar simulación
        obs, reward, terminated, truncated, info = env.step(...)
        
        step += 1
    
    # Exportar análisis final
    xai_explainer.export_history("analisis_mision_xai.json")
    
    return results
```

---

## 6. Casos de Uso Prácticos

### 6.1 Debuggear Comportamiento Anómalo

**Problema**: "¿Por qué BRAVO ignora un fuego cercano?"

**Solución XAI**:
1. Ir a pestaña "Explicabilidad IA"
2. Seleccionar agente "BRAVO"
3. Encontrar el paso problemático
4. Revisar mapa de atención → "Ahh, ALPHA ya está manejando ese fuego"
5. Revisar razonamiento táctico → "BRAVO prioriza perímetro sobre fuegos cercanos"

### 6.2 Validar Mejoras de Entrenamiento

**Pregunta**: "¿Mejoró el comportamiento después del último entrenamiento?"

**Proceso XAI**:
1. Ejecutar simulación antigua → Generar explicaciones XAI
2. Ejecutar simulación nueva → Generar explicaciones XAI
3. Comparar en pestaña "Análisis Estadístico"
4. Analizar:
   - ¿Cambió la distribución de acciones?
   - ¿Mejoró la confianza promedio?
   - ¿Reducción de distancia al objetivo?

### 6.3 Investigar Correlaciones

**Pregunta**: "¿Cuando la confianza es baja, qué factores importan más?"

**Proceso XAI**:
1. Ir a "Análisis Estadístico Multi-Agente"
2. Observar scatter: Confianza vs Distancia
3. Identificar puntos de baja confianza
4. Revisar importancia de factores en esos pasos
5. Encontrar correlaciones interesantes

---

## 7. Formato de Exportación JSON

### 7.1 Estructura del Historial Exportado

```json
{
  "statistics": {
    "total_decisions": 100,
    "action_counts": {
      "Mover Arriba": 15,
      "Mover Abajo": 20,
      "Apagar Fuego": 45,
      ...
    },
    "agent_stats": {
      "ALPHA": {
        "total_decisions": 50,
        "average_confidence": 0.72,
        "average_distance_to_target": 2.5
      },
      "BRAVO": {
        "total_decisions": 50,
        "average_confidence": 0.68,
        "average_distance_to_target": 4.2
      }
    }
  },
  "histories": {
    "ALPHA": [
      {
        "timestamp": "2024-01-15T10:30:45.123456",
        "agent_id": "ALPHA",
        "agent_role": "nearest",
        "position": [5, 5],
        "action": 1,
        "action_name": "Mover Abajo",
        "explanation": "...",
        "tactical_reasoning": "...",
        "importance_scores": {
          "proximidad_fuego": 0.85,
          "cantidad_fuegos": 0.62,
          ...
        },
        "distance_to_target": 2.0,
        "confidence": 0.72
      },
      ...
    ],
    "BRAVO": [...]
  }
}
```

---

## 8. Integración con MongoDB Atlas (Opcional)

Si tienes MongoDB Atlas configurado, el sistema XAI puede almacenar explicaciones:

```python
# En app.py - sidebar
with st.sidebar.expander("⚙️ Configuración XAI"):
    mongodb_uri = st.text_input("MongoDB Atlas URI (opcional)")
    st.session_state.mongodb_uri = mongodb_uri
```

```python
# En run_mission
if mongodb_uri:
    explainer = XAIExplainer(
        grid_size=grid_size,
        enable_mongodb=True  # Almacenar en MongoDB
    )
```

---

## 9. Troubleshooting

### Problema: "No hay decisiones XAI disponibles"

**Causa**: La simulación no capturó decisiones
**Solución**:
1. Inicia una misión completa
2. Espera a que termine
3. Regresa a la pestaña XAI
4. Las decisiones deberían aparecer

### Problema: "Mapa de atención se ve oscuro"

**Causa**: Todos los valores son muy bajos
**Solución**:
1. Verificar que hay fuegos activos
2. Asegurarse que el grid tiene árboles
3. Revisar que el agente está activo

### Problema: "Error al exportar historial"

**Causa**: No hay suficientemente decisiones capturadas
**Solución**:
1. Ejecutar simulación más larga
2. Asegurarse que hay decisiones del agente seleccionado
3. Revisar consola para mensajes de error

---

## 10. Recursos Adicionales

### Documentos Relacionados
- [MONGODB_ATLAS_SETUP.md](MONGODB_ATLAS_SETUP.md) - Integración con MongoDB
- [FOLIUM_ATLAS_README.md](FOLIUM_ATLAS_README.md) - Mapas geoespaciales
- [MONGODB_INTEGRATION_SUMMARY.md](MONGODB_INTEGRATION_SUMMARY.md) - Resumen de integración

### Archivos del Sistema
- `xai_explainer.py` - Módulo principal (721 líneas)
- `xai_visualization.py` - Visualizaciones (850+ líneas)
- `test_xai_system.py` - Suite de tests (350+ líneas)

### Scripts de Ejemplo
```bash
# Ejecutar tests
python test_xai_system.py

# Ejecutar aplicación con XAI
streamlit run app.py
```

---

## 11. Roadmap Futuro

### Próximas Características Planeadas

- [ ] **SHAP Values**: Explicaciones aditivas de Shapley
- [ ] **LIME**: Explicaciones locales interpretables
- [ ] **Attention Visualization**: Mapas de atención mejorados
- [ ] **Decision Trees**: Extracción de reglas de decisión
- [ ] **Counterfactual Explanations**: "¿Qué hubiera pasado si...?"
- [ ] **Real-time XAI**: Explicaciones durante la simulación en vivo

---

## Conclusión

El sistema XAI de Forest Guardian RL transforma agentes opacos en sistemas interpretables y auditables. Ahora puedes:

✅ Entender cada decisión
✅ Validar comportamientos
✅ Debuggear problemas
✅ Mejorar entrenamientos
✅ Demostrar confiabilidad

**¡Bienvenido a la IA Explicable!** 🧠✨

---

*Documentación actualizada: Enero 2024*
*Sistema XAI v1.0 - Forest Guardian RL*
