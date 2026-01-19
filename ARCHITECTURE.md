# 📊 ESTRUCTURA COMPLETA DEL PROYECTO

```
forestGuardianRL/
│
├── 🔴 ARCHIVOS DE APLICACIÓN PRINCIPAL
│   ├── app.py ⭐
│   │   └─ Aplicación Streamlit principal
│   │     • Interfaz web interactiva
│   │     • Barra lateral con controles
│   │     • Tablero de métricas en tiempo real
│   │     • Ejecución de misiones
│   │     • Gestión de estado de sesión
│   │
│   ├── forest_fire_env.py
│   │   └─ Entorno de simulación (Gymnasium)
│   │     • Lógica del grid
│   │     • Movimiento de agentes
│   │     • Propagación del fuego
│   │     • Generación de GIFs
│   │
│   ├── train_and_test.py
│   │   └─ Script original de ejecución
│   │     • Función make_the_magic()
│   │     • Generador de reportes HTML
│   │
│   └── train_and_test_refactored.py ⭐
│       └─ Versión refactorizada para Streamlit
│         • Clase MissionExecutor
│         • Clase TerminatorAgent mejorada
│         • Callbacks de progreso
│
├── 📚 MÓDULOS DE UTILIDAD
│   ├── visualization.py ⭐
│   │   └─ Herramientas de visualización Plotly
│   │     • create_heatmap_figure()
│   │     • create_metrics_timeseries()
│   │     • create_agent_positions_chart()
│   │     • create_summary_metrics()
│   │
│   ├── metrics.py ⭐
│   │   └─ Cálculo de métricas y KPIs
│   │     • Clase MetricsCalculator
│   │     • Clase MissionMetrics
│   │     • Clase KPIFormatter
│   │     • generate_mission_report()
│   │
│   └── config.py ⭐
│       └─ Configuraciones globales
│         • EnvironmentConfig
│         • DEMO_CONFIGS
│         • CONFIG_RANGES
│         • COLORS y MESSAGES
│
├── 📖 DOCUMENTACIÓN
│   ├── README.md
│   │   └─ Documentación original del proyecto
│   │
│   ├── STREAMLIT_README.md ⭐
│   │   └─ Guía completa de la aplicación Streamlit
│   │     • Instalación detallada
│   │     • Uso de la interfaz
│   │     • Interpretación de métricas
│   │     • Casos de uso
│   │     • Resolución de problemas
│   │
│   ├── QUICK_START.md ⭐
│   │   └─ Guía rápida en 3 minutos
│   │     • Instalación y ejecución
│   │     • Escenarios de uso
│   │     • Consejos profesionales
│   │     • Solución de problemas
│   │
│   └── ARCHITECTURE.md (este archivo)
│       └─ Descripción de la estructura
│
├── 🚀 SCRIPTS DE INICIO
│   ├── quick_start.py ⭐
│   │   └─ Menú interactivo en Python
│   │     • Selecciona: Streamlit, Misión de Prueba, Docs
│   │     • Verifica dependencias
│   │     • Instala paquetes si es necesario
│   │
│   └── start.sh ⭐
│       └─ Script bash para inicio rápido
│         • Crea entorno virtual
│         • Instala dependencias
│         • Menú interactivo
│
├── 📋 CONFIGURACIÓN
│   ├── requirements.txt ⭐
│   │   └─ Dependencias Python
│   │     • streamlit>=1.28.0
│   │     • plotly>=5.17.0
│   │     • gymnasium>=0.29.0
│   │     • numpy, matplotlib, pillow, pandas
│   │
│   └── .gitignore
│       └─ Archivos ignorados por git
│
└── 📁 CARPETAS
    └── GIF/
        └─ Almacena GIFs y reportes HTML generados
            • MISION_*.gif
            • MISION_*_REPORTE.html
```

---

## 🔑 ARCHIVOS CLAVE (Marcados con ⭐)

### 1. **app.py** - Corazón de Streamlit
```python
# Estructura principal:
- st.set_page_config()           # Configuración de página
- Session state management       # Gestión de estado
- Sidebar controls              # Barra lateral con parámetros
- KPI dashboard                 # Tablero de métricas
- run_mission()                 # Ejecutor de misiones
- Visualizaciones interactivas  # Gráficos Plotly en tiempo real
```

**Responsabilidades:**
- Interfaz de usuario
- Gestión de parámetros
- Actualización en tiempo real
- Orquestación de módulos

---

### 2. **visualization.py** - Gráficos y Visualización
```python
# Funciones principales:
- create_heatmap_figure()        # Grid interactivo
- create_metrics_timeseries()    # Gráficos de 4 métricas
- create_agent_positions_chart() # Trayectorias de drones
- create_summary_metrics()       # Resumen final
```

**Responsabilidades:**
- Crear visualizaciones Plotly
- Manejar interactividad
- Formatear datos para gráficos
- Gestionar colores y estilos

---

### 3. **metrics.py** - Cálculo de Métricas
```python
# Clases principales:
- MetricsCalculator          # Calcula métricas por paso
- MissionMetrics            # Almacena métricas finales
- KPIFormatter              # Formatea KPIs para visualización
```

**Responsabilidades:**
- Calcular porcentajes, ratios
- Trackear histórico de métricas
- Generar reportes de texto
- Formatar KPIs

---

### 4. **train_and_test_refactored.py** - Motor de Simulación
```python
# Clases principales:
- TerminatorAgent           # Agente inteligente
- MissionExecutor          # Ejecutor de simulación completa
```

**Funciones principales:**
- execute()                # Ejecuta una misión
- generate_tactical_report() # Genera HTML

**Responsabilidades:**
- Lógica de simulación
- Control de agentes
- Generación de reportes

---

### 5. **config.py** - Configuración Central
```python
# Componentes:
- EnvironmentConfig      # Dataclass con parámetros
- CONFIG_RANGES         # Límites válidos
- DEMO_CONFIGS          # Configuraciones predefinidas
- COLORS                # Mapa de colores
- MESSAGES              # Mensajes de estado
```

**Responsabilidades:**
- Definir constantes globales
- Validar parámetros
- Proporcionar configuraciones por defecto

---

## 🔄 FLUJO DE DATOS

```
┌──────────────────────────────────────────────────────────────┐
│                        STREAMLIT APP                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  SIDEBAR                          │        MAIN CONTENT     │
│  ├─ Parámetros                    │        ├─ KPI Cards    │
│  ├─ Botón "Iniciar Misión"        │        ├─ Heatmap      │
│  └─ Controles                     │        └─ Gráficos     │
│                                   │                         │
│  ↓                                │                         │
│  config.py (validación)           │                         │
│  ↓                                │                         │
│  train_and_test_refactored.py     │                         │
│  ├─ MissionExecutor               │                         │
│  ├─ ForestFireEnv                 │ ← Actualiza cada paso  │
│  └─ TerminatorAgent               │                         │
│                                   │                         │
│  ↓ Cada paso:                     │                         │
│  metrics.py (calcula)             │                         │
│  ├─ MetricsCalculator             │                         │
│  └─ step_metrics                  │ → visualization.py     │
│                                   │    (dibuja gráficos)   │
│                                   │                         │
│  ↓ Final:                         │                         │
│  KPIFormatter                     │ ← Muestra resultados   │
│  └─ generate_mission_report()     │                         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 📋 FLUJO DE EJECUCIÓN

```
1. INICIO
   └─ Usuario abre http://localhost:8501

2. SIDEBAR
   └─ Ajusta parámetros
      ├─ Tamaño Grid
      ├─ Propagación
      ├─ Árboles
      ├─ Drones
      ├─ Focos
      └─ Pasos

3. BOTÓN "INICIAR MISIÓN"
   └─ Crea ForestFireEnv con parámetros
      ├─ env.reset() → Grid inicial
      └─ MissionExecutor() → Prepara agentes

4. SIMULACIÓN (Bucle principal)
   ├─ Para cada paso hasta max_steps o terminar:
   │  ├─ agent.decide() → Obtiene acción
   │  ├─ env.step() → Ejecuta paso
   │  ├─ metrics.calculate_step_metrics() → Calcula métricas
   │  └─ visualization.create_*() → Dibuja gráficos
   │
   └─ Reporta progreso en tiempo real

5. FINALIZACIÓN
   ├─ Calcula MissionMetrics finales
   ├─ Formatea KPIs
   ├─ Muestra resumen
   └─ Permite nueva misión o ajustes

6. BOTÓN "LIMPIAR"
   └─ Reinicia estado y permite nuevo intento
```

---

## 🎯 CÓMO USAR CADA MÓDULO

### Para Agregar Nueva Métrica:

**1. En `metrics.py`:**
```python
# En MetricsCalculator.calculate_step_metrics()
metrics['new_metric'] = some_calculation

# En KPIFormatter
@staticmethod
def format_new_metric(metrics):
    return formatted_value
```

**2. En `visualization.py`:**
```python
# En create_metrics_timeseries()
metrics_history['new_metric'] = [...]  # Agregar histórico

fig.add_trace(
    go.Scatter(..., name='Nueva Métrica'),
    row=?, col=?
)
```

**3. En `app.py`:**
```python
# En run_mission()
metrics_callback() →  # Incluir nueva métrica
st.metric('Nueva Métrica', value)  # Mostrar
```

---

### Para Cambiar Estrategia de Agente:

**En `train_and_test_refactored.py`:**
```python
class TerminatorAgent:
    def decide(self, obs, pos):
        # Cambiar aquí la lógica
        # Retornar acción (0-6)
        pass
```

---

### Para Personalizar Interfaz:

**En `app.py`:**
```python
# Cambiar colores:
st.markdown("""
    <style>
    .metric-card { background: NEW_COLOR; }
    </style>
""", unsafe_allow_html=True)

# Agregar nuevas secciones:
st.header("Mi Nueva Sección")
st.write("Contenido aquí")
```

---

## 💾 PERSISTENCIA DE DATOS

**Durante la Misión:**
- `st.session_state.frames_history` → Almacena frames
- `st.session_state.metrics_history` → Almacena métricas
- `st.session_state.env` → Instancia del entorno

**Después de la Misión:**
- GIFs guardados en `GIF/MISION_*.gif`
- Reportes HTML en `GIF/MISION_*_REPORTE.html`

---

## 🔧 DEPENDENCIAS Y COMPATIBILIDAD

```
Python:         3.8+
Streamlit:      1.28.0+
Plotly:         5.17.0+
Gymnasium:      0.29.0+
NumPy:          1.21.0+
Matplotlib:     3.5.0+
Pillow:         9.0.0+
Pandas:         1.5.0+
```

---

## 📈 ESTADÍSTICAS DEL CÓDIGO

| Archivo | Líneas | Propósito |
|---------|--------|-----------|
| app.py | ~450 | Interfaz Streamlit |
| visualization.py | ~250 | Gráficos Plotly |
| metrics.py | ~300 | Cálculo de métricas |
| config.py | ~150 | Configuraciones |
| train_and_test_refactored.py | ~350 | Motor de simulación |
| **TOTAL** | **~1500** | **Código completamente funcional** |

---

**Fin de la documentación de arquitectura** 🎉
