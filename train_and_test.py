import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import numpy as np
from stable_baselines3 import PPO
from forest_fire_env import ForestFireEnv

# --- CEREBRO SCRIPT (Agente Naranja) ---
class ScriptedAgent:
    def decide(self, obs, pos, water):
        # 1. Si no tengo agua, voy al río (Fila 0)
        if water <= 0:
            if pos[0] > 0: return 0 # Mover Arriba
            return 6 # Esperar/Recargar
            
        # 2. Buscar fuego más cercano
        r, c = pos
        fires = np.argwhere(obs == 2)
        if len(fires) == 0: return 6 # Esperar
        
        dists = [abs(r-fr) + abs(c-fc) for fr, fc in fires]
        nearest_idx = np.argmin(dists)
        dist = dists[nearest_idx]
        
        # 3. Si estoy cerca, APAGAR
        if dist <= 2: return 5
        
        # 4. Si estoy lejos, Moverse hacia el fuego
        target = fires[nearest_idx]
        tr, tc = target
        if tr < r: return 0
        if tr > r: return 1
        if tc < c: return 2
        if tc > c: return 3
        return 6

def run_cooperative_simulation():
    print("="*60)
    print("INICIANDO SISTEMA MULTI-AGENTE (FOREST GUARDIAN)")
    print("="*60)
    
    # PASO 1: Entrenar IA (Rápido)
    print("\n1. Entrenando al Agente Azul (IA)... (Espere unos segundos)")
    train_env = ForestFireEnv(grid_size=20, num_agents=1)
    
    # Entrenamos solo 10k pasos para que veas el resultado rápido
    # Para el lunes puedes subirlo a 30000 o 50000 si quieres que sea más listo
    model = PPO("MlpPolicy", train_env, verbose=1)
    model.learn(total_timesteps=10000) 
    print(">>> Entrenamiento completado.")
    
    # PASO 2: Simulación
    print("\n2. Generando partida cooperativa...")
    env = ForestFireEnv(grid_size=20, num_agents=2, fire_spread_prob=0.1) 
    obs, _ = env.reset()
    
    script_bot = ScriptedAgent()
    frames = []
    frames.append(env._get_obs().copy()) # Guardar frame inicial
    
    done = False
    step = 0
    max_steps = 100 # Máximo pasos para el GIF
    
    while not done and step < max_steps:
        # Cerebro IA (Azul)
        action_ai, _ = model.predict(obs, deterministic=True)
        
        # Cerebro Script (Naranja)
        pos_bot = env.agent_positions[1]
        water_bot = env.water_tanks[1]
        action_bot = script_bot.decide(obs, pos_bot, water_bot)
        
        # Ejecutar
        obs, reward, terminated, truncated, _ = env.step([action_ai, action_bot])
        
        frames.append(env._get_obs().copy()) # Guardar foto para el GIF
        done = terminated or truncated
        step += 1
        
        # Feedback en terminal
        if step % 10 == 0:
            fires = np.sum(obs == 2)
            print(f"   -> Paso {step}: {fires} fuegos activos.")

    # PASO 3: Guardar GIF
    print(f"\n3. Generando GIF con {len(frames)} imágenes...")
    env.render_animation(frames, filename='forest_fire_coop.gif')
    
    print("\n" + "="*60)
    print("¡PROCESO TERMINADO!")
    print("Busca el archivo 'forest_fire_coop.gif' en tu carpeta.")
    print("="*60)

if __name__ == "__main__":
    run_cooperative_simulation()