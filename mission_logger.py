"""
Mission Logger para MongoDB Atlas.

Almacena resultados de simulaciones con historial XAI completo
para análisis post-misión y comparación de estrategias.

Autor: Forest Guardian RL Team
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid
import numpy as np

try:
    from pymongo import MongoClient, ASCENDING, DESCENDING
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False


class MissionLogger:
    """
    Logger para almacenar misiones en MongoDB Atlas.
    
    Esquema de documento:
    {
        "mission_id": "uuid",
        "timestamp": "ISO datetime",
        "geo_zone": "nombre del bosque",
        "geojson_file": "path al archivo",
        "configuration": {
            "grid_size": int,
            "num_agents": int,
            "fire_prob": float,
            "tree_density": float,
            "initial_fires": int,
            "max_steps": int
        },
        "kpis": {
            "kpi_survival_rate": float,
            "trees_saved_pct": float,
            "fires_extinguished": int,
            "water_consumed": int,
            "steps_taken": int,
            "mission_success": bool
        },
        "xai_log": [
            {
                "step": int,
                "agent_id": str,
                "agent_role": str,
                "position": [int, int],
                "action": int,
                "action_name": str,
                "explanation": str,
                "tactical_reasoning": str,
                "importance_scores": dict,
                "confidence": float,
                "distance_to_target": float
            }
        ],
        "agent_stats": {
            "ALPHA": {
                "decisions": int,
                "avg_confidence": float,
                "avg_distance": float
            },
            "BRAVO": {...}
        },
        "final_snapshot": {
            "type": "FeatureCollection",
            "features": [...]
        }
    }
    """
    
    def __init__(self, uri: Optional[str] = None, database: str = "forest_guardian"):
        """
        Inicializa el logger de misiones.
        
        Args:
            uri: URI de conexión a MongoDB Atlas
            database: Nombre de la base de datos
        """
        self.uri = uri
        self.database_name = database
        self.collection_name = "mission_logs"
        self.client = None
        self.db = None
        self.collection = None
        self.connected = False
        
        if uri and PYMONGO_AVAILABLE:
            self.connect()
    
    def connect(self) -> bool:
        """
        Conecta a MongoDB Atlas.
        
        Returns:
            True si la conexión fue exitosa
        """
        if not PYMONGO_AVAILABLE:
            print("❌ pymongo no está disponible")
            return False
        
        if not self.uri:
            print("❌ No hay URI de MongoDB configurado")
            return False
        
        try:
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=5000
            )
            
            # Probar conexión
            self.client.admin.command('ping')
            
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            
            # Crear índices
            self._create_indexes()
            
            self.connected = True
            print(f"✅ Conectado a MongoDB Atlas: {self.database_name}.{self.collection_name}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"❌ Error conectando a MongoDB: {e}")
            self.connected = False
            return False
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            self.connected = False
            return False
    
    def _create_indexes(self):
        """Crea índices en la colección para búsquedas eficientes."""
        try:
            # Índice por timestamp (descendente para misiones recientes)
            self.collection.create_index([("timestamp", DESCENDING)])
            
            # Índice por zona geográfica
            self.collection.create_index([("geo_zone", ASCENDING)])
            
            # Índice por tasa de supervivencia
            self.collection.create_index([("kpis.kpi_survival_rate", DESCENDING)])
            
            # Índice compuesto por zona y fecha
            self.collection.create_index([
                ("geo_zone", ASCENDING),
                ("timestamp", DESCENDING)
            ])
            
            print("✅ Índices creados en mission_logs")
        except Exception as e:
            print(f"⚠️ Error creando índices: {e}")
    
    def save_mission(self,
                     geo_zone: str,
                     geojson_file: Optional[str],
                     configuration: Dict[str, Any],
                     kpis: Dict[str, float],
                     xai_decisions: List[Any],
                     agent_stats: Optional[Dict] = None,
                     final_grid: Optional[np.ndarray] = None) -> Optional[str]:
        """
        Guarda una misión en MongoDB Atlas.
        
        Args:
            geo_zone: Nombre de la zona geográfica
            geojson_file: Path al archivo GeoJSON usado
            configuration: Configuración de la simulación
            kpis: KPIs finales de la misión
            xai_decisions: Lista de decisiones XAI
            agent_stats: Estadísticas por agente
            final_grid: Estado final del grid
            
        Returns:
            mission_id si fue exitoso, None si falló
        """
        if not self.connected:
            print("⚠️ No conectado a MongoDB. Misión no guardada.")
            return None
        
        try:
            # Generar ID único
            mission_id = str(uuid.uuid4())
            
            # Preparar log XAI
            xai_log = []
            for decision in xai_decisions:
                xai_log.append({
                    "step": len(xai_log),
                    "agent_id": decision.agent_id,
                    "agent_role": decision.agent_role,
                    "position": list(decision.position),
                    "action": decision.action,
                    "action_name": decision.action_name,
                    "explanation": decision.explanation,
                    "tactical_reasoning": decision.tactical_reasoning,
                    "importance_scores": decision.importance_scores,
                    "confidence": float(decision.confidence),
                    "distance_to_target": float(decision.distance_to_target),
                    "water_level": decision.water_level,
                    "timestamp": decision.timestamp.isoformat()
                })
            
            # Preparar final snapshot (GeoJSON del grid final)
            final_snapshot = None
            if final_grid is not None:
                final_snapshot = self._grid_to_geojson(final_grid)
            
            # Crear documento
            document = {
                "mission_id": mission_id,
                "timestamp": datetime.now().isoformat(),
                "geo_zone": geo_zone,
                "geojson_file": geojson_file,
                "configuration": configuration,
                "kpis": kpis,
                "xai_log": xai_log,
                "agent_stats": agent_stats or {},
                "final_snapshot": final_snapshot
            }
            
            # Insertar en MongoDB
            result = self.collection.insert_one(document)
            
            print(f"✅ Misión guardada: {mission_id}")
            print(f"   - Zona: {geo_zone}")
            print(f"   - KPI: {kpis.get('kpi_survival_rate', 0):.1f}%")
            print(f"   - Decisiones XAI: {len(xai_log)}")
            
            return mission_id
            
        except Exception as e:
            print(f"❌ Error guardando misión: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _grid_to_geojson(self, grid: np.ndarray) -> Dict:
        """
        Convierte grid a GeoJSON simplificado.
        
        Args:
            grid: Estado del grid
            
        Returns:
            Diccionario GeoJSON
        """
        features = []
        rows, cols = grid.shape
        
        # Crear features para fuegos y árboles
        for r in range(rows):
            for c in range(cols):
                if grid[r, c] in [1, 2]:  # Árbol o fuego
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [c, r]
                        },
                        "properties": {
                            "type": "tree" if grid[r, c] == 1 else "fire",
                            "status": "healthy" if grid[r, c] == 1 else "burning"
                        }
                    }
                    features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features
        }
    
    def get_recent_missions(self, limit: int = 10) -> List[Dict]:
        """
        Obtiene misiones recientes.
        
        Args:
            limit: Número máximo de misiones
            
        Returns:
            Lista de documentos de misiones
        """
        if not self.connected:
            return []
        
        try:
            missions = list(
                self.collection.find()
                .sort("timestamp", DESCENDING)
                .limit(limit)
            )
            
            # Convertir ObjectId a string para JSON
            for mission in missions:
                mission['_id'] = str(mission['_id'])
            
            return missions
            
        except Exception as e:
            print(f"❌ Error obteniendo misiones: {e}")
            return []
    
    def get_missions_by_zone(self, geo_zone: str, limit: int = 10) -> List[Dict]:
        """
        Obtiene misiones de una zona específica.
        
        Args:
            geo_zone: Nombre de la zona
            limit: Número máximo de misiones
            
        Returns:
            Lista de documentos de misiones
        """
        if not self.connected:
            return []
        
        try:
            missions = list(
                self.collection.find({"geo_zone": geo_zone})
                .sort("timestamp", DESCENDING)
                .limit(limit)
            )
            
            for mission in missions:
                mission['_id'] = str(mission['_id'])
            
            return missions
            
        except Exception as e:
            print(f"❌ Error obteniendo misiones por zona: {e}")
            return []
    
    def get_top_missions(self, limit: int = 10) -> List[Dict]:
        """
        Obtiene las mejores misiones por KPI de supervivencia.
        
        Args:
            limit: Número máximo de misiones
            
        Returns:
            Lista de documentos de misiones
        """
        if not self.connected:
            return []
        
        try:
            missions = list(
                self.collection.find()
                .sort("kpis.kpi_survival_rate", DESCENDING)
                .limit(limit)
            )
            
            for mission in missions:
                mission['_id'] = str(mission['_id'])
            
            return missions
            
        except Exception as e:
            print(f"❌ Error obteniendo top misiones: {e}")
            return []
    
    def get_mission_by_id(self, mission_id: str) -> Optional[Dict]:
        """
        Obtiene una misión específica por ID.
        
        Args:
            mission_id: ID de la misión
            
        Returns:
            Documento de la misión o None
        """
        if not self.connected:
            return None
        
        try:
            mission = self.collection.find_one({"mission_id": mission_id})
            
            if mission:
                mission['_id'] = str(mission['_id'])
            
            return mission
            
        except Exception as e:
            print(f"❌ Error obteniendo misión: {e}")
            return None
    
    def compare_missions(self, mission_ids: List[str]) -> Dict:
        """
        Compara múltiples misiones.
        
        Args:
            mission_ids: Lista de IDs de misiones
            
        Returns:
            Diccionario con comparación
        """
        if not self.connected:
            return {}
        
        try:
            missions = []
            for mid in mission_ids:
                mission = self.get_mission_by_id(mid)
                if mission:
                    missions.append(mission)
            
            if not missions:
                return {}
            
            # Calcular estadísticas comparativas
            comparison = {
                "missions": missions,
                "comparison": {
                    "best_survival_rate": max(m['kpis']['kpi_survival_rate'] for m in missions),
                    "worst_survival_rate": min(m['kpis']['kpi_survival_rate'] for m in missions),
                    "avg_survival_rate": sum(m['kpis']['kpi_survival_rate'] for m in missions) / len(missions),
                    "best_mission_id": max(missions, key=lambda m: m['kpis']['kpi_survival_rate'])['mission_id'],
                    "total_missions": len(missions)
                }
            }
            
            return comparison
            
        except Exception as e:
            print(f"❌ Error comparando misiones: {e}")
            return {}
    
    def get_statistics(self) -> Dict:
        """
        Obtiene estadísticas globales de todas las misiones.
        
        Returns:
            Diccionario con estadísticas
        """
        if not self.connected:
            return {}
        
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_missions": {"$sum": 1},
                        "avg_survival_rate": {"$avg": "$kpis.kpi_survival_rate"},
                        "max_survival_rate": {"$max": "$kpis.kpi_survival_rate"},
                        "min_survival_rate": {"$min": "$kpis.kpi_survival_rate"},
                        "avg_steps": {"$avg": "$kpis.steps_taken"}
                    }
                }
            ]
            
            result = list(self.collection.aggregate(pipeline))
            
            if result:
                stats = result[0]
                stats.pop('_id', None)
                return stats
            
            return {}
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return {}
    
    def delete_mission(self, mission_id: str) -> bool:
        """
        Elimina una misión.
        
        Args:
            mission_id: ID de la misión
            
        Returns:
            True si fue exitoso
        """
        if not self.connected:
            return False
        
        try:
            result = self.collection.delete_one({"mission_id": mission_id})
            
            if result.deleted_count > 0:
                print(f"✅ Misión eliminada: {mission_id}")
                return True
            else:
                print(f"⚠️ Misión no encontrada: {mission_id}")
                return False
            
        except Exception as e:
            print(f"❌ Error eliminando misión: {e}")
            return False
    
    def clear_all_missions(self) -> bool:
        """
        Elimina todas las misiones (usar con precaución).
        
        Returns:
            True si fue exitoso
        """
        if not self.connected:
            return False
        
        try:
            result = self.collection.delete_many({})
            print(f"✅ {result.deleted_count} misiones eliminadas")
            return True
            
        except Exception as e:
            print(f"❌ Error limpiando misiones: {e}")
            return False
    
    def close(self):
        """Cierra la conexión a MongoDB."""
        if self.client:
            self.client.close()
            self.connected = False
            print("✅ Conexión a MongoDB cerrada")


def save_mission_summary(mission_logger: Optional[MissionLogger],
                         geo_zone: str,
                         geojson_file: Optional[str],
                         configuration: Dict,
                         initial_trees: int,
                         final_trees: int,
                         fires_extinguished: int,
                         water_consumed: int,
                         steps_taken: int,
                         xai_decisions: List,
                         final_grid: Optional[np.ndarray] = None) -> Optional[str]:
    """
    Función helper para guardar resumen de misión.
    
    Args:
        mission_logger: Instancia de MissionLogger
        geo_zone: Nombre de la zona
        geojson_file: Path al archivo GeoJSON
        configuration: Configuración de la simulación
        initial_trees: Árboles iniciales
        final_trees: Árboles finales
        fires_extinguished: Fuegos extinguidos
        water_consumed: Agua consumida
        steps_taken: Pasos tomados
        xai_decisions: Lista de decisiones XAI
        final_grid: Estado final del grid
        
    Returns:
        mission_id si fue exitoso
    """
    if not mission_logger or not mission_logger.connected:
        print("⚠️ Mission logger no disponible, misión no guardada")
        return None
    
    # Calcular KPIs
    survival_rate = (final_trees / initial_trees * 100) if initial_trees > 0 else 0.0
    mission_success = survival_rate >= 70.0  # Umbral de éxito
    
    kpis = {
        "kpi_survival_rate": float(survival_rate),
        "trees_saved_pct": float(survival_rate),
        "fires_extinguished": fires_extinguished,
        "water_consumed": water_consumed,
        "steps_taken": steps_taken,
        "mission_success": mission_success,
        "initial_trees": initial_trees,
        "final_trees": final_trees
    }
    
    # Calcular estadísticas por agente
    agent_stats = {}
    for agent_id in set(d.agent_id for d in xai_decisions):
        agent_decisions = [d for d in xai_decisions if d.agent_id == agent_id]
        if agent_decisions:
            agent_stats[agent_id] = {
                "decisions": len(agent_decisions),
                "avg_confidence": float(np.mean([d.confidence for d in agent_decisions])),
                "avg_distance": float(np.mean([d.distance_to_target for d in agent_decisions])),
                "actions": {}
            }
            
            # Contar acciones
            for d in agent_decisions:
                action_name = d.action_name
                agent_stats[agent_id]["actions"][action_name] = \
                    agent_stats[agent_id]["actions"].get(action_name, 0) + 1
    
    # Guardar en MongoDB
    mission_id = mission_logger.save_mission(
        geo_zone=geo_zone,
        geojson_file=geojson_file,
        configuration=configuration,
        kpis=kpis,
        xai_decisions=xai_decisions,
        agent_stats=agent_stats,
        final_grid=final_grid
    )
    
    return mission_id
