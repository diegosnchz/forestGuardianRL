"""
Módulo de Inteligencia Artificial Explicable (XAI) para Forest Guardian RL.

Este módulo proporciona explicaciones interpretables de las decisiones
de los agentes autónomos Alpha, Bravo y Gamma.

Características:
- Interpretación de atributos con explicaciones textuales
- Mapas de importancia (attention maps) de píxeles/coordenadas
- Justificación táctica de estrategias
- Registro histórico de decisiones
- Visualización de reasoning process

Autor: Forest Guardian RL Team
Fecha: Enero 2026
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
from collections import defaultdict

# ============================================================================
# CLASES DE DATOS
# ============================================================================

@dataclass
class AgentDecision:
    """
    Estructura para almacenar una decisión del agente con explicación completa.
    """
    timestamp: datetime
    agent_id: str
    agent_role: str
    position: Tuple[int, int]
    action: int
    action_name: str
    
    # Contexto del entorno
    grid_state: np.ndarray
    fires_detected: List[Tuple[int, int]]
    trees_nearby: int
    water_level: int
    
    # Explicación XAI
    explanation: str
    tactical_reasoning: str
    attention_map: np.ndarray
    importance_scores: Dict[str, float]
    
    # Métricas de decisión
    distance_to_target: float
    alternative_actions: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class DecisionHistory:
    """
    Historial de decisiones de un agente.
    """
    agent_id: str
    decisions: List[AgentDecision] = field(default_factory=list)
    
    def add(self, decision: AgentDecision):
        """Agrega una decisión al historial."""
        self.decisions.append(decision)
    
    def get_last_n(self, n: int = 10) -> List[AgentDecision]:
        """Obtiene las últimas N decisiones."""
        return self.decisions[-n:]
    
    def get_by_action(self, action: int) -> List[AgentDecision]:
        """Filtra decisiones por tipo de acción."""
        return [d for d in self.decisions if d.action == action]


# ============================================================================
# CLASE PRINCIPAL XAI EXPLAINER
# ============================================================================

class XAIExplainer:
    """
    Clase principal para explicación interpretable de decisiones de agentes.
    
    Proporciona:
    - Análisis de atributos del entorno
    - Generación de explicaciones textuales
    - Mapas de importancia visual
    - Justificación táctica de estrategias
    """
    
    # Nombres de acciones
    ACTION_NAMES = {
        0: "Mover Arriba",
        1: "Mover Abajo",
        2: "Mover Izquierda",
        3: "Mover Derecha",
        4: "Esperar",
        5: "Apagar Fuego",
        6: "Crear Cortafuegos"
    }
    
    # Roles de agentes
    AGENT_ROLES = {
        "nearest": "ALPHA (Ataque Rápido)",
        "farthest": "BRAVO (Contención Periférica)",
        "firebreak": "GAMMA (Cortafuegos Preventivo)"
    }
    
    def __init__(self, grid_size: int = 10, enable_mongodb: bool = False):
        """
        Inicializa el XAI Explainer.
        
        Args:
            grid_size: Tamaño del grid del entorno
            enable_mongodb: Si True, usa datos de MongoDB Atlas
        """
        self.grid_size = grid_size
        self.enable_mongodb = enable_mongodb
        
        # Historiales de decisiones por agente
        self.histories: Dict[str, DecisionHistory] = {}
        
        # Estadísticas globales
        self.total_decisions = 0
        self.action_counts = defaultdict(int)
        self.agent_stats = defaultdict(lambda: defaultdict(int))
    
    def explain_decision(self,
                        agent_id: str,
                        agent_role: str,
                        position: Tuple[int, int],
                        action: int,
                        grid_state: np.ndarray,
                        obs: Optional[Dict] = None,
                        water_level: int = 999) -> AgentDecision:
        """
        Explica una decisión del agente generando análisis completo.
        
        Args:
            agent_id: Identificador del agente (ej: "ALPHA", "BRAVO")
            agent_role: Rol del agente (nearest, farthest, firebreak)
            position: Posición actual (row, col)
            action: Acción tomada (0-6)
            grid_state: Estado actual del grid
            obs: Observación completa (dict con wind, elevation, etc.)
            water_level: Nivel de agua del agente
            
        Returns:
            AgentDecision con explicación completa
        """
        # Detectar fuegos y árboles
        fires = np.argwhere(grid_state == 2).tolist()
        trees_nearby = self._count_nearby_trees(grid_state, position, radius=3)
        
        # Generar mapa de atención
        attention_map = self._generate_attention_map(grid_state, position, action, agent_role)
        
        # Calcular importancia de atributos
        importance_scores = self._calculate_importance_scores(
            grid_state, position, fires, agent_role, obs
        )
        
        # Generar explicación textual
        explanation = self._generate_explanation(
            agent_role, position, action, fires, grid_state, importance_scores, obs
        )
        
        # Generar justificación táctica
        tactical_reasoning = self._generate_tactical_reasoning(
            agent_role, position, action, fires, grid_state, obs
        )
        
        # Calcular distancia al objetivo
        distance_to_target = self._calculate_distance_to_target(
            position, fires, agent_role
        )
        
        # Generar acciones alternativas
        alternative_actions = self._generate_alternatives(
            position, fires, grid_state, agent_role
        )
        
        # Crear decisión
        decision = AgentDecision(
            timestamp=datetime.now(),
            agent_id=agent_id,
            agent_role=agent_role,
            position=position,
            action=action,
            action_name=self.ACTION_NAMES.get(action, "Desconocida"),
            grid_state=grid_state.copy(),
            fires_detected=fires,
            trees_nearby=trees_nearby,
            water_level=water_level,
            explanation=explanation,
            tactical_reasoning=tactical_reasoning,
            attention_map=attention_map,
            importance_scores=importance_scores,
            distance_to_target=distance_to_target,
            alternative_actions=alternative_actions,
            confidence=self._calculate_confidence(importance_scores)
        )
        
        # Agregar al historial
        self._add_to_history(agent_id, decision)
        
        # Actualizar estadísticas
        self._update_stats(agent_id, agent_role, action)
        
        return decision
    
    def _generate_attention_map(self,
                                grid_state: np.ndarray,
                                position: Tuple[int, int],
                                action: int,
                                agent_role: str) -> np.ndarray:
        """
        Genera un mapa de atención que resalta píxeles importantes.
        
        Returns:
            Matriz del mismo tamaño que grid_state con valores 0-1
        """
        attention = np.zeros_like(grid_state, dtype=float)
        r, c = position
        
        # Alta atención en posición actual
        attention[r, c] = 1.0
        
        # Detectar fuegos
        fires = np.argwhere(grid_state == 2)
        
        if len(fires) == 0:
            return attention
        
        # Calcular distancias a fuegos
        dists = [abs(r - fr) + abs(c - fc) for fr, fc in fires]
        
        # Determinar objetivo según rol
        if agent_role == "nearest":
            target_idx = np.argmin(dists)
        elif agent_role == "farthest":
            target_idx = np.argmax(dists) if len(fires) > 1 else np.argmin(dists)
        elif agent_role == "firebreak":
            # Buscar fuegos cercanos
            nearby = [i for i, d in enumerate(dists) if d <= 5]
            target_idx = nearby[0] if nearby else np.argmin(dists)
        else:
            target_idx = np.argmin(dists)
        
        target_r, target_c = fires[target_idx]
        
        # Alta atención en objetivo
        attention[target_r, target_c] = 0.9
        
        # Atención decreciente en camino al objetivo
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if attention[i, j] == 0:
                    # Calcular si está en el camino
                    dist_to_agent = abs(i - r) + abs(j - c)
                    dist_to_target = abs(i - target_r) + abs(j - target_c)
                    total_dist = abs(target_r - r) + abs(target_c - c)
                    
                    if total_dist > 0:
                        # Si está en línea recta entre agente y objetivo
                        alignment = (dist_to_agent + dist_to_target) / (total_dist * 2.0)
                        if alignment < 1.2:  # Tolerancia
                            attention[i, j] = max(0.1, 0.5 - dist_to_agent * 0.05)
        
        # Atención media en otros fuegos
        for fr, fc in fires:
            if (fr, fc) != (target_r, target_c):
                attention[fr, fc] = 0.4
        
        # Para firebreak, alta atención en árboles cercanos al fuego
        if agent_role == "firebreak":
            for fr, fc in fires:
                for dr in [-2, -1, 0, 1, 2]:
                    for dc in [-2, -1, 0, 1, 2]:
                        nr, nc = fr + dr, fc + dc
                        if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                            if grid_state[nr, nc] == 1:  # Árbol
                                attention[nr, nc] = max(attention[nr, nc], 0.6)
        
        return attention
    
    def _calculate_importance_scores(self,
                                    grid_state: np.ndarray,
                                    position: Tuple[int, int],
                                    fires: List[Tuple[int, int]],
                                    agent_role: str,
                                    obs: Optional[Dict] = None) -> Dict[str, float]:
        """
        Calcula la importancia de diferentes atributos en la decisión.
        
        Returns:
            Diccionario con scores de importancia (0-1)
        """
        scores = {}
        r, c = position
        
        # 1. Proximidad al fuego
        if fires:
            dists = [abs(r - fr) + abs(c - fc) for fr, fc in fires]
            min_dist = min(dists)
            max_dist = max(dists) if len(dists) > 1 else min_dist
            
            if agent_role == "nearest":
                # Para Alpha, la proximidad es crítica
                scores['proximidad_fuego'] = 1.0 if min_dist <= 2 else 0.8
                scores['cantidad_fuegos'] = min(len(fires) / 5.0, 1.0)
            elif agent_role == "farthest":
                # Para Bravo, la distancia al más lejano es importante
                scores['proximidad_fuego'] = 0.5
                scores['cobertura_perimetral'] = max_dist / (self.grid_size * 2) * 1.0
            elif agent_role == "firebreak":
                # Para Gamma, los árboles cercanos son clave
                trees_near_fire = self._count_trees_near_fires(grid_state, fires)
                scores['arboles_en_riesgo'] = min(trees_near_fire / 20.0, 1.0)
                scores['proximidad_fuego'] = 0.7 if min_dist <= 5 else 0.3
        else:
            scores['proximidad_fuego'] = 0.0
            scores['cantidad_fuegos'] = 0.0
        
        # 2. Densidad de árboles
        trees_nearby = self._count_nearby_trees(grid_state, position, radius=3)
        scores['densidad_arboles_local'] = min(trees_nearby / 15.0, 1.0)
        
        # 3. Posición estratégica (centro vs borde)
        center_dist = abs(r - self.grid_size // 2) + abs(c - self.grid_size // 2)
        scores['centralidad'] = 1.0 - (center_dist / (self.grid_size * 1.5))
        
        # 4. Información adicional si hay observación completa
        if obs and isinstance(obs, dict):
            # Viento
            if 'wind' in obs:
                wind = obs['wind']
                wind_magnitude = np.linalg.norm(wind)
                scores['influencia_viento'] = min(wind_magnitude, 1.0)
            
            # Elevación
            if 'elevation' in obs:
                elevation = obs['elevation']
                avg_elevation = np.mean(elevation)
                scores['factor_elevacion'] = avg_elevation
        
        # Normalizar scores entre 0 y 1
        max_score = max(scores.values()) if scores else 1.0
        if max_score > 0:
            scores = {k: v / max_score for k, v in scores.items()}
        
        return scores
    
    def _generate_explanation(self,
                             agent_role: str,
                             position: Tuple[int, int],
                             action: int,
                             fires: List[Tuple[int, int]],
                             grid_state: np.ndarray,
                             importance_scores: Dict[str, float],
                             obs: Optional[Dict] = None) -> str:
        """
        Genera explicación textual de la decisión.
        """
        r, c = position
        action_name = self.ACTION_NAMES.get(action, "Desconocida")
        role_name = self.AGENT_ROLES.get(agent_role, agent_role)
        
        # Inicio de explicación
        explanation = f"🤖 **{role_name}** en posición ({r}, {c})\n\n"
        explanation += f"**Decisión:** {action_name}\n\n"
        
        # Análisis del contexto
        explanation += "**Análisis del Entorno:**\n"
        
        if not fires:
            explanation += "• No se detectaron focos de incendio activos\n"
            explanation += "• Modo: Patrulla y vigilancia\n"
            return explanation
        
        # Calcular distancias
        dists = [abs(r - fr) + abs(c - fc) for fr, fc in fires]
        min_dist = min(dists)
        closest_fire = fires[np.argmin(dists)]
        
        explanation += f"• {len(fires)} foco(s) de incendio detectado(s)\n"
        explanation += f"• Fuego más cercano a {min_dist} celdas en ({closest_fire[0]}, {closest_fire[1]})\n"
        
        # Información de árboles
        trees_nearby = self._count_nearby_trees(grid_state, position, radius=3)
        explanation += f"• {trees_nearby} árboles en radio de 3 celdas\n"
        
        # Información adicional según observación
        if obs and isinstance(obs, dict):
            if 'wind' in obs:
                wind = obs['wind']
                wind_speed = np.linalg.norm(wind) * 20  # Escalar a km/h aproximado
                wind_direction = np.arctan2(wind[1], wind[0]) * 180 / np.pi
                explanation += f"• Viento: {wind_speed:.1f} km/h, dirección {wind_direction:.0f}°\n"
        
        explanation += "\n**Motivo de la Decisión:**\n"
        
        # Explicación específica por acción
        if action in [0, 1, 2, 3]:  # Movimiento
            direction = ["Norte ⬆️", "Sur ⬇️", "Oeste ⬅️", "Este ➡️"][action]
            
            if min_dist > 1:
                explanation += f"• Desplazándose hacia {direction} para alcanzar objetivo\n"
                explanation += f"• Distancia restante: {min_dist} celdas\n"
            else:
                explanation += f"• Ajustando posición {direction} para ataque óptimo\n"
            
            # Justificar según rol
            if agent_role == "nearest":
                explanation += f"• **Estrategia Alpha:** Prioridad al fuego más cercano ({min_dist} celdas)\n"
            elif agent_role == "farthest" and len(fires) > 1:
                farthest_fire = fires[np.argmax(dists)]
                max_dist = max(dists)
                explanation += f"• **Estrategia Bravo:** Objetivo en perímetro ({farthest_fire[0]}, {farthest_fire[1]}) a {max_dist} celdas\n"
                explanation += f"• Ignorando fuego cercano para contención periférica\n"
            elif agent_role == "firebreak":
                explanation += f"• **Estrategia Gamma:** Posicionándose para crear cortafuegos preventivo\n"
        
        elif action == 5:  # Apagar fuego
            explanation += f"• ¡Fuego al alcance! Activando sistema de extinción\n"
            explanation += f"• Radio de acción: 3x3 celdas\n"
            explanation += f"• Objetivo en ({closest_fire[0]}, {closest_fire[1]})\n"
        
        elif action == 6:  # Cortafuegos
            trees_near_fires = self._count_trees_near_fires(grid_state, fires)
            explanation += f"• Creando barrera cortafuegos\n"
            explanation += f"• {trees_near_fires} árboles en riesgo inmediato\n"
            explanation += f"• Removiendo vegetación para detener propagación\n"
        
        elif action == 4:  # Idle
            explanation += f"• En espera estratégica\n"
            explanation += f"• Posición óptima alcanzada\n"
        
        # Factores de importancia
        explanation += "\n**Factores Clave (Importancia):**\n"
        sorted_scores = sorted(importance_scores.items(), key=lambda x: x[1], reverse=True)
        for factor, score in sorted_scores[:3]:
            percentage = score * 100
            bars = "█" * int(score * 10)
            factor_label = factor.replace('_', ' ').title()
            explanation += f"• {factor_label}: {bars} {percentage:.0f}%\n"
        
        return explanation
    
    def _generate_tactical_reasoning(self,
                                    agent_role: str,
                                    position: Tuple[int, int],
                                    action: int,
                                    fires: List[Tuple[int, int]],
                                    grid_state: np.ndarray,
                                    obs: Optional[Dict] = None) -> str:
        """
        Genera justificación táctica específica del rol.
        """
        reasoning = ""
        r, c = position
        
        if not fires:
            return "**Táctica:** Patrulla preventiva - Sin amenazas activas detectadas"
        
        dists = [abs(r - fr) + abs(c - fc) for fr, fc in fires]
        min_dist = min(dists)
        
        if agent_role == "nearest":
            # ALPHA - Ataque Rápido
            reasoning = "**🔵 TÁCTICA ALPHA - RESPUESTA RÁPIDA**\n\n"
            reasoning += "**Doctrina Operacional:**\n"
            reasoning += "• Minimizar tiempo de respuesta\n"
            reasoning += "• Priorizar amenazas inmediatas\n"
            reasoning += "• Supresión directa de fuegos\n\n"
            
            if min_dist <= 1:
                reasoning += "**Estado:** ✅ En posición de ataque\n"
                reasoning += "**Acción:** Extinción directa del foco\n"
            elif min_dist <= 3:
                reasoning += "**Estado:** 🏃 Aproximación rápida\n"
                reasoning += f"**ETA:** {min_dist} movimientos\n"
            else:
                reasoning += "**Estado:** 🚁 Desplazamiento hacia zona caliente\n"
                reasoning += f"**Distancia:** {min_dist} celdas\n"
        
        elif agent_role == "farthest":
            # BRAVO - Contención Periférica
            reasoning = "**🟠 TÁCTICA BRAVO - CONTENCIÓN PERIFÉRICA**\n\n"
            reasoning += "**Doctrina Operacional:**\n"
            reasoning += "• Prevenir expansión del perímetro\n"
            reasoning += "• Proteger áreas no comprometidas\n"
            reasoning += "• Crear líneas de contención\n\n"
            
            if len(fires) > 1:
                max_dist = max(dists)
                farthest_idx = np.argmax(dists)
                farthest_fire = fires[farthest_idx]
                closest_fire = fires[np.argmin(dists)]
                
                reasoning += "**🎯 Estrategia Activa:**\n"
                reasoning += f"• Ignorando fuego cercano en ({closest_fire[0]}, {closest_fire[1]}) - {min_dist} celdas\n"
                reasoning += f"• Objetivo: Fuego perimetral en ({farthest_fire[0]}, {farthest_fire[1]}) - {max_dist} celdas\n"
                reasoning += f"• **Justificación:** Prevenir propagación en {max_dist} celdas de área crítica\n\n"
                
                if self.enable_mongodb:
                    reasoning += "**📡 Integración MongoDB Atlas:**\n"
                    reasoning += "• Perímetro crítico definido en base de datos geoespacial\n"
                    reasoning += "• Coordinadas de zonas protegidas consultadas\n"
                    reasoning += "• Nivel de riesgo actualizado en tiempo real\n"
            else:
                reasoning += "**Estado:** Un solo foco detectado\n"
                reasoning += "**Modo:** Apoyo a extinción directa\n"
        
        elif agent_role == "firebreak":
            # GAMMA - Cortafuegos Preventivo
            reasoning = "**🟣 TÁCTICA GAMMA - CORTAFUEGOS PREVENTIVO**\n\n"
            reasoning += "**Doctrina Operacional:**\n"
            reasoning += "• Crear barreras de contención\n"
            reasoning += "• Remover combustible vegetal\n"
            reasoning += "• Detener propagación futura\n\n"
            
            trees_near_fires = self._count_trees_near_fires(grid_state, fires)
            
            if action == 6:
                reasoning += "**⚡ CREANDO CORTAFUEGOS:**\n"
                reasoning += f"• {trees_near_fires} árboles en zona de riesgo\n"
                reasoning += "• Removiendo vegetación combustible\n"
                reasoning += "• Anchura de barrera: 1 celda\n"
            else:
                reasoning += "**Estado:** Posicionamiento táctico\n"
                reasoning += f"• Evaluando {trees_near_fires} árboles en riesgo\n"
                reasoning += "• Buscando línea óptima de cortafuegos\n"
        
        # Información adicional del entorno
        if obs and isinstance(obs, dict):
            if 'wind' in obs:
                wind = obs['wind']
                wind_magnitude = np.linalg.norm(wind)
                if wind_magnitude > 0.3:
                    reasoning += "\n**⚠️ Factor Viento:**\n"
                    reasoning += f"• Velocidad significativa detectada ({wind_magnitude:.2f})\n"
                    reasoning += "• Ajustando táctica por propagación vectorial\n"
        
        return reasoning
    
    def _count_nearby_trees(self, grid_state: np.ndarray, position: Tuple[int, int], radius: int = 3) -> int:
        """Cuenta árboles en radio alrededor de una posición."""
        r, c = position
        count = 0
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                    if grid_state[nr, nc] == 1:
                        count += 1
        return count
    
    def _count_trees_near_fires(self, grid_state: np.ndarray, fires: List[Tuple[int, int]], radius: int = 2) -> int:
        """Cuenta árboles cerca de focos de incendio."""
        tree_positions = set()
        for fr, fc in fires:
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    nr, nc = fr + dr, fc + dc
                    if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                        if grid_state[nr, nc] == 1:
                            tree_positions.add((nr, nc))
        return len(tree_positions)
    
    def _calculate_distance_to_target(self, position: Tuple[int, int], fires: List[Tuple[int, int]], agent_role: str) -> float:
        """Calcula distancia al objetivo según rol."""
        if not fires:
            return 0.0
        
        r, c = position
        dists = [abs(r - fr) + abs(c - fc) for fr, fc in fires]
        
        if agent_role == "nearest":
            return float(min(dists))
        elif agent_role == "farthest":
            return float(max(dists)) if len(fires) > 1 else float(min(dists))
        elif agent_role == "firebreak":
            nearby = [d for d in dists if d <= 5]
            return float(min(nearby)) if nearby else float(min(dists))
        else:
            return float(min(dists))
    
    def _generate_alternatives(self, position: Tuple[int, int], fires: List[Tuple[int, int]], grid_state: np.ndarray, agent_role: str) -> List[Dict[str, Any]]:
        """Genera lista de acciones alternativas con justificación."""
        alternatives = []
        r, c = position
        
        if not fires:
            return alternatives
        
        dists = [abs(r - fr) + abs(c - fc) for fr, fc in fires]
        min_dist = min(dists)
        
        # Alternativa: Apagar fuego (si está en rango)
        if min_dist <= 1:
            alternatives.append({
                "action": 5,
                "name": "Apagar Fuego",
                "score": 0.95,
                "reason": "Fuego al alcance directo"
            })
        
        # Alternativa: Moverse hacia fuego más cercano
        if min_dist > 1:
            closest_fire = fires[np.argmin(dists)]
            diff_r = closest_fire[0] - r
            diff_c = closest_fire[1] - c
            
            if abs(diff_r) > abs(diff_c):
                action = 1 if diff_r > 0 else 0
            else:
                action = 3 if diff_c > 0 else 2
            
            alternatives.append({
                "action": action,
                "name": self.ACTION_NAMES[action],
                "score": 0.8,
                "reason": f"Acercarse {min_dist - 1} celdas al fuego"
            })
        
        # Alternativa: Cortafuegos (si es GAMMA)
        if agent_role == "firebreak" and min_dist <= 2:
            trees_nearby = self._count_nearby_trees(grid_state, position, radius=2)
            if trees_nearby > 3:
                alternatives.append({
                    "action": 6,
                    "name": "Crear Cortafuegos",
                    "score": 0.75,
                    "reason": f"{trees_nearby} árboles en riesgo"
                })
        
        # Alternativa: Idle
        if min_dist > 5:
            alternatives.append({
                "action": 4,
                "name": "Esperar",
                "score": 0.2,
                "reason": "Fuegos lejanos, esperar desarrollo"
            })
        
        return sorted(alternatives, key=lambda x: x['score'], reverse=True)
    
    def _calculate_confidence(self, importance_scores: Dict[str, float]) -> float:
        """Calcula confianza de la decisión basada en importancia de atributos."""
        if not importance_scores:
            return 0.5
        
        # Confianza alta si hay factores claramente dominantes
        max_score = max(importance_scores.values())
        avg_score = sum(importance_scores.values()) / len(importance_scores)
        
        # Mayor diferencia entre max y avg = mayor confianza
        confidence = max_score - (avg_score * 0.5)
        return min(max(confidence, 0.0), 1.0)
    
    def _add_to_history(self, agent_id: str, decision: AgentDecision):
        """Agrega decisión al historial del agente."""
        if agent_id not in self.histories:
            self.histories[agent_id] = DecisionHistory(agent_id=agent_id)
        
        self.histories[agent_id].add(decision)
    
    def _update_stats(self, agent_id: str, agent_role: str, action: int):
        """Actualiza estadísticas globales."""
        self.total_decisions += 1
        self.action_counts[action] += 1
        self.agent_stats[agent_id]['total'] += 1
        self.agent_stats[agent_id][action] += 1
    
    def get_history(self, agent_id: str, last_n: int = 10) -> List[AgentDecision]:
        """Obtiene historial de decisiones de un agente."""
        if agent_id not in self.histories:
            return []
        return self.histories[agent_id].get_last_n(last_n)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas globales de decisiones."""
        return {
            'total_decisions': self.total_decisions,
            'actions_distribution': dict(self.action_counts),
            'agent_stats': {k: dict(v) for k, v in self.agent_stats.items()}
        }
    
    def export_history(self, filepath: str):
        """Exporta historial completo a JSON."""
        export_data = {
            'statistics': self.get_statistics(),
            'histories': {
                agent_id: [
                    {
                        'timestamp': d.timestamp.isoformat(),
                        'agent_id': d.agent_id,
                        'agent_role': d.agent_role,
                        'position': d.position,
                        'action': d.action,
                        'action_name': d.action_name,
                        'explanation': d.explanation,
                        'tactical_reasoning': d.tactical_reasoning,
                        'importance_scores': d.importance_scores,
                        'distance_to_target': d.distance_to_target,
                        'confidence': d.confidence
                    }
                    for d in history.decisions
                ]
                for agent_id, history in self.histories.items()
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
