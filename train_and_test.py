import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import numpy as np
import time
from forest_fire_env import ForestFireEnv

class TerminatorAgent:
    def __init__(self, role="nearest"):
        self.role = role # 'nearest' o 'farthest'

    def decide(self, obs, pos):
        r, c = pos
        fires = np.argwhere(obs == 2)
        
        if len(fires) == 0: return 6
        
        # Calcular distancias a todos los fuegos
        dists = [abs(r-fr) + abs(c-fc) for fr, fc in fires]
        
        # ESTRATEGIA DE EQUIPO:
        if self.role == "nearest":
            # El azul va al más cercano
            target_idx = np.argmin(dists)
        else:
            # El naranja intenta ir al más lejano (para rodear)
            # Pero si solo hay 1 fuego, va a ese.
            if len(fires) > 1:
                target_idx = np.argmax(dists)
            else:
                target_idx = np.argmin(dists)

        target_r, target_c = fires[target_idx]
        dist = dists[target_idx]
        
        # Disparar si estoy al lado
        if dist <= 1: 
            return 5
            
        # Moverse
        diff_r = target_r - r
        diff_c = target_c - c
        
        if abs(diff_r) > abs(diff_c):
            return 1 if diff_r > 0 else 0
        else:
            return 3 if diff_c > 0 else 2

def make_the_gif():
    print("="*60)
    print("GENERANDO DEMO ESTOCÁSTICA (SIN SUPERPOSICIÓN)")
    print("="*60)
    
    # Entorno aleatorio
    env = ForestFireEnv(grid_size=10, num_agents=2, initial_fires=3) 
    obs, _ = env.reset()
    
    # ASIGNAMOS ROLES PARA QUE NO SE PISEN
    agent_blue = TerminatorAgent(role="nearest")
    agent_orange = TerminatorAgent(role="farthest")
    
    frames = []
    frames.append(env._get_obs().copy())
    
    done = False
    step = 0
    max_steps = 80
    
    print(">>> Simulando partida cooperativa...")
    while not done and step < max_steps:
        # Decidir acciones
        act_blue = agent_blue.decide(obs, env.agent_positions[0])
        act_orange = agent_orange.decide(obs, env.agent_positions[1])
        
        # Ejecutar
        obs, _, terminated, _, _ = env.step([act_blue, act_orange])
        
        frames.append(env._get_obs().copy())
        done = terminated
        step += 1
        
        if step % 5 == 0:
            fuegos = np.sum(obs==2)
            print(f"   Step {step}: Quedan {fuegos} fuegos.")

    print(f"\n>>> Generando GIF único...")
    
    # Nombre único basado en el tiempo
    timestamp = int(time.time())
    filename = f'forest_fire_demo_{timestamp}.gif'
    
    env.render_animation(frames, filename=filename)

if __name__ == "__main__":
    make_the_gif()