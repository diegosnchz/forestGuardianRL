"""
Módulo de visualización para XAI (Explainable AI).

Proporciona funciones para visualizar mapas de atención, importancia
de atributos, y análisis de decisiones de agentes.

Autor: Forest Guardian RL Team
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any, Tuple, Optional
from xai_explainer import AgentDecision
import pandas as pd


def create_attention_heatmap(attention_map: np.ndarray,
                            grid_state: np.ndarray,
                            agent_position: Tuple[int, int],
                            title: str = "Mapa de Atención") -> plt.Figure:
    """
    Crea un heatmap de atención superpuesto sobre el grid.
    
    Args:
        attention_map: Matriz de atención (0-1)
        grid_state: Estado del grid
        agent_position: Posición del agente (r, c)
        title: Título del gráfico
        
    Returns:
        Figura de matplotlib
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Crear mapa de colores personalizado para atención
    colors = ['#ffffff', '#ffff99', '#ff9999', '#ff0000']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('attention', colors, N=n_bins)
    
    # Mostrar grid base
    grid_display = np.zeros_like(grid_state, dtype=float)
    grid_display[grid_state == 1] = 0.3  # Árboles en verde claro
    grid_display[grid_state == 2] = 0.6  # Fuegos en rojo claro
    
    # Capa base (grid)
    ax.imshow(grid_display, cmap='Greens', alpha=0.3, vmin=0, vmax=1)
    
    # Capa de atención
    im = ax.imshow(attention_map, cmap=cmap, alpha=0.7, vmin=0, vmax=1)
    
    # Marcar posición del agente
    r, c = agent_position
    ax.plot(c, r, 'b*', markersize=30, markeredgecolor='white', markeredgewidth=2)
    
    # Marcar fuegos
    fires = np.argwhere(grid_state == 2)
    if len(fires) > 0:
        ax.scatter(fires[:, 1], fires[:, 0], c='red', s=200, 
                  marker='X', edgecolors='black', linewidths=2, label='Fuegos')
    
    # Marcar árboles
    trees = np.argwhere(grid_state == 1)
    if len(trees) > 0:
        ax.scatter(trees[:, 1], trees[:, 0], c='green', s=50, 
                  marker='o', alpha=0.4, label='Árboles')
    
    # Configuración
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel('Columna', fontsize=12)
    ax.set_ylabel('Fila', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Nivel de Atención', fontsize=12)
    
    # Leyenda
    legend_elements = [
        mpatches.Patch(facecolor='blue', label='Agente'),
        mpatches.Patch(facecolor='red', label='Fuego'),
        mpatches.Patch(facecolor='green', label='Árbol', alpha=0.4),
        mpatches.Patch(facecolor='yellow', label='Atención Alta', alpha=0.7),
        mpatches.Patch(facecolor='white', label='Atención Baja', alpha=0.7)
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.15, 1))
    
    plt.tight_layout()
    return fig


def create_importance_chart(importance_scores: Dict[str, float],
                           title: str = "Importancia de Atributos") -> go.Figure:
    """
    Crea gráfico de barras de importancia de atributos con Plotly.
    
    Args:
        importance_scores: Diccionario con scores de importancia
        title: Título del gráfico
        
    Returns:
        Figura de Plotly
    """
    # Ordenar por importancia
    sorted_items = sorted(importance_scores.items(), key=lambda x: x[1], reverse=True)
    factors = [item[0].replace('_', ' ').title() for item in sorted_items]
    scores = [item[1] * 100 for item in sorted_items]
    
    # Crear gráfico
    fig = go.Figure()
    
    # Colores según importancia
    colors = ['#ff0000' if s > 80 else '#ff9900' if s > 60 else '#ffcc00' if s > 40 else '#99cc00'
              for s in scores]
    
    fig.add_trace(go.Bar(
        y=factors,
        x=scores,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(0,0,0,0.5)', width=1)
        ),
        text=[f"{s:.1f}%" for s in scores],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Importancia: %{x:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=18, family='Arial Black')
        ),
        xaxis_title="Importancia (%)",
        yaxis_title="Factor",
        xaxis=dict(range=[0, 110]),
        height=max(300, len(factors) * 50),
        showlegend=False,
        plot_bgcolor='rgba(240, 240, 240, 0.5)',
        font=dict(size=12)
    )
    
    return fig


def create_decision_timeline(decisions: List[AgentDecision],
                            metric: str = 'distance_to_target') -> go.Figure:
    """
    Crea línea de tiempo de decisiones mostrando una métrica.
    
    Args:
        decisions: Lista de decisiones
        metric: Métrica a visualizar ('distance_to_target', 'confidence', etc.)
        
    Returns:
        Figura de Plotly
    """
    if not decisions:
        return go.Figure()
    
    # Extraer datos
    timestamps = [d.timestamp for d in decisions]
    metric_values = [getattr(d, metric, 0) for d in decisions]
    actions = [d.action_name for d in decisions]
    
    # Crear gráfico
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=list(range(len(timestamps))),
        y=metric_values,
        mode='lines+markers',
        name=metric.replace('_', ' ').title(),
        line=dict(color='#667eea', width=3),
        marker=dict(size=10, color='#764ba2'),
        hovertemplate='<b>Step %{x}</b><br>' +
                      f'{metric.replace("_", " ").title()}: %{{y:.2f}}<br>' +
                      'Acción: %{text}<extra></extra>',
        text=actions
    ))
    
    fig.update_layout(
        title=f"Evolución de {metric.replace('_', ' ').title()}",
        xaxis_title="Paso de Decisión",
        yaxis_title=metric.replace('_', ' ').title(),
        hovermode='x',
        height=400,
        plot_bgcolor='rgba(240, 240, 240, 0.5)'
    )
    
    return fig


def create_action_distribution_chart(decisions: List[AgentDecision]) -> go.Figure:
    """
    Crea gráfico circular de distribución de acciones.
    
    Args:
        decisions: Lista de decisiones
        
    Returns:
        Figura de Plotly
    """
    if not decisions:
        return go.Figure()
    
    # Contar acciones
    action_counts = {}
    for d in decisions:
        action_counts[d.action_name] = action_counts.get(d.action_name, 0) + 1
    
    labels = list(action_counts.keys())
    values = list(action_counts.values())
    
    # Colores personalizados
    colors = px.colors.qualitative.Set3
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=colors),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title="Distribución de Acciones",
        height=500,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05)
    )
    
    return fig


def create_confidence_vs_distance_scatter(decisions: List[AgentDecision]) -> go.Figure:
    """
    Crea scatter plot de confianza vs distancia al objetivo.
    
    Args:
        decisions: Lista de decisiones
        
    Returns:
        Figura de Plotly
    """
    if not decisions:
        return go.Figure()
    
    confidences = [d.confidence for d in decisions]
    distances = [d.distance_to_target for d in decisions]
    actions = [d.action_name for d in decisions]
    steps = list(range(len(decisions)))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=distances,
        y=confidences,
        mode='markers',
        marker=dict(
            size=12,
            color=steps,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Paso"),
            line=dict(width=1, color='white')
        ),
        text=actions,
        hovertemplate='<b>%{text}</b><br>' +
                      'Distancia: %{x:.1f}<br>' +
                      'Confianza: %{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Confianza vs Distancia al Objetivo",
        xaxis_title="Distancia al Objetivo (celdas)",
        yaxis_title="Confianza de la Decisión",
        height=500,
        plot_bgcolor='rgba(240, 240, 240, 0.5)'
    )
    
    return fig


def create_tactical_reasoning_display(decision: AgentDecision) -> str:
    """
    Crea un display HTML formateado del razonamiento táctico.
    
    Args:
        decision: Decisión a mostrar
        
    Returns:
        String HTML
    """
    html = f"""
    <div style='border: 2px solid #667eea; border-radius: 10px; padding: 20px; 
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                margin: 10px 0;'>
        <h3 style='color: #667eea; margin-top: 0;'>
            🎯 {decision.agent_role.upper()} - {decision.action_name}
        </h3>
        
        <div style='background: white; padding: 15px; border-radius: 5px; margin: 10px 0;'>
            <h4 style='color: #764ba2; margin-top: 0;'>📊 Explicación</h4>
            <pre style='white-space: pre-wrap; font-family: Arial; font-size: 14px; line-height: 1.6;'>
{decision.explanation}
            </pre>
        </div>
        
        <div style='background: white; padding: 15px; border-radius: 5px; margin: 10px 0;'>
            <h4 style='color: #764ba2; margin-top: 0;'>⚔️ Razonamiento Táctico</h4>
            <pre style='white-space: pre-wrap; font-family: Arial; font-size: 14px; line-height: 1.6;'>
{decision.tactical_reasoning}
            </pre>
        </div>
        
        <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 15px;'>
            <div style='background: #667eea; color: white; padding: 10px; border-radius: 5px; text-align: center;'>
                <div style='font-size: 24px; font-weight: bold;'>{decision.distance_to_target:.1f}</div>
                <div style='font-size: 12px;'>Distancia al Objetivo</div>
            </div>
            <div style='background: #764ba2; color: white; padding: 10px; border-radius: 5px; text-align: center;'>
                <div style='font-size: 24px; font-weight: bold;'>{decision.confidence*100:.0f}%</div>
                <div style='font-size: 12px;'>Confianza</div>
            </div>
            <div style='background: #f093fb; color: white; padding: 10px; border-radius: 5px; text-align: center;'>
                <div style='font-size: 24px; font-weight: bold;'>{decision.water_level}</div>
                <div style='font-size: 12px;'>Agua Restante</div>
            </div>
        </div>
    </div>
    """
    return html


def create_multi_agent_comparison(decisions_dict: Dict[str, List[AgentDecision]]) -> go.Figure:
    """
    Crea comparación de múltiples agentes en un solo gráfico.
    
    Args:
        decisions_dict: Diccionario {agent_id: [decisions]}
        
    Returns:
        Figura de Plotly
    """
    fig = go.Figure()
    
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe']
    
    for idx, (agent_id, decisions) in enumerate(decisions_dict.items()):
        if not decisions:
            continue
        
        steps = list(range(len(decisions)))
        distances = [d.distance_to_target for d in decisions]
        
        fig.add_trace(go.Scatter(
            x=steps,
            y=distances,
            mode='lines+markers',
            name=agent_id,
            line=dict(color=colors[idx % len(colors)], width=2),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title="Comparación Multi-Agente: Distancia al Objetivo",
        xaxis_title="Paso de Decisión",
        yaxis_title="Distancia al Objetivo (celdas)",
        hovermode='x unified',
        height=500,
        plot_bgcolor='rgba(240, 240, 240, 0.5)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_importance_evolution_heatmap(decisions: List[AgentDecision]) -> go.Figure:
    """
    Crea heatmap de evolución de importancia de factores a lo largo del tiempo.
    
    Args:
        decisions: Lista de decisiones
        
    Returns:
        Figura de Plotly
    """
    if not decisions:
        return go.Figure()
    
    # Extraer todos los factores únicos
    all_factors = set()
    for d in decisions:
        all_factors.update(d.importance_scores.keys())
    
    factors = sorted(list(all_factors))
    
    # Crear matriz
    matrix = []
    for factor in factors:
        row = [d.importance_scores.get(factor, 0) * 100 for d in decisions]
        matrix.append(row)
    
    # Crear labels bonitos
    factor_labels = [f.replace('_', ' ').title() for f in factors]
    step_labels = [f"Step {i}" for i in range(len(decisions))]
    
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=step_labels,
        y=factor_labels,
        colorscale='RdYlGn',
        colorbar=dict(title="Importancia (%)"),
        hovertemplate='<b>%{y}</b><br>%{x}<br>Importancia: %{z:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="Evolución de Importancia de Factores",
        xaxis_title="Paso de Decisión",
        yaxis_title="Factor",
        height=max(400, len(factors) * 40)
    )
    
    return fig


def export_decision_report(decision: AgentDecision, filepath: str):
    """
    Exporta un reporte completo de una decisión como HTML.
    
    Args:
        decision: Decisión a exportar
        filepath: Ruta del archivo de salida
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>XAI Report - {decision.agent_id}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 20px;
            }}
            .section {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .metric {{
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 15px 25px;
                border-radius: 5px;
                margin: 5px;
            }}
            pre {{
                background: #f8f8f8;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #667eea;
                overflow-x: auto;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 XAI Decision Report</h1>
            <h2>{decision.agent_id} - {decision.agent_role.upper()}</h2>
            <p>Timestamp: {decision.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="section">
            <h3>📊 Decision Summary</h3>
            <div class="metric">
                <div style="font-size: 24px; font-weight: bold;">{decision.action_name}</div>
                <div>Action Taken</div>
            </div>
            <div class="metric">
                <div style="font-size: 24px; font-weight: bold;">({decision.position[0]}, {decision.position[1]})</div>
                <div>Position</div>
            </div>
            <div class="metric">
                <div style="font-size: 24px; font-weight: bold;">{decision.distance_to_target:.1f}</div>
                <div>Distance to Target</div>
            </div>
            <div class="metric">
                <div style="font-size: 24px; font-weight: bold;">{decision.confidence*100:.0f}%</div>
                <div>Confidence</div>
            </div>
        </div>
        
        <div class="section">
            <h3>💡 Explanation</h3>
            <pre>{decision.explanation}</pre>
        </div>
        
        <div class="section">
            <h3>⚔️ Tactical Reasoning</h3>
            <pre>{decision.tactical_reasoning}</pre>
        </div>
        
        <div class="section">
            <h3>📈 Importance Scores</h3>
            <ul>
            {"".join([f"<li><b>{k.replace('_', ' ').title()}:</b> {v*100:.1f}%</li>" 
                     for k, v in sorted(decision.importance_scores.items(), 
                                       key=lambda x: x[1], reverse=True)])}
            </ul>
        </div>
        
        <div class="section">
            <h3>🔄 Alternative Actions</h3>
            <ul>
            {"".join([f"<li><b>{alt['name']}:</b> {alt['reason']} (Score: {alt['score']*100:.0f}%)</li>" 
                     for alt in decision.alternative_actions])}
            </ul>
        </div>
    </body>
    </html>
    """
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
