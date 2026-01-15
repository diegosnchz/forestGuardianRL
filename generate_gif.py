"""
Script rápido para generar el GIF de visualización sin reentrenar
"""
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import numpy as np
from stable_baselines3 import PPO
from forest_fire_env import ForestFireEnv


class OperarioAgent:
    def __init__(self):
        self.name = "Operario (Rule-based System)"
    
    def decide_action(self, obs, agent_pos, water_level, max_water):
        row, col = agent_pos
        grid = obs
        neighbors = [
            (row - 1, col, 0), (row + 1, col, 1),
            (row, col - 1, 2), (row, col + 1, 3)
        ]
        adjacent_fire = False
        fire_count_nearby = 0
        adjacent_tree = False
        for n_row, n_col, _ in neighbors:
            if 0 <= n_row < len(grid) and 0 <= n_col < len(grid[0]):
                if grid[n_row, n_col] == 2:
                    adjacent_fire = True
                    fire_count_nearby += 1
                if grid[n_row, n_col] == 1:
                    adjacent_tree = True
        if row == 0 and water_level < max_water:
            return 6, "Recargando agua en el río"
        if adjacent_tree and water_level < 3 and fire_count_nearby > 0:
            return 4, "Cortafuegos: Cortando árbol adyacente"
        return None, "Sin amenaza inmediata - Navegador controla"


class NavegadorAgent:
    def __init__(self, model):
        self.model = model
        self.name = "Navegador (PPO Neural Network)"
    
    def decide_action(self, obs):
        processed = np.where(obs == 4, 3, obs)
        action, _states = self.model.predict(processed, deterministic=True)
        return action


class ForestGuardianManager:
    def __init__(self, ppo_model):
        self.operario = OperarioAgent()
        self.navegador = NavegadorAgent(ppo_model)
        self.name = "ForestGuardianManager"
        self.operario_actions = 0
        self.navegador_actions = 0
    
    @staticmethod
    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    @staticmethod
    def nearest_fire(obs, agent_pos):
        fires = np.argwhere(obs == 2)
        if len(fires) == 0:
            return None, None
        dists = [ForestGuardianManager.manhattan(agent_pos, tuple(f)) for f in fires]
        idx = int(np.argmin(dists))
        return tuple(fires[idx]), int(dists[idx])
    
    @staticmethod
    def has_adjacent(obs, agent_pos, value):
        r, c = agent_pos
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < obs.shape[0] and 0 <= nc < obs.shape[1]:
                if obs[nr, nc] == value:
                    return True, (nr, nc)
        return False, None
    
    @staticmethod
    def move_towards(agent_pos, target_pos):
        ar, ac = agent_pos
        tr, tc = target_pos
        if tr < ar:
            return 0
        if tr > ar:
            return 1
        if tc < ac:
            return 2
        if tc > ac:
            return 3
        return 6
    
    def decide_action(self, obs, agent_pos, water_level, max_water):
        nearest, dist = self.nearest_fire(obs, agent_pos)
        on_fire = (obs[agent_pos] == 2)
        adj_fire, adj_fire_pos = self.has_adjacent(obs, agent_pos, 2)
        
        if water_level == 0:
            self.operario_actions += 1
            reason = "Sin agua: Operario fuerza Wait/Recarga"
            return 6, self.operario.name, reason
        
        if dist == 1 and water_level > 0:
            if on_fire:
                self.operario_actions += 1
                reason = "Operario: Fuego en la celda -> Extinguir"
                return 5, self.operario.name, reason
            if adj_fire and adj_fire_pos is not None:
                action = self.move_towards(agent_pos, adj_fire_pos)
                self.operario_actions += 1
                reason = "Operario: Mover al fuego adyacente"
                return action, self.operario.name, reason
        
        action, reason = self.operario.decide_action(obs, agent_pos, water_level, max_water)
        if action is not None:
            self.operario_actions += 1
            return action, self.operario.name, reason
        
        action = self.navegador.decide_action(obs)
        reason = "Navegador: movimiento estratégico"
        
        if action == 5:
            valid = on_fire or adj_fire
            if not valid:
                if nearest is not None:
                    action = self.move_towards(agent_pos, nearest)
                    reason = "Bloqueo Extinguir: Navegar hacia el fuego"
                else:
                    action = 6
                    reason = "Bloqueo Extinguir: No hay fuego"
        elif action == 4:
            adj_tree, _ = self.has_adjacent(obs, agent_pos, 1)
            if not adj_tree and obs[agent_pos] != 1:
                if nearest is not None:
                    action = self.move_towards(agent_pos, nearest)
                    reason = "Bloqueo Talar: Navegar hacia el fuego"
                else:
                    action = 6
                    reason = "Bloqueo Talar: No hay objetivo"
        
        self.navegador_actions += 1
        return action, self.navegador.name, reason


def main():
    print("\n" + "="*60)
    print("GENERANDO GIF - FOREST GUARDIAN RL")
    print("="*60 + "\n")
    
    # Load trained model
    print("Cargando modelo entrenado...")
    model = PPO.load("ppo_forest_fire")
    print("✓ Modelo cargado\n")
    
    # Create manager
    manager = ForestGuardianManager(model)
    
    # Create single-agent environment (color changes based on who decides)
    print("Creando entorno...")
    vis_env = ForestFireEnv(grid_size=20, num_agents=1)
    obs, info = vis_env.reset()
    print("✓ Entorno creado")
    print("  (El agente cambia de color según quién decide:)")
    print("  🟦 Azul = Navegador (PPO) | 🟧 Naranja = Operario (Reglas)\n")
    
    frames = []
    agent_labels = []
    agent_positions = []
    
    # Initial frame - capture grid WITHOUT agent overlay
    initial_frame = vis_env.grid.copy()
    frames.append(initial_frame)
    agent_labels.append('navegador')
    agent_positions.append(vis_env.agent_pos)
    
    step = 0
    done = False
    total_reward = 0
    extinguish_count = 0
    
    print(f"Capturando simulación hasta que termine naturalmente...")
    print("-" * 60)
    
    while not done:
        # Decide action
        action, agent_name, reason = manager.decide_action(
            obs, vis_env.agent_pos, vis_env.water_tank, vis_env.max_water
        )
        
        # Determine which agent
        if 'Operario' in agent_name:
            agent_label = 'operario'
            symbol = '🟧'
            agent_marker = 4  # Orange
        else:
            agent_label = 'navegador'
            symbol = '🟦'
            agent_marker = 3  # Blue
        
        # Count extinguish actions
        action_int = int(action) if hasattr(action, '__iter__') else action
        if action_int == 5:
            extinguish_count += 1
        
        # Execute action
        obs, reward, terminated, truncated, info = vis_env.step(action)
        total_reward += reward
        done = terminated or truncated
        
        # Capture frame: grid state ONLY (no agent baked in)
        frame = vis_env.grid.copy()
        frames.append(frame)
        agent_labels.append(agent_label)
        agent_positions.append(vis_env.agent_pos)
        step += 1
        
        # Action names for display
        action_names = {0: "⬆️Arriba", 1: "⬇️Abajo", 2: "⬅️Izq", 3: "➡️Der", 
                       4: "✂️Talar", 5: "💧Apagar", 6: "⏸️Esperar"}
        
        # Show progress with more detail
        fires = np.sum(vis_env.grid == 2)
        trees = np.sum(vis_env.grid == 1)
        print(f"  Step {step:2d}: {symbol} {agent_label:10s} | Acción: {action_names.get(action_int, str(action_int)):12s} | "
              f"🔥:{fires:2d} 🌲:{trees:2d} 💧:{vis_env.water_tank}/{vis_env.max_water} | Reward: {reward:+6.1f}")
        
        # Safety limit
        if step >= 100:
            print(f"\n  ⚠ Alcanzado límite de seguridad de 100 pasos")
            break
    
    # Determine why episode ended
    final_fires = np.sum(vis_env.grid == 2)
    final_trees = np.sum(vis_env.grid == 1)
    initial_trees = vis_env.initial_tree_count
    destruction_pct = (1 - final_trees / initial_trees) * 100 if initial_trees > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"  ✓ Episodio terminó en paso {step}")
    print(f"{'='*60}")
    
    if final_fires == 0:
        print(f"  🎉 VICTORIA: Todos los fuegos fueron apagados")
        print(f"  🌲 Árboles salvados: {final_trees}/{initial_trees} ({100-destruction_pct:.1f}%)")
    elif destruction_pct >= 80:
        print(f"  💥 DERROTA: Bosque destruido (>{destruction_pct:.1f}% perdido)")
        print(f"  🔥 Fuegos restantes: {final_fires}")
    else:
        print(f"  ⚠️ Truncado por límite de pasos")
    
    print(f"\n  Acciones de Apagar ejecutadas: {extinguish_count}")
    print(f"  Recompensa total: {total_reward:.1f}")
    
    print("-" * 60)
    print(f"\n✓ {len(frames)} frames capturados")
    print(f"\nEstadísticas de agentes:")
    print(f"  🟧 Operario (Reglas):  {manager.operario_actions} acciones")
    print(f"  🟦 Navegador (PPO):    {manager.navegador_actions} acciones")
    
    # Find next version number
    import os
    import glob
    gif_dir = 'GIF'
    os.makedirs(gif_dir, exist_ok=True)
    existing_gifs = glob.glob(os.path.join(gif_dir, 'forest_fire_simulation_v*.gif'))
    version = 1
    if existing_gifs:
        versions = [int(f.split('_v')[-1].split('.')[0]) for f in existing_gifs if '_v' in f]
        if versions:
            version = max(versions) + 1
    
    gif_filename = os.path.join(gif_dir, f'forest_fire_simulation_v{version}.gif')
    
    # Generate GIF
    print(f"\nGenerando GIF animado...")
    vis_env.render_animation(
        frames, 
        agent_labels=agent_labels,
        filename=gif_filename, 
        fps=5
    )
    
    print("\n" + "="*60)
    print("✓ GIF GENERADO EXITOSAMENTE")
    print("="*60)
    print(f"\nArchivo: {gif_filename}")
    print(f"Frames: {len(frames)} (episodio completo sin relleno)")
    print(f"Duración: ~{len(frames)/5:.1f} segundos")
    print("\nCómo interpretar:")
    print("  - UN solo agente que cambia de color según quién decide")
    print("  - 🟦 Azul: Navegador (IA/PPO) está controlando")
    print("  - 🟧 Naranja: Operario (Reglas) está controlando")
    print("\nColores del entorno:")
    print("  ⚪ Blanco: Vacío/Quemado")
    print("  🟢 Verde: Árboles")
    print("  🔴 Rojo: Fuego")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
