import panel as pn
import holoviews as hv
import numpy as np
import pandas as pd
from numba_env import ForestFireMAEnv, CELL_TREE, CELL_FIRE, CELL_EMPTY, CELL_BURNT
from marl_agent import PPOAgent
import torch

pn.extension('bokeh', template='fast')

# --- CONFIG ---
GRID_SIZE = 40
N_AGENTS = 2
VIEW_RADIUS = 4

# Initialize Components
env = ForestFireMAEnv(grid_size=GRID_SIZE, n_agents=N_AGENTS, view_radius=VIEW_RADIUS)
agent = PPOAgent(n_agents=N_AGENTS, grid_size=GRID_SIZE)

# Global State
is_running = False
step_count = 0
obs = env.reset()[0]
total_rewards = []
forest_health_history = []
coordination_history = []

# --- PLOTTING ---
# We use HoloViews Streams/Pipe for high performance updates
pipe_grid = hv.streams.Pipe(data=np.zeros((GRID_SIZE, GRID_SIZE)))
pipe_agents = hv.streams.Pipe(data=[])
pipe_metrics = hv.streams.Pipe(data=pd.DataFrame({'step': [], 'health': [], 'coordination': []}))

def get_grid_plot(data):
    # Map raw ints to colors
    # 0: Empty (Black), 1: Tree (Green), 2: Fire (Red), 3: Burnt (Brown)
    cmap = ['#1a1a1a', '#2ecc71', '#e74c3c', '#5d4037'] 
    return hv.Image(data, bounds=(0, 0, GRID_SIZE, GRID_SIZE)).opts(
        cmap=cmap, clim=(0, 3), width=600, height=600, 
        xaxis=None, yaxis=None, title="Forest Grid"
    )

def get_agent_plot(data):
    if not data:
        return hv.Points([]).opts(color='cyan', size=18)
    return hv.Points(data).opts(color='#00ffff', size=18, marker='circle', line_color='black', line_width=2)

def get_metrics_plot(data):
    if data is None or len(data) < 2:
        return hv.Curve([], 'step', 'health').opts(title="Forest Health %", color='#2ecc71', ylim=(0, 100), xlim=(0, 100))
    return hv.Curve(data, 'step', 'health').opts(title="Forest Health %", color='#2ecc71', ylim=(0, 100), interpolation='linear')

# Combine Plots
grid_dmap = hv.DynamicMap(get_grid_plot, streams=[pipe_grid])
agent_dmap = hv.DynamicMap(get_agent_plot, streams=[pipe_agents])
metrics_dmap = hv.DynamicMap(get_metrics_plot, streams=[pipe_metrics])

main_view = (grid_dmap * agent_dmap).opts(bgcolor='#111111')

# --- SIMULATION LOOP ---
def get_heuristic_action(agent_idx, current_obs):
    grid = current_obs['grid']
    pos = current_obs['agents'][agent_idx]
    r, c = pos
    
    # Check if fire nearby in 3x3
    fire_nearby = False
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < grid.shape[0] and 0 <= nc < grid.shape[1]:
                if grid[nr, nc] == CELL_FIRE:
                    fire_nearby = True
                    break
    
    if fire_nearby:
        return 5 # Extinguish
    
    # Otherwise, move towards nearest fire
    fire_positions = np.argwhere(grid == CELL_FIRE)
    if len(fire_positions) == 0:
        return np.random.randint(1, 5) # Wander
        
    # Find closest fire
    dists = np.linalg.norm(fire_positions - pos, axis=1)
    target = fire_positions[np.argmin(dists)]
    
    tr, tc = target
    if tr < r: return 1 # UP
    if tr > r: return 2 # DOWN
    if tc < c: return 3 # LEFT
    if tc > c: return 4 # RIGHT
    
    return np.random.randint(1, 5) # Fallback wander

def step_sim():
    global obs, step_count, is_running
    if not is_running:
        return

    # 1. Get Actions
    # Extract agent local views from global grid
    # For prototype, we cheat and assume full grid passed or handle local extraction in Agent wrapper
    # But numba_env step expects simple actions.
    # Let's do random actions or simple heuristic for VISUAL DEMO if Agent not trained
    # Or try to run agent forward pass
    
    # Needs (Batch, N, 1, H, W)
    # Using heuristic for visual demo to show what agents SHOULD do
    actions = [get_heuristic_action(i, obs) for i in range(N_AGENTS)]
    
    # 2. Step Env
    next_obs, rewards, term, trunc, info = env.step(actions)
    obs = next_obs
    
    # 3. Update Plots
    # Grid
    pipe_grid.send(obs['grid'])
    
    # Agents (convert r,c to x,y for Bokeh: x=c, y=rows-r usually, but Image bounds are 0,0 to W,H)
    # hv.Image origin is typically bottom-left? Or top-left depending on params. 
    # Standard array (row, col) maps to (y, x) but inverted y often
    # Let's map directly: r -> y, c -> x. 
    # Numba grid[r,c]. 
    agent_pos = obs['agents']
    # Grid[r, c] -> Image(x, y)
    # If hv.Image(bounds=(0,0, G,G)), y increases upwards. 
    # Array row 0 is top -> y = G - 0.5
    # Array col 0 is left -> x = 0.5
    agent_coords = []
    for p in agent_pos:
        r, c = p
        agent_coords.append((c + 0.5, GRID_SIZE - r - 0.5))
    pipe_agents.send(agent_coords)
    
    # Metrics
    step_count += 1
    new_data = {'step': step_count, 'health': info.get('forest_health', 0), 'coordination': 0}
    
    # Update local history
    forest_health_history.append(new_data)
    if len(forest_health_history) > 100:
        forest_health_history.pop(0)
    
    # Send update every step for smoothness
    df = pd.DataFrame(forest_health_history)
    pipe_metrics.send(df)

# Callback
cb = pn.state.add_periodic_callback(step_sim, period=400, start=False)

# --- CONTROLS ---
btn_play = pn.widgets.Button(name='▶ Play', button_type='primary')
btn_stop = pn.widgets.Button(name='⏸ Pause', button_type='warning')
btn_reset = pn.widgets.Button(name='↺ Reset', button_type='danger')

def toggle_play(event):
    global is_running
    is_running = True
    if not cb.running:
        cb.start()

def toggle_stop(event):
    global is_running
    is_running = False
    cb.stop()

def output_reset(event):
    global obs, step_count
    obs = env.reset()[0]
    step_count = 0
    pipe_grid.send(obs['grid'])
    pipe_agents.send([])
    pipe_metrics.send(pd.DataFrame({'step': [], 'health': [], 'coordination': []}))

btn_play.on_click(toggle_play)
btn_stop.on_click(toggle_stop)
btn_reset.on_click(output_reset)

# --- LAYOUT ---
dashboard = pn.Row(
    pn.Column(
        pn.pane.Markdown("# 🌲 ForestGuardian 2.0: MARL Core"),
        pn.Row(btn_play, btn_stop, btn_reset),
        main_view
    ),
    pn.Column(
        pn.pane.Markdown("### Live Metrics"),
        metrics_dmap,
        pn.pane.Markdown("**System Status**:\n- Numba Physics: ON\n- GAT Network: Initialized\n- Device: CPU")
    )
)

if __name__ == "__main__":
    dashboard.show(port=5007)
