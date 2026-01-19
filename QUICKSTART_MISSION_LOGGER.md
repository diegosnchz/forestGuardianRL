# 🚀 QUICKSTART: Mission Logger

## ⚡ Inicio Rápido en 5 Minutos

### 1️⃣ Instalar dependencia

```bash
pip install pymongo
```

### 2️⃣ Configurar MongoDB Atlas

1. Ve a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Crea cuenta gratuita
3. Crea cluster M0 (gratis)
4. Crea usuario DB: 
   - Username: `forestguardian`
   - Password: `tu_password_segura`
5. Whitelist IP: `0.0.0.0/0` (para desarrollo)
6. Copia el connection string:

```
mongodb+srv://forestguardian:tu_password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

### 3️⃣ Probar conexión

```bash
python test_mission_logger.py
```

Pega tu URI cuando se solicite. Si todos los tests pasan, ¡estás listo! ✅

### 4️⃣ Usar en Streamlit

1. Ejecuta la app:
```bash
streamlit run app.py
```

2. En la sidebar:
   - Expande "🗺️ MongoDB Atlas (Opcional)"
   - Pega tu URI
   - Marca "Habilitar historial de misiones"
   - Verifica "✅ Mission Logger conectado"

3. Ejecuta una simulación normal

4. Ve a **Tab 7: "📜 Historial de Misiones"**

5. ¡Explora tu primera misión guardada!

---

## 📊 Usando el Historial

### 🕐 Ver Misiones Recientes

1. Tab 7 → "🕐 Recientes"
2. Ajusta slider de cantidad (5-50)
3. Selecciona una misión de la lista
4. Expande secciones:
   - ⚙️ Configuración
   - 🤖 Estadísticas por Agente
   - 🧠 Historial XAI (paso a paso)

### 🏆 Ver Top Misiones

1. Tab 7 → "🏆 Mejores"
2. Gráfico de ranking interactivo
3. Tabla con detalles
4. Identifica las mejores configuraciones

### 🔍 Buscar Misiones

1. Tab 7 → "🔍 Buscar"
2. Filtrar por:
   - Zona geográfica
   - Supervivencia mínima
3. Ver resultados filtrados

### 📊 Ver Estadísticas

1. Tab 7 → "📊 Estadísticas"
2. Métricas globales:
   - Total misiones
   - Supervivencia promedio
   - Mejor resultado
3. Gráficos:
   - Tendencia temporal
   - Distribución por zona
   - Promedios por zona

---

## 🎯 Ejemplos de Uso

### Comparar Configuraciones

**Objetivo**: ¿2 agentes o 4 agentes?

```python
# Ejecuta 5 misiones con 2 agentes
# Ejecuta 5 misiones con 4 agentes

# En Tab 7 → Estadísticas, observa:
# - Supervivencia promedio
# - Pasos promedio
# - Agua consumida promedio

# Conclusión: ¿Cuál configuración es más eficiente?
```

### Identificar Zonas Difíciles

**Objetivo**: ¿Qué zonas necesitan más agentes?

```python
# Ejecuta misiones en diferentes zonas:
# - Bosque A (50x50)
# - Bosque B (80x80)
# - Grid Aleatorio (100x100)

# En Tab 7 → Estadísticas → Supervivencia por Zona
# Identifica zonas con < 70% supervivencia
# Ajusta num_agents o fire_prob para esas zonas
```

### Debug de Fallo

**Objetivo**: ¿Por qué falló esta misión?

```python
# Encuentra misión fallida en Tab 7 → Recientes
# Selecciónala y expande "🧠 Historial XAI"
# Revisa paso a paso:
# - ¿Cuándo empezaron a propagarse fuegos incontrolables?
# - ¿Los agentes tomaron decisiones subóptimas?
# - ¿Se quedaron sin agua en momento crítico?

# Ajusta configuración basándote en el análisis
```

---

## 🛠️ Troubleshooting Rápido

### ❌ "Mission Logger no disponible"

```bash
pip install pymongo
```

Reinicia Streamlit.

### ❌ "No hay conexión a MongoDB Atlas"

- Verifica que la URI sea correcta
- Marca el checkbox "Habilitar historial de misiones"
- Verifica IP whitelist en MongoDB Atlas

### ❌ "Authentication failed"

Tu password tiene caracteres especiales. URL-encodea:

```python
from urllib.parse import quote_plus

password = "p@ssw0rd#2024"
encoded = quote_plus(password)
print(encoded)  # p%40ssw0rd%232024

# Usa en URI:
# mongodb+srv://user:p%40ssw0rd%232024@cluster...
```

### ⚠️ "Última misión: None"

Normal en primera ejecución. Ejecuta una misión y se guardará automáticamente.

### 📉 "No hay misiones registradas aún"

Ejecuta al menos una misión en la app principal.

---

## 📖 Documentación Completa

Para más detalles, lee:

- [MISSION_LOGGER_README.md](MISSION_LOGGER_README.md) - Documentación completa
- [mission_logger.py](mission_logger.py) - Código fuente comentado

---

## 🔮 Próximos Pasos

Después de dominar lo básico:

1. Experimenta con diferentes configuraciones
2. Analiza patrones en el historial XAI
3. Identifica las estrategias más efectivas
4. Usa estadísticas para optimizar tus agentes
5. Exporta datos para análisis externo (futuro)

---

**¿Necesitas ayuda?** Revisa [MISSION_LOGGER_README.md](MISSION_LOGGER_README.md) para casos de uso avanzados.

**Última actualización**: 2026-01-17
