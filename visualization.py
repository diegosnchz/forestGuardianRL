"""
Módulo de visualización para Forest Guardian RL
Proporciona funciones para crear visualizaciones interactivas con Plotly
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Tuple

# Mapeo de colores para los estados del grid
CELL_COLORS = {
    0: '#ffffff',   # Vacío
    1: '#00aa00',   # Árbol
    2: '#ff0000',   # Fuego
    3: '#0066ff',   # Agente 1 (Azul)
    4: '#ff9900'    # Agente 2 (Naranja)
}

CELL_LABELS = {
    0: 'Vacío',
    1: 'Árbol',
    2: 'Fuego',
    3: 'Dron Azul',
    4: 'Dron Naranja'
}

def create_heatmap_figure(
    grid: np.ndarray,
    step: int,
    title: str = "Visualización del Bosque"
) -> go.Figure:
    """
    Crea un heatmap interactivo del estado actual del bosque
    
    Args:
        grid: Array numpy con el estado actual (0-4)
        step: Número del paso de simulación
        title: Título de la visualización
    
    Returns:
        Figura Plotly lista para mostrar
    """
    custom_colorscale = [
        [0.0, CELL_COLORS[0]],
        [0.25, CELL_COLORS[1]],
        [0.5, CELL_COLORS[2]],
        [0.75, CELL_COLORS[3]],
        [1.0, CELL_COLORS[4]]
    ]
    
    fig = go.Figure(
        data=go.Heatmap(
            z=grid,
            colorscale=custom_colorscale,
            zmin=0,
            zmax=4,
            showscale=False,
            hovertemplate='Posición: (%{x}, %{y})<br>Estado: %{z}<extra></extra>',
            colorbar=dict(
                thickness=15,
                len=0.7,
                tickvals=[0, 1, 2, 3, 4],
                ticktext=['Vacío', 'Árbol', 'Fuego', 'D.Azul', 'D.Naranja']
            )
        )
    )
    
    fig.update_layout(
        title=f"{title} - Paso {step}",
        xaxis_title="Columna",
        yaxis_title="Fila",
        height=500,
        hovermode='closest',
        xaxis=dict(scaleanchor="y", scaleratio=1, side="bottom"),
        yaxis=dict(scaleanchor="x", scaleratio=1),
        plot_bgcolor='#f0f0f0',
        font=dict(family="Arial", size=12),
        margin=dict(l=80, r=80, t=100, b=80)
    )
    
    return fig

def create_metrics_timeseries(
    metrics_history: Dict[str, List],
    include_density: bool = True
) -> go.Figure:
    """
    Crea gráficos de series temporales de métricas
    
    Args:
        metrics_history: Diccionario con histórico de métricas
        include_density: Si incluir gráfico de densidad
    
    Returns:
        Figura Plotly con subplots
    """
    if not metrics_history['step']:
        return None
    
    n_rows = 2 if include_density else 1
    n_cols = 2
    
    fig = make_subplots(
        rows=n_rows, cols=n_cols,
        subplot_titles=(
            "Fuegos Activos",
            "Árboles Salvados (%)",
            "Agua Consumida",
            "Densidad de Bosque"
        ) if include_density else (
            "Fuegos Activos",
            "Árboles Salvados (%)"
        ),
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "scatter"}, {"type": "scatter"}]
        ] if include_density else [
            [{"type": "scatter"}, {"type": "scatter"}]
        ]
    )
    
    steps = metrics_history['step']
    
    # Gráfico 1: Fuegos activos (rojo)
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=metrics_history['active_fires'],
            mode='lines+markers',
            name='Fuegos',
            line=dict(color='#ff0000', width=2),
            marker=dict(size=6)
        ),
        row=1, col=1
    )
    
    # Gráfico 2: Árboles salvados (verde)
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=metrics_history['saved_trees'],
            mode='lines+markers',
            name='% Árboles',
            line=dict(color='#00aa00', width=2),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(0, 170, 0, 0.1)'
        ),
        row=1, col=2
    )
    
    if include_density:
        # Gráfico 3: Agua consumida (azul)
        fig.add_trace(
            go.Scatter(
                x=steps,
                y=metrics_history['water_used'],
                mode='lines',
                name='Agua',
                line=dict(color='#0066ff', width=2),
                fill='tozeroy',
                fillcolor='rgba(0, 102, 255, 0.1)'
            ),
            row=2, col=1
        )
        
        # Gráfico 4: Densidad (púrpura)
        if metrics_history['saved_trees']:
            max_trees = max(metrics_history['saved_trees']) if metrics_history['saved_trees'] else 100
            density = [t / max_trees for t in metrics_history['saved_trees']]
            fig.add_trace(
                go.Scatter(
                    x=steps,
                    y=density,
                    mode='lines+markers',
                    name='Densidad',
                    line=dict(color='#764ba2', width=2),
                    marker=dict(size=5)
                ),
                row=2, col=2
            )
    
    # Actualizar axes
    fig.update_xaxes(title_text="Paso", row=1, col=1)
    fig.update_xaxes(title_text="Paso", row=1, col=2)
    fig.update_yaxes(title_text="Conteo", row=1, col=1)
    fig.update_yaxes(title_text="Porcentaje (%)", row=1, col=2)
    
    if include_density:
        fig.update_xaxes(title_text="Paso", row=2, col=1)
        fig.update_xaxes(title_text="Paso", row=2, col=2)
        fig.update_yaxes(title_text="Unidades", row=2, col=1)
        fig.update_yaxes(title_text="Ratio", row=2, col=2)
    
    fig.update_layout(
        height=600 if include_density else 400,
        showlegend=True,
        hovermode='x unified',
        plot_bgcolor='#f9f9f9',
        font=dict(family="Arial", size=11),
        margin=dict(l=80, r=80, t=100, b=80)
    )
    
    return fig

def create_agent_positions_chart(
    agents_positions_history: List[List[Tuple[int, int]]],
    grid_size: int
) -> go.Figure:
    """
    Crea un gráfico de trayectoria de agentes
    
    Args:
        agents_positions_history: Lista de posiciones de agentes en cada paso
        grid_size: Tamaño de la cuadrícula
    
    Returns:
        Figura Plotly
    """
    if not agents_positions_history:
        return None
    
    fig = go.Figure()
    
    # Trayectoria del Dron 1 (Azul)
    agent1_x = [pos[0][1] for pos in agents_positions_history]  # columna
    agent1_y = [pos[0][0] for pos in agents_positions_history]  # fila
    
    fig.add_trace(go.Scatter(
        x=agent1_x, y=agent1_y,
        mode='lines+markers',
        name='Dron Azul (Proximidad)',
        line=dict(color='#0066ff', width=2),
        marker=dict(size=5)
    ))
    
    # Trayectoria del Dron 2 (Naranja) si existe
    if len(agents_positions_history[0]) > 1:
        agent2_x = [pos[1][1] for pos in agents_positions_history]
        agent2_y = [pos[1][0] for pos in agents_positions_history]
        
        fig.add_trace(go.Scatter(
            x=agent2_x, y=agent2_y,
            mode='lines+markers',
            name='Dron Naranja (Contención)',
            line=dict(color='#ff9900', width=2),
            marker=dict(size=5)
        ))
    
    fig.update_layout(
        title="Trayectorias de Drones",
        xaxis_title="Columna",
        yaxis_title="Fila",
        height=500,
        hovermode='closest',
        xaxis=dict(scaleanchor="y", scaleratio=1, range=[-0.5, grid_size-0.5]),
        yaxis=dict(scaleanchor="x", scaleratio=1, range=[-0.5, grid_size-0.5]),
        plot_bgcolor='#f0f0f0',
        font=dict(family="Arial", size=12),
        margin=dict(l=80, r=80, t=100, b=80)
    )
    
    return fig

def create_summary_metrics(
    steps: int,
    trees_saved_pct: float,
    fires_extinguished: int,
    water_used: int,
    initial_trees: int,
    final_trees: int
) -> Dict:
    """
    Crea un resumen de métricas principales
    
    Args:
        steps: Número de pasos ejecutados
        trees_saved_pct: Porcentaje de árboles salvados
        fires_extinguished: Número de fuegos extintos
        water_used: Unidades de agua consumidas
        initial_trees: Número inicial de árboles
        final_trees: Número final de árboles
    
    Returns:
        Diccionario con métricas resumidas
    """
    return {
        'duration': f"{steps} pasos",
        'trees_saved': f"{trees_saved_pct:.1f}%",
        'trees_lost': f"{initial_trees - final_trees}",
        'fires_extinguished': fires_extinguished,
        'water_used': water_used,
        'efficiency': f"{fires_extinguished / max(steps, 1) * 100:.2f} focos/paso"
    }
