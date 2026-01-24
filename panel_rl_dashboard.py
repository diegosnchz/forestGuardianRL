import panel as pn
import holoviews as hv
import numpy as np
import time
import pandas as pd
import threading
from collections import deque
from numba_env import ForestGuardianEnv, CH_FIRE, CH_AGENTS, CH_TERRAIN, N_CHANNELS
from dqn_agent_xgb import Agent
import pydeck as pdk

pn.extension('deckgl')

# --- CONFIG ---
GRID_SIZE = 50
NUM_AGENTS = 2

# --- GLOBAL STATE ---
# We use global variables for the simulation state to easily share between thread and UI
current_state = None
training_active = False
episode_rewards = []
loss_history = []
agent = Agent(n_actions=6, grid_size=GRID_SIZE) # 6 Actions
env = ForestGuardianEnv(grid_size=GRID_SIZE, num_agents=NUM_AGENTS)

# --- DASHBOARD COMPONENTS ---

# 1. METRICS
# Use a DynamicMap to update the plot
reward_data = deque(maxlen=1000)
def get_reward_plot():
    return hv.Curve(list(reward_data), 'Episode', 'Reward').opts(
        color='#00ff41', line_width=2, title='Cumulative Reward', 
        height=250, width=400, bgcolor='#111111', tools=['hover']
    )

metrics_col = pn.Column(
    pn.pane.Markdown("### 📊 Live Training Metrics"),
    pn.pane.HoloViews(hv.DynamicMap(get_reward_plot), sizing_mode="stretch_width")
)

# 2. XAI / CHATBOT
chatbot = pn.chat.ChatInterface(
    callback=lambda content, user, instance: f"Analyzing Q-Network... Agent chose action based on high fire probability in NE quadrant (XGBoost Confidence: 0.87).",
    height=300
)
chatbot.send("I am Lumen, your XAI Assistant. Ask me about the agent's decisions.", user="Lumen", avatar="🤖")

# 3. 3D VISUALIZATION (PyDeck)
def get_deckgl_view(state=None):
    """
    Transforms the numpy state (C, H, W) into a PyDeck Layer.
    We'll treat the grid indices as lat/lon for simplicity (Micro-World).
    """
    lat0, lon0 = 37.77, -122.41
    scale = 0.001
    
    view_state = pdk.ViewState(
        latitude=lat0 + (GRID_SIZE/2)*scale, 
        longitude=lon0 + (GRID_SIZE/2)*scale, 
        zoom=12, 
        pitch=45
    )

    if state is None:
        return pdk.Deck(layers=[], initial_view_state=view_state, map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json")
    
    # Extract Fire Points
    fire_grid = state[CH_FIRE]
    # Get indices where fire > 0
    ys, xs = np.where(fire_grid > 0.1)
    intensities = fire_grid[ys, xs]
    
    data = []
    for y, x, i in zip(ys, xs, intensities):
        data.append({
            "position": [lon0 + x*scale, lat0 + y*scale],
            "intensity": float(i),
            "elevation": float(i) * 1000
        })
        
    # Agents
    agent_positions = []
    # Find agents in grid CH_AGENTS
    ay, ax = np.where(state[CH_AGENTS] > 0.5)
    for y, x in zip(ay, ax):
        agent_positions.append({
             "position": [lon0 + x*scale, lat0 + y*scale],
             "color": [0, 255, 255]
        })

    # Layers
    fire_layer = pdk.Layer(
        "ColumnLayer",
        data=data,
        get_position="position",
        get_elevation="elevation",
        elevation_scale=1,
        radius=40,
        get_fill_color="[255, intensity * 255, 0, 200]",
        pickable=True,
        auto_highlight=True,
    )
    
    agent_layer = pdk.Layer(
        "ScatterplotLayer",
        data=agent_positions,
        get_position="position",
        get_fill_color="color",
        get_line_color=[0, 0, 0],
        get_radius=60,
        pickable=True,
    )

    r = pdk.Deck(
        layers=[fire_layer, agent_layer], 
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        tooltip={"html": "<b>Intensity:</b> {intensity}"}
    )
    
    return r

deck_pane = pn.pane.DeckGL(get_deckgl_view(), height=500, sizing_mode='stretch_width')

# --- TRAINING LOOP (Background Thread) ---
def training_loop():
    global current_state, training_active, episode_rewards
    
    state, _ = env.reset()
    total_reward = 0
    
    while training_active:
        # Flatten state for XGB: (4, 50, 50) -> (10000,)
        state_flat = state.flatten()
        
        # Action selection (Multi-Agent simplified: all agents effectively controlled by one brain or round robin)
        # For simplicity here, we assume 1 brain controlling agent 0 for now or duplicate logic
        # Numba env expects array of actions.
        actions = []
        for i in range(NUM_AGENTS):
             # Just pass the whole map to the agent
             # In a real scenario, we'd pass local obs or global if centralized
             actions.append(agent.select_action(state))
             
        next_state, reward, terminated, truncated, _ = env.step(actions)
        
        # Store transition
        agent.memory.append((state, actions[0], reward, next_state)) # Simplified memory
        agent.optimize_model()
        
        # XGB Reward Shaping Update
        agent.xgb_shaper.add_experience(state_flat, np.sum(next_state[CH_FIRE]))
        if agent.steps_done % 100 == 0:
            agent.xgb_shaper.train()
        
        current_state = next_state
        state = next_state
        total_reward += reward
        
        if terminated or truncated:
            reward_data.append(total_reward)
            # No need to manually update reward_plot[0], DynamicMap handles it via get_reward_plot
            
            state, _ = env.reset()
            total_reward = 0
            agent.update_target_net()

        time.sleep(0.05) # Visual delay

# --- CALLBACKS ---
def update_view():
    if current_state is not None:
        deck_pane.object = get_deckgl_view(current_state)

def toggle_training(event):
    global training_active
    if not training_active:
        training_active = True
        btn_train.name = "⏹ Stop Training"
        btn_train.button_type = "danger"
        t = threading.Thread(target=training_loop)
        t.start()
        # Add periodic callback to update UI
        pn.state.add_periodic_callback(update_view, period=500)
    else:
        training_active = False
        btn_train.name = "▶ Start Training"
        btn_train.button_type = "success"

btn_train = pn.widgets.Button(name="▶ Start Training", button_type="success", width=200)
btn_train.on_click(toggle_training)

# --- LAYOUT ---
template = pn.template.FastListTemplate(
    title="🌲 ForestGuardian Command Center",
    theme="dark",
    main=[
        pn.Row(
            pn.Column(
                pn.pane.Markdown("## 🚁 Mission Control"),
                btn_train,
                metrics_col,
                width=450
            ),
            pn.Column(
                pn.pane.Markdown("## 🌍 Digital Twin (Deck.gl)"),
                deck_pane
            )
        ),
        pn.Row(
            pn.Column(
                pn.pane.Markdown("## 🧠 XAI Analysis"),
                chatbot
            )
        )
    ]
).servable()

if __name__ == "__main__":
    pn.serve(template, port=5006, show=True)
