# Forest Guardian RL 🌲🔥

Sistema de control multi-agente para extinción de incendios forestales con algoritmos tácticos coordinados.

**🌍 NUEVO: Integración GIS completa con 13 bosques reales del mundo y mapas interactivos Folium**

---

## ⚡ Inicio Rápido con GIS

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar aplicación web
streamlit run app.py

# 3. Seleccionar "Bosques Reales" en la barra lateral

# 4. ¡Observar simulación en mapas interactivos!
```

**📖 Documentación GIS**: Ver [GIS_README.md](GIS_README.md) para guía completa

---

## Estructura del Proyecto

### Archivos Principales

- **`app.py`**: Interfaz web Streamlit (incluye modo GIS)

- **`train_and_test.py`**: Pipeline de simulación y generación de reportes
  - Despliega 2 drones autónomos con algoritmos tácticos
  - Genera GIF de la misión automáticamente
  - Crea reporte HTML interactivo con estadísticas

- **`forest_fire_env.py`**: Entorno Gymnasium personalizado
  - Grid 10x10 (1000m² de terreno simulado)
  - Fuego se propaga con probabilidad 0.1
  - Agua infinita (999 unidades)
  - Sistema de colisiones entre agentes

### 🌍 Módulos GIS (NUEVO)

- **`gis_locations.py`**: Base de datos de 13 bosques reales
- **`forest_fire_gis.py`**: Extensión de entorno con coordenadas geográficas
- **`gis_visualization.py`**: Generador de mapas Folium interactivos

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
- `streamlit>=1.28.0` - Interfaz web
- `folium>=0.14.0` - Mapas interactivos ⭐ GIS
- `streamlit-folium>=0.15.0` - Integración Streamlit-Folium ⭐ GIS
- `plotly>=5.17.0` - Gráficos interactivos

### 3. Ejecutar Aplicación

**Opción A: Interfaz Web (con GIS)**
```bash
streamlit run app.py
```

**Opción B: Simulación en Terminal**
```bash
python3 train_and_test.py
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

## 🗺️ Caracteristicas GIS

### Bosques Reales Disponibles (13)
- Amazonas - Perú
- Pantanal - Brasil
- Sierra Nevada - Colombia
- Selva Daintree - Australia
- Borneo - Malasia
- Y 8 más en Africa, Asia y Europa

### Funcionalidades GIS
- ✅ Mapas interactivos Folium con OpenStreetMap/Satélite
- ✅ Conversión automática grid ↔ coordenadas geográficas
- ✅ Heatmaps de intensidad de fuego
- ✅ Posiciones de drones en mapas reales
- ✅ Información de bosques integrada
- ✅ Entrada de coordenadas personalizadas

## Visualización del GIF

- **Blanco**: Vacío/Quemado
- **Verde**: Árboles
- **Rojo**: Fuego
- **Azul**: Agente (Búsqueda Rápida)
- **Naranja**: Agente (Contención Pesada)

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
- ✅ **GIS Integration**: 13 bosques reales con mapas Folium interactivos
- ✅ **Coordenadas Geográficas**: Conversión automática grid ↔ lat/lon

## 📖 Documentación

- [GIS_README.md](GIS_README.md) - Guía completa de uso del módulo GIS
- [INTEGRACION_GIS.md](INTEGRACION_GIS.md) - Detalles técnicos de implementación
- [RESUMEN_GIS.txt](RESUMEN_GIS.txt) - Resumen ejecutivo del proyecto GIS
