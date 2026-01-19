"""
Ejemplos de consultas geoespaciales para Forest Guardian RL.

Este script demuestra cómo realizar consultas geoespaciales
en MongoDB Atlas para operaciones de drones forestales.

Autor: Forest Guardian RL Team
"""

from pymongo import MongoClient
from typing import List, Dict, Any, Tuple
import sys

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

MONGODB_URI = "mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority"
DATABASE_NAME = "forest_guardian"
COLLECTION_NAME = "mapa_forestal"

# ============================================================================


class ForestGuardianQueries:
    """
    Clase con ejemplos de consultas geoespaciales para Forest Guardian RL.
    """
    
    def __init__(self, uri: str, db_name: str, collection_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
    
    def find_zones_near_point(self, longitude: float, latitude: float, 
                              max_distance_km: float = 5.0) -> List[Dict]:
        """
        Encuentra zonas forestales cerca de un punto (posición del drone).
        
        Args:
            longitude: Longitud del punto
            latitude: Latitud del punto
            max_distance_km: Radio de búsqueda en kilómetros
            
        Returns:
            Lista de zonas ordenadas por proximidad
        """
        point = {
            "type": "Point",
            "coordinates": [longitude, latitude]
        }
        
        results = self.collection.find({
            "location": {
                "$near": {
                    "$geometry": point,
                    "$maxDistance": max_distance_km * 1000  # Convertir a metros
                }
            }
        })
        
        return list(results)
    
    def find_zones_within_polygon(self, coordinates: List[List[float]]) -> List[Dict]:
        """
        Encuentra zonas dentro de un polígono (área de operación).
        
        Args:
            coordinates: Lista de coordenadas [[lon, lat], ...]
            
        Returns:
            Lista de zonas dentro del polígono
        """
        # Asegurar que el polígono esté cerrado
        if coordinates[0] != coordinates[-1]:
            coordinates.append(coordinates[0])
        
        polygon = {
            "type": "Polygon",
            "coordinates": [coordinates]
        }
        
        results = self.collection.find({
            "location": {
                "$geoWithin": {
                    "$geometry": polygon
                }
            }
        })
        
        return list(results)
    
    def find_high_risk_zones(self) -> List[Dict]:
        """
        Encuentra todas las zonas de alto riesgo de incendio.
        
        Returns:
            Lista de zonas de alto riesgo
        """
        results = self.collection.find({
            "properties.riesgo_incendio": "alto"
        })
        
        return list(results)
    
    def find_zones_by_type(self, zone_type: str) -> List[Dict]:
        """
        Encuentra zonas por tipo (coniferas, mixto, protegida, etc.).
        
        Args:
            zone_type: Tipo de zona a buscar
            
        Returns:
            Lista de zonas del tipo especificado
        """
        results = self.collection.find({
            "tipo": zone_type
        })
        
        return list(results)
    
    def find_monitoring_stations_near_fire(self, fire_longitude: float, 
                                          fire_latitude: float,
                                          max_distance_km: float = 10.0) -> List[Dict]:
        """
        Encuentra estaciones de monitoreo cerca de un incendio.
        
        Args:
            fire_longitude: Longitud del incendio
            fire_latitude: Latitud del incendio
            max_distance_km: Radio de búsqueda
            
        Returns:
            Lista de estaciones cercanas
        """
        point = {
            "type": "Point",
            "coordinates": [fire_longitude, fire_latitude]
        }
        
        results = self.collection.find({
            "tipo": "estacion",
            "properties.operativa": True,
            "location": {
                "$near": {
                    "$geometry": point,
                    "$maxDistance": max_distance_km * 1000
                }
            }
        })
        
        return list(results)
    
    def calculate_optimal_response_path(self, fire_longitude: float,
                                       fire_latitude: float) -> Dict[str, Any]:
        """
        Calcula la respuesta óptima a un incendio.
        
        Encuentra la estación más cercana y zonas de alto riesgo alrededor.
        
        Args:
            fire_longitude: Longitud del incendio
            fire_latitude: Latitud del incendio
            
        Returns:
            Diccionario con estación más cercana y zonas de riesgo
        """
        # Encontrar estación más cercana
        stations = self.find_monitoring_stations_near_fire(
            fire_longitude, fire_latitude, max_distance_km=20.0
        )
        
        if not stations:
            return {
                "status": "error",
                "message": "No se encontraron estaciones operativas cercanas"
            }
        
        closest_station = stations[0]
        
        # Encontrar zonas de riesgo alrededor del incendio
        risk_zones = []
        nearby_zones = self.find_zones_near_point(
            fire_longitude, fire_latitude, max_distance_km=3.0
        )
        
        for zone in nearby_zones:
            risk_level = zone.get("properties", {}).get("riesgo_incendio", "medio")
            if risk_level in ["alto", "medio"]:
                risk_zones.append(zone)
        
        return {
            "status": "success",
            "closest_station": {
                "name": closest_station.get("nombre"),
                "coordinates": closest_station["location"]["coordinates"],
                "drone_capacity": closest_station.get("properties", {}).get("capacidad_drones", 0)
            },
            "risk_zones": [
                {
                    "name": z.get("nombre"),
                    "type": z.get("tipo"),
                    "risk_level": z.get("properties", {}).get("riesgo_incendio"),
                    "area": z.get("area")
                }
                for z in risk_zones
            ],
            "recommendation": self._generate_recommendation(len(risk_zones), closest_station)
        }
    
    def _generate_recommendation(self, risk_zones_count: int, station: Dict) -> str:
        """
        Genera recomendación basada en el análisis.
        """
        drone_capacity = station.get("properties", {}).get("capacidad_drones", 0)
        
        if risk_zones_count > drone_capacity:
            return (f"⚠️ ALERTA CRÍTICA: {risk_zones_count} zonas de riesgo detectadas. "
                   f"Estación tiene capacidad para {drone_capacity} drones. "
                   f"Se requiere apoyo adicional.")
        elif risk_zones_count > 0:
            return (f"✅ RESPUESTA VIABLE: {risk_zones_count} zonas de riesgo. "
                   f"Desplegar {risk_zones_count} drones desde {station.get('nombre')}.")
        else:
            return "✅ Sin zonas de riesgo inmediatas detectadas."
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de la base de datos.
        
        Returns:
            Diccionario con estadísticas
        """
        total = self.collection.count_documents({})
        
        # Contar por tipo
        types = self.collection.distinct("tipo")
        type_counts = {}
        for t in types:
            count = self.collection.count_documents({"tipo": t})
            type_counts[t] = count
        
        # Contar por nivel de riesgo
        risk_levels = ["bajo", "medio", "alto"]
        risk_counts = {}
        for level in risk_levels:
            count = self.collection.count_documents({
                "properties.riesgo_incendio": level
            })
            risk_counts[level] = count
        
        # Área total
        total_area = 0
        for doc in self.collection.find({"area": {"$exists": True}}):
            total_area += doc.get("area", 0)
        
        return {
            "total_documents": total,
            "types": type_counts,
            "risk_levels": risk_counts,
            "total_area_hectares": round(total_area, 2)
        }
    
    def close(self):
        """Cierra la conexión con MongoDB."""
        self.client.close()


# ============================================================================
# EJEMPLOS DE USO
# ============================================================================

def main():
    """
    Función principal con ejemplos de uso.
    """
    print("\n" + "="*70)
    print("🌲 FOREST GUARDIAN RL - EJEMPLOS DE CONSULTAS GEOESPACIALES 🌲")
    print("="*70 + "\n")
    
    # Validar configuración
    if "<username>" in MONGODB_URI or "<password>" in MONGODB_URI:
        print("❌ Error: Debes configurar tu URI de MongoDB Atlas")
        print("   Edita las variables MONGODB_URI en este script\n")
        sys.exit(1)
    
    # Crear instancia
    queries = ForestGuardianQueries(MONGODB_URI, DATABASE_NAME, COLLECTION_NAME)
    
    try:
        # ====================================================================
        # EJEMPLO 1: Estadísticas generales
        # ====================================================================
        print("📊 EJEMPLO 1: Estadísticas Generales")
        print("-" * 70)
        
        stats = queries.get_statistics()
        print(f"Total de documentos: {stats['total_documents']}")
        print(f"Área total: {stats['total_area_hectares']} hectáreas")
        
        print("\nDocumentos por tipo:")
        for tipo, count in stats['types'].items():
            print(f"  - {tipo}: {count}")
        
        print("\nZonas por nivel de riesgo:")
        for level, count in stats['risk_levels'].items():
            print(f"  - {level}: {count}")
        
        # ====================================================================
        # EJEMPLO 2: Buscar zonas cerca de un punto (drone)
        # ====================================================================
        print("\n\n🚁 EJEMPLO 2: Zonas cerca de la posición del drone")
        print("-" * 70)
        
        drone_lon = -99.1950
        drone_lat = 19.4150
        
        print(f"Posición del drone: [{drone_lon}, {drone_lat}]")
        print("Buscando zonas dentro de 5 km...\n")
        
        nearby = queries.find_zones_near_point(drone_lon, drone_lat, max_distance_km=5.0)
        
        for i, zone in enumerate(nearby[:5], 1):  # Mostrar primeras 5
            name = zone.get("nombre", "Sin nombre")
            tipo = zone.get("tipo", "desconocido")
            coords = zone["location"]["coordinates"]
            print(f"{i}. {name}")
            print(f"   Tipo: {tipo}")
            print(f"   Coordenadas: {coords}")
        
        # ====================================================================
        # EJEMPLO 3: Zonas dentro de un área de operación
        # ====================================================================
        print("\n\n📍 EJEMPLO 3: Zonas dentro del área de operación")
        print("-" * 70)
        
        # Definir polígono de área de operación
        area_coords = [
            [-99.2100, 19.4000],
            [-99.1800, 19.4000],
            [-99.1800, 19.4300],
            [-99.2100, 19.4300],
            [-99.2100, 19.4000]
        ]
        
        print("Buscando zonas dentro del polígono de operación...\n")
        
        zones_in_area = queries.find_zones_within_polygon(area_coords)
        
        for zone in zones_in_area:
            name = zone.get("nombre", "Sin nombre")
            tipo = zone.get("tipo", "desconocido")
            print(f"- {name} ({tipo})")
        
        # ====================================================================
        # EJEMPLO 4: Zonas de alto riesgo
        # ====================================================================
        print("\n\n⚠️  EJEMPLO 4: Zonas de alto riesgo de incendio")
        print("-" * 70)
        
        high_risk = queries.find_high_risk_zones()
        
        if high_risk:
            print(f"Se encontraron {len(high_risk)} zonas de alto riesgo:\n")
            for zone in high_risk:
                name = zone.get("nombre", "Sin nombre")
                area = zone.get("area", "N/A")
                coords = zone["location"]["coordinates"]
                print(f"- {name}")
                print(f"  Área: {area} hectáreas")
                print(f"  Ubicación: {coords}")
        else:
            print("✅ No hay zonas de alto riesgo registradas")
        
        # ====================================================================
        # EJEMPLO 5: Respuesta óptima a incendio
        # ====================================================================
        print("\n\n🔥 EJEMPLO 5: Cálculo de respuesta óptima a incendio")
        print("-" * 70)
        
        fire_lon = -99.1980
        fire_lat = 19.4180
        
        print(f"🔥 Incendio detectado en: [{fire_lon}, {fire_lat}]")
        print("Calculando respuesta óptima...\n")
        
        response = queries.calculate_optimal_response_path(fire_lon, fire_lat)
        
        if response["status"] == "success":
            station = response["closest_station"]
            print(f"📡 Estación más cercana: {station['name']}")
            print(f"   Coordenadas: {station['coordinates']}")
            print(f"   Capacidad de drones: {station['drone_capacity']}")
            
            print(f"\n⚠️  Zonas de riesgo cercanas ({len(response['risk_zones'])}):")
            for zone in response["risk_zones"]:
                print(f"   - {zone['name']} ({zone['type']})")
                print(f"     Riesgo: {zone['risk_level']}, Área: {zone['area']} ha")
            
            print(f"\n💡 Recomendación:")
            print(f"   {response['recommendation']}")
        else:
            print(f"❌ {response['message']}")
        
        # ====================================================================
        # EJEMPLO 6: Buscar por tipo
        # ====================================================================
        print("\n\n🏛️  EJEMPLO 6: Zonas protegidas")
        print("-" * 70)
        
        protected = queries.find_zones_by_type("protegida")
        
        if protected:
            print(f"Se encontraron {len(protected)} zonas protegidas:\n")
            for zone in protected:
                name = zone.get("nombre", "Sin nombre")
                area = zone.get("area", "N/A")
                print(f"- {name} ({area} hectáreas)")
        else:
            print("No hay zonas protegidas registradas")
        
        print("\n" + "="*70)
        print("✅ Ejemplos completados exitosamente")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error ejecutando ejemplos: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        queries.close()
        print("🔌 Conexión cerrada\n")


if __name__ == "__main__":
    main()
