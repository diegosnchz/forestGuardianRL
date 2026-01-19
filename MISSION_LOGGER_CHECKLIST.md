# ✅ Mission Logger - Checklist de Verificación

## 📋 Pre-requisitos

- [ ] Python 3.8+ instalado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] `pymongo` instalado específicamente (`pip install pymongo`)
- [ ] Cuenta de MongoDB Atlas creada (gratis)
- [ ] Cluster M0 creado en MongoDB Atlas
- [ ] Usuario de base de datos creado
- [ ] IP en whitelist (0.0.0.0/0 para desarrollo)
- [ ] Connection string copiado

---

## 🧪 Test de Conexión

### Opción 1: Script de Test

```bash
python test_mission_logger.py
```

**Verificar:**
- [ ] ✅ Conexión exitosa
- [ ] ✅ Misión guardada con UUID
- [ ] ✅ Misión recuperada correctamente
- [ ] ✅ Consultas funcionando
- [ ] ✅ Estadísticas globales disponibles

### Opción 2: Python REPL

```bash
python
```

```python
from mission_logger import MissionLogger
import numpy as np

# Reemplaza con tu URI
uri = "mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority"

logger = MissionLogger(uri=uri)
connected = logger.connect()
print(f"Conectado: {connected}")

# Test básico de inserción
if connected:
    mission_id = logger.save_mission(
        geo_zone="Test Zone",
        geojson_file="test.geojson",
        configuration={"grid_size": 30},
        kpis={"kpi_survival_rate": 75.0, "mission_success": True},
        xai_log=[],
        agent_stats={},
        final_grid=np.zeros((30, 30))
    )
    print(f"Mission ID: {mission_id}")
    
    # Recuperar
    mission = logger.get_mission_by_id(mission_id)
    print(f"Recuperada: {mission['geo_zone']}")
    
    # Limpiar
    logger.delete_mission(mission_id)
    print("✅ Test completado")
```

**Verificar:**
- [ ] `Conectado: True`
- [ ] UUID generado correctamente
- [ ] Misión recuperada con datos correctos
- [ ] Sin errores en ningún paso

---

## 🎨 Test de Streamlit UI

### 1. Iniciar Aplicación

```bash
streamlit run app.py
```

**Verificar:**
- [ ] Aplicación inicia sin errores
- [ ] 7 tabs visibles (incluyendo "📜 Historial de Misiones")
- [ ] No hay excepciones en terminal

### 2. Configurar Mission Logger

En la **sidebar**:

1. Expandir "🗺️ MongoDB Atlas (Opcional)"
2. Pegar URI de MongoDB Atlas
3. Verificar: "✅ URI configurado"
4. Marcar checkbox "Habilitar historial de misiones"
5. Verificar: "✅ Mission Logger conectado"

**Verificar:**
- [ ] Mensaje "✅ Mission Logger conectado" aparece
- [ ] No hay mensajes de error
- [ ] Checkbox está marcado

### 3. Ejecutar Primera Misión

1. Configurar parámetros de misión (cualquier valor)
2. Click "🚀 Iniciar Simulación"
3. Esperar a que termine (progress bar → 100%)
4. Verificar mensaje: "📝 Misión guardada: [UUID]..."

**Verificar:**
- [ ] Misión se ejecuta normalmente
- [ ] Mensaje "📝 Misión guardada" aparece
- [ ] UUID se muestra correctamente (8 caracteres + ...)
- [ ] No hay errores en terminal

### 4. Verificar Tab 7 - Recientes

1. Ir a Tab 7: "📜 Historial de Misiones"
2. Debe mostrar: "✅ Conectado a MongoDB Atlas"
3. Ir a sub-tab "🕐 Recientes"
4. Debe mostrar tabla con 1 misión
5. Seleccionar misión en dropdown
6. Verificar métricas (Supervivencia, Fuegos, Agua, Pasos)

**Verificar:**
- [ ] Tab 7 se abre sin errores
- [ ] Mensaje de conexión exitosa
- [ ] Tabla muestra 1 misión
- [ ] Selector de misión funciona
- [ ] Métricas se muestran correctamente
- [ ] Expandibles funcionan (Configuración, Agentes, XAI)

### 5. Verificar Tab 7 - Mejores

1. Ir a sub-tab "🏆 Mejores"
2. Verificar gráfico de barras
3. Verificar tabla de ranking

**Verificar:**
- [ ] Gráfico se renderiza correctamente
- [ ] Tabla muestra datos correctos
- [ ] Colores correctos (verde/amarillo)

### 6. Verificar Tab 7 - Buscar

1. Ir a sub-tab "🔍 Buscar"
2. Seleccionar zona "Todas"
3. Slider supervivencia mínima: 0%
4. Click "🔍 Buscar"
5. Verificar resultados

**Verificar:**
- [ ] Filtros funcionan
- [ ] Botón de búsqueda responde
- [ ] Resultados se muestran correctamente

### 7. Verificar Tab 7 - Estadísticas

1. Ir a sub-tab "📊 Estadísticas"
2. Verificar 4 métricas globales
3. Verificar gráficos (tendencia, pie chart, bar chart)

**Verificar:**
- [ ] 4 cards de métricas visibles
- [ ] Gráfico de tendencia temporal se renderiza
- [ ] Pie chart de distribución por zona se renderiza
- [ ] Bar chart de supervivencia por zona se renderiza

### 8. Test con Múltiples Misiones

1. Ejecutar 5 misiones con diferentes configuraciones
2. Volver a Tab 7
3. Verificar que aparecen todas las misiones

**Verificar:**
- [ ] 5 misiones en tabla de Recientes
- [ ] Gráficos de estadísticas actualizados
- [ ] Ordenamiento correcto (más reciente primero)
- [ ] Todas las misiones son seleccionables

---

## 🔧 Troubleshooting

### ❌ "pymongo not installed"

```bash
pip install pymongo
# Reiniciar Streamlit
```

### ❌ "Connection timeout"

**Posibles causas:**
1. IP no está en whitelist de MongoDB Atlas
   - Solución: Agregar 0.0.0.0/0 en Network Access
2. Cluster está pausado
   - Solución: Resume cluster en MongoDB Atlas
3. URI incorrecta
   - Solución: Verificar URI copiada correctamente

### ❌ "Authentication failed"

**Causa:** Password con caracteres especiales no encoded

**Solución:**
```python
from urllib.parse import quote_plus
password = "p@ssw0rd#2024"
encoded = quote_plus(password)
print(encoded)  # Usa esto en URI
```

### ❌ "Mission Logger no disponible"

**Verificar:**
1. `import pymongo` funciona en Python
2. Checkbox "Habilitar historial de misiones" está marcado
3. URI fue ingresado correctamente
4. Mensaje de conexión es "✅" no "❌"

### ⚠️ "No hay misiones registradas aún"

**Normal en primera ejecución.** Ejecuta una misión primero.

### ⚠️ Tab 7 muestra error

**Verificar en terminal:**
1. Buscar stack trace completo
2. Verificar versión de pymongo: `pip show pymongo`
3. Verificar versión de streamlit: `pip show streamlit`

**Versiones requeridas:**
- `pymongo >= 4.6.0`
- `streamlit >= 1.28.0`

---

## 📊 Verificación de Datos en MongoDB Atlas

### Opción 1: MongoDB Atlas Web UI

1. Login en [MongoDB Atlas](https://cloud.mongodb.com/)
2. Ir a "Database" → "Browse Collections"
3. Seleccionar database: `forestguardian`
4. Seleccionar collection: `mission_logs`
5. Ver documentos

**Verificar:**
- [ ] Database `forestguardian` existe
- [ ] Collection `mission_logs` existe
- [ ] Documentos tienen estructura correcta
- [ ] Campos `mission_id`, `timestamp`, `kpis`, `xai_log` presentes

### Opción 2: MongoDB Compass (Opcional)

1. Descargar [MongoDB Compass](https://www.mongodb.com/products/compass)
2. Conectar con tu URI
3. Navegar a `forestguardian.mission_logs`
4. Explorar documentos

---

## 🎯 Test de Funcionalidad Completa

### Escenario 1: Optimización de Configuración

**Objetivo:** Determinar si 2 agentes o 4 agentes es mejor

1. [ ] Ejecutar 3 misiones con 2 agentes
2. [ ] Ejecutar 3 misiones con 4 agentes
3. [ ] Ir a Tab 7 → Estadísticas
4. [ ] Comparar supervivencia promedio
5. [ ] Conclusión: ¿Cuál configuración es mejor?

### Escenario 2: Análisis de Zona

**Objetivo:** Identificar zona más difícil

1. [ ] Ejecutar misiones en "Grid Aleatorio"
2. [ ] Ejecutar misiones en zona GeoJSON (si disponible)
3. [ ] Ir a Tab 7 → Estadísticas → Supervivencia por Zona
4. [ ] Identificar zona con menor supervivencia

### Escenario 3: Debug de Fallo

**Objetivo:** Entender por qué falló una misión

1. [ ] Ejecutar misión que falle (< 50% supervivencia)
2. [ ] Ir a Tab 7 → Recientes
3. [ ] Seleccionar misión fallida
4. [ ] Expandir "🧠 Historial XAI"
5. [ ] Revisar decisiones paso a paso
6. [ ] Identificar punto de inflexión

---

## 📝 Checklist de Producción

### Seguridad
- [ ] URI no está hardcoded en código
- [ ] Password está URL-encoded
- [ ] IP whitelist es específico (no 0.0.0.0/0)
- [ ] Usuario tiene permisos mínimos necesarios
- [ ] Backups configurados en MongoDB Atlas

### Performance
- [ ] Índices creados correctamente (verificar en Atlas)
- [ ] Límite de misiones recientes configurado (max 50)
- [ ] GeoJSON snapshot deshabilitado si no se usa
- [ ] XAI log filtrado a decisiones importantes

### Monitoreo
- [ ] Monitoreo de espacio en disco (512 MB límite)
- [ ] Monitoreo de conexiones activas
- [ ] Alertas configuradas para errores
- [ ] Logs de errores guardados

### Documentación
- [ ] README actualizado con Mission Logger
- [ ] QUICKSTART compartido con equipo
- [ ] Ejemplos de uso documentados
- [ ] API reference disponible

---

## ✅ Sign-off Final

**Una vez completados todos los tests:**

- [ ] ✅ Conexión a MongoDB Atlas funcional
- [ ] ✅ Misiones se guardan automáticamente
- [ ] ✅ Tab 7 muestra historial correctamente
- [ ] ✅ Consultas y filtros funcionan
- [ ] ✅ Gráficos se renderizan correctamente
- [ ] ✅ XAI log se almacena completo
- [ ] ✅ Estadísticas se calculan correctamente
- [ ] ✅ Sin errores en terminal
- [ ] ✅ Documentación revisada

**Estado del sistema:** 🟢 **PRODUCTION READY**

---

**Notas adicionales:**
```
[Espacio para notas del usuario sobre configuración específica, issues encontrados, etc.]






```

---

**Fecha de verificación:** ________________  
**Verificado por:** ________________  
**Versión:** 1.0.0
