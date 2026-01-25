import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np

class GATLayer(nn.Module):
    """
    Simple Graph Attention head implementation in pure PyTorch.
    Inputs:
        h: (batch, N, in_features) node features
        adj: (batch, N, N) adjacency matrix (0/1)
    """
    def __init__(self, in_features: int, out_features: int, dropout: float = 0.6, alpha: float = 0.2):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.dropout = dropout
        self.alpha = alpha
        
        self.W = nn.Linear(in_features, out_features, bias=False)
        self.a = nn.Linear(2*out_features, 1, bias=False)
        self.leakyrelu = nn.LeakyReLU(self.alpha)

    def forward(self, h, adj):
        B, N, _ = h.size()
        Wh = self.W(h) # (B, N, out)
        
        # Prepare for attention mechanism
        # simple all-pair combination
        Wh1 = Wh.repeat(1, 1, N).view(B, N*N, self.out_features)
        Wh2 = Wh.repeat(1, N, 1)  # (B, N*N, out)
        
        # Concatenate and apply attention mechanism
        a_input = torch.cat([Wh1, Wh2], dim=2)
        e = self.leakyrelu(self.a(a_input).view(B, N, N))
        
        # Mask using adjacency
        zero_vec = -9e15 * torch.ones_like(e)
        attention = torch.where(adj > 0, e, zero_vec)
        attention = F.softmax(attention, dim=2)
        attention = F.dropout(attention, self.dropout, training=self.training)
        
        h_prime = torch.bmm(attention, Wh)
        return F.elu(h_prime)

class MARLNetwork(nn.Module):
    def __init__(self, n_actions: int, input_dims: int, hidden_dim: int = 64):
        super().__init__()
        # 1. Grid Encoder (CNN) for local view
        # Expecting input (1, ViewSize, ViewSize)
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=0),
            nn.ReLU(),
            nn.Flatten()
        )
        
        # Compute Flatten dim
        # If view_radius=4, size=9x9.
        # Conv1 -> 9x9x16
        # Conv2 -> 7x7x32 -> 1568
        self.cnn_out_dim = 1568 
        
        # 2. Agent Embedding (Local Grid + Position?)
        # For simplicity, just Local Grid Features for now.
        
        # 3. GAT Layer (Communication)
        self.gat = GATLayer(self.cnn_out_dim, hidden_dim)
        
        # 4. Actor & Critic Heads
        self.actor = nn.Linear(hidden_dim, n_actions)
        self.critic = nn.Linear(hidden_dim, 1)
        
    def forward(self, obs_grids, adj_matrix):
        """
        obs_grids: (Batch, N_Agents, 1, H, W) 
        adj_matrix: (Batch, N_Agents, N_Agents)
        """
        B, N, C, H, W = obs_grids.size()
        
        # Flatten batch/agent dims for CNN
        cnn_in = obs_grids.view(B*N, C, H, W).float()
        features = self.cnn(cnn_in)
        
        # Reshape back to (B, N, cnn_out)
        features = features.view(B, N, -1)
        
        # GAT Pass (Communication context)
        # Note: We treat B as batch dimension
        agent_embeddings = self.gat(features, adj_matrix)
        
        # Heads
        logits = self.actor(agent_embeddings) # (B, N, actions)
        values = self.critic(agent_embeddings) # (B, N, 1)
        
        return logits, values

class PPOAgent:
    def __init__(self, n_agents, grid_size, n_actions=6, lr=0.0003, gamma=0.99, eps_clip=0.2):
        self.n_agents = n_agents
        self.gamma = gamma
        self.eps_clip = eps_clip
        
        self.policy = MARLNetwork(n_actions, grid_size)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)
        
        self.policy_old = MARLNetwork(n_actions, grid_size)
        self.policy_old.load_state_dict(self.policy.state_dict())
        
        self.MseLoss = nn.MSELoss()
        
    def get_action(self, obs_grids, adj):
        """
        Select action for inference (no grad).
        obs_grids: (N, 1, H, W) numpy or torch
        adj: (N, N) numpy or torch
        """
        # Add Batch Dim
        if not torch.is_tensor(obs_grids):
            obs_grids = torch.tensor(obs_grids, dtype=torch.float32).unsqueeze(0) # (1, N, 1, H, W)
            adj = torch.tensor(adj, dtype=torch.float32).unsqueeze(0) # (1, N, N)
            
        with torch.no_grad():
            logits, val = self.policy_old(obs_grids, adj)
            
        probs = F.softmax(logits, dim=-1)
        dist = torch.distributions.Categorical(probs)
        action = dist.sample()
        
        return action.squeeze(0).numpy(), dist.log_prob(action).squeeze(0), val.squeeze(0)

    def update(self, memory):
        # Implementation of PPO update loop
        # Unroll memory...
        # For prototype simplicity, this is placeholder structure
        pass
        
    def save(self, path):
        torch.save(self.policy.state_dict(), path)
        
    def load(self, path: str):
        self.policy.load_state_dict(torch.load(path, weights_only=True))
