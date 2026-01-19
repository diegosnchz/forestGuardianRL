# 🗄️ Configuración de MongoDB Atlas para Forest Guardian RL

Esta guía te ayudará a configurar MongoDB Atlas y cargar tus datos GeoJSON de zonas forestales.

## 📋 Índice

1. [Prerrequisitos](#prerrequisitos)
2. [Configuración de MongoDB Atlas](#configuración-de-mongodb-atlas)
3. [Instalación de Dependencias](#instalación-de-dependencias)
4. [Uso del Script de Carga](#uso-del-script-de-carga)
5. [Consultas Geoespaciales](#consultas-geoespaciales)
6. [Integración con Forest Guardian](#integración-con-forest-guardian)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerrequisitos

- Cuenta de MongoDB Atlas (gratuita)
- Python 3.8+
- Archivo GeoJSON con zonas forestales

## 🌐 Configuración de MongoDB Atlas

### Paso 1: Crear Cuenta y Cluster

1. Ve a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Crea una cuenta gratuita (M0 Sandbox)
3. Crea un nuevo cluster:
   - Selecciona proveedor: **AWS**, **Google Cloud** o **Azure**
   - Región: Selecciona la más cercana a tu ubicación
   - Cluster Tier: **M0 Sandbox (Free)**
   - Nombre del cluster: `ForestGuardian`

### Paso 2: Configurar Seguridad

#### a) Database Access (Usuario)

1. Ve a **Security → Database Access**
2. Haz clic en **Add New Database User**
3. Configura:
   ```
   Authentication Method: Password
   Username: forest_admin
   Password: [Genera una contraseña segura]
   Database User Privileges: Atlas admin
   ```
4. Guarda el usuario

#### b) Network Access (IP Whitelist)

1. Ve a **Security → Network Access**
2. Haz clic en **Add IP Address**
3. Opciones:
   - **Para desarrollo local**: Haz clic en "Allow Access from Anywhere" (0.0.0.0/0)
   - **Para producción**: Agrega solo tu IP específica
4. Confirma

### Paso 3: Obtener Connection String

1. Ve a **Deployment → Database**
2. Haz clic en **Connect** en tu cluster
3. Selecciona **Connect your application**
4. Copia la URI de conexión:
   ```
   mongodb+srv://forest_admin:<password>@forestguardian.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. **Reemplaza `<password>`** con tu contraseña real

---

## 📦 Instalación de Dependencias

Instala el driver de MongoDB para Python:

```bash
pip install pymongo
```

O si usas el `requirements.txt` del proyecto:

```bash
pip install -r requirements.txt
```

Agrega `pymongo` a tu `requirements.txt` si no está:

```txt
pymongo>=4.6.0
```

---

## 🚀 Uso del Script de Carga

### Paso 1: Configurar el Script

Edita el archivo `upload_geojson_to_atlas.py`:

```python
# CONFIGURACIÓN - MODIFICA ESTOS VALORES

# URI de conexión a MongoDB Atlas
MONGODB_URI = "mongodb+srv://forest_admin:TU_PASSWORD@forestguardian.xxxxx.mongodb.net/?retryWrites=true&w=majority"

# Ruta al archivo GeoJSON local
GEOJSON_FILE = "zonas_forestales.geojson"

# Nombre de la base de datos
DATABASE_NAME = "forest_guardian"

# Nombre de la colección
COLLECTION_NAME = "mapa_forestal"

# Limpiar colección antes de insertar (True/False)
CLEAR_COLLECTION = False
```

### Paso 2: Preparar tu Archivo GeoJSON

Tu archivo debe seguir el formato GeoJSON estándar:

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "id": "zona_001",
      "properties": {
        "nombre": "Bosque Norte",
        "tipo": "coniferas",
        "area": 125.5,
        "riesgo_incendio": "alto"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [-99.2000, 19.4200],
            [-99.1900, 19.4200],
            [-99.1900, 19.4300],
            [-99.2000, 19.4300],
            [-99.2000, 19.4200]
          ]
        ]
      }
    }
  ]
}
```

**Nota**: Se incluye un archivo de ejemplo `zonas_forestales_ejemplo.geojson` que puedes usar como plantilla.

### Paso 3: Ejecutar el Script

```bash
python upload_geojson_to_atlas.py
```

**Salida esperada:**

```
======================================================================
🌲 FOREST GUARDIAN RL - GEOJSON TO MONGODB ATLAS UPLOADER 🌲
======================================================================

2026-01-19 10:30:00 - INFO - 🔌 Conectando a MongoDB Atlas...
2026-01-19 10:30:01 - INFO - ✅ Conectado exitosamente a la base de datos 'forest_guardian'
2026-01-19 10:30:01 - INFO - 📁 Usando colección: 'mapa_forestal'
2026-01-19 10:30:01 - INFO - 📖 Leyendo archivo: zonas_forestales.geojson
2026-01-19 10:30:01 - INFO - ✅ Archivo GeoJSON válido cargado
2026-01-19 10:30:01 - INFO - 📊 Total de features encontradas: 7
2026-01-19 10:30:01 - INFO - 🔄 Preparando 7 documentos...
2026-01-19 10:30:01 - INFO - ✅ 7 documentos preparados exitosamente
2026-01-19 10:30:01 - INFO - 📤 Insertando 7 documentos...
2026-01-19 10:30:02 - INFO - ✅ 7 documentos insertados exitosamente
2026-01-19 10:30:02 - INFO - 🔧 Creando índice geoespacial 2dsphere...
2026-01-19 10:30:02 - INFO - ✅ Índice 'location_2dsphere' creado exitosamente
2026-01-19 10:30:02 - INFO - ✅ Índice de nombre creado
2026-01-19 10:30:02 - INFO - ✅ Índice de tipo creado

======================================================================
📊 RESUMEN DE LA COLECCIÓN
======================================================================
2026-01-19 10:30:02 - INFO - 📁 Base de datos: forest_guardian
2026-01-19 10:30:02 - INFO - 📚 Colección: mapa_forestal
2026-01-19 10:30:02 - INFO - 📄 Total de documentos: 7

2026-01-19 10:30:02 - INFO - 🔍 Índices:
2026-01-19 10:30:02 - INFO -    - _id_: {'_id': 1}
2026-01-19 10:30:02 - INFO -    - location_2dsphere: {'location': '2dsphere'}
2026-01-19 10:30:02 - INFO -    - nombre_index: {'nombre': 1}
2026-01-19 10:30:02 - INFO -    - tipo_index: {'tipo': 1}

2026-01-19 10:30:02 - INFO - 📝 Ejemplo de documento:
2026-01-19 10:30:02 - INFO -    - ID: 65abc123...
2026-01-19 10:30:02 - INFO -    - Nombre: Bosque de Pinos - Zona Norte
2026-01-19 10:30:02 - INFO -    - Tipo geometría: Polygon
======================================================================

✅ ¡Proceso completado exitosamente!
```

---

## 🔍 Consultas Geoespaciales

### Verificar Datos en MongoDB Atlas

1. Ve a **Deployment → Database**
2. Haz clic en **Browse Collections**
3. Navega a: `forest_guardian` → `mapa_forestal`

### Consultas Geoespaciales con Python

Crea un archivo `query_example.py`:

```python
from pymongo import MongoClient

# Conectar
client = MongoClient("mongodb+srv://forest_admin:PASSWORD@forestguardian.xxxxx.mongodb.net/")
db = client["forest_guardian"]
collection = db["mapa_forestal"]

# 1. Encontrar zonas cerca de un punto (coordenadas del drone)
drone_position = {
    "type": "Point",
    "coordinates": [-99.1950, 19.4150]  # [longitud, latitud]
}

zonas_cercanas = collection.find({
    "location": {
        "$near": {
            "$geometry": drone_position,
            "$maxDistance": 5000  # 5km en metros
        }
    }
})

print("🚁 Zonas cerca del drone:")
for zona in zonas_cercanas:
    print(f"  - {zona['nombre']}: {zona['tipo']}")

# 2. Encontrar zonas dentro de un polígono (área de búsqueda)
area_busqueda = {
    "type": "Polygon",
    "coordinates": [[
        [-99.2100, 19.4000],
        [-99.1800, 19.4000],
        [-99.1800, 19.4300],
        [-99.2100, 19.4300],
        [-99.2100, 19.4000]
    ]]
}

zonas_en_area = collection.find({
    "location": {
        "$geoWithin": {
            "$geometry": area_busqueda
        }
    }
})

print("\n📍 Zonas en el área de búsqueda:")
for zona in zonas_en_area:
    print(f"  - {zona['nombre']}")

# 3. Encontrar zonas de alto riesgo
zonas_alto_riesgo = collection.find({
    "properties.riesgo_incendio": "alto"
})

print("\n⚠️  Zonas de alto riesgo:")
for zona in zonas_alto_riesgo:
    location = zona['location']['coordinates']
    print(f"  - {zona['nombre']}: {location}")

client.close()
```

Ejecuta:

```bash
python query_example.py
```

---

## 🤖 Integración con Forest Guardian

### Agregar Cliente MongoDB al Ambiente

Edita `forest_fire_env.py`:

```python
from pymongo import MongoClient
from typing import Optional

class ForestFireEnv(gym.Env):
    def __init__(self, ..., mongodb_uri: Optional[str] = None):
        # ... código existente ...
        
        # Cliente MongoDB
        self.mongo_client = None
        self.mongo_db = None
        if mongodb_uri:
            self.mongo_client = MongoClient(mongodb_uri)
            self.mongo_db = self.mongo_client["forest_guardian"]
    
    def get_nearby_zones(self, position: tuple, radius_km: float = 2.0):
        """
        Obtiene zonas forestales cerca de una posición.
        
        Args:
            position: Tupla (row, col) en la grid
            radius_km: Radio de búsqueda en kilómetros
        
        Returns:
            Lista de zonas cercanas
        """
        if not self.mongo_db:
            return []
        
        # Convertir posición de grid a coordenadas geográficas
        # (Ajustar según tu sistema de coordenadas)
        lat = self.location_lat + (position[0] - self.grid_size/2) * 0.001
        lon = self.location_lon + (position[1] - self.grid_size/2) * 0.001
        
        point = {
            "type": "Point",
            "coordinates": [lon, lat]
        }
        
        zones = self.mongo_db["mapa_forestal"].find({
            "location": {
                "$near": {
                    "$geometry": point,
                    "$maxDistance": radius_km * 1000  # Convertir a metros
                }
            }
        })
        
        return list(zones)
    
    def get_zone_risk_level(self, position: tuple) -> str:
        """
        Determina el nivel de riesgo de la zona actual.
        """
        zones = self.get_nearby_zones(position, radius_km=0.5)
        
        if not zones:
            return "desconocido"
        
        # Obtener el riesgo de la zona más cercana
        return zones[0].get("properties", {}).get("riesgo_incendio", "medio")
```

### Usar Datos Geoespaciales en Agentes

Edita `train_and_test.py`:

```python
class TerminatorAgent:
    def __init__(self, env, role="nearest"):
        self.env = env
        self.role = role
    
    def decide(self, obs, agent_pos):
        # Obtener información de riesgo de la zona actual
        risk_level = self.env.get_zone_risk_level(agent_pos)
        
        # Ajustar estrategia según riesgo
        if risk_level == "alto":
            # Priorizar cortafuegos en zonas de alto riesgo
            if self.role == "firebreak":
                return self._find_firebreak_target(obs['grid'], agent_pos)
        
        # Estrategia normal...
        # ... resto del código ...
```

---

## 🛠️ Troubleshooting

### Error: "Authentication failed"

**Problema**: Usuario o contraseña incorrectos.

**Solución**:
1. Verifica que hayas reemplazado `<password>` con tu contraseña real
2. Si la contraseña tiene caracteres especiales, codifícalos:
   - `@` → `%40`
   - `#` → `%23`
   - `$` → `%24`

### Error: "No module named 'pymongo'"

**Solución**:
```bash
pip install pymongo
```

### Error: "ServerSelectionTimeoutError"

**Problema**: No se puede conectar al cluster.

**Solución**:
1. Verifica tu conexión a internet
2. Confirma que tu IP esté en la whitelist
3. Revisa que la URI sea correcta

### Error: "GeoJSON geometry is invalid"

**Problema**: Coordenadas inválidas en el GeoJSON.

**Solución**:
1. Verifica que las coordenadas estén en formato `[longitud, latitud]`
2. Asegúrate de que los polígonos estén cerrados (primer punto = último punto)
3. Usa herramientas como [geojson.io](https://geojson.io) para validar

### Los datos no aparecen en Atlas

**Solución**:
1. Verifica en el log que dice "documentos insertados exitosamente"
2. Refresca la vista en Atlas UI (F5)
3. Verifica que estés viendo la base de datos y colección correctas

---

## 📚 Recursos Adicionales

- [MongoDB Atlas Docs](https://www.mongodb.com/docs/atlas/)
- [Geospatial Queries](https://www.mongodb.com/docs/manual/geospatial-queries/)
- [GeoJSON Spec](https://geojson.org/)
- [PyMongo Tutorial](https://pymongo.readthedocs.io/)
- [GeoJSON Validator](https://geojsonlint.com/)

---

## 🎯 Próximos Pasos

1. ✅ Configura MongoDB Atlas
2. ✅ Carga tus datos GeoJSON
3. ✅ Verifica con consultas de prueba
4. 🔄 Integra con Forest Guardian RL
5. 🚀 Entrena agentes con datos geoespaciales reales

---

**¿Necesitas ayuda?** Consulta la documentación o crea un issue en GitHub.

---

**Forest Guardian RL Team** | Enero 2026
