import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque
import xgboost as xgb
import os

# --- HYPERPARAMETERS ---
BATCH_SIZE = 64
GAMMA = 0.99
EPS_START = 1.0
EPS_END = 0.05
EPS_DECAY = 1000
TARGET_UPDATE = 10
LR = 1e-4

class DQN(nn.Module):
    def __init__(self, n_observations, n_actions):
        super(DQN, self).__init__()
        # Input: (C, H, W). We flatten or use Conv2d for grid
        # For 50x50 grid, Conv2d is better.
        # But for minimal dependencies/simplicity in this file, let's use a small Conv net.
        
        self.conv = nn.Sequential(
            nn.Conv2d(4, 16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2), # 50 -> 25
            nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2), # 25 -> 12
            nn.Flatten()
        )
        
        # Calculate size after conv
        # 50 -> 25 -> 12. 12*12*32 = 4608
        conv_out_size = 12 * 12 * 32
        
        self.fc = nn.Sequential(
            nn.Linear(conv_out_size, 256),
            nn.ReLU(),
            nn.Linear(256, n_actions)
        )

    def forward(self, x):
        x = self.conv(x)
        return self.fc(x)

class XGBRewardShaper:
    """
    Simulates a 'Model-Based' component.
    Predicts the 'Fire Intensity' of the NEXT state given CURRENT state using XGBoost.
    This helps the agent 'foresee' danger which the DQN might learn slowly.
    """
    def __init__(self):
        self.model = None
        self.buffer_x = []
        self.buffer_y = []
        
    def add_experience(self, state_flat, next_fire_intensity):
        """Accumulate data for online training"""
        self.buffer_x.append(state_flat)
        self.buffer_y.append(next_fire_intensity)
        
    def train(self):
        if len(self.buffer_x) < 100: return
        
        X = np.array(self.buffer_x)
        y = np.array(self.buffer_y)
        
        # Simple XGB Regressor
        self.model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=10, max_depth=3)
        self.model.fit(X, y)
        
        # Keep buffer manageable (sliding window)
        if len(self.buffer_x) > 5000:
            self.buffer_x = self.buffer_x[-1000:]
            self.buffer_y = self.buffer_y[-1000:]
            
    def predict_risk(self, state_flat):
        if self.model is None: return 0.0
        # return predicted fire intensity
        return self.model.predict(np.array([state_flat]))[0]

class Agent:
    def __init__(self, n_actions, grid_size=50):
        self.n_actions = n_actions
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.policy_net = DQN(4, n_actions).to(self.device).float()
        self.target_net = DQN(4, n_actions).to(self.device).float()
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=LR)
        self.memory = deque(maxlen=10000)
        self.steps_done = 0
        
        # Hybrid Component
        self.xgb_shaper = XGBRewardShaper()

    def select_action(self, state):
        sample = random.random()
        eps_threshold = EPS_END + (EPS_START - EPS_END) * \
            np.exp(-1. * self.steps_done / EPS_DECAY)
        self.steps_done += 1
        
        if sample > eps_threshold:
            with torch.no_grad():
                # State to tensor (1, C, H, W)
                state_t = torch.tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
                return self.policy_net(state_t).max(1)[1].view(1, 1).item()
        else:
            return random.randrange(self.n_actions)

    def optimize_model(self):
        if len(self.memory) < BATCH_SIZE:
            return
        
        transitions = random.sample(self.memory, BATCH_SIZE)
        batch = list(zip(*transitions))
        
        # Unpack
        state_batch = torch.tensor(np.array(batch[0]), device=self.device, dtype=torch.float32)
        action_batch = torch.tensor(batch[1], device=self.device).unsqueeze(1)
        reward_batch = torch.tensor(batch[2], device=self.device, dtype=torch.float32)
        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None, batch[3])), device=self.device, dtype=torch.bool)
        
        non_final_next_states = torch.tensor(np.array([s for s in batch[3] if s is not None]), device=self.device, dtype=torch.float32)

        # Q(s, a)
        state_action_values = self.policy_net(state_batch).gather(1, action_batch)

        # V(s_{t+1})
        next_state_values = torch.zeros(BATCH_SIZE, device=self.device)
        next_state_values[non_final_mask] = self.target_net(non_final_next_states).max(1)[0].detach()
        
        expected_state_action_values = (next_state_values * GAMMA) + reward_batch

        # Loss
        criterion = nn.SmoothL1Loss()
        loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

        self.optimizer.zero_grad()
        loss.backward()
        for param in self.policy_net.parameters():
            param.grad.data.clamp_(-1, 1)
        self.optimizer.step()

    def update_target_net(self):
        self.target_net.load_state_dict(self.policy_net.state_dict())
        
    def save(self, path="dqn_model.pth"):
        torch.save(self.policy_net.state_dict(), path)

