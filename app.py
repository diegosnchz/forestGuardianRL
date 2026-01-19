import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from forest_fire_env import ForestFireEnv
from train_and_test import TerminatorAgent
import pandas as pd

# ============================================================================
# CONFIGURACIÓN DE STREAMLIT
# ============================================================================
st.set_page_config(
    page_title="Forest Guardian RL",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ESTILOS Y CONFIGURACIÓN GLOBAL
# ============================================================================
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 14px;
        opacity: 0.9;
    }
    .status-running {
        color: #00ff41;
        font-weight: bold;
    }
    .status-idle {
        color: #888888;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# INICIALIZAR SESSION STATE
# ============================================================================
if 'mission_active' not in st.session_state:
    st.session_state.mission_active = False
if 'env' not in st.session_state:
    st.session_state.env = None
if 'frames_history' not in st.session_state:
    st.session_state.frames_history = []
if 'metrics_history' not in st.session_state:
    st.session_state.metrics_history = {
        'step': [],
        'active_fires': [],
        'saved_trees': [],
        'water_used': [],
        'agents_position': []
    }
if 'initial_trees_count' not in st.session_state:
    st.session_state.initial_trees_count = 0

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def create_grid_figure(obs, step):
    """Crea una visualización Plotly del grid actual"""
    # Colores: 0=blanco (vacío), 1=verde (árbol), 2=rojo (fuego), 3=azul (agente1), 4=naranja (agente2)
    custom_colorscale = [
        [0.0, '#ffffff'],   # vacío
        [0.25, '#00aa00'],  # árbol
        [0.5, '#ff0000'],   # fuego
        [0.75, '#0066ff'],  # agente azul
        [1.0, '#ff9900']    # agente naranja
    ]
    
    fig = go.Figure(
        data=go.Heatmap(
            z=obs,
            colorscale=custom_colorscale,
            zmin=0,
            zmax=4,
            showscale=False,
            hovertemplate='Posición: (%{x}, %{y})<br>Estado: %{z}<extra></extra>'
        )
    )
    
    fig.update_layout(
        title=f"Visualización del Bosque - Paso {step}",
        xaxis_title="Eje X",
        yaxis_title="Eje Y",
        height=500,
        hovermode='closest',
        xaxis=dict(scaleanchor="y", scaleratio=1),
        yaxis=dict(scaleanchor="x", scaleratio=1),
        plot_bgcolor='#f0f0f0'
    )
    
    return fig

def create_metrics_dashboard(metrics_history):
    """Crea gráficos de métricas a lo largo del tiempo"""
    if not metrics_history['step']:
        return None
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Fuegos Activos", "Árboles Salvados", "Agua Consumida", "Densidad de Bosque"),
        specs=[[{"type": "scatter"}, {"type": "scatter"}],
               [{"type": "scatter"}, {"type": "scatter"}]]
    )
    
    steps = metrics_history['step']
    
    # Fuegos activos
    fig.add_trace(
        go.Scatter(x=steps, y=metrics_history['active_fires'], 
                   mode='lines+markers', name='Fuegos', line=dict(color='red', width=2)),
        row=1, col=1
    )
    
    # Árboles salvados
    fig.add_trace(
        go.Scatter(x=steps, y=metrics_history['saved_trees'], 
                   mode='lines+markers', name='Árboles Salvados', line=dict(color='green', width=2)),
        row=1, col=2
    )
    
    # Agua consumida
    fig.add_trace(
        go.Scatter(x=steps, y=metrics_history['water_used'], 
                   mode='lines', name='Agua Consumida', line=dict(color='blue', width=2)),
        row=2, col=1
    )
    
    # Densidad de bosque (árboles/total celdas)
    density = [t/100 for t in metrics_history['saved_trees']]
    fig.add_trace(
        go.Scatter(x=steps, y=density, 
                   mode='lines+markers', name='Densidad Bosque', line=dict(color='purple', width=2)),
        row=2, col=2
    )
    
    fig.update_xaxes(title_text="Paso de Simulación", row=1, col=1)
    fig.update_xaxes(title_text="Paso de Simulación", row=1, col=2)
    fig.update_xaxes(title_text="Paso de Simulación", row=2, col=1)
    fig.update_xaxes(title_text="Paso de Simulación", row=2, col=2)
    
    fig.update_yaxes(title_text="Conteo", row=1, col=1)
    fig.update_yaxes(title_text="% Salvado", row=1, col=2)
    fig.update_yaxes(title_text="Unidades", row=2, col=1)
    fig.update_yaxes(title_text="Ratio", row=2, col=2)
    
    fig.update_layout(height=600, showlegend=True, hovermode='x unified')
    
    return fig

def run_mission(env, num_agents, max_steps=100):
    """Ejecuta la misión y actualiza métricas en tiempo real"""
    obs, _ = env.reset()
    st.session_state.initial_trees_count = np.sum(env.grid == 1)
    
    # Inicializar agentes
    agent_blue = TerminatorAgent(role="nearest")
    agent_orange = TerminatorAgent(role="farthest")
    
    # Limpiar historia
    st.session_state.frames_history = []
    st.session_state.metrics_history = {
        'step': [],
        'active_fires': [],
        'saved_trees': [],
        'water_used': [],
        'agents_position': []
    }
    
    # Placeholders para actualización en tiempo real
    col1, col2, col3, col4 = st.columns(4)
    
    placeholder_grid = st.empty()
    placeholder_metrics = st.empty()
    placeholder_status = st.empty()
    
    frames = []
    frames.append(env._get_obs().copy())
    
    done = False
    step = 0
    
    with placeholder_status.container():
        st.info("🚀 Misión iniciada - Drones desplegados")
    
    while not done and step < max_steps:
        # Decisiones de los agentes
        act_blue = agent_blue.decide(obs, env.agent_positions[0])
        act_orange = agent_orange.decide(obs, env.agent_positions[1])
        
        # Ejecutar paso
        obs, _, terminated, _, _ = env.step([act_blue, act_orange])
        
        frames.append(env._get_obs().copy())
        
        # Calcular métricas
        current_fires = np.sum(obs == 2)
        current_trees = np.sum(obs == 1)
        trees_saved_pct = (current_trees / st.session_state.initial_trees_count * 100) if st.session_state.initial_trees_count > 0 else 0
        water_used = 999 - env.water_tanks[0]  # Asumiendo que ambos usan la misma cantidad
        
        # Guardar en historia
        st.session_state.metrics_history['step'].append(step)
        st.session_state.metrics_history['active_fires'].append(current_fires)
        st.session_state.metrics_history['saved_trees'].append(trees_saved_pct)
        st.session_state.metrics_history['water_used'].append(water_used)
        st.session_state.metrics_history['agents_position'].append(env.agent_positions.copy())
        
        # Actualizar visualización en tiempo real
        with col1:
            col1.metric("Fuegos Activos", f"{current_fires}", delta=None)
        with col2:
            col2.metric("Árboles Salvados", f"{trees_saved_pct:.1f}%", delta=None)
        with col3:
            col3.metric("Agua Consumida", f"{water_used}", delta=None)
        with col4:
            col4.metric("Paso", f"{step}/{max_steps}", delta=None)
        
        # Actualizar grid
        with placeholder_grid.container():
            fig_grid = create_grid_figure(obs, step)
            st.plotly_chart(fig_grid, use_container_width=True)
        
        # Actualizar gráficos de métricas
        with placeholder_metrics.container():
            fig_metrics = create_metrics_dashboard(st.session_state.metrics_history)
            if fig_metrics:
                st.plotly_chart(fig_metrics, use_container_width=True)
        
        done = terminated
        step += 1
        time.sleep(0.2)  # Pequeña pausa para visualización
    
    # Estado final
    st.session_state.frames_history = frames
    
    with placeholder_status.container():
        if done:
            st.success("✅ Misión completada - Todos los fuegos extinguidos")
        else:
            st.warning(f"⏱️ Misión completada por tiempo máximo ({max_steps} pasos)")
    
    return True

# ============================================================================
# BARRA LATERAL (SIDEBAR)
# ============================================================================
st.sidebar.title("🎮 Centro de Control")
st.sidebar.markdown("---")

st.sidebar.header("⚙️ Parámetros de Simulación")

# Parámetros ajustables
grid_size = st.sidebar.slider(
    "Tamaño del Grid (lado)",
    min_value=8,
    max_value=15,
    value=10,
    step=1,
    help="Tamaño de la cuadrícula del bosque"
)

fire_spread_prob = st.sidebar.slider(
    "Probabilidad de Propagación del Fuego",
    min_value=0.0,
    max_value=0.5,
    value=0.1,
    step=0.01,
    help="Probabilidad de que el fuego se propague a celdas adyacentes"
)

initial_trees = st.sidebar.slider(
    "Densidad de Árboles",
    min_value=0.3,
    max_value=0.9,
    value=0.6,
    step=0.05,
    help="Proporción de celdas ocupadas por árboles (0-1)"
)

num_agents = st.sidebar.radio(
    "Número de Drones",
    options=[1, 2, 3],
    value=2,
    help="Cantidad de drones autónomos a desplegar"
)

initial_fires = st.sidebar.slider(
    "Focos de Fuego Iniciales",
    min_value=1,
    max_value=5,
    value=3,
    step=1,
    help="Número de focos de incendio al inicio de la misión"
)

max_steps = st.sidebar.slider(
    "Pasos Máximos de Simulación",
    min_value=50,
    max_value=200,
    value=100,
    step=10,
    help="Tiempo máximo de ejecución de la misión"
)

st.sidebar.markdown("---")
st.sidebar.header("🎯 Acciones")

# Botón de inicio de misión
col_btn1, col_btn2 = st.sidebar.columns(2)

with col_btn1:
    if st.button("🚀 Iniciar Misión", use_container_width=True, key="start_mission"):
        st.session_state.mission_active = True
        st.session_state.env = ForestFireEnv(
            grid_size=grid_size,
            fire_spread_prob=fire_spread_prob,
            initial_trees=initial_trees,
            initial_fires=initial_fires,
            num_agents=num_agents
        )

with col_btn2:
    if st.button("🔄 Limpiar", use_container_width=True, key="reset"):
        st.session_state.mission_active = False
        st.session_state.frames_history = []
        st.session_state.metrics_history = {
            'step': [],
            'active_fires': [],
            'saved_trees': [],
            'water_used': [],
            'agents_position': []
        }
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("""
    **Forest Guardian RL** es un sistema de control autónomo 
    para la contención de incendios forestales mediante drones equipados 
    con inteligencia artificial.
    
    🔴 Rojo = Fuego
    🟢 Verde = Árbol
    🔵 Azul = Dron 1
    🟠 Naranja = Dron 2
""")

# ============================================================================
# CONTENIDO PRINCIPAL
# ============================================================================
st.title("🔥 Forest Guardian RL - Centro de Control de Misión")
st.markdown("""
    **Sistema Autónomo de Control de Incendios Forestales**
    
    Visualiza en tiempo real cómo los drones equipados con IA contienen incendios forestales
    usando estrategias de busca y fuego coordinadas.
""")

st.markdown("---")

# TABLERO DE MÉTRICAS (KPIs)
st.header("📊 Tablero de Métricas")

if st.session_state.mission_active and st.session_state.env:
    # Crear 4 columnas para las métricas principales
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Bosque Salvado</div>
            <div class="metric-value" id="metric-saved">--</div>
            <div class="metric-label">% de cobertura forestal</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col2:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="metric-label">Fuegos Activos</div>
            <div class="metric-value" id="metric-fires">--</div>
            <div class="metric-label">Focos detectados</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col3:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="metric-label">Agua Consumida</div>
            <div class="metric-value" id="metric-water">--</div>
            <div class="metric-label">Unidades de agua</div>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col4:
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <div class="metric-label">Tiempo Transcurrido</div>
            <div class="metric-value" id="metric-time">--</div>
            <div class="metric-label">Pasos de simulación</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Ejecutar la misión
    run_mission(st.session_state.env, num_agents, max_steps)
    
else:
    st.info("👈 Ajusta los parámetros en el panel izquierdo y presiona '🚀 Iniciar Misión' para comenzar")
    
    # Mostrar demo con parámetros por defecto
    col_demo1, col_demo2 = st.columns([1, 1])
    with col_demo1:
        st.subheader("📋 Parámetros Disponibles")
        st.markdown("""
        - **Tamaño del Grid**: Dimensiones del área de simulación
        - **Probabilidad de Propagación**: Velocidad de expansión del fuego
        - **Densidad de Árboles**: Vegetación inicial del bosque
        - **Número de Drones**: Unidades autónomas disponibles
        - **Focos Iniciales**: Incendios para contener
        - **Pasos Máximos**: Duración máxima de la misión
        """)
    
    with col_demo2:
        st.subheader("🎯 Leyenda de Símbolos")
        st.markdown("""
        | Símbolo | Significado |
        |---------|------------|
        | 🟢 Verde | Árbol / Vegetación |
        | 🔴 Rojo | Fuego activo |
        | 🔵 Azul | Dron 1 (Búsqueda Rápida) |
        | 🟠 Naranja | Dron 2 (Contención) |
        | ⚪ Blanco | Celda vacía |
        """)

st.markdown("---")

# Información técnica
with st.expander("ℹ️ Información Técnica"):
    st.markdown("""
    ### Arquitectura del Sistema
    
    **Forest Guardian RL** utiliza un enfoque de aprendizaje por refuerzo descentralizado con dos agentes:
    
    1. **Dron Azul (ALPHA)**: Estrategia de "Búsqueda de Proximidad"
       - Identifica el fuego más cercano
       - Responde rápidamente a nuevos focos
    
    2. **Dron Naranja (BRAVO)**: Estrategia de "Contención Periférica"
       - Busca fuegos distantes
       - Previene la propagación en el perímetro
    
    ### Mecánicas del Entorno
    
    - **Grid**: 10x10 celdas (configurable)
    - **Estados de Celda**: Vacío (0), Árbol (1), Fuego (2), Agente1 (3), Agente2 (4)
    - **Acciones**: Arriba, Abajo, Izquierda, Derecha, Idle, Apagar (radio 3x3)
    - **Propagación del Fuego**: Estocástica, basada en probabilidad configurada
    - **Agua**: Infinita para los drones (tanques de 999 unidades)
    
    ### Métricas Clave
    
    - **Bosque Salvado**: Porcentaje de árboles que permanecen intactos
    - **Fuegos Activos**: Número de focos aún en expansión
    - **Agua Consumida**: Unidades de agua utilizadas por los drones
    - **Tiempo Transcurrido**: Pasos de simulación ejecutados
    """)
