# 🚀 Guía de Inicio Rápido - Forest Guardian RL Streamlit

## En 3 minutos: De cero a simulación completa

### Paso 1: Instalar y Ejecutar (2 minutos)

```bash
# Navega a la carpeta del proyecto
cd /workspaces/forestGuardianRL

# Instala las dependencias necesarias
pip install -r requirements.txt

# Inicia la aplicación Streamlit
streamlit run app.py
```

✅ **Resultado**: Se abrirá automáticamente en `http://localhost:8501`

---

## Estructura de la Interfaz

### 📍 Barra Lateral (Izquierda)
Aquí encontrarás todos los controles para ajustar la simulación:

```
⚙️ PARÁMETROS DE SIMULACIÓN
├── Tamaño del Grid (8-15)           → Dimensiones del bosque
├── Probabilidad de Fuego (0.0-0.5)  → Velocidad de propagación
├── Densidad de Árboles (0.3-0.9)    → Cantidad de vegetación
├── Número de Drones (1-3)           → Unidades autónomas
├── Focos Iniciales (1-5)            → Incendios al inicio
└── Pasos Máximos (50-200)           → Duración máxima

🎯 ACCIONES
├── 🚀 Iniciar Misión  → EJECUTA LA SIMULACIÓN
└── 🔄 Limpiar         → Reinicia todo
```

### 🎨 Área Central (Centro)
Visualización en tiempo real durante la misión:

```
📊 TABLERO DE MÉTRICAS (Top)
├── Bosque Salvado (%)    → Cobertura vegetal protegida
├── Fuegos Activos        → Incendios aún sin controlar
├── Agua Consumida        → Recursos utilizados
└── Tiempo Transcurrido   → Pasos ejecutados

📈 VISUALIZACIÓN INTERACTIVA (Abajo)
├── Heatmap del Grid      → Estado actual (colores interactivos)
└── Gráficos de Series    → Métricas a lo largo del tiempo
```

---

## 🎮 Cómo Usar

### Escenario 1: Simulación Simple (Principiante)

```
1. Abre http://localhost:8501
2. En la barra lateral, deja todos los valores por defecto:
   - Grid: 10×10
   - Fuego: 0.1 (moderado)
   - Árboles: 0.6
   - Drones: 2
   - Pasos: 100

3. Presiona el botón azul: "🚀 Iniciar Misión"

4. Observa cómo:
   ✓ Los drones (azul 🔵 y naranja 🟠) se mueven
   ✓ El fuego (rojo 🔴) se propaga y es extinguido
   ✓ Los árboles (verde 🟢) se protegen o queman
   ✓ Las métricas se actualizan en tiempo real
```

**Resultado esperado**: 
- Tiempo: ~30 segundos
- Bosque salvado: 70-85%
- Fuegos extintos: 3/3 ✓

---

### Escenario 2: Parámetros Personalizados (Intermedio)

```
Experimento: "¿Qué pasa si aumentamos la propagación del fuego?"

Configuración:
┌─────────────────────────────────┐
│ Tamaño Grid:        10          │
│ Propagación:        0.25 ⬆️     │ (Muy agresivo)
│ Árboles:            0.6         │
│ Drones:             2           │
│ Focos Iniciales:    4 ⬆️        │ (Más fuegos)
│ Pasos:              100         │
└─────────────────────────────────┘

Presiona "🚀 Iniciar Misión"

Observa:
- ¿Qué tan rápido se propaga el fuego?
- ¿Los drones logran contenerlo?
- ¿Cuál es el % de bosque salvado?
- ¿Cuál es la diferencia vs. escenario 1?
```

---

### Escenario 3: Análisis Avanzado (Experto)

```
Comparación: "1 Dron vs 3 Drones contra fuego agresivo"

PRUEBA A: Un solo dron
┌─────────────────────────────────┐
│ Tamaño Grid:        12          │
│ Propagación:        0.2         │ (Agresivo)
│ Árboles:            0.5         │
│ Drones:             1 ⬇️        │ (Mínimo)
│ Focos Iniciales:    4           │
│ Pasos:              150         │
└─────────────────────────────────┘

PRUEBA B: Tres drones
┌─────────────────────────────────┐
│ Tamaño Grid:        12          │
│ Propagación:        0.2         │ (Igual)
│ Árboles:            0.5         │ (Igual)
│ Drones:             3 ⬆️        │ (Máximo)
│ Focos Iniciales:    4           │ (Igual)
│ Pasos:              150         │ (Igual)
└─────────────────────────────────┘

Compara los resultados:
- Diferencia en % de bosque salvado
- Diferencia en tiempo de respuesta
- Análisis de costo-beneficio
```

---

## 🎯 Casos de Uso Interesantes

### 1️⃣ **La Tormenta Perfecta**
```
Grid: 15×15 (máximo)
Propagación: 0.3 (muy agresivo)
Árboles: 0.8 (denso)
Drones: 3 (máximo)
Focos: 5 (máximo)
Pasos: 200 (máximo)

Pregunta: ¿Pueden los drones contener una catástrofe?
```

### 2️⃣ **Eficiencia Mínima**
```
Grid: 8 (mínimo)
Propagación: 0.05 (muy lento)
Árboles: 0.3 (disperso)
Drones: 1
Focos: 1
Pasos: 50 (mínimo)

Pregunta: ¿Cuál es el escenario más sencillo?
```

### 3️⃣ **Punto de Quiebre**
```
Mantén todo igual pero aumenta lentamente:
- Propagación: 0.1 → 0.15 → 0.2 → 0.25 → 0.3

Pregunta: ¿En qué punto fallan 2 drones?
```

---

## 📊 Interpretación de Gráficos

### Heatmap (Cuadrícula Principal)
```
Colores:
🟢 Verde     = Árbol (bueno, proteger)
🔴 Rojo      = Fuego (malo, extinguir)
🔵 Azul      = Dron 1 (persigue fuego cercano)
🟠 Naranja   = Dron 2 (persigue fuego lejano)
⚪ Blanco    = Celda vacía (quemada o desocupada)

Interactividad:
- Pasa el mouse para ver coordenadas
- Observa el movimiento de drones
- Sigue la propagación del fuego
```

### Gráfico de Fuegos Activos (Arriba izquierda)
```
📈 Línea ROJA descendente = Éxito (fuegos bajo control)
📈 Línea ROJA ascendente = Fracaso (fuegos propagándose)
📈 Línea ROJA plana = Punto de equilibrio
```

### Gráfico de Árboles Salvados (Arriba derecha)
```
📈 Línea VERDE ascendente = Bosque recuperándose
📈 Línea VERDE descendente = Bosque siendo consumido
📈 Línea VERDE plana = Equilibrio frágil
```

### Gráfico de Agua Consumida (Abajo izquierda)
```
📈 Línea AZUL = Cantidad de agua gastada
   Pendiente suave = Uso eficiente
   Pendiente abrupta = Drones trabajando al máximo
```

### Gráfico de Densidad (Abajo derecha)
```
📈 Línea PÚRPURA = Proporción de bosque aún vivo
   >0.8 = Misión exitosa
   0.5-0.8 = Parcialmente exitosa
   <0.5 = Fracaso
```

---

## 💡 Tips Profesionales

### Para Simulaciones Rápidas
```
- Usa Grid pequeño (8-9)
- Reduce Pasos máximos (50-75)
- Baja Densidad de Árboles (0.4-0.5)
Resultado: Simulación en 5-10 segundos
```

### Para Análisis Detallados
```
- Usa Grid mediano (10-12)
- Aumenta Pasos máximos (150-200)
- Mantén Densidad alta (0.6-0.8)
Resultado: Simulación en 30-60 segundos con datos ricos
```

### Para Casos Extremos
```
- Usa Grid grande (13-15)
- Máximo Propagación (0.25-0.3)
- Máximo Focos (4-5)
- Máximo Drones (3)
Resultado: Análisis de límites del sistema
```

### Debug de Problemas
```
- Si es muy lento: reduce Grid y Pasos
- Si no ves cambios: aumenta Propagación
- Si falta agua: los drones tienen tanques infinitos (999)
- Si gráficos "congelados": presiona "Limpiar" y reinicia
```

---

## 🔄 Flujo Típico de Uso

```
1. ABRE STREAMLIT
   streamlit run app.py
   
2. CONFIGURA PARÁMETROS
   Ajusta sliders en la barra lateral
   
3. INICIA MISIÓN
   Presiona "🚀 Iniciar Misión"
   
4. OBSERVA EN TIEMPO REAL
   Mira cómo los drones luchan contra el fuego
   
5. ANALIZA RESULTADOS
   Revisa el heatmap y los gráficos finales
   
6. AJUSTA Y PRUEBA DE NUEVO
   Modifica parámetros y vuelve al paso 3
```

---

## 📱 Compatibilidad

✅ **Navegadores Soportados**
- Chrome/Chromium (mejor rendimiento)
- Firefox (bueno)
- Safari (aceptable)
- Edge (aceptable)

⚠️ **No Soportado**
- Internet Explorer (demasiado antiguo)
- Navegadores móviles (interfaz no optimizada)

---

## 🚨 Solución de Problemas

### Problema: "streamlit: command not found"
```bash
# Solución:
pip install streamlit
```

### Problema: "Port 8501 already in use"
```bash
# Opción 1: Espera 30 segundos y reinicia
# Opción 2: Usa otro puerto
streamlit run app.py --server.port 8502
```

### Problema: Visualización lenta o congelada
```bash
# Solución: Reduce los parámetros
# - Grid: 8-9 (en lugar de 10-15)
# - Pasos: 50-75 (en lugar de 100-200)
```

### Problema: No veo cambios en tiempo real
```bash
# Presiona F5 para recargar la página
# O presiona "Limpiar" y reinicia
```

---

## 🎓 Conceptos Clave

### Grid (Cuadrícula)
- Representa el área forestal
- 10×10 = 100 celdas
- Cada celda puede ser: árbol, fuego, agente o vacío

### Probabilidad de Propagación
- Determina qué tan rápido se expande el fuego
- 0.05 = Fuego lento (fácil de contener)
- 0.3 = Fuego muy rápido (difícil de contener)

### Drones Autónomos
- Agentes inteligentes sin control humano
- Estrategia 1 (Azul): Busca fuego cercano
- Estrategia 2 (Naranja): Persigue fuego lejano
- Estrategia 3 (Si existe): Apoyo estratégico

### Agua Infinita
- Los drones tienen tanques de 999 unidades
- Nunca se quedan sin agua
- Enfoque: Coordinación tácica, no recursos

---

**¡Ya estás listo para experimentar con Forest Guardian RL! 🚀**

Próximos pasos: Modifica las estrategias de los agentes en `train_and_test_refactored.py` para implementar tus propios algoritmos.
