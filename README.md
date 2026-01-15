# Forest Guardian RL 🌲🔥

Sistema jerárquico de control para extinción de incendios forestales usando Reinforcement Learning.

## Estructura del Proyecto

### Archivos Principales

- **`train_and_test.py`**: Pipeline completo de entrenamiento y generación de GIF
  - Entrena modelo PPO (Navegador)
  - Prueba arquitectura jerárquica
  - Genera GIF automáticamente

- **`forest_fire_env.py`**: Entorno Gymnasium personalizado
  - Grid 20x20
  - Fuego se propaga cada 15 pasos (lento)
  - Árboles tardan 8 ciclos (120 pasos) en quemarse
  - Sistema de agua/recargas

- **`requirements.txt`**: Dependencias necesarias

### Carpetas

- **`GIF/`**: Contiene los GIFs generados automáticamente

## Uso

### Entrenar y Generar GIF

```bash
python train_and_test.py
```

Esto ejecutará:
1. **Entrenamiento**: PPO se entrena durante 50,000 pasos
2. **Testing**: Evalúa el modelo en 3 episodios
3. **Visualización**: Muestra un episodio dual-agent
4. **GIF**: Genera automáticamente un GIF en `GIF/forest_fire_training_v*.gif`

## Arquitectura Jerárquica

### Componentes

1. **Navegador (PPO Neural Network)**
   - Red neuronal entrenada con PPO
   - Control estratégico del movimiento
   - Busca y se acerca a los fuegos

2. **Operario (Reglas)**
   - Sistema basado en reglas
   - Decisiones críticas:
     - Sin agua → recargar
     - Fuego adyacente + agua → extinguir
     - Crear cortafuegos

3. **Manager**
   - Controlador jerárquico
   - Arbitrador entre Navegador y Operario
   - Bloquea acciones inválidas

## Visualización del GIF

- **Blanco**: Vacío/Quemado
- **Verde**: Árboles
- **Rojo**: Fuego
- **Azul**: Agente (Navegador controlando)
- **Naranja**: Agente (Operario controlando)

## Parámetros Clave

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| Grid Size | 20x20 | Tamaño del entorno |
| Fire Spread Interval | 15 pasos | Frecuencia de propagación del fuego |
| Fire Burnout Age | 8 ciclos | Ciclos hasta que el fuego se apaga |
| Initial Fires | 3 | Incendios iniciales |
| Water Tank | 10 | Capacidad de agua |

## Salida Esperada

```
✓ Modelo entrenado: ppo_forest_fire.zip
✓ GIF generado: GIF/forest_fire_training_v1.gif
✓ Frames: ~100
✓ Duración: ~20 segundos
```

## Información de Ejecución

- **Tiempo de entrenamiento**: ~2-3 minutos
- **GPU/CPU**: CPU es suficiente
- **RAM mínimo**: 2GB
- **Dependencias**: gymnasium, stable-baselines3, numpy, matplotlib

## Modificaciones Recientes

- ✅ Fuego se propaga cada **15 pasos** (antes 5)
- ✅ Árboles tardan **8 ciclos** en quemarse (antes 3)
- ✅ GIF se genera **automáticamente** al final de train_and_test.py
- ✅ Proyecto simplificado (solo archivos esenciales)
