import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from forest_fire_env import ForestFireEnv


def train_agent(total_timesteps=20000):
    """Train a PPO agent on the ForestFireEnv."""
    print("Creating environment...")
    env = ForestFireEnv()
    
    print("Initializing PPO agent...")
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
    
    print(f"\nTraining for {total_timesteps} timesteps...")
    model.learn(total_timesteps=total_timesteps)
    
    print("\nSaving model...")
    model.save("ppo_forest_fire")
    
    return model, env


def test_agent(model, env, n_episodes=5):
    """Test the trained agent and visualize results."""
    print(f"\n{'='*50}")
    print(f"Testing trained agent for {n_episodes} episodes...")
    print(f"{'='*50}\n")
    
    episode_rewards = []
    episode_lengths = []
    
    for episode in range(n_episodes):
        obs, info = env.reset()
        done = False
        total_reward = 0
        steps = 0
        
        print(f"\nEpisode {episode + 1}/{n_episodes}")
        
        while not done:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            total_reward += reward
            steps += 1
        
        episode_rewards.append(total_reward)
        episode_lengths.append(steps)
        
        print(f"  Total Reward: {total_reward:.2f}")
        print(f"  Steps: {steps}")
        print(f"  Trees remaining: {np.sum(env.grid == 1)}")
        print(f"  Fires remaining: {np.sum(env.grid == 2)}")
    
    print(f"\n{'='*50}")
    print(f"Test Results Summary:")
    print(f"  Average Reward: {np.mean(episode_rewards):.2f} ± {np.std(episode_rewards):.2f}")
    print(f"  Average Length: {np.mean(episode_lengths):.2f} ± {np.std(episode_lengths):.2f}")
    print(f"{'='*50}\n")
    
    return episode_rewards, episode_lengths


def visualize_episode(model, env):
    """Visualize a single episode step by step."""
    print("\nVisualizing a single episode...")
    
    obs, info = env.reset()
    done = False
    frames = []
    
    # Create figure for animation
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Capture initial state
    frames.append(env.grid.copy())
    
    step = 0
    max_steps = 50  # Limit visualization steps
    
    while not done and step < max_steps:
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        frames.append(env.grid.copy())
        step += 1
    
    # Create a visualization showing key frames
    n_frames_to_show = min(6, len(frames))
    frame_indices = np.linspace(0, len(frames) - 1, n_frames_to_show, dtype=int)
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Forest Fire Episode Visualization', fontsize=16)
    
    for idx, frame_idx in enumerate(frame_indices):
        row = idx // 3
        col = idx % 3
        ax = axes[row, col]
        
        # Reconstruct the display grid for this frame
        display_grid = frames[frame_idx].copy()
        
        # Create color map
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
    plt.savefig('forest_fire_visualization.png', dpi=150, bbox_inches='tight')
    print(f"Visualization saved to 'forest_fire_visualization.png'")
    plt.show()


def plot_training_progress(episode_rewards):
    """Plot the episode rewards over time."""
    plt.figure(figsize=(10, 6))
    plt.plot(episode_rewards, alpha=0.6, label='Episode Reward')
    
    # Add moving average
    window = min(50, len(episode_rewards) // 10)
    if window > 1:
        moving_avg = np.convolve(episode_rewards, np.ones(window)/window, mode='valid')
        plt.plot(range(window-1, len(episode_rewards)), moving_avg, 
                 'r-', linewidth=2, label=f'Moving Average ({window})')
    
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.title('Training Progress')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('training_progress.png', dpi=150, bbox_inches='tight')
    print(f"Training progress plot saved to 'training_progress.png'")
    plt.show()


def main():
    """Main function to train and test the agent."""
    print("="*50)
    print("Forest Fire RL Environment with PPO")
    print("="*50)
    
    # Train the agent
    model, env = train_agent(total_timesteps=20000)
    
    # Test the agent
    episode_rewards, episode_lengths = test_agent(model, env, n_episodes=5)
    
    # Visualize an episode
    visualize_episode(model, env)
    
    print("\nTraining and testing complete!")


if __name__ == "__main__":
    main()
