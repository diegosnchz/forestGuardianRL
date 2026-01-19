# 🔥 Forest Guardian RL - Aplicación Streamlit

**Sistema Autónomo de Control de Incendios Forestales con Visualización en Tiempo Real**

## 📋 Descripción

Forest Guardian RL es una aplicación de simulación interactiva que demuestra cómo los drones equipados con inteligencia artificial pueden contener incendios forestales de manera coordinada. Utiliza un enfoque de aprendizaje por refuerzo descentralizado con dos agentes autónomos que emplean diferentes estrategias tácticas.

### Características Principales

✨ **Visualización Dinámica en Tiempo Real**
- Heatmaps interactivos con Plotly que se actualizan en cada paso
- Visualización del estado del bosque, fuegos y posiciones de drones
- Gráficos de series temporales para análisis de desempeño

⚙️ **Controles Interactivos en Barra Lateral**
- Ajustar parámetros en vivo: tamaño del grid, probabilidad de fuego, densidad de árboles
- Seleccionar número de drones (1-3 unidades)
- Configurar número de focos iniciales y pasos máximos

📊 **Tablero de Métricas (KPIs)**
- Porcentaje de bosque salvado en tiempo real
- Contador de fuegos activos
- Agua consumida por drones
- Tiempo transcurrido de simulación

🚀 **Ejecución de Misiones**
- Botón "Iniciar Misión" para ejecutar simulación completa
- Visualización progresiva del avance
- Reportes automáticos al finalizar

---

## 🛠️ Instalación

### Requisitos Previos
- Python 3.8+
- pip o conda

### Paso 1: Clonar o Descargar el Repositorio

```bash
cd /ruta/del/proyecto
```

### Paso 2: Instalar Dependencias

```bash
pip install -r requirements.txt
```

El archivo `requirements.txt` incluye:
- `streamlit` - Framework para crear aplicaciones web
- `plotly` - Visualizaciones interactivas
- `gymnasium` - Entorno de RL
- `numpy`, `matplotlib`, `pillow` - Dependencias de cómputo

---

## 🚀 Ejecución

### Iniciar la Aplicación Streamlit

```bash
streamlit run app.py
```

Esto abrirá automáticamente la aplicación en tu navegador (generalmente en `http://localhost:8501`).

### Interfaz Principal

#### Barra Lateral (Left Panel)
La barra lateral contiene todos los controles de configuración:

1. **Tamaño del Grid** (8-15)
   - Define las dimensiones del área de simulación
   - Valores más altos = mayor complejidad

2. **Probabilidad de Propagación del Fuego** (0.0-0.5)
   - Controla qué tan rápido se propaga el fuego
   - 0.05 = Propagación lenta y controlada
   - 0.3+ = Propagación agresiva y caótica

3. **Densidad de Árboles** (0.3-0.9)
   - Proporción de celdas ocupadas por vegetación
   - 0.9 = Bosque denso (más complicado de proteger)
   - 0.3 = Bosque disperso (más fácil de contener)

4. **Número de Drones** (1-3)
   - Cantidad de unidades autónomas desplegadas
   - Más drones = mayor capacidad de respuesta
   - Mayor costo computacional

5. **Focos de Fuego Iniciales** (1-5)
   - Número de incendios al inicio de la misión
   - Mayor número = Misión más desafiante

6. **Pasos Máximos de Simulación** (50-200)
   - Duración máxima de la simulación
   - Mayor tiempo = Más oportunidades de respuesta

#### Área Central (Main Content)
Muestra el tablero de métricas y la visualización en tiempo real:

**Tablero de KPIs**
- 4 tarjetas de métricas principales con colores degradados
- Se actualizan en tiempo real durante la misión

**Visualización Interactiva**
- Heatmap del estado actual del bosque
- Gráficos de series temporales con 4 métricas clave

---

## 📊 Leyenda de Símbolos

| Color | Estado | Descripción |
|-------|--------|-------------|
| 🟢 Verde | Árbol | Vegetación a proteger |
| 🔴 Rojo | Fuego | Incendio activo |
| 🔵 Azul | Dron 1 | Agente de "Búsqueda Rápida" |
| 🟠 Naranja | Dron 2 | Agente de "Contención Periférica" |
| ⚪ Blanco | Vacío | Celda quemada o desocupada |

---

## 🤖 Estrategias de los Agentes

### Dron Azul (ALPHA) - Búsqueda de Proximidad
- **Objetivo**: Identificar y extinguir incendios cercanos
- **Estrategia**: Se dirige al fuego más próximo
- **Ventaja**: Respuesta rápida a nuevos focos
- **Ideal para**: Prevenir propagación inicial

### Dron Naranja (BRAVO) - Contención Periférica
- **Objetivo**: Controlar incendios en el perímetro
- **Estrategia**: Se dirige al fuego más distante
- **Ventaja**: Evita que el fuego se expanda
- **Ideal para**: Contener avance general

---

## 📈 Interpretación de Métricas

### Bosque Salvado (%)
- **> 80%**: Misión exitosa, protección excelente
- **60-80%**: Parcialmente exitosa, daño moderado
- **< 60%**: Fallida, daño severo

### Fuegos Activos
- **0**: Incendio completamente contenido
- **Aumento progresivo**: Control insuficiente
- **Disminución**: Drones ganando control

### Agua Consumida
- **< 300**: Consumo eficiente
- **300-600**: Consumo normal
- **> 600**: Alto consumo, posible ineficiencia táctica

### Tiempo Transcurrido
- **Menos pasos = Respuesta rápida**: Agentes coordinados
- **Muchos pasos = Lenta respuesta**: Baja eficiencia

---

## 💡 Casos de Uso Ejemplo

### Experimento 1: Impacto de la Densidad de Árboles
```
Parámetros:
- Grid: 10x10
- Fuego: 0.1 (moderado)
- Árboles: 0.3 → 0.9 (varias pruebas)
- Drones: 2
- Pasos: 100

Hipótesis: Mayor densidad = más difícil de contener
```

### Experimento 2: Número Óptimo de Drones
```
Parámetros:
- Grid: 10x10
- Fuego: 0.2 (agresivo)
- Árboles: 0.6
- Drones: 1 vs 2 vs 3 (comparar)
- Pasos: 100

Hipótesis: 2 drones es óptimo (costo/beneficio)
```

### Experimento 3: Propagación Caótica
```
Parámetros:
- Grid: 12x12
- Fuego: 0.3 (muy agresivo)
- Árboles: 0.5
- Drones: 3 (máximo)
- Pasos: 150

Hipótesis: Alta propagación requiere máximos recursos
```

---

## 🔧 Estructura del Código

```
forestGuardianRL/
├── app.py                      # Aplicación principal Streamlit
├── forest_fire_env.py          # Entorno Gymnasium (core)
├── train_and_test.py           # Original - Generador de GIFs
├── train_and_test_refactored.py # Versión refactorizada
├── visualization.py            # Módulo de visualización Plotly
├── metrics.py                  # Cálculo de métricas y KPIs
├── config.py                   # Configuraciones globales
├── requirements.txt            # Dependencias Python
├── README.md                   # Este archivo
└── GIF/                        # Carpeta de GIFs generados
```

### Módulos Clave

**app.py**
- Interfaz de Streamlit principal
- Gestión de estado de sesión
- Sidebar con controles
- Ejecución de misiones

**visualization.py**
- Funciones para crear heatmaps
- Gráficos de series temporales
- Trayectorias de agentes

**metrics.py**
- Cálculo de métricas en tiempo real
- Clase `MissionMetrics` con datos finales
- Formateadores de KPIs

**config.py**
- Constantes globales
- Configuraciones predefinidas
- Rangos de validación

---

## 🎨 Personalización

### Cambiar Colores
Edita el diccionario `CELL_COLORS` en `visualization.py`:

```python
CELL_COLORS = {
    0: '#ffffff',   # Vacío
    1: '#00aa00',   # Árbol
    2: '#ff0000',   # Fuego
    3: '#0066ff',   # Agente 1
    4: '#ff9900'    # Agente 2
}
```

### Modificar Estrategias de Agentes
Edita la clase `TerminatorAgent` en `train_and_test_refactored.py`:

```python
def decide(self, obs: np.ndarray, pos: Tuple[int, int]) -> int:
    # Aquí implementar lógica personalizada
    ...
```

### Ajustar Parámetros por Defecto
Edita `config.py`:

```python
DEFAULT_CONFIG = EnvironmentConfig(
    grid_size=10,
    fire_spread_prob=0.1,  # Cambiar aquí
    initial_trees=0.6,     # Cambiar aquí
    initial_fires=3,
    num_agents=2
)
```

---

## ⚡ Tips de Optimización

1. **Para simulaciones rápidas**: Aumenta velocidad reduciendo pasos máximos
2. **Para análisis detallados**: Usa pasos máximos altos (150-200)
3. **Para debugging**: Mantén grid pequeño (8-10) y parámetros conservadores
4. **Para casos extremos**: Aumenta drones y reduce densidad de árboles

---

## 🐛 Resolución de Problemas

### Error: "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install streamlit
```

### Error: "Port 8501 already in use"
```bash
streamlit run app.py --server.port 8502
```

### Simulación muy lenta
- Reduce tamaño del grid (8-10)
- Reduce pasos máximos (50-75)
- Reduce densidad de árboles

### Gráficos no se actualizan
- Recarga la página (F5)
- Limpia cache: `streamlit cache clear`

---

## 📚 Referencias Técnicas

- **Gymnasium**: https://gymnasium.farama.org/
- **Streamlit**: https://docs.streamlit.io/
- **Plotly**: https://plotly.com/python/
- **Reinforcement Learning**: https://en.wikipedia.org/wiki/Reinforcement_learning

---

## 📝 Licencia

Este proyecto es de código abierto y está disponible para propósitos educativos y de investigación.

---

## 👤 Autor

Creado como demostración de sistemas de control autónomo para gestión de desastres naturales.

---

## 🎯 Roadmap Futuro

- [ ] Integración con datos reales de incendios
- [ ] Algoritmos de aprendizaje más avanzados (PPO, DQN)
- [ ] Exportación de datos a CSV/JSON
- [ ] Predicción de próximos focos
- [ ] Múltiples niveles de dificultad
- [ ] Configuraciones guardadas
- [ ] Comparación entre misiones

---

**¡Gracias por usar Forest Guardian RL! 🌲🚀**
