"""
Demostración del sistema de fuego realista
- Fuego avanza 5x más lento que el agente (cada 5 pasos)
- Fuego consume cada cuadrado 3x más lento (3 ciclos = 15 pasos)
"""
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import numpy as np
from forest_fire_env import ForestFireEnv

print("\n" + "="*70)
print("DEMOSTRACIÓN: SISTEMA DE FUEGO REALISTA")
print("="*70)
print("\nCaracterísticas:")
print("  🔥 Fuego se propaga cada 5 pasos (5x más lento que el agente)")
print("  ⏳ Cada fuego arde durante 3 ciclos antes de consumirse (15 pasos)")
print("  🚶 Agente se mueve cada paso → tiene 5x más tiempo para reaccionar")
print("="*70 + "\n")

# Crear entorno pequeño para ver mejor
env = ForestFireEnv(
    grid_size=10,
    fire_spread_prob=0.7,  # Alta probabilidad para ver propagación
    initial_trees=0.7,
    initial_fires=2
)

obs, info = env.reset()
print("Estado inicial:")
print(f"  Árboles: {np.sum(env.grid == 1)}")
print(f"  Fuegos: {np.sum(env.grid == 2)}")
print(f"  Fire spread interval: {env.fire_spread_interval} pasos")
print(f"  Fire burnout age: {env.fire_burnout_age} ciclos ({env.fire_burnout_age * env.fire_spread_interval} pasos)")

print("\n" + "-"*70)
print("Ejecutando 30 pasos con acción WAIT para observar el fuego...")
print("-"*70 + "\n")

symbols = {0: '·', 1: '🌲', 2: '🔥', 3: '🤖'}

for step in range(30):
    obs, reward, terminated, truncated, info = env.step(6)  # Wait action
    
    trees = np.sum(env.grid == 1)
    fires = np.sum(env.grid == 2)
    
    # Mostrar cada paso relevante (múltiplos de 5 + eventos)
    if step % 5 == 0 or fires != prev_fires if 'prev_fires' in locals() else True:
        print(f"Paso {step:2d}: Árboles={trees:3d} | Fuegos={fires:2d} | Fire ages: {len(env.fire_age)}")
        
        # Mostrar detalles de edad de fuegos en pasos clave
        if step % 5 == 0 and len(env.fire_age) > 0:
            ages_summary = {}
            for pos, age in env.fire_age.items():
                ages_summary[age] = ages_summary.get(age, 0) + 1
            print(f"         Distribución de edades: {ages_summary}")
    
    prev_fires = fires
    
    if terminated or truncated:
        print(f"\n  ⚠ Episodio terminado en paso {step+1}")
        if fires == 0:
            print("     Razón: Todos los fuegos se apagaron")
        else:
            print(f"     Razón: Bosque destruido ({trees} árboles restantes)")
        break

print("\n" + "="*70)
print("CONCLUSIONES")
print("="*70)
print("\n✅ El fuego ahora es MUCHO más lento y realista:")
print(f"   - Se propaga cada {env.fire_spread_interval} pasos en lugar de cada paso")
print(f"   - Cada fuego arde {env.fire_burnout_age} ciclos ({env.fire_burnout_age * env.fire_spread_interval} pasos totales)")
print("   - Los operarios tienen TIEMPO SUFICIENTE para:")
print("     • Detectar el fuego")
print("     • Moverse hacia él (hasta 5 pasos)")
print("     • Extinguirlo antes de que se propague")
print("\n💡 Esto hace el entorno más estratégico y realista")
print("="*70 + "\n")
