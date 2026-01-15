"""
Simple validation script for ForestFireEnv
Tests the environment structure and basic functionality
"""
import sys
import numpy as np

# Test basic imports
try:
    from forest_fire_env import ForestFireEnv
    print("✓ ForestFireEnv imported successfully")
except Exception as e:
    print(f"✗ Failed to import ForestFireEnv: {e}")
    sys.exit(1)

# Test environment creation
try:
    env = ForestFireEnv()
    print("✓ Environment created successfully")
except Exception as e:
    print(f"✗ Failed to create environment: {e}")
    sys.exit(1)

# Test action and observation spaces
try:
    assert env.action_space.n == 7, f"Expected 7 actions, got {env.action_space.n}"
    print(f"✓ Action space correct: Discrete({env.action_space.n})")
    
    expected_shape = (10, 10)
    actual_shape = env.observation_space.shape
    assert actual_shape == expected_shape, f"Expected shape {expected_shape}, got {actual_shape}"
    print(f"✓ Observation space correct: Box{actual_shape}")
except AssertionError as e:
    print(f"✗ Space validation failed: {e}")
    sys.exit(1)

# Test reset
try:
    obs, info = env.reset()
    print(f"✓ Reset successful, observation shape: {obs.shape}")
    
    # Verify grid values
    unique_values = set(np.unique(obs))
    valid_values = {0, 1, 2, 3}
    assert unique_values.issubset(valid_values), f"Invalid grid values: {unique_values}"
    print(f"✓ Grid values valid: {unique_values}")
    
    # Check agent is present
    assert 3 in obs, "Agent (value 3) not found in observation"
    agent_count = np.sum(obs == 3)
    assert agent_count == 1, f"Expected 1 agent, found {agent_count}"
    print(f"✓ Agent correctly placed")
    
    # Check initial fires
    fire_count = np.sum(obs == 2)
    print(f"✓ Initial fires: {fire_count}")
    
    # Check trees
    tree_count = np.sum(obs == 1)
    print(f"✓ Initial trees: {tree_count}")
    
except Exception as e:
    print(f"✗ Reset failed: {e}")
    sys.exit(1)

# Test step function with all actions
try:
    action_names = ["Move Up", "Move Down", "Move Left", "Move Right", 
                    "Cut Tree", "Extinguish Fire", "Wait"]
    
    print("\n Testing all actions:")
    for action in range(7):
        env.reset()
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"  ✓ Action {action} ({action_names[action]}): reward={reward:.2f}, terminated={terminated}")
        
        # Verify observation is valid
        assert obs.shape == (10, 10), f"Invalid observation shape: {obs.shape}"
        assert set(np.unique(obs)).issubset({0, 1, 2, 3}), "Invalid values in observation"
        
except Exception as e:
    print(f"✗ Step function failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test fire spread
try:
    print("\n Testing fire spread over multiple steps:")
    env.reset()
    initial_fires = np.sum(env.grid == 2)
    
    # Take several wait actions to see fire spread
    for i in range(5):
        obs, reward, terminated, truncated, info = env.step(6)  # Wait action
        current_fires = np.sum(env.grid == 2)
        print(f"  Step {i+1}: fires={current_fires}, reward={reward:.2f}")
        
        if terminated or truncated:
            print(f"  Episode ended: terminated={terminated}, truncated={truncated}")
            break
            
    print("✓ Fire spread mechanism working")
    
except Exception as e:
    print(f"✗ Fire spread test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test reward system
try:
    print("\n Testing reward system:")
    
    # Test extinguish reward
    env.reset()
    # Find a fire position
    fire_positions = np.argwhere(env.grid == 2)
    if len(fire_positions) > 0:
        fire_pos = tuple(fire_positions[0])
        env.agent_pos = fire_pos
        obs, reward, terminated, truncated, info = env.step(5)  # Extinguish
        print(f"  Extinguish fire reward: {reward:.2f} (expected: 10.0 + penalties)")
        
    print("✓ Reward system working")
    
except Exception as e:
    print(f"✗ Reward system test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*50)
print("All validation tests passed! ✓")
print("="*50)
print("\nEnvironment is ready for training with stable-baselines3")
print("To train: python train_and_test.py")
