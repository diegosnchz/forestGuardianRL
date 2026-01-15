import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from forest_fire_env import ForestFireEnv


class OperarioAgent:
    """
    Sub-Agente Operario: Sistema basado en reglas (Hard-coded Logic)
    
    Este agente implementa la lógica de decisiones basada en reglas,
    similar al sistema de crafteo de MineRL. Toma decisiones inmediatas
    basadas en el estado del entorno sin necesidad de aprendizaje.
    
    Responsabilidades:
    - Extinguir fuegos si está adyacente y tiene agua
    - Recargar agua si está en la zona del río
    - Crear cortafuegos si el fuego es muy grande
    """
    
    def __init__(self):
        self.name = "Operario (Rule-based System)"
    
    def decide_action(self, obs, agent_pos, water_level, max_water):
        """
        Decide una acción basada en reglas hardcoded.
        
        Args:
            obs: Observación del entorno (grid)
            agent_pos: Posición actual del agente (row, col)
            water_level: Nivel actual de agua
            max_water: Máximo nivel de agua
            
        Returns:
            action: Acción seleccionada (0-6)
            reason: Razón de la decisión (para debugging)
        """
        row, col = agent_pos
        grid = obs
        
        # Verificar si hay fuego adyacente
        neighbors = [
            (row - 1, col, "up"),
            (row + 1, col, "down"),
            (row, col - 1, "left"),
            (row, col + 1, "right")
        ]
        
        adjacent_fire = False
        fire_count_nearby = 0
        
        for n_row, n_col, direction in neighbors:
            if 0 <= n_row < len(grid) and 0 <= n_col < len(grid[0]):
                if grid[n_row, n_col] == 2:  # Fuego
                    adjacent_fire = True
                    fire_count_nearby += 1
        
        # Regla 1: Si estoy en la zona del río (fila 0) y no tengo agua maxima -> Esperar
        if row == 0 and water_level < max_water:
            return 6, "Recargando agua en el río"
        
        # Regla 2: Si hay fuego adyacente y tengo agua -> Extinguir
        if adjacent_fire and water_level > 0:
            return 5, f"Extinguiendo fuego adyacente (fuegos cercanos: {fire_count_nearby})"
        
        # Regla 3: Si no tengo agua y hay fuego -> Navegar al río
        if water_level == 0 and fire_count_nearby > 0:
            # Moverse hacia arriba (hacia el río en fila 0)
            if row > 0:
                return 0, "Sin agua! Navegando al río"
            else:
                return 6, "Esperando en el río para recargar"
        
        # Regla 4: Si hay árbol adyacente y tengo agua baja -> Cortar árbol (cortafuegos)
        adjacent_tree = False
        for n_row, n_col, direction in neighbors:
            if 0 <= n_row < len(grid) and 0 <= n_col < len(grid[0]):
                if grid[n_row, n_col] == 1 and fire_count_nearby > 0:  # Árbol + hay fuego
                    adjacent_tree = True
        
        if adjacent_tree and water_level < 3 and fire_count_nearby > 0:
            return 4, "Cortando árbol para crear cortafuegos"
        
        # Si no hay urgencia, devolver None (dejar que el Navegante controle)
        return None, "No hay amenaza inmediata - Navegante toma control"


class NavegadorAgent:
    """
    Sub-Agente Navegador: Modelo PPO para movimiento inteligente
    
    Este agente es una red neuronal entrenada con PPO que aprende a:
    - Navegar hacia los fuegos para extinguirlos
    - Navegar hacia la zona del río para recargar agua
    - Evitar áreas densas de árboles cuando sea posible
    
    Este agente solo se activa cuando el Operario no tiene una regla aplicable.
    """
    
    def __init__(self, model):
        self.model = model
        self.name = "Navegador (PPO Neural Network)"
    
    def decide_action(self, obs):
        """
        Decide una acción usando el modelo PPO entrenado.
        
        Args:
            obs: Observación del entorno (grid)
            
        Returns:
            action: Acción seleccionada (0-6)
        """
        action, _states = self.model.predict(obs, deterministic=True)
        return action


class ForestGuardianManager:
    """
    Controlador Jerárquico: Coordina Sub-Agentes
    
    Implementa la arquitectura MineRL-inspired donde:
    - El Operario maneja situaciones inmediatas y críticas
    - El Navegador maneja la navegación estratégica
    
    Esta arquitectura permite:
    1. Decisiones rápidas y confiables (Operario)
    2. Aprendizaje y adaptación (Navegador)
    3. Escalabilidad a más sub-agentes especializados
    """
    
    def __init__(self, ppo_model):
        self.operario = OperarioAgent()
        self.navegador = NavegadorAgent(ppo_model)
        self.name = "ForestGuardianManager (Hierarchical Controller)"
        
        # Estadísticas para debugging
        self.operario_actions = 0
        self.navegador_actions = 0
        self.operario_action_history = []
        self.navegador_action_history = []
    
    def decide_action(self, obs, agent_pos, water_level, max_water):
        """
        Decide la mejor acción coordinando ambos sub-agentes.
        
        Proceso:
        1. Intenta aplicar una regla del Operario
        2. Si no hay regla aplicable, usa el Navegador
        
        Args:
            obs: Observación del entorno
            agent_pos: Posición del agente
            water_level: Nivel de agua
            max_water: Máximo nivel de agua
            
        Returns:
            action: Acción seleccionada
            agent_name: Nombre del sub-agente que decidió
        """
        
        # Primero intenta el Operario
        action, reason = self.operario.decide_action(obs, agent_pos, water_level, max_water)
        
        if action is not None:
            # El Operario tiene una decisión basada en reglas
            self.operario_actions += 1
            self.operario_action_history.append(reason)
            return action, self.operario.name, reason
        else:
            # El Navegador toma el control para exploración/aprendizaje
            action = self.navegador.decide_action(obs)
            self.navegador_actions += 1
            self.navegador_action_history.append(f"Action {action}")
            return action, self.navegador.name, "Strategic movement"
    
    def print_statistics(self):
        """Imprime estadísticas de uso de los sub-agentes."""
        total = self.operario_actions + self.navegador_actions
        if total == 0:
            return
        
        operario_pct = (self.operario_actions / total) * 100
        navegador_pct = (self.navegador_actions / total) * 100
        
        print(f"\n{'='*60}")
        print(f"Estadísticas del ForestGuardianManager:")
        print(f"{'='*60}")
        print(f"Total de acciones: {total}")
        print(f"  - Operario (Reglas):  {self.operario_actions:4d} ({operario_pct:5.1f}%)")
        print(f"  - Navegador (PPO):    {self.navegador_actions:4d} ({navegador_pct:5.1f}%)")
        print(f"{'='*60}\n")


def train_agent(total_timesteps=50000):
    """Train a PPO agent on the ForestFireEnv."""
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
    """
    Test the trained agent using the Hierarchical Manager.
    
    Esto demuestra la arquitectura MineRL donde:
    - El Operario maneja situaciones críticas (sin agua, fuego adyacente, etc)
    - El Navegador aprende a explorar y navegar estratégicamente
    """
    print(f"\n{'='*60}")
    print(f"PRUEBA CON ARQUITECTURA JERÁRQUICA (Hierarchical RL)")
    print(f"{'='*60}")
    print(f"Testing {n_episodes} episodes with ForestGuardianManager...")
    print(f"{'='*60}\n")
    
    # Crear el manager jerárquico
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
            # Usar el Manager jerárquico para decidir la acción
            action, agent_name, reason = manager.decide_action(
                obs, 
                env.agent_pos, 
                env.water_tank, 
                env.max_water
            )
            
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            total_reward += reward
            steps += 1
            
            # Debug: mostrar información cada 10 pasos
            if steps % 10 == 0:
                print(f"  Step {steps}: Agent={agent_name[:20]:20s} | "
                      f"Water={env.water_tank}/{env.max_water} | "
                      f"Reward={total_reward:7.1f}")
        
        episode_rewards.append(total_reward)
        episode_lengths.append(steps)
        operario_pct = (manager.operario_actions / (manager.operario_actions + 
                                                    manager.navegador_actions)) * 100 if (manager.operario_actions + 
                                                                                           manager.navegador_actions) > 0 else 0
        episode_operario_usage.append(operario_pct)
        
        print(f"{'-'*60}")
        print(f"  Total Reward: {total_reward:.2f}")
        print(f"  Steps: {steps}")
        print(f"  Trees remaining: {np.sum(env.grid == 1)}")
        print(f"  Fires remaining: {np.sum(env.grid == 2)}")
        print(f"  Operario usage: {operario_pct:.1f}%")
    
    print(f"\n{'='*60}")
    print(f"Resumen de Pruebas con Arquitectura Jerárquica:")
    print(f"{'='*60}")
    print(f"  Average Reward: {np.mean(episode_rewards):.2f} ± {np.std(episode_rewards):.2f}")
    print(f"  Average Length: {np.mean(episode_lengths):.2f} ± {np.std(episode_lengths):.2f}")
    print(f"  Average Operario Usage: {np.mean(episode_operario_usage):.1f}%")
    print(f"{'='*60}\n")
    
    # Imprimir estadísticas del manager
    manager.print_statistics()
    
    return episode_rewards, episode_lengths, manager


def visualize_episode(model, env):
    """Visualize an episode using the hierarchical manager."""
    print("\nVisualizing a single episode with Hierarchical Manager...")
    
    # Crear el manager para la visualización
    manager = ForestGuardianManager(model)
    
    obs, info = env.reset()
    done = False
    frames = []
    actions_taken = []
    
    # Capture initial state
    frames.append(env.grid.copy())
    
    step = 0
    max_steps = 50
    
    while not done and step < max_steps:
        action, agent_name, reason = manager.decide_action(
            obs, 
            env.agent_pos, 
            env.water_tank, 
            env.max_water
        )
        actions_taken.append((agent_name, reason))
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        frames.append(env.grid.copy())
        step += 1
    
    # Create a visualization showing key frames
    n_frames_to_show = min(6, len(frames))
    frame_indices = np.linspace(0, len(frames) - 1, n_frames_to_show, dtype=int)
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Forest Fire - Hierarchical RL Episode Visualization', fontsize=16)
    
    for idx, frame_idx in enumerate(frame_indices):
        row = idx // 3
        col = idx % 3
        ax = axes[row, col]
        
        display_grid = frames[frame_idx].copy()
        
        colors = np.zeros((env.grid_size, env.grid_size, 3))
        colors[display_grid == 0] = [1, 1, 1]      # White for empty
        colors[display_grid == 1] = [0, 0.7, 0]    # Green for trees
        colors[display_grid == 2] = [1, 0, 0]      # Red for fire
        colors[display_grid == 3] = [0, 0, 1]      # Blue for agent
        
        ax.imshow(colors, interpolation='nearest')
        ax.grid(True, which='both', color='black', linewidth=0.5)
        ax.set_xticks(np.arange(-0.5, env.grid_size, 1))
        ax.set_yticks(np.arange(-0.5, env.grid_size, 1))
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        
        trees = np.sum(frames[frame_idx] == 1)
        fires = np.sum(frames[frame_idx] == 2)
        ax.set_title(f'Step {frame_idx} | Trees: {trees} | Fires: {fires}')
    
    plt.tight_layout()
    plt.savefig('forest_fire_hierarchical_visualization.png', dpi=150, bbox_inches='tight')
    print(f"Visualization saved to 'forest_fire_hierarchical_visualization.png'")
    plt.show()


def main():
    """Main function to train and test the agent."""
    print("\n" + "="*60)
    print("FOREST GUARDIAN RL - ARQUITECTURA JERÁRQUICA (MineRL-Inspired)")
    print("="*60 + "\n")
    
    # 1. Entrenar el Navegador (PPO)
    model, env = train_agent(total_timesteps=50000)
    
    # 2. Prueba con arquitectura jerárquica
    hierarchical_rewards, hierarchical_lengths, manager = test_agent(model, env, n_episodes=3)
    
    # 3. Visualizar un episodio con arquitectura jerárquica
    visualize_episode(model, env)
    
    print("\n" + "="*60)
    print("Training and testing complete!")
    print("="*60)
    print(f"\nGenerated files:")
    print(f"  - ppo_forest_fire.zip (trained Navegador model)")
    print(f"  - forest_fire_hierarchical_visualization.png")
    print(f"\nArchitecture Summary:")
    print(f"  - Operario Agent: Rule-based system for critical decisions")
    print(f"  - Navegador Agent: PPO neural network for strategic movement")
    print(f"  - Manager: Hierarchical controller coordinating both agents")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
