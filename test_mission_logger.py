#!/usr/bin/env python3
"""
Test rápido del Mission Logger
Verifica conexión, inserción y consulta básica
"""

import sys
import numpy as np
from mission_logger import MissionLogger, save_mission_summary

def test_mission_logger():
    """Test básico del Mission Logger"""
    
    print("=" * 60)
    print("🧪 TEST MISSION LOGGER")
    print("=" * 60)
    
    # Solicitar URI
    print("\n📝 Ingresa tu MongoDB Atlas URI:")
    print("Ejemplo: mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority")
    uri = input("URI: ").strip()
    
    if not uri:
        print("❌ No se proporcionó URI")
        return False
    
    # Test 1: Conexión
    print("\n🔌 Test 1: Conexión a MongoDB...")
    logger = MissionLogger(uri=uri)
    
    if not logger.connect():
        print("❌ Error conectando a MongoDB")
        return False
    
    print("✅ Conexión exitosa")
    print(f"   Base de datos: {logger.db_name}")
    print(f"   Colección: {logger.collection.name}")
    
    # Test 2: Guardar misión
    print("\n💾 Test 2: Guardar misión de prueba...")
    
    try:
        mission_id = save_mission_summary(
            mission_logger=logger,
            geo_zone="Test Zone",
            geojson_file="test.geojson",
            configuration={
                "grid_size": 30,
                "num_agents": 2,
                "fire_prob": 0.1,
                "tree_density": 0.3,
                "max_steps": 100
            },
            initial_trees=500,
            final_trees=425,
            fires_extinguished=8,
            water_consumed=32,
            steps_taken=85,
            xai_decisions=[],
            final_grid=np.random.randint(0, 4, (30, 30))
        )
        
        print(f"✅ Misión guardada: {mission_id}")
    except Exception as e:
        print(f"❌ Error guardando misión: {e}")
        return False
    
    # Test 3: Recuperar misión
    print(f"\n🔍 Test 3: Recuperar misión por ID...")
    
    try:
        mission = logger.get_mission_by_id(mission_id)
        
        if mission:
            print(f"✅ Misión recuperada:")
            print(f"   Zona: {mission['geo_zone']}")
            print(f"   Supervivencia: {mission['kpis']['kpi_survival_rate']:.1f}%")
            print(f"   Timestamp: {mission['timestamp']}")
        else:
            print("❌ No se pudo recuperar la misión")
            return False
    except Exception as e:
        print(f"❌ Error recuperando misión: {e}")
        return False
    
    # Test 4: Consultas
    print("\n📊 Test 4: Consultas básicas...")
    
    try:
        # Recientes
        recent = logger.get_recent_missions(limit=5)
        print(f"✅ Misiones recientes: {len(recent)}")
        
        # Top
        top = logger.get_top_missions(limit=3)
        print(f"✅ Top misiones: {len(top)}")
        
        # Estadísticas
        stats = logger.get_statistics()
        if stats:
            print(f"✅ Estadísticas globales:")
            print(f"   Total misiones: {stats['total_missions']}")
            print(f"   Supervivencia promedio: {stats['avg_survival_rate']:.1f}%")
        else:
            print("⚠️  No hay estadísticas disponibles")
    except Exception as e:
        print(f"❌ Error en consultas: {e}")
        return False
    
    # Test 5: Limpieza (opcional)
    print("\n🗑️  Test 5: Limpieza...")
    print("¿Eliminar la misión de prueba? (s/n)")
    response = input().strip().lower()
    
    if response == 's':
        try:
            if logger.delete_mission(mission_id):
                print("✅ Misión de prueba eliminada")
            else:
                print("⚠️  No se pudo eliminar la misión")
        except Exception as e:
            print(f"❌ Error eliminando misión: {e}")
    else:
        print("ℹ️  Misión de prueba conservada")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("✅ TODOS LOS TESTS PASARON")
    print("=" * 60)
    print("\n💡 Próximos pasos:")
    print("   1. Ejecuta una simulación en app.py")
    print("   2. Ve a Tab 7 'Historial de Misiones'")
    print("   3. Explora tus misiones guardadas")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = test_mission_logger()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
