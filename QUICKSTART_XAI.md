# 🚀 Guía de Inicio Rápido - Sistema XAI

## 5 Minutos para Entender XAI

### Paso 1: Ejecutar la Aplicación (30 segundos)

```bash
cd /workspaces/forestGuardianRL
streamlit run app.py
```

Abre `http://localhost:8501` en tu navegador.

### Paso 2: Configurar Simulación (1 minuto)

En el panel izquierdo:
- **Tamaño del Grid**: 10x10 (default)
- **Probabilidad de Propagación**: 0.15
- **Densidad de Árboles**: 0.3
- **Focos Iniciales**: 3
- **Pasos Máximos**: 50

### Paso 3: Iniciar Misión (2 minutos)

Presiona el botón "🚀 Iniciar Misión"

Verás cómo los drones ALPHA 🔵 y BRAVO 🟠 luchan contra los fuegos 🔥

### Paso 4: Ver Explicaciones (1 minuto 30 segundos)

Cuando termine, busca la pestaña **"🧠 Explicabilidad IA (XAI)"**

---

## 🎯 Las 4 Cosas Principales que Verás

### 1. 📊 Última Decisión
```
┌─────────────────────────────────────────┐
│ Agente: ALPHA (Ataque Rápido)          │
│ Acción: Mover Abajo                     │
│ Posición: (5, 5) → (6, 5)              │
│ Distancia al fuego: 2 celdas            │
│ Confianza: 72%                          │
├─────────────────────────────────────────┤
│ Explicación: Por qué hizo esto          │
│ Razonamiento: Estrategia táctico        │
│ Factores: Qué influyó más              │
└─────────────────────────────────────────┘
```

### 2. 📈 Evolución Temporal
```
Gráficos que muestran:
├── Cómo cambió la distancia al fuego
├── Confianza de las decisiones
├── Qué acciones tomó más
└── Comparación entre ALPHA y BRAVO
```

### 3. 🗺️ Mapas de Atención
```
Colores intensos = Muy importante
Colores claros   = Poco importante

    Rojo oscuro  → Posición del agente
    Rojo brillante → Fuego objetivo
    Naranja      → Camino estratégico
    Amarillo     → Área de influencia
    Blanco       → Sin importancia
```

### 4. 📉 Análisis Estadístico
```
Tabla con todas las decisiones:
├── Paso
├── Acción tomada
├── Distancia al objetivo
├── Nivel de confianza
└── Agua disponible
```

---

## 💡 Ejemplos de Preguntas Que Puedes Responder

### Pregunta 1: "¿Por qué ALPHA ignoró un fuego?"
**Respuesta en XAI**:
1. Abre la pestaña "🧠 XAI"
2. Selecciona ALPHA
3. Busca el paso problemático
4. Lee la "Explicación" y "Razonamiento Táctico"
5. ¡Entenderás exactamente por qué!

### Pregunta 2: "¿Qué factor fue más importante?"
**Respuesta en XAI**:
1. Abre la pestaña "🧠 XAI"
2. Ve a "📊 Última Decisión"
3. Mira el gráfico "Importancia de Atributos"
4. Las barras mostrarán cada factor

### Pregunta 3: "¿Cómo cambió la estrategia con el tiempo?"
**Respuesta en XAI**:
1. Abre la pestaña "🧠 XAI"
2. Ve a "📈 Evolución Temporal"
3. Mira el gráfico "Evolución de Importancia de Factores"
4. ¡Verás cómo cambió el comportamiento!

### Pregunta 4: "¿Cuál agente fue mejor?"
**Respuesta en XAI**:
1. Abre la pestaña "🧠 XAI"
2. Ve a "📉 Análisis Estadístico"
3. Mira "Comparación de Agentes"
4. Compara métricas lado a lado

---

## 🔧 Controles Interactivos

### En "📊 Última Decisión"
- **Botón**: "💾 Exportar Reporte" → Descarga HTML con análisis

### En "📈 Evolución Temporal"
- **Dropdown**: Elige qué métrica ver (Distancia/Confianza/Agua)
- **Gráficos**: Pasa el mouse para ver valores exactos

### En "🗺️ Mapas de Atención"
- **Slider**: Mueve para ver diferentes pasos
- **Métricas**: Distancia, Acción, Confianza actualizados automáticamente
- **Expandibles**: Haz clic para ver explicaciones completas

### En "📉 Análisis Estadístico"
- **Tabla**: Ordena haciendo clic en encabezados
- **Botón**: "💾 Exportar Todo (JSON)" → Descarga historial completo

---

## 📊 Interpretando los Datos

### Mapa de Atención - Qué Significa

```
ROJO OSCURO (1.0):  "El agente está aquí. Es lo más importante"
ROJO BRILLANTE (0.9): "El fuego está aquí. Es el objetivo"
NARANJA (0.5):      "Camino hacia el objetivo"
AMARILLO (0.2):     "Zona de influencia, poco relevante"
BLANCO (0.0):       "No importa para esta decisión"
```

### Importancia de Atributos - Qué Significa

```
██████████ 100% = "Este factor fue CRÍTICO"
██████░░░░ 60%  = "Este factor fue IMPORTANTE"
████░░░░░░ 40%  = "Este factor fue MODERADO"
░░░░░░░░░░ 0%   = "Este factor NO importó"
```

---

## 🎓 Los 8 Factores (Qué es Cada Barra)

```
1. Proximidad Fuego
   → ¿Qué tan cerca está el fuego más cercano?
   → Alto = Fuego muy cerca, debe ir rápido

2. Cantidad Fuegos
   → ¿Cuántos focos hay activos?
   → Alto = Muchos fuegos, situación crítica

3. Cobertura Periférica
   → ¿Qué tan alejado está del perímetro?
   → (Solo para BRAVO - agente naranja)

4. Árboles En Riesgo
   → ¿Hay árboles junto a fuegos?
   → Alto = Riesgo de propagación, debe apagar

5. Densidad Local de Árboles
   → ¿Hay muchos árboles alrededor?
   → Alto = Mucho combustible disponible

6. Centralidad
   → ¿Está cerca del centro?
   → Bajo = Está en la periferia

7. Influencia Viento
   → ¿Hay viento?
   → (Solo si el simulador lo incluye)

8. Factor Elevación
   → ¿Qué tan alto/bajo está?
   → (Solo si el simulador lo incluye)
```

---

## 🔄 Flujo Típico de Uso

```
1. START
   ↓
2. CONFIGURAR parámetros en sidebar
   ↓
3. PRESIONAR "🚀 Iniciar Misión"
   ↓
4. ESPERAR a que termine la simulación
   ↓
5. ABRIR pestaña "🧠 Explicabilidad IA"
   ↓
6. SELECCIONAR agente (ALPHA o BRAVO)
   ↓
7. EXPLORAR:
   ├── 📊 Última decisión
   ├── 📈 Cómo cambió con el tiempo
   ├── 🗺️ Mapas de atención interactivos
   └── 📉 Estadísticas y comparación
   ↓
8. EXPORTAR reportes (HTML o JSON)
   ↓
9. END (o REPETIR con otros parámetros)
```

---

## 📱 Mobile/Responsive

La interfaz es completamente responsive:
- ✅ Desktop (recomendado para mejor experiencia)
- ✅ Tablet (funcional pero apretado)
- ✅ Mobile (funcional pero no recomendado)

---

## ⚡ Tips y Trucos

### Tip 1: Comparar Comportamientos
1. Ejecuta con probabilidad baja (0.05) → Nota decisiones de BRAVO
2. Ejecuta con probabilidad alta (0.3) → Nota decisiones de ALPHA
3. Compara en la pestaña XAI → ¡Diferencias evidentes!

### Tip 2: Encontrar el Momento Crítico
1. Ve a "📈 Evolución Temporal"
2. Mira la gráfica "Distancia al Objetivo"
3. Nota dónde cae más rápido → Eso fue lo más eficiente

### Tip 3: Entender Cambios de Estrategia
1. Ve a "🗺️ Mapas de Atención"
2. Mueve el slider lentamente a través de pasos
3. Observa cómo cambia el mapa rojo/naranja → Cambios de estrategia

### Tip 4: Exportar para Análisis Externo
1. Ve a "📉 Análisis Estadístico"
2. Presiona "💾 Exportar Todo (JSON)"
3. Abre en Python/Excel para análisis más profundo

---

## 🐛 Si Algo No Funciona

### Problema: "No hay decisiones XAI"
**Solución**: 
- Ejecuta una simulación completa (no solo 5 pasos)
- Espera a que termine completamente
- Luego abre la pestaña XAI

### Problema: "Mapa se ve muy oscuro/claro"
**Solución**:
- Es normal - depende de la situación del fuego
- Oscuro = Atención muy concentrada
- Claro = Atención distribuida

### Problema: "La pestaña XAI no aparece"
**Solución**:
- Asegúrate de tener `plotly` y `matplotlib` instalados
- `pip install plotly matplotlib`
- Reinicia streamlit

---

## 📚 Próximos Pasos

### Para Principiantes:
1. ✅ Lee esta guía (ya lo estás haciendo)
2. → Ejecuta la app y juega con los parámetros
3. → Explora la pestaña XAI después de cada simulación
4. → Lee `XAI_README.md` para casos más avanzados

### Para Investigadores:
1. Lee `XAI_README.md` para detalles técnicos
2. Revisa `XAI_IMPLEMENTATION_SUMMARY.md` para arquitectura
3. Usa `test_xai_system.py` como referencia de API
4. Modifica `xai_explainer.py` para agregar nuevos factores

### Para Desarrolladores:
1. Revisa el código en `xai_explainer.py`
2. Entiende la estructura de `AgentDecision`
3. Extiende `xai_visualization.py` con tus propios gráficos
4. Integra con tu propio entorno o modelo

---

## 🎬 Video Demo Simulado (Pasos)

Si ejecutas el sistema, verás:

```
PASO 1-5: Los drones aún no ven el fuego
├─ ALPHA: Patrullando el grid
├─ BRAVO: En posición periférica
└─ XAI: Factores equilibrados

PASO 6-10: ALPHA detecta el fuego
├─ ALPHA: ¡FUEGO DETECTADO! Proximidad al fuego = 100%
├─ BRAVO: Aún patrullando (ignorando fuego cercano)
└─ XAI: Proximidad_fuego se dispara en ALPHA

PASO 11-15: BRAVO detecta otro fuego lejano
├─ ALPHA: Extinguiendo fuego cercano
├─ BRAVO: Aproximándose a fuego lejano
└─ XAI: Cobertura_periférica alta en BRAVO

PASO 16-20: Crisis (múltiples fuegos)
├─ ALPHA: Cantidad_fuegos = 100%, decisiones más rápidas
├─ BRAVO: Cortafuegos preventivo, Arboles_en_riesgo alto
└─ XAI: Múltiples factores activos simultáneamente
```

---

## 📞 Preguntas Frecuentes

**P: ¿Por qué veo diferentes explicaciones cada vez?**
R: Porque el entorno es estocástico (tiene aleatoriedad), así que cada simulación es diferente.

**P: ¿Puedo cambiar el tamaño del grid?**
R: Sí, en el sidebar hay una opción "Tamaño del Grid" (5-20)

**P: ¿Qué pasa si cambio los parámetros?**
R: Los agentes se adaptan, y verás explicaciones diferentes.

**P: ¿Puedo usar esto con mi propio modelo?**
R: Sí, el sistema XAI es independiente. Solo debes integrar como en `app.py`.

**P: ¿Dónde están los datos de importancia almacenados?**
R: En memoria durante la simulación. Puedes exportar a JSON con el botón.

---

## 🎯 Conclusión

¡Ahora eres un usuario experto de XAI! 🎉

Puedes:
- ✅ Entender cada decisión de los agentes
- ✅ Visualizar mapas de atención
- ✅ Analizar importancia de factores
- ✅ Comparar comportamientos
- ✅ Exportar y analizar datos

**¡Que disfrutes explorando la Inteligencia Artificial Explicable!** 🧠✨

---

**Tiempo estimado de lectura**: 5 minutos ✓
**Tiempo estimado para probar**: 10 minutos ✓
**Tiempo estimado para dominar**: 30 minutos ✓

---

*Guía de Inicio Rápido - Forest Guardian RL XAI*
*Última actualización: Enero 2024*
