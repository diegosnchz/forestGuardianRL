import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from forest_fire_env import ForestFireEnv


class OperarioAgent:
    """
    Sub-Agente Operario: Sistema basado en reglas (Hard-coded Logic)
    
    Responsabilidades clave (forzadas por el Manager):
    - Si hay fuego a distancia 1 y tengo agua: mover/extinguir (prioridad máxima)
    - Si agua == 0: esperar/recargar (prioridad máxima)
    - Reglas complementarias de seguridad (navegación al río, cortafuegos)
    """
    
    def __init__(self):
        self.name = "Operario (Rule-based System)"
    
    def decide_action(self, obs, agent_pos, water_level, max_water):
        """Reglas complementarias (manager aplicará las forzadas)."""
        row, col = agent_pos
        grid = obs
        
        # Verificar entorno adyacente
        neighbors = [
            (row - 1, col, 0),   # up action id
            (row + 1, col, 1),   # down
            (row, col - 1, 2),   # left
            (row, col + 1, 3)    # right
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
        
        # Si estoy en el río y falta agua -> Esperar (recargar)
        if row == 0 and water_level < max_water:
            return 6, "Recargando agua en el río"
        
        # Si hay árbol adyacente y poco agua y hay fuego cerca -> Cortafuegos
        if adjacent_tree and water_level < 3 and fire_count_nearby > 0:
            return 4, "Cortafuegos: Cortando árbol adyacente"
        
        # Ceder control al Navegador si no hay urgencia
        return None, "Sin amenaza inmediata - Navegador controla"


class NavegadorAgent:
    """
    Sub-Agente Navegador: Modelo PPO para movimiento inteligente.
    Preprocesa la observación para soportar multi-agente visual (4→3).
    """
    
    def __init__(self, model):
        self.model = model
        self.name = "Navegador (PPO Neural Network)"
    
    def decide_action(self, obs):
        # Preprocesar: reemplazar '4' (segundo agente) por '3' para el modelo
        processed = np.where(obs == 4, 3, obs)
        action, _states = self.model.predict(processed, deterministic=True)
        return action


class ForestGuardianManager:
    """
    Controlador Jerárquico con restricciones:
    - Fuerza al Operario en casos críticos.
    - Bloquea acciones de PPO (talar/apagar) si no hay objetivos adyacentes.
    """
    
    def __init__(self, ppo_model):
        self.operario = OperarioAgent()
        self.navegador = NavegadorAgent(ppo_model)
        self.name = "ForestGuardianManager (Hierarchical Controller)"
        
        self.operario_actions = 0
        self.navegador_actions = 0
        self.operario_action_history = []
        self.navegador_action_history = []
    
    @staticmethod
    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    @staticmethod
    def nearest_fire(obs, agent_pos):
        fires = np.argwhere(obs == 2)
        if len(fires) == 0:
            return None, None  # no fires
        # find nearest
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
            return 0  # up
        if tr > ar:
            return 1  # down
        if tc < ac:
            return 2  # left
        if tc > ac:
            return 3  # right
        return 6  # already there -> wait
    
    def decide_action(self, obs, agent_pos, water_level, max_water):
        # Reglas forzadas primero
        nearest, dist = self.nearest_fire(obs, agent_pos)
        on_fire = (obs[agent_pos] == 2)
        adj_fire, adj_fire_pos = self.has_adjacent(obs, agent_pos, 2)
        
        # 1) Sin agua -> Operario fuerza recarga
        if water_level == 0:
            self.operario_actions += 1
            reason = "Sin agua: Operario fuerza Wait/Recarga"
            self.operario_action_history.append(reason)
            return 6, self.operario.name, reason
        
        # 2) Fuego a distancia 1 y tengo agua -> Operario fuerza acción
        if dist == 1 and water_level > 0:
            if on_fire:
                self.operario_actions += 1
                reason = "Operario: Fuego en la celda -> Extinguir"
                self.operario_action_history.append(reason)
                return 5, self.operario.name, reason
            if adj_fire and adj_fire_pos is not None:
                # Moverse hacia el fuego adyacente (un paso)
                action = self.move_towards(agent_pos, adj_fire_pos)
                self.operario_actions += 1
                reason = "Operario: Mover al fuego adyacente para extinguir"
                self.operario_action_history.append(reason)
                return action, self.operario.name, reason
        
        # 3) Reglas complementarias del Operario
        action, reason = self.operario.decide_action(obs, agent_pos, water_level, max_water)
        if action is not None:
            self.operario_actions += 1
            self.operario_action_history.append(reason)
            return action, self.operario.name, reason
        
        # 4) Navegador (PPO) toma control con restricciones
        action = self.navegador.decide_action(obs)
        reason = "Navegador: movimiento estratégico"
        
        # Bloquear talar/apagar si no hay objetivo adyacente
        if action == 5:  # Extinguir
            valid = on_fire or adj_fire
            if not valid:
                if nearest is not None:
                    action = self.move_towards(agent_pos, nearest)
                    reason = "Bloqueo Extinguir: Navegar hacia el fuego"
                else:
                    action = 6
                    reason = "Bloqueo Extinguir: No hay fuego, esperar"
        elif action == 4:  # Talar
            adj_tree, adj_tree_pos = self.has_adjacent(obs, agent_pos, 1)
            if not adj_tree and obs[agent_pos] != 1:
                if nearest is not None:
                    action = self.move_towards(agent_pos, nearest)
                    reason = "Bloqueo Talar: Navegar hacia el fuego"
                else:
                    action = 6
                    reason = "Bloqueo Talar: No hay objetivo, esperar"
        
        self.navegador_actions += 1
        self.navegador_action_history.append(reason)
        return action, self.navegador.name, reason
    
    def print_statistics(self):
        total = self.operario_actions + self.navegador_actions
        if total == 0:
            return
        operario_pct = (self.operario_actions / total) * 100
        navegador_pct = (self.navegador_actions / total) * 100
        print(f"\n{'='*60}")
        print("Estadísticas del ForestGuardianManager:")
        print(f"{'='*60}")
        print(f"Total de acciones: {total}")
        print(f"  - Operario (Reglas/Forzadas): {self.operario_actions:4d} ({operario_pct:5.1f}%)")
        print(f"  - Navegador (PPO):            {self.navegador_actions:4d} ({navegador_pct:5.1f}%)")
        print(f"{'='*60}\n")


def train_agent(total_timesteps=50000):
    print("="*60)
    print("ENTRENAMIENTO DEL NAVEGADOR (PPO Agent)")
    print("="*60)
    print("Creating environment...")
    env = ForestFireEnv()
    
    print("Initializing PPO agent (Navegador)...")
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
    )
    
    print(f"\nTraining Navegador for {total_timesteps} timesteps...")
    model.learn(total_timesteps=total_timesteps)
    
    print("\nSaving model...")
    model.save("ppo_forest_fire")
    
    return model, env


def test_agent(model, env, n_episodes=5):
    print(f"\n{'='*60}")
    print("PRUEBA CON ARQUITECTURA JERÁRQUICA (Hierarchical RL)")
    print(f"{'='*60}")
    print(f"Testing {n_episodes} episodes with ForestGuardianManager...")
    print(f"{'='*60}\n")
    manager = ForestGuardianManager(model)
    episode_rewards = []
    episode_lengths = []
    episode_operario_usage = []
    for episode in range(n_episodes):
        obs, info = env.reset()
        done = False
        total_reward = 0
        steps = 0
        print(f"\nEpisode {episode + 1}/{n_episodes}")
        print(f"{'-'*60}")
        while not done:
            action, agent_name, reason = manager.decide_action(
                obs, env.agent_pos, env.water_tank, env.max_water
            )
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            total_reward += reward
            steps += 1
            if steps % 10 == 0:
                print(f"  Step {steps}: Agent={agent_name[:20]:20s} | Water={env.water_tank}/{env.max_water} | Reward={total_reward:7.1f}")
        episode_rewards.append(total_reward)
        episode_lengths.append(steps)
        operario_pct = (manager.operario_actions / (manager.operario_actions + manager.navegador_actions)) * 100 if (manager.operario_actions + manager.navegador_actions) > 0 else 0
        episode_operario_usage.append(operario_pct)
        print(f"{'-'*60}")
        print(f"  Total Reward: {total_reward:.2f}")
        print(f"  Steps: {steps}")
        print(f"  Trees remaining: {np.sum(env.grid == 1)}")
        print(f"  Fires remaining: {np.sum(env.grid == 2)}")
        print(f"  Operario usage: {operario_pct:.1f}%")
    print(f"\n{'='*60}")
    print("Resumen de Pruebas con Arquitectura Jerárquica:")
    print(f"{'='*60}")
    print(f"  Average Reward: {np.mean(episode_rewards):.2f} ± {np.std(episode_rewards):.2f}")
    print(f"  Average Length: {np.mean(episode_lengths):.2f} ± {np.std(episode_lengths):.2f}")
    print(f"  Average Operario Usage: {np.mean(episode_operario_usage):.1f}%")
    print(f"{'='*60}\n")
    manager.print_statistics()
    return episode_rewards, episode_lengths, manager


def visualize_episode(model, env):
    """Visualize an episode with dual-agent display and save as animated GIF."""
    print("\nGenerating animated GIF with dual-agent visualization...")
    
    manager = ForestGuardianManager(model)
    # Use dual-agent environment for visualization
    vis_env = ForestFireEnv(num_agents=2)
    obs, info = vis_env.reset()
    done = False
    frames = []
    agent_labels = []
    
    # Initial frame
    frames.append(vis_env._get_obs())
    agent_labels.append('inicio')
    
    step = 0
    max_steps = 100  # Increased for longer episodes
    
    while not done and step < max_steps:
        # Decide action using manager
        action, agent_name, reason = manager.decide_action(
            obs, vis_env.agent_pos, vis_env.water_tank, vis_env.max_water
        )
        
        # Determine which agent is acting
        if 'Operario' in agent_name:
            agent_label = 'operario'
        else:
            agent_label = 'navegador'
        
        obs, reward, terminated, truncated, info = vis_env.step(action)
        done = terminated or truncated
        
        # Capture frame with agent positions
        frames.append(vis_env._get_obs())
        agent_labels.append(agent_label)
        step += 1
    
    print(f"Episode completed: {step} steps")
    
    # Save animated GIF
    vis_env.render_animation(
        frames, 
        agent_labels=agent_labels,
        filename='forest_fire_simulation.gif', 
        fps=6
    )
    
    print(f"\nVisualization complete!")
    print(f"  - Animated GIF: forest_fire_simulation.gif")
    print(f"  - Total frames: {len(frames)}")
    print(f"  - Operario actions: {manager.operario_actions}")
    print(f"  - Navegador actions: {manager.navegador_actions}")


def main():
    print("\n" + "="*60)
    print("FOREST GUARDIAN RL - ARQUITECTURA JERÁRQUICA (MineRL-Inspired)")
    print("="*60 + "\n")
    model, env = train_agent(total_timesteps=50000)
    hierarchical_rewards, hierarchical_lengths, manager = test_agent(model, env, n_episodes=3)
    visualize_episode(model, env)
    print("\n" + "="*60)
    print("Training and testing complete!")
    print("="*60)
    print(f"\nGenerated files:")
    print(f"  - ppo_forest_fire.zip (trained Navegador model)")
    print(f"  - forest_fire_simulation.gif (animated episode)")
    print(f"\nArchitecture Summary:")
    print(f"  - Operario Agent: Rule-based system for critical decisions")
    print(f"  - Navegador Agent: PPO neural network for strategic movement")
    print(f"  - Manager: Hierarchical controller coordinating both agents")
    print(f"\nVisualization:")
    print(f"  - Blue square: Navegador (PPO) acting")
    print(f"  - Orange square: Operario (Rules) acting")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
