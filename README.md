# Forest Guardian RL 🌲🔥

Sistema de control multi-agente para extinción de incendios forestales con algoritmos tácticos coordinados, sistema XAI de explicabilidad, y **Mission Logger para tracking histórico en MongoDB Atlas**.

## 🆕 Nuevas Características

### 📜 Mission Logger (MongoDB Atlas)
- **Persistencia**: Guarda automáticamente cada simulación en MongoDB Atlas
- **XAI History**: Almacena el historial completo de decisiones XAI paso a paso
- **Analytics**: Compara configuraciones y optimiza estrategias
- **Estadísticas Globales**: Tendencias, ranking de mejores misiones, filtros por zona

👉 **[QUICKSTART Mission Logger](QUICKSTART_MISSION_LOGGER.md)** - Empieza en 5 minutos  
👉 **[Documentación completa Mission Logger](MISSION_LOGGER_README.md)** - API y casos de uso

### 🧠 Sistema XAI (Explainable AI)
- **Interpretación de Decisiones**: Explicación textual de cada acción del agente
- **Mapas de Importancia**: Visualiza qué píxeles influyeron más en cada decisión
- **Justificación Táctica**: Razonamiento detrás de decisiones complejas
- **Confidence Scores**: Nivel de confianza del agente en cada paso

👉 **[QUICKSTART XAI](QUICKSTART_XAI.md)** - Guía rápida  
👉 **[Documentación completa XAI](XAI_README.md)** - Sistema completo

## Estructura del Proyecto

### Archivos Principales

- **`train_and_test.py`**: Pipeline de simulación y generación de reportes
  - Despliega 2 drones autónomos con algoritmos tácticos
  - Genera GIF de la misión automáticamente
  - Crea reporte HTML interactivo con estadísticas

- **`forest_fire_env.py`**: Entorno Gymnasium personalizado
  - Grid 10x10 (1000m² de terreno simulado)
  - Fuego se propaga con probabilidad 0.1
  - Agua infinita (999 unidades)
  - Sistema de colisiones entre agentes

- **`requirements.txt`**: Dependencias necesarias

### Carpetas

- **`GIF/`**: Contiene los GIFs generados automáticamente

## Instalación y Uso

### 1. Clonar el Repositorio

```bash
git clone -b liadaHistorica https://github.com/diegosnchz/forestGuardianRL.git
cd forestGuardianRL
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Dependencias incluidas:**
- `gymnasium>=0.29.0` - Entorno de RL
- `stable-baselines3>=2.0.0` - Algoritmo PPO
- `matplotlib>=3.5.0` - Visualización
- `numpy>=1.21.0` - Operaciones numéricas
- `pillow>=9.0.0` - Generación de GIF
- `streamlit>=1.28.0` - Dashboard interactivo
- `plotly>=5.17.0` - Gráficos interactivos
- `folium>=0.14.0` - Mapas geoespaciales
- `pymongo>=4.6.0` - **MongoDB Atlas (Mission Logger)**

### 3. Configurar MongoDB Atlas (Opcional - para Mission Logger)

```bash
# 1. Crea cuenta gratuita en MongoDB Atlas
# 2. Crea cluster M0 (gratis)
# 3. Whitelist IP: 0.0.0.0/0
# 4. Copia connection string

# 5. Prueba conexión:
python test_mission_logger.py
```

👉 **Ver [QUICKSTART Mission Logger](QUICKSTART_MISSION_LOGGER.md)** para guía detallada

### 4. Ejecutar Dashboard Interactivo (Recomendado)

```bash
streamlit run app.py
```

Esto abrirá un dashboard interactivo con:
- **Tab 1**: Configuración y ejecución de misiones
- **Tab 2**: Métricas en tiempo real
- **Tab 3**: Visualización de agentes
- **Tab 4**: Resumen y exportación
- **Tab 5**: Mapas geoespaciales (MongoDB Atlas)
- **Tab 6**: 🧠 Explicabilidad IA (XAI)
- **Tab 7**: 📜 **Historial de Misiones (Mission Logger)**

### 5. Ejecutar Simulación por Terminal

```bash
python train_and_test.py
```

Esto ejecutará:
1. **Despliegue**: Inicializa 2 drones con algoritmos tácticos diferentes
2. **Simulación**: Ejecuta misión de extinción (máx. 100 pasos)
3. **Visualización**: Genera GIF en `GIF/MISION_[timestamp].gif`
4. **Reporte**: Crea HTML interactivo con métricas de eficiencia

## Arquitectura Multi-Agente

### Agentes Tácticos

1. **UNIDAD ALPHA (Azul) - TerminatorAgent "nearest"**
   - Dron de Intervención Rápida
   - Algoritmo: Busca el fuego más cercano
   - Estrategia: Ataque directo e inmediato
   - Radio de extinción: 3x3

2. **UNIDAD BRAVO (Naranja) - TerminatorAgent "farthest"**
   - Dron de Contención Pesada
   - Algoritmo: Ataca focos perimetrales lejanos
   - Estrategia: Envolvimiento y contención
   - Radio de extinción: 3x3

3. **Sistema de Coordinación**
   - Prevención de colisiones física
   - Coordinación implícita por roles diferentes
   - Sin comunicación directa entre agentes

## Visualización del GIF

- **Blanco**: Vacío/Quemado
- **Verde**: Árboles
- **Rojo**: Fuego
- **Azul**: Agente (Navegador controlando)
- **Naranja**: Agente (Operario controlando)

## Parámetros Clave

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| Grid Size | 10x10 | Tamaño del entorno (1000m²) |
| Fire Spread Prob | 0.1 (10%) | Probabilidad de propagación por paso |
| Initial Trees | 60% | Cobertura forestal inicial |
| Initial Fires | 3 | Focos de incendio iniciales |
| Water Tank | 999 (∞) | Agua infinita para cada agente |
| Max Steps | 100 | Tiempo máximo de simulación |

## Información de Ejecución

- **Tiempo de simulación**: ~10-30 segundos por misión
- **GPU/CPU**: CPU es suficiente (no requiere GPU)
- **RAM mínimo**: 1GB
- **Python**: Compatible con Python 3.8+
- **Sistema Operativo**: Windows, Linux, macOS
- **Salida**: GIF + Reporte HTML portátil (no requiere servidor)

## Salida Esperada

```
✓ GIF generado: GIF/MISION_[timestamp].gif
✓ Reporte HTML: GIF/MISION_[timestamp]_REPORTE.html
✓ Frames: ~50-100 (según duración de la misión)
✓ Estadísticas: % árboles salvados, focos neutralizados, tiempo de respuesta
```

## Características Técnicas

- ✅ **Grid 10x10** con física de colisiones entre agentes
- ✅ **Agua infinita** (999 unidades) - foco en estrategia, no en gestión de recursos
- ✅ **Sistema multi-agente** con roles diferenciados (nearest/farthest)
- ✅ **Generación automática** de GIF y reporte HTML con métricas
- ✅ **Reporte portable**: HTML con GIF embebido en base64 (sin dependencias externas)
