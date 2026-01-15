"""
Demo script showing the ForestFireEnv in action
Runs a random policy to demonstrate the environment
"""
import numpy as np
from forest_fire_env import ForestFireEnv


def run_random_episode(env, seed=None, max_steps=50):
    """Run one episode with random actions."""
    obs, info = env.reset(seed=seed)
    
    print(f"\n{'='*60}")
    print(f"Starting Episode (seed={seed})")
    print(f"{'='*60}")
    
    action_names = [
        "Move Up ↑", "Move Down ↓", "Move Left ←", "Move Right →",
        "Cut Tree 🪓", "Extinguish 💧", "Wait ⏸"
    ]
    
    # Initial state
    print("\nInitial State:")
    env.render()
    
    total_reward = 0
    step_count = 0
    
    for step in range(max_steps):
        # Choose random action
        action = env.action_space.sample()
        
        # Take action
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        step_count += 1
        
        # Print step info
        print(f"\n--- Step {step_count} ---")
        print(f"Action: {action_names[action]}")
        print(f"Reward: {reward:.2f} (Total: {total_reward:.2f})")
        print(f"Trees: {np.sum(env.grid == 1)}, Fires: {np.sum(env.grid == 2)}")
        
        # Check if episode ended
        if terminated:
            print("\n🏁 Episode TERMINATED")
            break
        if truncated:
            print("\n⏱ Episode TRUNCATED (max steps)")
            break
    
    print(f"\n{'='*60}")
    print(f"Episode Summary")
    print(f"{'='*60}")
    print(f"Total Steps: {step_count}")
    print(f"Total Reward: {total_reward:.2f}")
    print(f"Final Trees: {np.sum(env.grid == 1)}")
    print(f"Final Fires: {np.sum(env.grid == 2)}")
    
    # Final state
    print("\nFinal State:")
    env.render()
    
    return total_reward, step_count


def main():
    """Main demo function."""
    print("="*60)
    print("Forest Fire Environment - Random Policy Demo")
    print("="*60)
    
    # Create environment
    env = ForestFireEnv(
        grid_size=20,
        fire_spread_prob=0.3,
        initial_trees=0.6,
        initial_fires=3
    )
    
    print(f"\nEnvironment Configuration:")
    print(f"  Grid Size: {env.grid_size}x{env.grid_size}")
    print(f"  Fire Spread Probability: {env.fire_spread_prob}")
    print(f"  Initial Trees Ratio: {env.initial_trees}")
    print(f"  Initial Fires: {env.initial_fires}")
    
    # Run a few episodes
    n_episodes = 3
    rewards = []
    lengths = []
    
    for episode in range(n_episodes):
        reward, length = run_random_episode(env, seed=episode, max_steps=30)
        rewards.append(reward)
        lengths.append(length)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Overall Summary ({n_episodes} episodes)")
    print(f"{'='*60}")
    print(f"Average Reward: {np.mean(rewards):.2f} ± {np.std(rewards):.2f}")
    print(f"Average Length: {np.mean(lengths):.2f} ± {np.std(lengths):.2f}")
    print(f"\n✅ Demo complete!")
    print(f"\nNote: This is a RANDOM policy. Train with PPO for better results:")
    print(f"  python train_and_test.py")


if __name__ == "__main__":
    main()
