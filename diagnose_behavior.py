"""
Script de diagnóstico para verificar el comportamiento del entorno
"""
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import numpy as np
from forest_fire_env import ForestFireEnv

print("\n" + "="*60)
print("DIAGNÓSTICO DEL COMPORTAMIENTO DEL ENTORNO")
print("="*60 + "\n")

# Crear entorno con parámetros que faciliten ver la propagación
env = ForestFireEnv(
    grid_size=10,  # Más pequeño para ver mejor
    fire_spread_prob=0.8,  # Alta probabilidad de propagación
    initial_trees=0.7,
    initial_fires=2
)

obs, info = env.reset()
print("Estado inicial:")
print(f"  Árboles: {np.sum(env.grid == 1)}")
print(f"  Fuegos: {np.sum(env.grid == 2)}")
print(f"  Agente en: {env.agent_pos}")

print("\nGrid inicial:")
symbols = {0: '·', 1: '🌲', 2: '🔥', 3: '🤖'}
grid_with_agent = obs.copy()
for row in grid_with_agent:
    print(' '.join([symbols.get(cell, str(cell)) for cell in row]))

print("\n" + "-"*60)
print("Ejecutando 10 pasos con acción WAIT (6)...")
print("-"*60 + "\n")

for step in range(10):
    # Ejecutar acción WAIT para ver solo la propagación del fuego
    obs, reward, terminated, truncated, info = env.step(6)
    
    trees = np.sum(env.grid == 1)
    fires = np.sum(env.grid == 2)
    
    print(f"Paso {step+1}:")
    print(f"  Árboles: {trees} | Fuegos: {fires} | Reward: {reward:+6.2f}")
    
    # Mostrar grid si hay fuego
    if fires > 0:
        grid_with_agent = obs.copy()
        for row in grid_with_agent:
            print('  ' + ' '.join([symbols.get(cell, str(cell)) for cell in row]))
        print()
    
    if terminated or truncated:
        print(f"\n  ⚠ Episodio terminado en paso {step+1}")
        if terminated:
            print(f"     Razón: {'Victoria (fuegos apagados)' if fires == 0 else 'Derrota (bosque destruido)'}")
        break

print("\n" + "="*60)
print("DIAGNÓSTICO COMPLETADO")
print("="*60)
print("\nObservaciones:")
print("  - Los fuegos se QUEMAN después de propagarse (realista)")
print("  - Esto simula que el fuego consume el combustible")
print("  - El agente debe EXTINGUIR los fuegos ANTES de que se propaguen")
print("  - Si no hay árboles adyacentes, el fuego se apaga solo")
print("="*60 + "\n")
