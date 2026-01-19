"""
Módulo de métricas y KPIs para Forest Guardian RL
Proporciona funciones para calcular y presentar indicadores clave de desempeño
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MissionMetrics:
    """Clase para almacenar métricas de una misión"""
    mission_id: str
    timestamp: str
    duration_steps: int
    initial_trees: int
    final_trees: int
    trees_saved_pct: float
    initial_fires: int
    fires_extinguished: int
    max_water: int
    water_used: int
    grid_size: int
    num_agents: int
    fire_spread_prob: float
    
    def to_dict(self) -> Dict:
        """Convierte las métricas a diccionario"""
        return {
            'mission_id': self.mission_id,
            'timestamp': self.timestamp,
            'duration_steps': self.duration_steps,
            'initial_trees': self.initial_trees,
            'final_trees': self.final_trees,
            'trees_saved_pct': self.trees_saved_pct,
            'initial_fires': self.initial_fires,
            'fires_extinguished': self.fires_extinguished,
            'max_water': self.max_water,
            'water_used': self.water_used,
            'grid_size': self.grid_size,
            'num_agents': self.num_agents,
            'fire_spread_prob': self.fire_spread_prob
        }

class MetricsCalculator:
    """Calcula métricas en tiempo real durante la simulación"""
    
    def __init__(self, initial_state: np.ndarray, env_config: Dict):
        """
        Inicializa el calculador de métricas
        
        Args:
            initial_state: Grid inicial del entorno
            env_config: Configuración del entorno (num_agents, fire_spread_prob, etc)
        """
        self.initial_state = initial_state.copy()
        self.env_config = env_config
        self.initial_trees = np.sum(initial_state == 1)
        self.initial_fires = np.sum(initial_state == 2)
        
        # Histórico de métricas por paso
        self.step_metrics = []
    
    def calculate_step_metrics(
        self,
        current_state: np.ndarray,
        step: int,
        water_tanks: List[int]
    ) -> Dict:
        """
        Calcula métricas para el paso actual
        
        Args:
            current_state: Grid actual del entorno
            step: Número del paso
            water_tanks: Cantidad de agua en tanques de cada dron
        
        Returns:
            Diccionario con métricas del paso
        """
        current_trees = np.sum(current_state == 1)
        current_fires = np.sum(current_state == 2)
        
        # Calcular porcentaje de árboles salvados
        trees_saved_pct = (current_trees / self.initial_trees * 100) if self.initial_trees > 0 else 0
        
        # Calcular agua consumida (asumiendo tanque inicial de 999)
        max_water = 999
        water_used = sum([max_water - tank for tank in water_tanks]) / len(water_tanks)
        
        metrics = {
            'step': step,
            'active_trees': current_trees,
            'active_fires': current_fires,
            'trees_saved_pct': trees_saved_pct,
            'water_used': water_used,
            'trees_lost': self.initial_trees - current_trees,
            'fires_extinguished': self.initial_fires - current_fires if current_fires >= 0 else self.initial_fires
        }
        
        self.step_metrics.append(metrics)
        return metrics
    
    def get_final_metrics(self, final_state: np.ndarray, total_steps: int) -> MissionMetrics:
        """
        Calcula métricas finales de la misión
        
        Args:
            final_state: Estado final del grid
            total_steps: Número total de pasos ejecutados
        
        Returns:
            Objeto MissionMetrics con los resultados finales
        """
        final_trees = np.sum(final_state == 1)
        final_fires = np.sum(final_state == 2)
        
        trees_saved_pct = (final_trees / self.initial_trees * 100) if self.initial_trees > 0 else 0
        fires_extinguished = max(0, self.initial_fires - final_fires)
        
        # Calcular agua consumida total
        if self.step_metrics:
            avg_water_used = self.step_metrics[-1]['water_used']
        else:
            avg_water_used = 0
        
        metrics = MissionMetrics(
            mission_id=f"FOREST_{int(datetime.now().timestamp())}",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            duration_steps=total_steps,
            initial_trees=self.initial_trees,
            final_trees=final_trees,
            trees_saved_pct=trees_saved_pct,
            initial_fires=self.initial_fires,
            fires_extinguished=fires_extinguished,
            max_water=999,
            water_used=int(avg_water_used),
            grid_size=self.env_config.get('grid_size', 10),
            num_agents=self.env_config.get('num_agents', 2),
            fire_spread_prob=self.env_config.get('fire_spread_prob', 0.1)
        )
        
        return metrics

class KPIFormatter:
    """Formatea KPIs para visualización"""
    
    @staticmethod
    def format_efficiency_score(metrics: MissionMetrics) -> float:
        """
        Calcula un score de eficiencia (0-100)
        
        Args:
            metrics: MissionMetrics con datos de la misión
        
        Returns:
            Score de eficiencia
        """
        # 40% = % de árboles salvados
        # 40% = rapidez en extinguir fuegos (fuegos/pasos)
        # 20% = uso eficiente de agua
        
        trees_score = metrics.trees_saved_pct
        
        if metrics.duration_steps > 0:
            fires_score = (metrics.fires_extinguished / max(metrics.initial_fires, 1)) * 100
            speed_score = min(100, (metrics.initial_fires / metrics.duration_steps) * 100)
        else:
            fires_score = 0
            speed_score = 0
        
        efficiency = (trees_score * 0.4) + (fires_score * 0.35) + (speed_score * 0.25)
        return min(100, efficiency)
    
    @staticmethod
    def format_water_efficiency(metrics: MissionMetrics) -> str:
        """Calcula eficiencia de uso de agua"""
        if metrics.fires_extinguished > 0:
            water_per_fire = metrics.water_used / metrics.fires_extinguished
            return f"{water_per_fire:.1f} unidades/fuego"
        return "N/A"
    
    @staticmethod
    def format_mission_status(metrics: MissionMetrics) -> Tuple[str, str]:
        """
        Determina el estado y color de la misión
        
        Args:
            metrics: MissionMetrics
        
        Returns:
            Tupla (estado_texto, color_bootstrap)
        """
        if metrics.trees_saved_pct >= 80 and metrics.fires_extinguished == metrics.initial_fires:
            return ("✅ MISIÓN EXITOSA", "success")
        elif metrics.trees_saved_pct >= 60:
            return ("⚠️ MISIÓN PARCIAL", "warning")
        else:
            return ("❌ MISIÓN FALLIDA", "danger")
    
    @staticmethod
    def create_kpi_card(label: str, value: str, unit: str = "", color: str = "primary") -> str:
        """
        Crea HTML para una tarjeta de KPI
        
        Args:
            label: Etiqueta del KPI
            value: Valor a mostrar
            unit: Unidad de medida
            color: Color de Bootstrap (primary, success, danger, warning, info)
        
        Returns:
            HTML formateado
        """
        colors_map = {
            'primary': '#667eea',
            'success': '#00aa00',
            'danger': '#ff0000',
            'warning': '#ffaa00',
            'info': '#0066ff'
        }
        
        color_hex = colors_map.get(color, '#667eea')
        
        return f"""
        <div style="background: linear-gradient(135deg, {color_hex} 0%, rgba(0,0,0,0.1) 100%); 
                    padding: 20px; border-radius: 10px; color: white; text-align: center; 
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin: 10px 0;">
            <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">{label}</div>
            <div style="font-size: 32px; font-weight: bold; margin: 10px 0;">{value}</div>
            <div style="font-size: 12px; opacity: 0.8;">{unit}</div>
        </div>
        """

def generate_mission_report(metrics: MissionMetrics) -> str:
    """
    Genera un reporte de texto de la misión
    
    Args:
        metrics: MissionMetrics con datos de la misión
    
    Returns:
        Reporte formateado como string
    """
    status, _ = KPIFormatter.format_mission_status(metrics)
    efficiency = KPIFormatter.format_efficiency_score(metrics)
    water_eff = KPIFormatter.format_water_efficiency(metrics)
    
    report = f"""
╔════════════════════════════════════════════════════════════════╗
║               REPORTE DE MISIÓN - FOREST GUARDIAN              ║
╚════════════════════════════════════════════════════════════════╝

ID MISIÓN: {metrics.mission_id}
FECHA: {metrics.timestamp}
ESTADO: {status}

────────────────────────────────────────────────────────────────
MÉTRICAS DE DESEMPEÑO
────────────────────────────────────────────────────────────────

🌲 COBERTURA FORESTAL
   • Árboles iniciales: {metrics.initial_trees}
   • Árboles finales: {metrics.final_trees}
   • Árboles perdidos: {metrics.initial_trees - metrics.final_trees}
   • Porcentaje salvado: {metrics.trees_saved_pct:.1f}%

🔥 CONTROL DE INCENDIOS
   • Focos iniciales: {metrics.initial_fires}
   • Focos extintos: {metrics.fires_extinguished}
   • Focos restantes: {metrics.initial_fires - metrics.fires_extinguished}

⏱️  DURACIÓN
   • Pasos totales: {metrics.duration_steps}
   • Tiempo promedio/fuego: {metrics.duration_steps / max(metrics.fires_extinguished, 1):.1f} pasos

💧 RECURSOS UTILIZADOS
   • Agua consumida: {metrics.water_used}/{metrics.max_water} unidades
   • Eficiencia de agua: {water_eff}

📊 CONFIGURACIÓN DE ENTORNO
   • Tamaño de cuadrícula: {metrics.grid_size}×{metrics.grid_size}
   • Número de drones: {metrics.num_agents}
   • Probabilidad de propagación: {metrics.fire_spread_prob}

────────────────────────────────────────────────────────────────
SCORE DE EFICIENCIA: {efficiency:.1f}/100
────────────────────────────────────────────────────────────────
"""
    
    return report
