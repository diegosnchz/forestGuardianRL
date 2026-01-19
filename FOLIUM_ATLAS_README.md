# 🗺️ Integración Folium + MongoDB Atlas - Guía Completa

Esta guía explica cómo usar la visualización geoespacial en Streamlit con MongoDB Atlas.

## 📋 Tabla de Contenidos

1. [Vista General](#vista-general)
2. [Instalación](#instalación)
3. [Configuración](#configuración)
4. [Uso en Streamlit](#uso-en-streamlit)
5. [Funcionalidades](#funcionalidades)
6. [API Reference](#api-reference)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Vista General

La integración **Folium + MongoDB Atlas** proporciona:

- ✅ **Visualización interactiva** de datos geoespaciales en mapas de Folium
- ✅ **Sincronización en tiempo real** con MongoDB Atlas
- ✅ **Tooltips dinámicos** con información de estado (humedad, riesgo, etc.)
- ✅ **Botones de control** para reiniciar y actualizar la base de datos
- ✅ **Modo demo** sin necesidad de conexión a Atlas
- ✅ **Heatmap de riesgo** configurable
- ✅ **Capas personalizables** (zonas, estaciones, rutas)
- ✅ **Exportación de datos** a GeoJSON

---

## 📦 Instalación

### Paso 1: Instalar Dependencias

```bash
pip install pymongo streamlit-folium
```

O desde el `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Paso 2: Verificar Instalación

Ejecuta el script de validación:

```bash
python validate_mongodb_setup.py
```

**Salida esperada:**

```
✅ VALIDACIÓN COMPLETA - TODO CORRECTO
   ✓ Python 3.12.1
   ✓ pymongo instalado
   ✓ streamlit-folium instalado
```

---

## ⚙️ Configuración

### Opción 1: Modo Demo (Sin MongoDB Atlas)

No requiere configuración. Usa datos del archivo GeoJSON local.

### Opción 2: Modo Completo (Con MongoDB Atlas)

1. **Crear Cuenta en MongoDB Atlas** (gratuito)
   - Ve a https://cloud.mongodb.com
   - Crea un cluster M0 (gratuito)

2. **Configurar Acceso**
   - Database Access: Crea usuario y contraseña
   - Network Access: Agrega tu IP o permite desde cualquier lugar (0.0.0.0/0)

3. **Obtener URI de Conexión**
   ```
   mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority
   ```

4. **Cargar Datos Iniciales**
   ```bash
   # Edita el archivo upload_geojson_to_atlas.py con tu URI
   python upload_geojson_to_atlas.py
   ```

---

## 🚀 Uso en Streamlit

### Abrir la Aplicación

```bash
streamlit run app.py
```

### Navegar a la Pestaña de Mapa

1. Inicia una misión (opcional)
2. Ve a la pestaña **"🗺️ Mapa Geoespacial (Atlas)"**

### Configurar MongoDB Atlas (Opcional)

En la **sidebar** (panel izquierdo):

1. Expande **"🗺️ MongoDB Atlas (Opcional)"**
2. Pega tu **URI de MongoDB Atlas**
3. Especifica el archivo **GeoJSON** (por defecto: `zonas_forestales_ejemplo.geojson`)

### Modo Demo

Si no configuras URI, la app funciona en **modo demo**:

- Carga datos desde `zonas_forestales_ejemplo.geojson`
- No requiere conexión a internet
- Funcionalidades limitadas (sin actualización en tiempo real)

---

## 🎨 Funcionalidades

### 1. Visualización de Features

El mapa muestra automáticamente:

- **🌲 Zonas Forestales** (polígonos verdes)
  - Coníferas: Verde bosque `#228B22`
  - Mixto: Verde claro `#90EE90`
  - Protegida: Verde oscuro `#006400`

- **📡 Estaciones de Monitoreo** (marcadores rojos)
  - Icono de torre de transmisión
  - Tooltip con capacidad de drones

- **🛤️ Rutas de Patrulla** (líneas azules)
  - Trayectorias de vigilancia
  - Frecuencia y longitud

### 2. Tooltips Interactivos

Cada feature muestra un tooltip HTML con:

```
┌──────────────────────────┐
│ Bosque de Pinos          │
├──────────────────────────┤
│ Tipo: coníferas          │
│ Riesgo: ALTO 🔴          │
│ Humedad: 45%             │
│ Temperatura: 28°C        │
│ Área: 125.5 ha           │
│ Densidad: 850 árb/ha     │
└──────────────────────────┘
```

### 3. Capas del Mapa

Control de capas en la esquina superior derecha:

- ✅ **Zonas Forestales**: Polígonos de áreas protegidas
- ✅ **Estaciones**: Puntos de monitoreo
- ✅ **Rutas de Patrulla**: Trayectorias de vigilancia
- ✅ **Mapa de Calor**: Visualización de riesgo (opcional)

**Capas base:**
- OpenStreetMap (por defecto)
- CartoDB Positron (claro)
- CartoDB Dark Matter (oscuro)
- Stamen Terrain (relieve)

### 4. Herramientas del Mapa

- 📏 **Medidor de Distancia**: Mide distancias en el mapa
- 🗺️ **Minimap**: Vista general en la esquina
- 🖥️ **Fullscreen**: Expande el mapa a pantalla completa

### 5. Controles de Base de Datos

#### 🔄 Actualizar Mapa
Recarga los datos desde MongoDB Atlas.

#### 🗑️ Limpiar BD
Elimina todos los documentos de la colección `mapa_forestal`.

**⚠️ Advertencia:** Esta acción es irreversible.

#### 📤 Recargar GeoJSON
Limpia la base de datos y vuelve a cargar desde el archivo GeoJSON especificado.

**Uso típico:**
1. Modificas `zonas_forestales_ejemplo.geojson`
2. Haces clic en **"📤 Recargar GeoJSON"**
3. Los cambios se reflejan en Atlas y en el mapa

#### 💾 Exportar GeoJSON
Descarga los datos actuales de MongoDB Atlas como archivo `.geojson`.

---

## 📊 Estadísticas en Tiempo Real

El mapa muestra 4 métricas clave:

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ 📍 Total    │ 🌲 Zonas    │ 📡 Estac.   │ ⚠️ Alto     │
│   Features  │   Forest.   │             │    Riesgo   │
│      7      │      3      │      3      │      1      │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

---

## 🔍 API Reference

### Clase Principal: `AtlasFoliumSync`

```python
from atlas_folium_sync import AtlasFoliumSync

sync = AtlasFoliumSync(
    uri="mongodb+srv://...",
    database="forest_guardian",
    collection="mapa_forestal"
)
```

#### Métodos Principales

##### `get_all_features() -> List[Dict]`
Recupera todos los documentos de la colección.

```python
features = sync.get_all_features()
print(f"Total: {len(features)} features")
```

##### `get_features_by_type(zone_type: str) -> List[Dict]`
Filtra features por tipo.

```python
estaciones = sync.get_features_by_type("estacion")
zonas_alto_riesgo = [
    f for f in sync.get_all_features()
    if f.get('properties', {}).get('riesgo_incendio') == 'alto'
]
```

##### `update_zone_state(zone_id: str, state_updates: Dict) -> bool`
Actualiza el estado de una zona en Atlas.

```python
# Actualizar humedad de una zona
sync.update_zone_state(
    zone_id="zona_norte_001",
    state_updates={
        "properties.humedad": 35,
        "properties.temperatura": 32,
        "properties.riesgo_incendio": "alto"
    }
)
```

##### `clear_database() -> Tuple[bool, int]`
Limpia todos los documentos.

```python
success, count = sync.clear_database()
if success:
    print(f"Eliminados {count} documentos")
```

##### `reload_from_geojson(geojson_path: str) -> Tuple[bool, int]`
Recarga datos desde GeoJSON.

```python
success, count = sync.reload_from_geojson("zonas_forestales.geojson")
if success:
    print(f"Insertados {count} documentos")
```

##### `close()`
Cierra la conexión con MongoDB.

```python
sync.close()
```

---

### Función de Visualización: `create_atlas_folium_map`

```python
from atlas_folium_sync import create_atlas_folium_map

mapa = create_atlas_folium_map(
    features=features,
    center=(19.4200, -99.1900),  # (lat, lon)
    zoom_start=13,
    show_heatmap=True
)
```

**Parámetros:**
- `features`: Lista de documentos de Atlas
- `center`: Tupla (latitud, longitud). Si es `None`, se calcula automáticamente
- `zoom_start`: Nivel de zoom inicial (1-18)
- `show_heatmap`: Si `True`, muestra heatmap de riesgo

---

### Componente Streamlit: `streamlit_atlas_map_viewer`

```python
from atlas_folium_sync import streamlit_atlas_map_viewer

streamlit_atlas_map_viewer(
    uri="mongodb+srv://...",
    geojson_path="zonas_forestales_ejemplo.geojson",
    enable_reload=True
)
```

**Parámetros:**
- `uri`: URI de MongoDB Atlas. Si es `None`, usa modo demo
- `geojson_path`: Ruta al archivo GeoJSON para recargas
- `enable_reload`: Si `True`, muestra botones de control de BD

---

## 🎨 Personalización de Colores

### Colores por Tipo de Zona

Edita `ZONE_COLORS` en `atlas_folium_sync.py`:

```python
ZONE_COLORS = {
    'coniferas': '#228B22',      # Verde bosque
    'mixto': '#90EE90',           # Verde claro
    'protegida': '#006400',       # Verde oscuro
    'estacion': '#FF4500',        # Rojo-naranja
    'ruta': '#1E90FF',            # Azul
    'default': '#808080'          # Gris
}
```

### Colores por Nivel de Riesgo

Edita `RISK_COLORS`:

```python
RISK_COLORS = {
    'bajo': '#00FF00',    # Verde
    'medio': '#FFA500',   # Naranja
    'alto': '#FF0000',    # Rojo
    'critico': '#8B0000'  # Rojo oscuro
}
```

---

## 🛠️ Troubleshooting

### Problema 1: "streamlit-folium no está instalado"

**Solución:**
```bash
pip install streamlit-folium
```

### Problema 2: "pymongo no está instalado"

**Solución:**
```bash
pip install pymongo
```

### Problema 3: No se conecta a MongoDB Atlas

**Causas posibles:**
- URI incorrecta
- Usuario/contraseña incorrectos
- IP no está en whitelist

**Solución:**
1. Verifica tu URI en MongoDB Atlas
2. Revisa Database Access y Network Access
3. Prueba la conexión:
   ```python
   from pymongo import MongoClient
   client = MongoClient("mongodb+srv://...")
   client.admin.command('ping')  # Debe retornar {'ok': 1.0}
   ```

### Problema 4: El mapa no se muestra

**Solución:**
1. Verifica que hay datos en la colección
2. Revisa la consola del navegador (F12) en busca de errores JavaScript
3. Prueba con el modo demo (sin URI)

### Problema 5: "Error al cargar archivo demo"

**Solución:**
1. Verifica que `zonas_forestales_ejemplo.geojson` existe en el directorio
2. Revisa que el archivo tiene formato GeoJSON válido:
   ```bash
   python -c "import json; json.load(open('zonas_forestales_ejemplo.geojson'))"
   ```

### Problema 6: Tooltips no muestran información

**Causa:** Faltan campos en los documentos de Atlas.

**Solución:**
Asegúrate de que tus documentos tengan esta estructura:

```json
{
  "location": {
    "type": "Polygon",
    "coordinates": [...]
  },
  "properties": {
    "nombre": "Bosque Norte",
    "tipo": "coniferas",
    "riesgo_incendio": "alto",
    "humedad": 45,
    "temperatura": 28,
    "area": 125.5
  },
  "tipo": "coniferas",
  "nombre": "Bosque Norte"
}
```

---

## 📚 Ejemplos de Uso

### Ejemplo 1: Actualizar Estado de Zona en Tiempo Real

```python
from atlas_folium_sync import AtlasFoliumSync

# Conectar
sync = AtlasFoliumSync(uri="mongodb+srv://...")

# Simular actualización de sensor
sync.update_zone_state(
    zone_id="zona_norte_001",
    state_updates={
        "properties.humedad": 30,  # Bajó la humedad
        "properties.temperatura": 35,  # Subió la temperatura
        "properties.riesgo_incendio": "critico"  # ¡Peligro!
    }
)

print("✅ Estado actualizado en Atlas")
sync.close()
```

### Ejemplo 2: Filtrar Zonas de Alto Riesgo

```python
from atlas_folium_sync import AtlasFoliumSync

sync = AtlasFoliumSync(uri="mongodb+srv://...")

# Obtener todas las zonas
features = sync.get_all_features()

# Filtrar alto riesgo
high_risk = [
    f for f in features
    if f.get('properties', {}).get('riesgo_incendio') == 'alto'
]

print(f"⚠️ {len(high_risk)} zonas de alto riesgo:")
for zone in high_risk:
    name = zone.get('nombre', 'Sin nombre')
    area = zone.get('area', 'N/A')
    print(f"  - {name} ({area} ha)")

sync.close()
```

### Ejemplo 3: Exportar Datos Modificados

```python
from atlas_folium_sync import AtlasFoliumSync
import json

sync = AtlasFoliumSync(uri="mongodb+srv://...")

# Obtener features
features = sync.get_all_features()

# Convertir a GeoJSON
geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "id": f.get("metadata", {}).get("feature_id"),
            "properties": f.get("properties", {}),
            "geometry": f.get("location", {})
        }
        for f in features
    ]
}

# Guardar
with open("export.geojson", "w") as file:
    json.dump(geojson, file, indent=2)

print("✅ Datos exportados a export.geojson")
sync.close()
```

---

## 🎓 Recursos Adicionales

- [Documentación de Folium](https://python-visualization.github.io/folium/)
- [MongoDB Atlas Docs](https://www.mongodb.com/docs/atlas/)
- [Streamlit-Folium](https://github.com/randyzwitch/streamlit-folium)
- [GeoJSON Specification](https://geojson.org/)
- [MongoDB Geospatial Queries](https://www.mongodb.com/docs/manual/geospatial-queries/)

---

## 🤝 Contribuir

¿Encontraste un bug o tienes una idea de mejora?

1. Abre un issue en GitHub
2. Describe el problema o la mejora propuesta
3. Si es posible, incluye código de ejemplo

---

**Creado por**: Forest Guardian RL Team  
**Versión**: 1.0.0  
**Fecha**: Enero 2026

---

**¿Preguntas?** Consulta la documentación completa:
- [MONGODB_ATLAS_SETUP.md](MONGODB_ATLAS_SETUP.md) - Configuración de Atlas
- [MONGODB_INTEGRATION_SUMMARY.md](MONGODB_INTEGRATION_SUMMARY.md) - Resumen ejecutivo
