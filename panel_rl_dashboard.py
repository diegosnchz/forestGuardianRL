import panel as pn
import holoviews as hv
import numpy as np
import pandas as pd
from numba_env import ForestFireMAEnv, CELL_TREE, CELL_FIRE, CELL_EMPTY, CELL_BURNT
from marl_agent import PPOAgent
from xai_assistant import XAIAssistant
import torch

# Configuration for Senior High-Fidelity feel
pn.extension('bokeh', template='fast', notifications=True)
hv.extension('bokeh')

# Helper to load CSS
def load_css(file_path):
    with open(file_path, 'r') as f:
        return f.read()

# Apply Deep Blue Theme
try:
    pn.config.raw_css.append(load_css('dashboard_assets/style.css'))
except:
    pass

# --- CONFIG ---
GRID_SIZE = 40
N_AGENTS = 2
VIEW_RADIUS = 4

# Initialize Components
env = ForestFireMAEnv(grid_size=GRID_SIZE, n_agents=N_AGENTS, view_radius=VIEW_RADIUS)
xai = XAIAssistant()

# Global State
is_running = False
step_count = 0
obs = env.reset()[0]
current_agents = obs['agents']
forest_health_history = []

# --- STREAMS ---
pipe_grid = hv.streams.Pipe(data=np.zeros((GRID_SIZE, GRID_SIZE)))
pipe_agents = hv.streams.Pipe(data=[])
pipe_metrics = hv.streams.Pipe(data=pd.DataFrame({'step': [], 'health': [], 'severity': []}))

# --- PLOTTING FUNCTIONS ---
def get_grid_plot(data):
    # Enterprise Dark Palette
    # 0: BG, 1: Trees (Muted Teal), 2: Fire (Alert Red), 3: Burnt (Navy)
    cmap = ['#020c1b', '#1d3d33', '#f56565', '#233554'] 
    return hv.Image(data, bounds=(0, 0, GRID_SIZE, GRID_SIZE)).opts(
        cmap=cmap, clim=(0, 3), 
        width=None, height=None, responsive=True,
        xaxis=None, yaxis=None, 
        toolbar=None, border_line_color=None
    )

def get_agent_plot(data):
    if not data:
        return hv.Points([]).opts(color='#64ffda', size=12)
    return hv.Points(data).opts(
        color='#64ffda', size=15, 
        marker='circle', line_color='#e6f1ff', line_width=1,
        tools=[]
    )

def get_line_plot(data, y_field, color, title):
    if data is None or len(data) < 2:
        return hv.Curve([], 'step', y_field).opts(title=title, color=color)
    return hv.Curve(data, 'step', y_field).opts(
        color=color, line_width=2, 
        responsive=True, height=200, toolbar=None,
        active_tools=[], border_line_color=None,
        background_fill_color=None,
    ).opts(
        xlabel="", ylabel="",
        show_grid=True, gridstyle={'grid_line_color': '#1d2d50'}
    )

# Dynamic Maps
grid_dmap = hv.DynamicMap(get_grid_plot, streams=[pipe_grid])
agent_dmap = hv.DynamicMap(get_agent_plot, streams=[pipe_agents])
metrics_health_dmap = hv.DynamicMap(lambda data: get_line_plot(data, 'health', '#64ffda', "Health"), streams=[pipe_metrics])
metrics_severity_dmap = hv.DynamicMap(lambda data: get_line_plot(data, 'severity', '#f56565', "Severity"), streams=[pipe_metrics])

main_view = (grid_dmap * agent_dmap).opts(
    bgcolor='#020c1b',
    responsive=True
)

# --- CHATBOT ---
chat_interface = pn.chat.ChatInterface(
    callback=lambda msg, user, instance: xai.query(msg, {'grid': obs['grid'], 'agents': obs['agents']}),
    height=400,
    sizing_mode='stretch_width',
    show_undo=False, show_clear=False, show_rerun=False
)
chat_interface.send(xai.welcome_message(), user="System", avatar="🛡️", respond=False)

# --- SIMULATION LOOP ---
def get_heuristic_action(agent_idx, current_obs):
    grid = current_obs['grid']
    pos = current_obs['agents'][agent_idx]
    r, c = pos
    fire_nearby = np.any(grid[max(0,r-1):r+2, max(0,c-1):c+2] == CELL_FIRE)
    if fire_nearby: return 5 
    fire_positions = np.argwhere(grid == CELL_FIRE)
    if len(fire_positions) == 0: return np.random.randint(1, 5) 
    dists = np.linalg.norm(fire_positions - pos, axis=1)
    target = fire_positions[np.argmin(dists)]
    tr, tc = target
    if tr < r: return 1 
    if tr > r: return 2 
    if tc < c: return 3 
    if tc > c: return 4 
    return np.random.randint(1, 5)

def step_sim():
    global obs, step_count, is_running, current_agents
    if not is_running: return
    actions = [get_heuristic_action(i, obs) for i in range(N_AGENTS)]
    prev_agents = obs['agents'].copy()
    next_obs, rewards, term, trunc, info = env.step(actions)
    obs = next_obs
    current_agents = obs['agents']
    
    pipe_grid.send(obs['grid'])
    agent_coords = [(c + 0.5, GRID_SIZE - r - 0.5) for r, c in current_agents]
    pipe_agents.send(agent_coords)
    
    step_count += 1
    fires_count = np.sum(obs['grid'] == CELL_FIRE)
    severity = (fires_count / (GRID_SIZE*GRID_SIZE)) * 500
    
    new_data = {'step': step_count, 'health': info.get('forest_health', 0), 'severity': severity}
    forest_health_history.append(new_data)
    if len(forest_health_history) > 100: forest_health_history.pop(0)
    pipe_metrics.send(pd.DataFrame(forest_health_history))
    
    if step_count % 20 == 0:
        insight = xai.analyze_step(obs, prev_agents, current_agents, rewards)
        if insight: chat_interface.send(insight, user="Tactical Insight", avatar="📡", respond=False)

cb = pn.state.add_periodic_callback(step_sim, period=400, start=False)

# --- CONTROLS ---
btn_play = pn.widgets.Button(name='INITIATE MISSION', button_type='primary', sizing_mode='stretch_width')
btn_stop = pn.widgets.Button(name='HALT OPERATION', button_type='warning', sizing_mode='stretch_width')
btn_reset = pn.widgets.Button(name='PURGE SYSTEM', button_type='danger', sizing_mode='stretch_width')

def toggle_play(event):
    global is_running
    is_running = True
    if not cb.running: cb.start()

def toggle_stop(event):
    global is_running
    is_running = False
    cb.stop()

def output_reset(event):
    global obs, step_count, forest_health_history
    obs = env.reset()[0]
    step_count = 0
    forest_health_history = []
    pipe_grid.send(obs['grid'])
    pipe_agents.send([])
    pipe_metrics.send(pd.DataFrame({'step': [], 'health': [], 'severity': []}))
    chat_interface.send("Core Reactivated. Standing by.", user="System", avatar="🔄", respond=False)

btn_play.on_click(toggle_play)
btn_stop.on_click(toggle_stop)
btn_reset.on_click(output_reset)

# --- LAYOUT ---
sidebar = pn.Column(
    pn.pane.Markdown("# FOREST GUARDIAN", css_classes=['muted-text']),
    pn.pane.Markdown("SYSTEM PROTOCOL V2.5", css_classes=['protocol-text']),
    pn.layout.Divider(),
    pn.pane.Markdown("### MISSION CONTROLS"),
    btn_play, btn_stop, btn_reset,
    pn.layout.Divider(),
    pn.pane.Markdown("### CORE INDICATORS"),
    pn.indicators.Number(name="UNIT COUNT", value=N_AGENTS, font_size="1.5rem"),
    pn.indicators.Number(name="TIME ELAPSED", value=step_count, font_size="1.5rem"),
    sizing_mode='stretch_height', width=250
)

# Grid Layout
gspec = pn.GridSpec(sizing_mode='stretch_both', min_height=800)

# Top Left: Digital Twin
gspec[0:5, 0:7] = pn.Column(
    pn.pane.Markdown("### TACTICAL DIGITAL TWIN", css_classes=['card-title']),
    main_view,
    css_classes=['pastel-card']
)

# Right: Intelligence Hub
gspec[0:8, 7:12] = pn.Column(
    pn.pane.Markdown("### INTELLIGENCE HUB", css_classes=['card-title']),
    chat_interface,
    css_classes=['pastel-card', 'chat-container']
)

# Bottom Left: Analytics
gspec[5:8, 0:3] = pn.Column(
    pn.pane.Markdown("### FOREST HEALTH", css_classes=['card-title']),
    metrics_health_dmap,
    css_classes=['pastel-card']
)

gspec[5:8, 3:7] = pn.Column(
    pn.pane.Markdown("### THREAT LEVEL", css_classes=['card-title']),
    metrics_severity_dmap,
    css_classes=['pastel-card']
)

template = pn.template.FastListTemplate(
    title="FOREST GUARDIAN // DIGITAL TWIN",
    sidebar=[sidebar],
    main=[gspec],
    header_background="#0a192f",
    accent_base_color="#64ffda",
    main_max_width="100%",
    theme="dark"
)

if __name__ == "__main__":
    # Autoreload enabled for Senior Dev experience
    pn.serve(template, port=5007, show=True, autoreload=True)
