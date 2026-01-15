import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import numpy as np
from forest_fire_env import ForestFireEnv

class TerminatorAgent:
    def decide(self, obs, pos):
        r, c = pos
        # Buscar todos los fuegos
        fires = np.argwhere(obs == 2)
        
        if len(fires) == 0: return 6 # Victoria, descansar
        
        # Buscar el fuego más cercano
        dists = [abs(r-fr) + abs(c-fc) for fr, fc in fires]
        nearest_idx = np.argmin(dists)
        target_r, target_c = fires[nearest_idx]
        dist = dists[nearest_idx]
        
        # LÓGICA AGRESIVA:
        # Si la distancia es 1 (adyacente) o 0 (encima), APAGAR.
        # El entorno apaga en radio 3x3, así que esto es seguro.
        if dist <= 1: 
            return 5
        
        # MOVERSE HACIA EL FUEGO
        # Prioridad: Moverse en el eje donde la distancia es mayor
        diff_r = target_r - r
        diff_c = target_c - c
        
        if abs(diff_r) > abs(diff_c):
            # Mover vertical
            return 1 if diff_r > 0 else 0
        else:
            # Mover horizontal
            return 3 if diff_c > 0 else 2

def make_the_gif():
    print("="*60)
    print("GENERANDO DEMO FINAL (10x10) - CARPETA PERSONALIZADA")
    print("="*60)
    
    # Creamos entorno
    env = ForestFireEnv(grid_size=10, num_agents=2) 
    obs, _ = env.reset()
    
    agent_blue = TerminatorAgent()
    agent_orange = TerminatorAgent()
    
    frames = []
    frames.append(env._get_obs().copy())
    
    done = False
    step = 0
    max_steps = 60
    
    print(">>> Simulando partida...")
    while not done and step < max_steps:
        # Decidir acciones
        act_blue = agent_blue.decide(obs, env.agent_positions[0])
        act_orange = agent_orange.decide(obs, env.agent_positions[1])
        
        # Ejecutar
        obs, _, terminated, _, _ = env.step([act_blue, act_orange])
        
        frames.append(env._get_obs().copy())
        done = terminated
        step += 1
        
        fuegos = np.sum(obs==2)
        if step % 5 == 0:
            print(f"   Step {step}: Quedan {fuegos} celdas de fuego.")

    print(f"\n>>> Generando GIF con {len(frames)} frames...")
    # Nombre de archivo único
    env.render_animation(frames, filename='forest_fire_success.gif')

if __name__ == "__main__":
    make_the_gif()