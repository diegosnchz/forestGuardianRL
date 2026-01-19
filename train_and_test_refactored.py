"""
Módulo de entrenamiento y pruebas para Forest Guardian RL
Refactorizado para integración con Streamlit
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import numpy as np
import time
import base64
from typing import List, Tuple, Dict, Callable, Optional
from forest_fire_env import ForestFireEnv
from metrics import MetricsCalculator, MissionMetrics
import json

# ============================================================================
# AGENTES TÁCTICOS
# ============================================================================

class TerminatorAgent:
    """Agente inteligente para combatir incendios"""
    
    def __init__(self, role: str = "nearest"):
        """
        Inicializa el agente
        
        Args:
            role: "nearest" para proximidad, "farthest" para contención periférica
        """
        self.role = role

    def decide(self, obs: np.ndarray, pos: Tuple[int, int]) -> int:
        """
        Decide la acción del agente basada en el estado observado
        
        Args:
            obs: Grid de observación
            pos: Posición actual del agente (row, col)
        
        Returns:
            Acción (0-6): arriba, abajo, izquierda, derecha, idle, apagar, explorar
        """
        r, c = pos
        fires = np.argwhere(obs == 2)
        
        # Si no hay fuegos, explorar
        if len(fires) == 0:
            return 6
        
        # Calcular distancias
        dists = [abs(r - fr) + abs(c - fc) for fr, fc in fires]
        
        # Seleccionar objetivo según rol
        if self.role == "nearest":
            target_idx = np.argmin(dists)
        else:  # farthest
            if len(fires) > 1:
                target_idx = np.argmax(dists)
            else:
                target_idx = np.argmin(dists)

        target_r, target_c = fires[target_idx]
        dist = dists[target_idx]
        
        # Si el fuego está adyacente, apagar
        if dist <= 1:
            return 5
        
        # Mover hacia el objetivo
        diff_r = target_r - r
        diff_c = target_c - c
        
        if abs(diff_r) > abs(diff_c):
            return 1 if diff_r > 0 else 0  # Abajo o Arriba
        else:
            return 3 if diff_c > 0 else 2  # Derecha o Izquierda

# ============================================================================
# EJECUTOR DE MISIONES
# ============================================================================

class MissionExecutor:
    """Ejecuta una misión completa de Forest Guardian"""
    
    def __init__(self, env: ForestFireEnv, num_agents: int):
        """
        Inicializa el ejecutor
        
        Args:
            env: Instancia del entorno
            num_agents: Número de drones
        """
        self.env = env
        self.num_agents = num_agents
        self.agents = self._create_agents()
        self.frames = []
        self.metrics_calc = None
    
    def _create_agents(self) -> List[TerminatorAgent]:
        """Crea los agentes tácticos"""
        roles = ["nearest", "farthest", "nearest"]
        return [TerminatorAgent(role=roles[i]) for i in range(self.num_agents)]
    
    def execute(
        self,
        max_steps: int = 100,
        progress_callback: Optional[Callable] = None,
        metrics_callback: Optional[Callable] = None
    ) -> Tuple[List[np.ndarray], MissionMetrics]:
        """
        Ejecuta la misión completa
        
        Args:
            max_steps: Máximo número de pasos
            progress_callback: Función para reportar progreso
            metrics_callback: Función para actualizar métricas en tiempo real
        
        Returns:
            Tupla (frames, métricas finales)
        """
        # Reset
        obs, _ = self.env.reset()
        self.frames = []
        self.frames.append(obs.copy())
        
        # Inicializar calculador de métricas
        self.metrics_calc = MetricsCalculator(
            obs.copy(),
            {
                'grid_size': self.env.grid_size,
                'fire_spread_prob': self.env.fire_spread_prob,
                'initial_trees': self.env.initial_trees,
                'num_agents': self.num_agents
            }
        )
        
        done = False
        step = 0
        
        while not done and step < max_steps:
            # Obtener decisiones
            actions = []
            for i, agent in enumerate(self.agents):
                action = agent.decide(obs, self.env.agent_positions[i])
                actions.append(action)
            
            # Ejecutar paso
            obs, _, terminated, _, _ = self.env.step(actions)
            self.frames.append(obs.copy())
            
            # Calcular métricas del paso
            step_metrics = self.metrics_calc.calculate_step_metrics(
                obs, step, self.env.water_tanks
            )
            
            # Reportar progreso
            if metrics_callback:
                metrics_callback(step_metrics)
            
            if progress_callback:
                progress_callback(step, max_steps)
            
            done = terminated
            step += 1
        
        # Obtener métricas finales
        final_metrics = self.metrics_calc.get_final_metrics(obs, step)
        
        return self.frames, final_metrics

# ============================================================================
# GENERADOR DE REPORTES
# ============================================================================

def generate_tactical_report(
    gif_path: str,
    stats: Dict,
    mission_id: str = None
) -> str:
    """
    Genera un dashboard HTML con el reporte de la misión
    
    Args:
        gif_path: Ruta del GIF generado
        stats: Diccionario con estadísticas
        mission_id: ID de la misión
    
    Returns:
        Ruta del archivo HTML generado
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    if not mission_id:
        mission_id = int(time.time())
    
    # Convertir GIF a base64
    try:
        with open(gif_path, "rb") as gif_file:
            encoded_string = base64.b64encode(gif_file.read()).decode('utf-8')
        gif_tag = f'<img src="data:image/gif;base64,{encoded_string}" alt="Simulación de Misión">'
    except:
        gif_tag = f'<p style="color: red;">Error al cargar GIF desde {gif_path}</p>'

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>REPORTE DE MISIÓN - FOREST GUARDIAN</title>
        <style>
            body {{ font-family: 'Courier New', monospace; background-color: #1a1a1a; color: #00ff41; margin: 0; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: #000; border: 2px solid #00ff41; padding: 20px; box-shadow: 0 0 20px rgba(0, 255, 65, 0.2); }}
            h1 {{ border-bottom: 1px solid #00ff41; padding-bottom: 10px; text-transform: uppercase; letter-spacing: 2px; }}
            h2 {{ color: #00ff41; margin-top: 20px; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
            .video-box {{ border: 1px solid #333; text-align: center; padding: 10px; background: #111; }}
            .stats-box {{ border: 1px solid #333; padding: 15px; background: #0a0a0a; }}
            .metric {{ margin-bottom: 15px; border-left: 3px solid #00ff41; padding-left: 10px; }}
            .label {{ font-size: 0.9em; color: #888; }}
            .value {{ font-size: 1.3em; font-weight: bold; color: #00ff41; }}
            .status-bar {{ width: 100%; background: #333; height: 15px; margin-top: 5px; border-radius: 3px; overflow: hidden; }}
            .fill {{ height: 100%; background: #00ff41; border-radius: 3px; transition: width 0.3s; }}
            .agent-info {{ margin-top: 20px; border-top: 1px dashed #444; padding-top: 10px; }}
            .agent-blue {{ color: #4488ff; }}
            .agent-orange {{ color: #ffaa00; }}
            img {{ max-width: 100%; border: 1px solid #444; border-radius: 5px; }}
            .header-info {{ display: flex; justify-content: space-between; margin-bottom: 20px; padding: 10px; background: #111; border: 1px solid #333; border-radius: 5px; }}
            .header-info span {{ margin-right: 20px; }}
            .success {{ color: #00ff41; }}
            .warning {{ color: #ffaa00; }}
            .failure {{ color: #ff3333; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚔️ SISTEMA FOREST GUARDIAN v2.5 - INFORME POST-OPERATIVO</h1>
            
            <div class="header-info">
                <span><strong>ID MISIÓN:</strong> {mission_id}</span>
                <span><strong>FECHA:</strong> {timestamp}</span>
                <span><strong>ESTADO:</strong> <span class="success">MISIÓN COMPLETADA</span></span>
            </div>

            <div class="grid">
                <div class="video-box">
                    <p style="color: #888; margin-top: 0;">>> REPRODUCIENDO SEÑAL DE SATÉLITE TÉRMICA</p>
                    {gif_tag}
                    <p style="font-size: 0.8em; margin-top: 10px; color: #888;">Visualización térmica del terreno en tiempo real</p>
                </div>

                <div class="stats-box">
                    <h2>📊 MÉTRICAS DE EFICIENCIA</h2>
                    
                    <div class="metric">
                        <span class="label">SUPERFICIE FORESTAL SALVADA</span>
                        <span class="value">{stats.get('trees_saved', 0)}%</span>
                        <div class="status-bar"><div class="fill" style="width: {stats.get('trees_saved', 0)}%;"></div></div>
                    </div>

                    <div class="metric">
                        <span class="label">FOCOS NEUTRALIZADOS</span>
                        <span class="value">{stats.get('fires_extinguished', 0)}</span>
                        <div style="font-size: 0.9em; color: #888;">De {stats.get('initial_fires', 0)} focos iniciales</div>
                    </div>

                    <div class="metric">
                        <span class="label">TIEMPO DE RESPUESTA</span>
                        <span class="value">{stats.get('steps', 0)} pasos</span>
                        <div style="font-size: 0.9em; color: #888;">Aproximadamente {stats.get('steps', 0)} minutos simulados</div>
                    </div>

                    <div class="metric">
                        <span class="label">RECURSOS UTILIZADOS</span>
                        <span class="value">{stats.get('water_used', 0)}/{stats.get('max_water', 999)}</span>
                        <div style="font-size: 0.9em; color: #888;">Unidades de agua consumidas</div>
                    </div>

                    <div class="agent-info">
                        <h3>⚙️ DESPLIEGUE DE UNIDADES AUTÓNOMAS</h3>
                        <p><strong class="agent-blue">UNIDAD ALPHA (AZUL):</strong> Dron de Intervención Rápida<br>
                        <em style="color: #666;">Algoritmo:</em> Búsqueda de Proximidad. Prioriza focos inminentes.</p>
                        
                        <p><strong class="agent-orange">UNIDAD BRAVO (NARANJA):</strong> Dron de Contención Pesada<br>
                        <em style="color: #666;">Algoritmo:</em> Envolvimiento Táctico. Ataca focos perimetrales.</p>
                    </div>
                </div>
            </div>

            <div style="margin-top: 30px; border-top: 2px solid #00ff41; padding-top: 20px;">
                <h2>✅ CONCLUSIÓN DEL SISTEMA:</h2>
                <p>El algoritmo de control autónomo ha demostrado capacidad para coordinar múltiples unidades 
                sin colisiones en un entorno estocástico dinámico. La intervención autónoma minimizó el daño 
                ambiental y eliminó la exposición de personal humano a peligros.</p>
                <p style="text-align: right; font-size: 0.9em; color: #666;">
                    GENERADO POR FOREST GUARDIAN AI ENGINE - Sistema de Protección Forestal Autónomo v2.5
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Guardar reporte
    report_filename = gif_path.replace(".gif", "_REPORTE.html")
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return report_filename

# ============================================================================
# FUNCIÓN PRINCIPAL LEGACY (Compatible con script original)
# ============================================================================

def make_the_magic():
    """Función original para ejecutar misión desde terminal"""
    print("="*60)
    print("INICIANDO PROTOCOLO DE EMERGENCIA FORESTAL")
    print("="*60)
    
    env = ForestFireEnv(grid_size=10, num_agents=2, initial_fires=3)
    executor = MissionExecutor(env, num_agents=2)
    
    print(">>> Desplegando drones (Simulación en curso)...")
    frames, metrics = executor.execute(max_steps=100)
    
    print(f"\n>>> Generando evidencia visual...")
    timestamp = int(time.time())
    gif_filename = f'MISION_{timestamp}.gif'
    
    # Guardar GIF
    base_dir = "GIF"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    full_gif_path = os.path.join(base_dir, gif_filename)
    env.render_animation(frames, filename=gif_filename)
    
    # Generar reporte
    stats = {
        'trees_saved': metrics.trees_saved_pct,
        'fires_extinguished': metrics.fires_extinguished,
        'steps': metrics.duration_steps,
        'water_used': metrics.water_used,
        'max_water': metrics.max_water,
        'initial_fires': metrics.initial_fires
    }
    
    print(f">>> Redactando Informe Táctico Automático...")
    report_path = generate_tactical_report(full_gif_path, stats, metrics.mission_id)
    
    print("\n" + "="*60)
    print("MISIÓN COMPLETADA CON ÉXITO")
    print("="*60)
    print(f"Para revisar el análisis detallado, abre este archivo:")
    print(f"{report_path}")
    print("="*60)

if __name__ == "__main__":
    make_the_magic()
