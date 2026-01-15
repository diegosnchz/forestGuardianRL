# Forest Guardian RL

Ejercicio Máster - Entorno de Aprendizaje por Refuerzo para combatir incendios forestales.

## Descripción

Este proyecto implementa un entorno personalizado de Gymnasium para entrenar agentes de RL que aprendan a gestionar incendios forestales. El agente debe moverse por un bosque de 10x10, extinguir incendios y prevenir la destrucción del bosque.

### Características del Entorno

- **Grid**: 10x10 celdas
- **Estados**:
  - 0 = Vacío (celda quemada)
  - 1 = Árbol
  - 2 = Fuego
  - 3 = Agente

- **Espacio de Acciones** (Discrete(7)):
  - 0: Mover arriba
  - 1: Mover abajo
  - 2: Mover izquierda
  - 3: Mover derecha
  - 4: Talar árbol
  - 5: Apagar fuego
  - 6: Esperar

- **Sistema de Recompensas**:
  - +10: Apagar un fuego
  - -0.1: Por cada fuego activo en cada paso
  - -100: Si el bosque es destruido (>80% de árboles perdidos)
  - +50: Bonus por extinguir todos los incendios

- **Mecánica de Fuego**:
  - El fuego se expande estocásticamente a árboles vecinos
  - Probabilidad de expansión: 30% por defecto
  - Los fuegos se apagan después de expandirse (simulando consumo)

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

### 1. Demo Rápido (Sin Entrenamiento)

Ejecuta una demostración con política aleatoria para ver el entorno en acción:

```bash
python demo.py
```

### 2. Validar el Entorno

Ejecuta el script de prueba para verificar que el entorno funciona correctamente:

```bash
python test_env.py
```

### 3. Entrenar y Probar el Agente

Entrena un agente PPO durante 20,000 pasos y visualiza los resultados:

```bash
python train_and_test.py
```

Este script:
1. Crea el entorno ForestFireEnv
2. Entrena un agente PPO durante 20,000 timesteps
3. Guarda el modelo entrenado
4. Ejecuta 5 episodios de prueba
5. Genera visualizaciones con matplotlib

### Archivos Generados

Después del entrenamiento:
- `ppo_forest_fire.zip`: Modelo entrenado
- `forest_fire_visualization.png`: Visualización de un episodio completo
- `training_progress.png`: Gráfico de progreso del entrenamiento (si disponible)

## Estructura del Proyecto

```
forestGuardianRL/
├── forest_fire_env.py    # Implementación del entorno Gymnasium
├── train_and_test.py     # Script de entrenamiento y prueba
├── test_env.py           # Script de validación del entorno
├── demo.py               # Demo con política aleatoria
├── requirements.txt      # Dependencias del proyecto
├── .gitignore           # Archivos ignorados por git
└── README.md            # Este archivo
```

## Requisitos

- Python 3.8+
- gymnasium >= 0.29.0
- stable-baselines3 >= 2.0.0
- matplotlib >= 3.5.0
- numpy >= 1.21.0

## Personalización

Puedes ajustar los parámetros del entorno al crear la instancia:

```python
env = ForestFireEnv(
    grid_size=10,              # Tamaño del grid
    fire_spread_prob=0.3,      # Probabilidad de expansión del fuego
    initial_trees=0.6,         # Proporción inicial de árboles
    initial_fires=3            # Número de fuegos iniciales
)
```
