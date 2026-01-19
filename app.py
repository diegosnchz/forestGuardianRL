import streamlit as st
import numpy as np
import time
from forest_fire_env import ForestFireEnv
from train_and_test import TerminatorAgent
import pandas as pd
from gis_locations import BOSQUES_REALES, ESCENARIOS_REALES
from forest_fire_gis import ForestFireGISEnv
from gis_visualization import MapaForestGuardian
from visualization import (
    create_heatmap_figure,
    create_metrics_timeseries,
    create_agent_positions_chart,
    create_summary_metrics
)
try:
    from streamlit_folium import st_folium
except ImportError:
    st_folium = None

# Importar módulo de visualización Atlas-Folium
try:
    from atlas_folium_sync import streamlit_atlas_map_viewer, PYMONGO_AVAILABLE, STREAMLIT_FOLIUM_AVAILABLE
except ImportError:
    streamlit_atlas_map_viewer = None
    PYMONGO_AVAILABLE = False
    STREAMLIT_FOLIUM_AVAILABLE = False

# Importar módulos XAI (Explainable AI)
try:
    from xai_explainer import XAIExplainer
    from xai_visualization import (
        create_attention_heatmap,
        create_importance_chart,
        create_decision_timeline,
        create_action_distribution_chart,
        create_confidence_vs_distance_scatter,
        create_tactical_reasoning_display,
        create_multi_agent_comparison,
        create_importance_evolution_heatmap,
        export_decision_report
    )
    import plotly.graph_objects as go
    import matplotlib.pyplot as plt
    XAI_AVAILABLE = True
except ImportError:
    XAI_AVAILABLE = False

# Importar módulo de Mission Logger
try:
    from mission_logger import MissionLogger, save_mission_summary
    MISSION_LOGGER_AVAILABLE = True
except ImportError:
    MISSION_LOGGER_AVAILABLE = False

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
if 'simulation_mode' not in st.session_state:
    st.session_state.simulation_mode = 'grid_aleatorio'
if 'selected_bosque' not in st.session_state:
    st.session_state.selected_bosque = None
if 'gis_scenario' not in st.session_state:
    st.session_state.gis_scenario = None
if 'xai_decisions' not in st.session_state:
    st.session_state.xai_decisions = []
if 'xai_explainer' not in st.session_state:
    st.session_state.xai_explainer = None
if 'mission_logger' not in st.session_state:
    st.session_state.mission_logger = None
if 'last_mission_id' not in st.session_state:
    st.session_state.last_mission_id = None

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

# Funciones auxiliares ahora importadas de visualization.py
# create_heatmap_figure, create_metrics_timeseries, create_agent_positions_chart

def run_mission(env, num_agents, max_steps=100):
    """Ejecuta la misión y actualiza métricas en tiempo real"""
    obs, _ = env.reset()
    st.session_state.initial_trees_count = np.sum(env.grid == 1)
    
    # Inicializar agentes
    agent_blue = TerminatorAgent(role="nearest")
    agent_orange = TerminatorAgent(role="farthest")
    
    # Inicializar XAI Explainer
    if XAI_AVAILABLE:
        grid_size = env.grid.shape[0]
        st.session_state.xai_explainer = XAIExplainer(
            grid_size=grid_size,
            enable_mongodb=st.session_state.get('mongodb_uri', None) is not None
        )
        st.session_state.xai_decisions = []  # Limpiar decisiones anteriores
    
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
        
        # Generar explicaciones XAI si está disponible
        if XAI_AVAILABLE and st.session_state.xai_explainer:
            try:
                # Explicar decisión del agente azul
                decision_blue = st.session_state.xai_explainer.explain_decision(
                    agent_id="ALPHA",
                    agent_role="nearest",
                    position=env.agent_positions[0],
                    action=act_blue,
                    grid_state=obs.copy(),
                    obs={'step': step},
                    water_level=env.water_tanks[0]
                )
                st.session_state.xai_decisions.append(decision_blue)
                
                # Explicar decisión del agente naranja
                decision_orange = st.session_state.xai_explainer.explain_decision(
                    agent_id="BRAVO",
                    agent_role="farthest",
                    position=env.agent_positions[1],
                    action=act_orange,
                    grid_state=obs.copy(),
                    obs={'step': step},
                    water_level=env.water_tanks[1]
                )
                st.session_state.xai_decisions.append(decision_orange)
            except Exception as e:
                # No fallar si hay error en XAI
                pass
        
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
            fig_grid = create_heatmap_figure(obs, step, "Estado del Bosque")
            st.plotly_chart(fig_grid, use_container_width=True)
        
        # Actualizar gráficos de métricas
        with placeholder_metrics.container():
            fig_metrics = create_metrics_timeseries(
                st.session_state.metrics_history,
                include_density=True
            )
            if fig_metrics:
                st.plotly_chart(fig_metrics, use_container_width=True)
        
        done = terminated
        step += 1
        time.sleep(0.2)  # Pequeña pausa para visualización
    
    # Estado final
    st.session_state.frames_history = frames
    
    # Calcular métricas finales
    final_trees = np.sum(obs == 1)
    fires_extinguished = st.session_state.initial_trees_count - final_trees  # Aproximado
    water_consumed = 999 - env.water_tanks[0]
    
    # Guardar misión en MongoDB si está disponible
    if MISSION_LOGGER_AVAILABLE and st.session_state.mission_logger:
        try:
            geo_zone = st.session_state.get('selected_bosque', 'Grid Aleatorio')
            geojson_file = st.session_state.get('geojson_file', None)
            
            configuration = {
                "grid_size": env.grid.shape[0],
                "num_agents": num_agents,
                "fire_prob": env.fire_propagation_prob,
                "tree_density": 0.3,  # Default o desde config
                "initial_fires": len(np.argwhere(frames[0] == 2)),
                "max_steps": max_steps
            }
            
            mission_id = save_mission_summary(
                mission_logger=st.session_state.mission_logger,
                geo_zone=geo_zone,
                geojson_file=geojson_file,
                configuration=configuration,
                initial_trees=st.session_state.initial_trees_count,
                final_trees=final_trees,
                fires_extinguished=fires_extinguished,
                water_consumed=water_consumed,
                steps_taken=step,
                xai_decisions=st.session_state.xai_decisions if XAI_AVAILABLE else [],
                final_grid=obs
            )
            
            if mission_id:
                st.session_state.last_mission_id = mission_id
                print(f"✅ Misión guardada en MongoDB: {mission_id}")
        except Exception as e:
            print(f"⚠️ Error guardando misión: {e}")
    
    with placeholder_status.container():
        if done:
            st.success("✅ Misión completada - Todos los fuegos extinguidos")
        else:
            st.warning(f"⏱️ Misión completada por tiempo máximo ({max_steps} pasos)")
        
        # Mostrar ID de misión si fue guardada
        if st.session_state.last_mission_id:
            st.info(f"💾 Misión guardada: `{st.session_state.last_mission_id}`")
    
    # Mostrar resumen final con visualization.py
    st.markdown("---")
    st.subheader("📊 Resumen de la Misión")
    
    col_sum1, col_sum2 = st.columns(2)
    
    with col_sum1:
        # Crear resumen de métricas usando visualization.py
        final_trees = np.sum(obs == 1)
        trees_saved_pct = (final_trees / st.session_state.initial_trees_count * 100) if st.session_state.initial_trees_count > 0 else 0
        fires_extinguished = st.session_state.metrics_history['active_fires'][0] if st.session_state.metrics_history['active_fires'] else 0
        
        summary = create_summary_metrics(
            steps=step,
            trees_saved_pct=trees_saved_pct,
            fires_extinguished=fires_extinguished,
            water_used=st.session_state.metrics_history['water_used'][-1] if st.session_state.metrics_history['water_used'] else 0,
            initial_trees=st.session_state.initial_trees_count,
            final_trees=final_trees
        )
        
        st.markdown("### 📈 Métricas Finales")
        st.write(f"**Duración:** {summary['duration']}")
        st.write(f"**Árboles Salvados:** {summary['trees_saved']}")
        st.write(f"**Árboles Perdidos:** {summary['trees_lost']}")
        st.write(f"**Fuegos Extintos:** {summary['fires_extinguished']}")
        st.write(f"**Agua Consumida:** {summary['water_used']}")
        st.write(f"**Eficiencia:** {summary['efficiency']}")
    
    with col_sum2:
        # Gráfico de trayectorias de drones usando visualization.py
        if st.session_state.metrics_history['agents_position']:
            st.markdown("### 🚁 Trayectorias de Drones")
            fig_traj = create_agent_positions_chart(
                st.session_state.metrics_history['agents_position'],
                env.grid_size
            )
            if fig_traj:
                st.plotly_chart(fig_traj, use_container_width=True)
    
    return True

# ============================================================================
# BARRA LATERAL (SIDEBAR)
# ============================================================================
st.sidebar.title("🎮 Centro de Control")
st.sidebar.markdown("---")

# ============================================================================
# BARRA LATERAL (SIDEBAR)
# ============================================================================
st.sidebar.title("🎮 Centro de Control")
st.sidebar.markdown("---")

# SELECTOR DE MODO DE SIMULACIÓN
st.sidebar.header("🌍 Modo de Simulación")
simulation_mode = st.sidebar.radio(
    "Tipo de Escenario",
    options=["Grid Aleatorio", "Bosques Reales"],
    index=0 if st.session_state.simulation_mode == 'grid_aleatorio' else 1,
    help="Elige entre un grid aleatorio o un bosque real con coordenadas geográficas"
)

# Actualizar estado
if simulation_mode == "Grid Aleatorio":
    st.session_state.simulation_mode = 'grid_aleatorio'
else:
    st.session_state.simulation_mode = 'gis'

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Parámetros de Simulación")

# PARÁMETROS ESPECÍFICOS POR MODO
if st.session_state.simulation_mode == 'grid_aleatorio':
    # Parámetros para grid aleatorio
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

else:
    # Parámetros para bosques reales (GIS)
    scenario_type = st.sidebar.radio(
        "Tipo de Bosque",
        options=["Escenarios Predefinidos", "Personalizado"],
        index=0,
        help="Usa un escenario predefinido o ingresa coordenadas personalizadas"
    )

    if scenario_type == "Escenarios Predefinidos":
        scenario_names = list(ESCENARIOS_REALES.keys())
        selected_scenario = st.sidebar.selectbox(
            "Seleccionar Escenario",
            options=scenario_names,
            help="Escenarios GIS predefinidos con bosques reales"
        )
        st.session_state.gis_scenario = ESCENARIOS_REALES[selected_scenario]
        
        # Mostrar información del bosque
        bosque_info = st.session_state.gis_scenario['bosque']
        with st.sidebar.expander("ℹ️ Información del Bosque"):
            st.write(f"**País:** {bosque_info.pais}")
            st.write(f"**Ubicación:** {bosque_info.latitud:.4f}°, {bosque_info.longitud:.4f}°")
            st.write(f"**Área:** {bosque_info.area_km2:.0f} km²")
            st.write(f"**Amenazas:** {', '.join(bosque_info.amenazas)}")
            st.write(f"**Descripción:** {bosque_info.descripcion}")
    else:
        # Entrada personalizada
        st.sidebar.write("**Ingresar Coordenadas Personalizadas**")
        custom_lat = st.sidebar.number_input(
            "Latitud",
            min_value=-90.0,
            max_value=90.0,
            value=-3.4653,
            step=0.0001,
            format="%.4f"
        )
        custom_lon = st.sidebar.number_input(
            "Longitud",
            min_value=-180.0,
            max_value=180.0,
            value=-62.2159,
            step=0.0001,
            format="%.4f"
        )
        custom_name = st.sidebar.text_input("Nombre del Bosque", "Mi Bosque")
        
        # Crear bosque personalizado
        from gis_locations import BosqueReal
        custom_bosque = BosqueReal(
            nombre=custom_name,
            pais="Personalizado",
            latitud=custom_lat,
            longitud=custom_lon,
            area_km2=50.0,
            densidad="media",
            amenazas=["fire"],
            descripcion="Bosque personalizado para simulación"
        )
        st.session_state.gis_scenario = {
            'name': custom_name,
            'bosque': custom_bosque,
            'initial_fires': 3,
            'initial_trees': 0.65,
            'fire_spread_prob': 0.15
        }
    
    # Parámetros ajustables para GIS
    fire_spread_prob = st.sidebar.slider(
        "Probabilidad de Propagación del Fuego",
        min_value=0.0,
        max_value=0.5,
        value=st.session_state.gis_scenario.get('fire_spread_prob', 0.1),
        step=0.01,
        help="Probabilidad de que el fuego se propague"
    )
    
    initial_trees = st.sidebar.slider(
        "Densidad de Árboles",
        min_value=0.3,
        max_value=0.9,
        value=st.session_state.gis_scenario.get('initial_trees', 0.65),
        step=0.05,
        help="Proporción de cobertura forestal"
    )

num_agents = st.sidebar.radio(
    "Número de Drones",
    options=[1, 2, 3],
    index=1,
    help="Cantidad de drones autónomos a desplegar"
)

initial_fires = st.sidebar.slider(
    "Focos de Fuego Iniciales",
    min_value=1,
    max_value=5,
    value=st.session_state.gis_scenario.get('initial_fires', 3) if st.session_state.simulation_mode == 'gis' else 3,
    step=1,
    help="Número de focos de incendio al inicio"
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

# CONFIGURACIÓN DE MONGODB ATLAS
if streamlit_atlas_map_viewer and PYMONGO_AVAILABLE:
    with st.sidebar.expander("🗺️ MongoDB Atlas (Opcional)", expanded=False):
        mongodb_uri = st.text_input(
            "URI de MongoDB Atlas",
            type="password",
            help="mongodb+srv://user:pass@cluster.mongodb.net/...",
            key="mongodb_uri"
        )
        
        geojson_file = st.text_input(
            "Archivo GeoJSON",
            value="zonas_forestales_ejemplo.geojson",
            help="Ruta al archivo GeoJSON para carga/recarga",
            key="geojson_file"
        )
        
        if mongodb_uri:
            st.success("✅ URI configurado")
        else:
            st.info("💡 Configura para habilitar mapa geoespacial")
        
        # Mission Logger - Usar el mismo URI de MongoDB Atlas
        st.markdown("---")
        st.markdown("### 💾 Mission Logger")
        
        enable_mission_logger = st.checkbox(
            "Habilitar historial de misiones",
            value=True,
            help="Guarda automáticamente los resultados de cada misión"
        )
        
        if enable_mission_logger and mongodb_uri and MISSION_LOGGER_AVAILABLE:
            # Intentar conectar al mission logger
            if st.session_state.mission_logger is None:
                try:
                    st.session_state.mission_logger = MissionLogger(uri=mongodb_uri)
                    if st.session_state.mission_logger.connect():
                        st.success("✅ Mission Logger conectado")
                    else:
                        st.error("❌ Error conectando Mission Logger")
                        st.session_state.mission_logger = None
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.session_state.mission_logger = None
            else:
                # Ya está conectado
                if st.session_state.mission_logger.connected:
                    st.success("✅ Mission Logger conectado")
                    
                    # Mostrar última misión guardada
                    if st.session_state.last_mission_id:
                        st.info(f"📝 Última misión: {st.session_state.last_mission_id[:8]}...")
                else:
                    st.warning("⚠️ Desconectado - intentando reconectar...")
                    if st.session_state.mission_logger.connect():
                        st.success("✅ Reconectado")
                    else:
                        st.error("❌ No se pudo reconectar")
        elif enable_mission_logger and not MISSION_LOGGER_AVAILABLE:
            st.error("❌ pymongo no instalado")
            st.code("pip install pymongo", language="bash")
        elif enable_mission_logger and not mongodb_uri:
            st.warning("⚠️ Necesitas configurar MongoDB URI arriba")
        elif not enable_mission_logger:
            st.info("💡 Activa para guardar historial de misiones")
            # Limpiar mission logger si está deshabilitado
            st.session_state.mission_logger = None

st.sidebar.markdown("---")
st.sidebar.header("🎯 Acciones")

# Botón de inicio de misión
col_btn1, col_btn2 = st.sidebar.columns(2)

with col_btn1:
    if st.button("🚀 Iniciar Misión", use_container_width=True, key="start_mission"):
        st.session_state.mission_active = True
        
        if st.session_state.simulation_mode == 'grid_aleatorio':
            # Crear ambiente de grid aleatorio
            st.session_state.env = ForestFireEnv(
                grid_size=grid_size,
                fire_spread_prob=fire_spread_prob,
                initial_trees=initial_trees,
                initial_fires=initial_fires,
                num_agents=num_agents
            )
        else:
            # Crear ambiente GIS con bosque real
            bosque = st.session_state.gis_scenario['bosque']
            st.session_state.env = ForestFireGISEnv(
                bosque=bosque,
                grid_size=10,
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
    
    # MOSTRAR MAPA GIS SI ESTÁ EN MODO GIS
    if st.session_state.simulation_mode == 'gis' and st.session_state.env:
        st.subheader("🗺️ Visualización Geográfica del Bosque")
        
        # Crear visualizador de mapas
        try:
            map_visualizer = MapaForestGuardian(st.session_state.env)
            
            # Opciones de visualización del mapa
            col_map_opt1, col_map_opt2, col_map_opt3 = st.columns(3)
            
            with col_map_opt1:
                show_heatmap = st.checkbox("🔥 Mostrar Heatmap de Fuego", value=True)
            with col_map_opt2:
                show_grid = st.checkbox("📐 Mostrar Grid de Simulación", value=True)
            with col_map_opt3:
                show_forest_info = st.checkbox("ℹ️ Información del Bosque", value=True)
            
            # Generar mapa con opciones seleccionadas
            map_obj = map_visualizer.crear_mapa_completo(
                incluir_heatmap=show_heatmap,
                incluir_grid=show_grid,
                incluir_drones=True,
                incluir_arboles=True,
                incluir_info=False  # Manejamos la info por separado debajo
            )
            
            # Mostrar mapa con streamlit-folium
            if st_folium:
                st_folium(map_obj, width=st.session_state.env.grid_size * 50, height=500)
            else:
                st.warning("⚠️ streamlit-folium no está instalado. Instálalo con: pip install streamlit-folium")
            
            # Mostrar información del bosque
            if show_forest_info:
                st.markdown("---")
                col_info1, col_info2 = st.columns(2)
                
                with col_info1:
                    bosque = st.session_state.env.bosque
                    st.markdown(f"### 🌲 {bosque.nombre}")
                    st.write(f"**País:** {bosque.pais}")
                    st.write(f"**Coordenadas:** {bosque.latitud:.4f}°, {bosque.longitud:.4f}°")
                    st.write(f"**Área:** {bosque.area_km2:.0f} km²")
                
                with col_info2:
                    st.markdown("### 📊 Resumen de la Misión")
                    bounds = st.session_state.env.get_grid_bounds()
                    st.write(f"**Área Cubierta:** {st.session_state.env.get_coverage_area_km2():.2f} km²")
                    st.write(f"**Centro:** {bounds['center_lat']:.4f}°, {bounds['center_lon']:.4f}°")
                    st.write(f"**Límites:** N={bounds['north']:.4f}°, S={bounds['south']:.4f}°")
        
        except Exception as e:
            st.error(f"❌ Error al generar el mapa: {str(e)}")
    
    # Ejecutar la misión
    run_mission(st.session_state.env, num_agents, max_steps)
    
    # PESTAÑAS CON ANÁLISIS ADICIONALES
    if st.session_state.frames_history and len(st.session_state.frames_history) > 0:
        st.markdown("---")
        st.header("📊 Análisis Detallado de la Misión")
        
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📈 Series Temporales",
            "🔥 Análisis de Fuego",
            "🚁 Trayectorias de Drones",
            "📊 Estadísticas Finales",
            "🗺️ Mapa Geoespacial (Atlas)",
            "🧠 Explicabilidad IA (XAI)",
            "📜 Historial de Misiones"
        ])
        
        with tab1:
            st.subheader("Series Temporales de Métricas")
            if st.session_state.metrics_history['step']:
                # Usar visualización de visualization.py
                from visualization import create_metrics_timeseries
                
                fig_timeseries = create_metrics_timeseries(
                    st.session_state.metrics_history,
                    include_density=True
                )
                
                if fig_timeseries:
                    st.plotly_chart(fig_timeseries, use_container_width=True)
                    
                    # Descargar datos
                    col_dl1, col_dl2 = st.columns(2)
                    with col_dl1:
                        import pandas as pd
                        df_metrics = pd.DataFrame(st.session_state.metrics_history)
                        csv = df_metrics.to_csv(index=False)
                        st.download_button(
                            label="📥 Descargar Métricas (CSV)",
                            data=csv,
                            file_name="forest_guardian_metrics.csv",
                            mime="text/csv"
                        )
        
        with tab2:
            st.subheader("🔥 Análisis de Propagación del Fuego")
            
            col_fire1, col_fire2 = st.columns(2)
            
            with col_fire1:
                # Gráfico de fuegos activos a lo largo del tiempo
                import plotly.graph_objects as go
                
                fig_fires = go.Figure()
                fig_fires.add_trace(go.Scatter(
                    x=st.session_state.metrics_history['step'],
                    y=st.session_state.metrics_history['active_fires'],
                    mode='lines+markers',
                    name='Fuegos Activos',
                    line=dict(color='#ff0000', width=3),
                    fill='tozeroy',
                    fillcolor='rgba(255, 0, 0, 0.2)'
                ))
                
                fig_fires.update_layout(
                    title="Evolución de Fuegos Activos",
                    xaxis_title="Paso",
                    yaxis_title="Número de Fuegos",
                    hovermode='x',
                    height=400
                )
                
                st.plotly_chart(fig_fires, use_container_width=True)
            
            with col_fire2:
                # Estadísticas de fuego
                st.markdown("### 📊 Estadísticas")
                
                if st.session_state.metrics_history['active_fires']:
                    max_fires = max(st.session_state.metrics_history['active_fires'])
                    min_fires = min(st.session_state.metrics_history['active_fires'])
                    avg_fires = sum(st.session_state.metrics_history['active_fires']) / len(st.session_state.metrics_history['active_fires'])
                    
                    st.metric("Fuegos Máximos", max_fires)
                    st.metric("Fuegos Mínimos", min_fires)
                    st.metric("Promedio", f"{avg_fires:.1f}")
                    
                    # Tasa de extinción
                    initial_fires = st.session_state.metrics_history['active_fires'][0]
                    final_fires = st.session_state.metrics_history['active_fires'][-1]
                    extinction_rate = ((initial_fires - final_fires) / initial_fires * 100) if initial_fires > 0 else 0
                    
                    st.metric("Tasa de Extinción", f"{extinction_rate:.1f}%")
        
        with tab3:
            st.subheader("🚁 Análisis de Movimiento de Drones")
            
            if st.session_state.metrics_history['agents_position']:
                from visualization import create_agent_positions_chart
                
                # Gráfico de trayectorias
                fig_traj = create_agent_positions_chart(
                    st.session_state.metrics_history['agents_position'],
                    st.session_state.env.grid_size
                )
                
                if fig_traj:
                    st.plotly_chart(fig_traj, use_container_width=True)
                    
                    # Estadísticas de movimiento
                    st.markdown("---")
                    st.markdown("### 📏 Estadísticas de Movimiento")
                    
                    col_mov1, col_mov2, col_mov3 = st.columns(3)
                    
                    # Calcular distancia total recorrida por cada dron
                    positions_history = st.session_state.metrics_history['agents_position']
                    
                    for agent_idx in range(num_agents):
                        total_distance = 0
                        for i in range(1, len(positions_history)):
                            pos_prev = positions_history[i-1][agent_idx] if len(positions_history[i-1]) > agent_idx else (0, 0)
                            pos_curr = positions_history[i][agent_idx] if len(positions_history[i]) > agent_idx else (0, 0)
                            
                            # Distancia Manhattan
                            distance = abs(pos_curr[0] - pos_prev[0]) + abs(pos_curr[1] - pos_prev[1])
                            total_distance += distance
                        
                        col = [col_mov1, col_mov2, col_mov3][agent_idx]
                        with col:
                            drone_colors = ["🔵", "🟠", "🟣"]
                            st.metric(
                                f"{drone_colors[agent_idx]} Dron {agent_idx + 1}",
                                f"{total_distance} celdas"
                            )
        
        with tab4:
            st.subheader("📊 Resumen Final de la Misión")
            
            # Crear resumen detallado
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            with col_stat1:
                st.markdown("### 🌳 Bosque")
                final_trees = np.sum(st.session_state.frames_history[-1] == 1) if st.session_state.frames_history else 0
                trees_saved_pct = (final_trees / st.session_state.initial_trees_count * 100) if st.session_state.initial_trees_count > 0 else 0
                trees_lost = st.session_state.initial_trees_count - final_trees
                
                st.metric("Árboles Iniciales", st.session_state.initial_trees_count)
                st.metric("Árboles Salvados", final_trees, f"{trees_saved_pct:.1f}%")
                st.metric("Árboles Perdidos", trees_lost, f"-{100-trees_saved_pct:.1f}%")
            
            with col_stat2:
                st.markdown("### 🔥 Fuegos")
                initial_fires = st.session_state.metrics_history['active_fires'][0] if st.session_state.metrics_history['active_fires'] else 0
                final_fires = st.session_state.metrics_history['active_fires'][-1] if st.session_state.metrics_history['active_fires'] else 0
                fires_extinguished = initial_fires - final_fires
                
                st.metric("Fuegos Iniciales", initial_fires)
                st.metric("Fuegos Extintos", fires_extinguished)
                st.metric("Fuegos Restantes", final_fires)
            
            with col_stat3:
                st.markdown("### 🚁 Drones")
                total_steps = len(st.session_state.metrics_history['step'])
                water_used = st.session_state.metrics_history['water_used'][-1] if st.session_state.metrics_history['water_used'] else 0
                
                st.metric("Pasos Totales", total_steps)
                st.metric("Agua Consumida", f"{water_used} L")
                
                # Eficiencia
                if water_used > 0 and fires_extinguished > 0:
                    efficiency = fires_extinguished / water_used * 100
                    st.metric("Eficiencia", f"{efficiency:.2f}%")
                else:
                    st.metric("Eficiencia", "N/A")
            
            # Gráfico de comparación final
            st.markdown("---")
            st.markdown("### 📊 Comparación: Estado Inicial vs Final")
            
            import plotly.graph_objects as go
            
            fig_comparison = go.Figure()
            
            categories = ['Árboles', 'Fuegos']
            initial_values = [st.session_state.initial_trees_count, initial_fires]
            final_values = [final_trees, final_fires]
            
            fig_comparison.add_trace(go.Bar(
                name='Inicial',
                x=categories,
                y=initial_values,
                marker_color='#667eea'
            ))
            
            fig_comparison.add_trace(go.Bar(
                name='Final',
                x=categories,
                y=final_values,
                marker_color='#764ba2'
            ))
            
            fig_comparison.update_layout(
                title="Comparación Estado Inicial vs Final",
                xaxis_title="Categoría",
                yaxis_title="Cantidad",
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig_comparison, use_container_width=True)
        
        with tab5:
            st.subheader("🗺️ Mapa Geoespacial - MongoDB Atlas")
            
            # Verificar si el módulo está disponible
            if streamlit_atlas_map_viewer and PYMONGO_AVAILABLE and STREAMLIT_FOLIUM_AVAILABLE:
                # Obtener configuración de MongoDB desde session_state
                mongodb_uri = st.session_state.get('mongodb_uri', None)
                geojson_file = st.session_state.get('geojson_file', 'zonas_forestales_ejemplo.geojson')
                
                if not mongodb_uri:
                    st.warning("⚠️ No hay URI de MongoDB Atlas configurado")
                    st.info("""
                    💡 **Para usar el mapa geoespacial:**
                    
                    1. Configura tu URI de MongoDB Atlas en la sidebar (panel izquierdo)
                    2. Si no tienes cuenta, puedes usar el modo demo con el archivo GeoJSON local
                    3. Lee la documentación en `MONGODB_ATLAS_SETUP.md` para más detalles
                    """)
                    
                    # Modo demo sin conexión
                    st.markdown("---")
                    st.markdown("### 📍 Modo Demo (Sin conexión a Atlas)")
                    
                    col_demo_a, col_demo_b = st.columns(2)
                    
                    with col_demo_a:
                        if st.button("🗺️ Cargar Mapa Demo", use_container_width=True):
                            # Llamar al viewer sin URI (modo demo)
                            streamlit_atlas_map_viewer(
                                uri=None,
                                geojson_path=geojson_file,
                                enable_reload=False
                            )
                    
                    with col_demo_b:
                        st.info("""
                        El modo demo carga datos desde el archivo GeoJSON local
                        sin necesidad de conexión a MongoDB Atlas.
                        """)
                else:
                    # Modo completo con MongoDB Atlas
                    st.success("✅ Conectado a MongoDB Atlas")
                    
                    # Llamar al componente de visualización completo
                    streamlit_atlas_map_viewer(
                        uri=mongodb_uri,
                        geojson_path=geojson_file,
                        enable_reload=True
                    )
            
            elif not PYMONGO_AVAILABLE:
                st.error("❌ pymongo no está instalado")
                st.code("pip install pymongo", language="bash")
                st.info("Instala pymongo para habilitar la integración con MongoDB Atlas")
            
            elif not STREAMLIT_FOLIUM_AVAILABLE:
                st.error("❌ streamlit-folium no está instalado")
                st.code("pip install streamlit-folium", language="bash")
                st.info("Instala streamlit-folium para habilitar la visualización de mapas")
            
            else:
                st.error("❌ El módulo atlas_folium_sync.py no está disponible")
                st.info("Asegúrate de que el archivo atlas_folium_sync.py esté en el directorio del proyecto")
        
        with tab6:
            st.subheader("🧠 Explicabilidad IA (XAI) - Análisis de Decisiones")
            
            # Verificar si XAI está disponible
            if not XAI_AVAILABLE:
                st.error("❌ Módulos XAI no disponibles")
                st.code("pip install plotly matplotlib", language="bash")
                st.info("Instala las dependencias para habilitar el sistema de explicabilidad")
            else:
                # Verificar si hay decisiones XAI guardadas
                if 'xai_decisions' not in st.session_state or not st.session_state.xai_decisions:
                    st.warning("⚠️ No hay decisiones XAI disponibles")
                    st.info("""
                    💡 **Para generar explicaciones XAI:**
                    
                    1. Inicia una misión con los parámetros deseados
                    2. Durante la simulación, el sistema XAI captura las decisiones
                    3. Regresa a esta pestaña para ver los análisis detallados
                    
                    El sistema XAI explica:
                    - **Por qué** cada agente tomó una decisión específica
                    - **Qué factores** influyeron más en la decisión
                    - **Cómo** se distribuye la atención en el mapa
                    - **Cuáles** alternativas se consideraron
                    """)
                else:
                    # Obtener decisiones
                    all_decisions = st.session_state.xai_decisions
                    
                    # Agrupar por agente
                    decisions_by_agent = {}
                    for decision in all_decisions:
                        agent_id = decision.agent_id
                        if agent_id not in decisions_by_agent:
                            decisions_by_agent[agent_id] = []
                        decisions_by_agent[agent_id].append(decision)
                    
                    # Selector de agente
                    st.markdown("### 🤖 Seleccionar Agente")
                    selected_agent = st.selectbox(
                        "Agente",
                        options=list(decisions_by_agent.keys()),
                        format_func=lambda x: f"{x} ({len(decisions_by_agent[x])} decisiones)"
                    )
                    
                    agent_decisions = decisions_by_agent[selected_agent]
                    
                    # Tabs internos para diferentes visualizaciones
                    xai_tab1, xai_tab2, xai_tab3, xai_tab4 = st.tabs([
                        "📊 Última Decisión",
                        "📈 Evolución Temporal",
                        "🔥 Mapas de Atención",
                        "📉 Análisis Estadístico"
                    ])
                    
                    with xai_tab1:
                        st.markdown("#### 🎯 Última Decisión del Agente")
                        
                        last_decision = agent_decisions[-1]
                        
                        # Display HTML del razonamiento táctico
                        st.markdown(create_tactical_reasoning_display(last_decision), unsafe_allow_html=True)
                        
                        # Gráfico de importancia
                        st.markdown("#### 📊 Importancia de Atributos")
                        fig_importance = create_importance_chart(
                            last_decision.importance_scores,
                            f"Factores de Decisión - {selected_agent}"
                        )
                        st.plotly_chart(fig_importance, use_container_width=True)
                        
                        # Alternativas consideradas
                        if last_decision.alternative_actions:
                            st.markdown("#### 🔄 Alternativas Consideradas")
                            for alt in last_decision.alternative_actions:
                                with st.expander(f"🎯 {alt['name']} (Score: {alt['score']*100:.0f}%)"):
                                    st.write(alt['reason'])
                        
                        # Botón de exportación
                        col_exp1, col_exp2 = st.columns([3, 1])
                        with col_exp2:
                            if st.button("💾 Exportar Reporte", key="export_last"):
                                filename = f"xai_report_{selected_agent}_{last_decision.timestamp.strftime('%Y%m%d_%H%M%S')}.html"
                                export_decision_report(last_decision, filename)
                                st.success(f"✅ Reporte exportado: {filename}")
                    
                    with xai_tab2:
                        st.markdown("#### 📈 Evolución de Decisiones")
                        
                        # Selector de métrica
                        col_metric1, col_metric2 = st.columns(2)
                        with col_metric1:
                            metric_option = st.selectbox(
                                "Métrica a visualizar",
                                ["distance_to_target", "confidence", "water_level"]
                            )
                        
                        # Timeline
                        fig_timeline = create_decision_timeline(agent_decisions, metric_option)
                        st.plotly_chart(fig_timeline, use_container_width=True)
                        
                        # Distribución de acciones
                        st.markdown("#### 🎯 Distribución de Acciones")
                        col_dist1, col_dist2 = st.columns(2)
                        
                        with col_dist1:
                            fig_actions = create_action_distribution_chart(agent_decisions)
                            st.plotly_chart(fig_actions, use_container_width=True)
                        
                        with col_dist2:
                            fig_scatter = create_confidence_vs_distance_scatter(agent_decisions)
                            st.plotly_chart(fig_scatter, use_container_width=True)
                        
                        # Evolución de importancia
                        st.markdown("#### 🔥 Evolución de Importancia de Factores")
                        fig_evolution = create_importance_evolution_heatmap(agent_decisions)
                        st.plotly_chart(fig_evolution, use_container_width=True)
                    
                    with xai_tab3:
                        st.markdown("#### 🗺️ Mapas de Atención por Paso")
                        
                        # Selector de paso
                        step_index = st.slider(
                            "Paso de la simulación",
                            min_value=0,
                            max_value=len(agent_decisions) - 1,
                            value=len(agent_decisions) - 1,
                            key="attention_step_slider"
                        )
                        
                        selected_decision = agent_decisions[step_index]
                        
                        # Mostrar información del paso
                        col_info1, col_info2, col_info3, col_info4 = st.columns(4)
                        with col_info1:
                            st.metric("Paso", step_index)
                        with col_info2:
                            st.metric("Acción", selected_decision.action_name)
                        with col_info3:
                            st.metric("Distancia", f"{selected_decision.distance_to_target:.1f}")
                        with col_info4:
                            st.metric("Confianza", f"{selected_decision.confidence*100:.0f}%")
                        
                        # Mapa de atención
                        st.markdown("##### 🔥 Mapa de Atención")
                        try:
                            fig_attention = create_attention_heatmap(
                                selected_decision.attention_map,
                                selected_decision.grid_state,
                                selected_decision.position,
                                f"Atención - {selected_agent} (Paso {step_index})"
                            )
                            st.pyplot(fig_attention)
                            plt.close(fig_attention)
                        except Exception as e:
                            st.error(f"Error al generar mapa de atención: {e}")
                        
                        # Explicación del paso
                        st.markdown("##### 💡 Explicación de la Decisión")
                        with st.expander("Ver explicación completa"):
                            st.text(selected_decision.explanation)
                        
                        st.markdown("##### ⚔️ Razonamiento Táctico")
                        with st.expander("Ver razonamiento táctico"):
                            st.text(selected_decision.tactical_reasoning)
                    
                    with xai_tab4:
                        st.markdown("#### 📊 Análisis Estadístico Multi-Agente")
                        
                        # Comparación multi-agente
                        if len(decisions_by_agent) > 1:
                            st.markdown("##### 🤝 Comparación de Agentes")
                            fig_comparison = create_multi_agent_comparison(decisions_by_agent)
                            st.plotly_chart(fig_comparison, use_container_width=True)
                        
                        # Estadísticas generales
                        st.markdown("##### 📈 Estadísticas del Agente")
                        
                        total_decisions = len(agent_decisions)
                        avg_confidence = np.mean([d.confidence for d in agent_decisions])
                        avg_distance = np.mean([d.distance_to_target for d in agent_decisions])
                        
                        # Contar acciones
                        action_counts = {}
                        for d in agent_decisions:
                            action_counts[d.action_name] = action_counts.get(d.action_name, 0) + 1
                        most_common_action = max(action_counts.items(), key=lambda x: x[1])
                        
                        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                        
                        with col_stat1:
                            st.metric("Total Decisiones", total_decisions)
                        with col_stat2:
                            st.metric("Confianza Promedio", f"{avg_confidence*100:.1f}%")
                        with col_stat3:
                            st.metric("Distancia Promedio", f"{avg_distance:.1f}")
                        with col_stat4:
                            st.metric("Acción Más Común", f"{most_common_action[0]}")
                        
                        # Tabla de decisiones
                        st.markdown("##### 📋 Historial de Decisiones")
                        
                        df_decisions = pd.DataFrame([
                            {
                                "Paso": i,
                                "Acción": d.action_name,
                                "Posición": f"({d.position[0]}, {d.position[1]})",
                                "Distancia": f"{d.distance_to_target:.1f}",
                                "Confianza": f"{d.confidence*100:.0f}%",
                                "Agua": d.water_level,
                                "Timestamp": d.timestamp.strftime("%H:%M:%S")
                            }
                            for i, d in enumerate(agent_decisions)
                        ])
                        
                        st.dataframe(df_decisions, use_container_width=True, height=400)
                        
                        # Exportar todas las decisiones
                        col_exp_all1, col_exp_all2 = st.columns([3, 1])
                        with col_exp_all2:
                            if st.button("💾 Exportar Todo (JSON)", key="export_all_json"):
                                import json
                                from datetime import datetime
                                
                                # Preparar datos para JSON
                                export_data = {
                                    "agent_id": selected_agent,
                                    "total_decisions": len(agent_decisions),
                                    "export_timestamp": datetime.now().isoformat(),
                                    "decisions": [
                                        {
                                            "step": i,
                                            "action": d.action,
                                            "action_name": d.action_name,
                                            "position": d.position,
                                            "distance_to_target": d.distance_to_target,
                                            "confidence": d.confidence,
                                            "water_level": d.water_level,
                                            "importance_scores": d.importance_scores,
                                            "timestamp": d.timestamp.isoformat()
                                        }
                                        for i, d in enumerate(agent_decisions)
                                    ]
                                }
                                
                                filename = f"xai_history_{selected_agent}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                                with open(filename, 'w', encoding='utf-8') as f:
                                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                                
                                st.success(f"✅ Historial exportado: {filename}")
        
        with tab7:
            st.subheader("📜 Historial de Misiones - MongoDB Atlas")
            
            # Verificar si Mission Logger está disponible
            if not MISSION_LOGGER_AVAILABLE:
                st.error("❌ Mission Logger no disponible")
                st.code("pip install pymongo", language="bash")
                st.info("Instala pymongo para habilitar el historial de misiones")
            elif not st.session_state.mission_logger or not st.session_state.mission_logger.connected:
                st.warning("⚠️ No hay conexión a MongoDB Atlas")
                st.info("""
                💡 **Para usar el historial de misiones:**
                
                1. Configura tu URI de MongoDB Atlas en la sidebar
                2. Ejecuta una misión
                3. Regresa a esta pestaña para ver el historial
                """)
            else:
                # Mission logger está disponible y conectado
                st.success("✅ Conectado a MongoDB Atlas")
                
                # Tabs internos para diferentes vistas
                hist_tab1, hist_tab2, hist_tab3, hist_tab4 = st.tabs([
                    "🕐 Recientes",
                    "🏆 Mejores",
                    "🔍 Buscar",
                    "📊 Estadísticas"
                ])
                
                with hist_tab1:
                    st.markdown("#### 🕐 Misiones Recientes")
                    
                    # Control de cantidad
                    limit = st.slider("Número de misiones", 5, 50, 10, key="recent_limit")
                    
                    # Obtener misiones
                    missions = st.session_state.mission_logger.get_recent_missions(limit)
                    
                    if not missions:
                        st.info("No hay misiones registradas aún")
                    else:
                        st.write(f"**Total: {len(missions)} misiones**")
                        
                        # Crear tabla de misiones
                        import pandas as pd
                        mission_data = []
                        for m in missions:
                            mission_data.append({
                                "ID": m['mission_id'][:8] + "...",
                                "Zona": m['geo_zone'],
                                "Supervivencia": f"{m['kpis']['kpi_survival_rate']:.1f}%",
                                "Fuegos": m['kpis']['fires_extinguished'],
                                "Pasos": m['kpis']['steps_taken'],
                                "Éxito": "✅" if m['kpis']['mission_success'] else "❌",
                                "Fecha": m['timestamp'][:19]
                            })
                        
                        df = pd.DataFrame(mission_data)
                        st.dataframe(df, use_container_width=True, height=400)
                        
                        # Selector de misión para detalles
                        st.markdown("---")
                        st.markdown("#### 📋 Detalles de Misión")
                        
                        mission_options = {f"{m['mission_id'][:8]}... - {m['geo_zone']} ({m['kpis']['kpi_survival_rate']:.1f}%)": m['mission_id'] 
                                         for m in missions}
                        
                        selected_option = st.selectbox("Seleccionar misión", list(mission_options.keys()))
                        
                        if selected_option:
                            selected_id = mission_options[selected_option]
                            mission = st.session_state.mission_logger.get_mission_by_id(selected_id)
                            
                            if mission:
                                # Mostrar detalles
                                col_det1, col_det2, col_det3, col_det4 = st.columns(4)
                                
                                with col_det1:
                                    st.metric("Supervivencia", f"{mission['kpis']['kpi_survival_rate']:.1f}%")
                                with col_det2:
                                    st.metric("Fuegos Apagados", mission['kpis']['fires_extinguished'])
                                with col_det3:
                                    st.metric("Agua Usada", mission['kpis']['water_consumed'])
                                with col_det4:
                                    st.metric("Pasos", mission['kpis']['steps_taken'])
                                
                                # Configuración
                                with st.expander("⚙️ Configuración"):
                                    st.json(mission['configuration'])
                                
                                # Estadísticas por agente
                                if mission.get('agent_stats'):
                                    with st.expander("🤖 Estadísticas por Agente"):
                                        for agent_id, stats in mission['agent_stats'].items():
                                            st.markdown(f"**{agent_id}**")
                                            col_ag1, col_ag2 = st.columns(2)
                                            with col_ag1:
                                                st.write(f"Decisiones: {stats['decisions']}")
                                                st.write(f"Confianza promedio: {stats['avg_confidence']:.2f}")
                                            with col_ag2:
                                                st.write(f"Distancia promedio: {stats['avg_distance']:.2f}")
                                                if stats.get('actions'):
                                                    st.write("Acciones:")
                                                    for action, count in stats['actions'].items():
                                                        st.write(f"  • {action}: {count}")
                                            st.markdown("---")
                                
                                # XAI Log
                                if mission.get('xai_log') and len(mission['xai_log']) > 0:
                                    with st.expander(f"🧠 Historial XAI ({len(mission['xai_log'])} decisiones)"):
                                        xai_df = pd.DataFrame([
                                            {
                                                "Paso": d['step'],
                                                "Agente": d['agent_id'],
                                                "Acción": d['action_name'],
                                                "Distancia": f"{d['distance_to_target']:.1f}",
                                                "Confianza": f"{d['confidence']*100:.0f}%"
                                            }
                                            for d in mission['xai_log']
                                        ])
                                        st.dataframe(xai_df, use_container_width=True, height=300)
                
                with hist_tab2:
                    st.markdown("#### 🏆 Mejores Misiones (por Supervivencia)")
                    
                    # Control de cantidad
                    top_limit = st.slider("Número de misiones", 5, 20, 10, key="top_limit")
                    
                    # Obtener top misiones
                    top_missions = st.session_state.mission_logger.get_top_missions(top_limit)
                    
                    if not top_missions:
                        st.info("No hay misiones registradas aún")
                    else:
                        st.write(f"**Top {len(top_missions)} misiones**")
                        
                        # Gráfico de ranking
                        fig_ranking = go.Figure()
                        
                        fig_ranking.add_trace(go.Bar(
                            x=[f"{m['geo_zone']} ({m['mission_id'][:6]})" for m in top_missions],
                            y=[m['kpis']['kpi_survival_rate'] for m in top_missions],
                            marker_color=['#28a745' if m['kpis']['mission_success'] else '#ffc107' 
                                        for m in top_missions],
                            text=[f"{m['kpis']['kpi_survival_rate']:.1f}%" for m in top_missions],
                            textposition='outside'
                        ))
                        
                        fig_ranking.update_layout(
                            title="Top Misiones por Tasa de Supervivencia",
                            xaxis_title="Misión",
                            yaxis_title="Tasa de Supervivencia (%)",
                            height=500,
                            showlegend=False
                        )
                        
                        st.plotly_chart(fig_ranking, use_container_width=True)
                        
                        # Tabla
                        top_data = []
                        for idx, m in enumerate(top_missions, 1):
                            top_data.append({
                                "#": idx,
                                "ID": m['mission_id'][:8] + "...",
                                "Zona": m['geo_zone'],
                                "Supervivencia": f"{m['kpis']['kpi_survival_rate']:.1f}%",
                                "Fuegos": m['kpis']['fires_extinguished'],
                                "Pasos": m['kpis']['steps_taken'],
                                "Fecha": m['timestamp'][:19]
                            })
                        
                        df_top = pd.DataFrame(top_data)
                        st.dataframe(df_top, use_container_width=True, height=400)
                
                with hist_tab3:
                    st.markdown("#### 🔍 Buscar Misiones")
                    
                    # Filtros
                    col_filt1, col_filt2 = st.columns(2)
                    
                    with col_filt1:
                        # Obtener zonas únicas
                        all_missions = st.session_state.mission_logger.get_recent_missions(100)
                        zones = list(set(m['geo_zone'] for m in all_missions))
                        selected_zone = st.selectbox("Filtrar por zona", ["Todas"] + sorted(zones))
                    
                    with col_filt2:
                        min_survival = st.slider("Supervivencia mínima (%)", 0, 100, 0)
                    
                    # Buscar
                    if st.button("🔍 Buscar", use_container_width=True):
                        if selected_zone == "Todas":
                            results = all_missions
                        else:
                            results = st.session_state.mission_logger.get_missions_by_zone(selected_zone, 50)
                        
                        # Filtrar por supervivencia
                        results = [m for m in results 
                                 if m['kpis']['kpi_survival_rate'] >= min_survival]
                        
                        st.write(f"**Resultados: {len(results)} misiones**")
                        
                        if results:
                            search_data = []
                            for m in results:
                                search_data.append({
                                    "ID": m['mission_id'][:8] + "...",
                                    "Zona": m['geo_zone'],
                                    "Supervivencia": f"{m['kpis']['kpi_survival_rate']:.1f}%",
                                    "Éxito": "✅" if m['kpis']['mission_success'] else "❌",
                                    "Fecha": m['timestamp'][:19]
                                })
                            
                            df_search = pd.DataFrame(search_data)
                            st.dataframe(df_search, use_container_width=True, height=400)
                        else:
                            st.info("No se encontraron misiones con esos criterios")
                
                with hist_tab4:
                    st.markdown("#### 📊 Estadísticas Globales")
                    
                    # Obtener estadísticas
                    stats = st.session_state.mission_logger.get_statistics()
                    
                    if not stats:
                        st.info("No hay datos suficientes para estadísticas")
                    else:
                        # Métricas principales
                        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                        
                        with col_stat1:
                            st.metric("Total Misiones", stats.get('total_missions', 0))
                        with col_stat2:
                            st.metric("Supervivencia Promedio", f"{stats.get('avg_survival_rate', 0):.1f}%")
                        with col_stat3:
                            st.metric("Mejor Resultado", f"{stats.get('max_survival_rate', 0):.1f}%")
                        with col_stat4:
                            st.metric("Pasos Promedio", f"{stats.get('avg_steps', 0):.0f}")
                        
                        st.markdown("---")
                        
                        # Gráficos de tendencias
                        recent_for_trend = st.session_state.mission_logger.get_recent_missions(50)
                        
                        if recent_for_trend:
                            # Timeline de supervivencia
                            fig_trend = go.Figure()
                            
                            fig_trend.add_trace(go.Scatter(
                                x=list(range(len(recent_for_trend))),
                                y=[m['kpis']['kpi_survival_rate'] for m in reversed(recent_for_trend)],
                                mode='lines+markers',
                                name='Tasa de Supervivencia',
                                line=dict(color='#667eea', width=2),
                                marker=dict(size=8)
                            ))
                            
                            fig_trend.update_layout(
                                title="Tendencia de Supervivencia (Últimas 50 Misiones)",
                                xaxis_title="Misión (orden cronológico)",
                                yaxis_title="Tasa de Supervivencia (%)",
                                height=400
                            )
                            
                            st.plotly_chart(fig_trend, use_container_width=True)
                            
                            # Distribución por zona
                            zones_count = {}
                            zones_avg = {}
                            for m in recent_for_trend:
                                zone = m['geo_zone']
                                zones_count[zone] = zones_count.get(zone, 0) + 1
                                if zone not in zones_avg:
                                    zones_avg[zone] = []
                                zones_avg[zone].append(m['kpis']['kpi_survival_rate'])
                            
                            col_chart1, col_chart2 = st.columns(2)
                            
                            with col_chart1:
                                fig_zones = go.Figure(data=[go.Pie(
                                    labels=list(zones_count.keys()),
                                    values=list(zones_count.values()),
                                    hole=0.4
                                )])
                                fig_zones.update_layout(
                                    title="Distribución por Zona",
                                    height=400
                                )
                                st.plotly_chart(fig_zones, use_container_width=True)
                            
                            with col_chart2:
                                fig_avg_zones = go.Figure(data=[go.Bar(
                                    x=list(zones_avg.keys()),
                                    y=[np.mean(v) for v in zones_avg.values()],
                                    marker_color='#764ba2'
                                )])
                                fig_avg_zones.update_layout(
                                    title="Supervivencia Promedio por Zona",
                                    yaxis_title="Supervivencia (%)",
                                    height=400
                                )
                                st.plotly_chart(fig_avg_zones, use_container_width=True)
                        
                        # Botón para limpiar base de datos
                        st.markdown("---")
                        st.markdown("#### ⚠️ Acciones Administrativas")
                        
                        col_admin1, col_admin2 = st.columns([3, 1])
                        
                        with col_admin2:
                            if st.button("🗑️ Limpiar Base de Datos", type="secondary"):
                                if st.session_state.mission_logger.clear_all_missions():
                                    st.success("✅ Base de datos limpiada")
                                    st.rerun()
                                else:
                                    st.error("❌ Error limpiando base de datos")
    
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
