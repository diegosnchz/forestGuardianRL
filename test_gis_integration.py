#!/usr/bin/env python3
"""
Script de prueba para validar la integración GIS del sistema Forest Guardian RL
"""

import sys
import traceback
from pathlib import Path

# Agregar directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Prueba que todos los módulos se importan correctamente"""
    print("=" * 60)
    print("TEST 1: Verificar importaciones")
    print("=" * 60)
    
    try:
        print("✓ Importando forest_fire_env...")
        from forest_fire_env import ForestFireEnv
        
        print("✓ Importando gis_locations...")
        from gis_locations import BosqueReal, BOSQUES_REALES, ESCENARIOS_REALES
        
        print("✓ Importando forest_fire_gis...")
        from forest_fire_gis import ForestFireGISEnv
        
        print("✓ Importando gis_visualization...")
        from gis_visualization import MapaForestGuardian
        
        print("\n✅ Todas las importaciones fueron exitosas\n")
        return True
    except Exception as e:
        print(f"\n❌ Error en importaciones:\n{traceback.format_exc()}\n")
        return False

def test_bosques_reales():
    """Prueba que los bosques reales estén correctamente definidos"""
    print("=" * 60)
    print("TEST 2: Verificar bosques reales")
    print("=" * 60)
    
    try:
        from gis_locations import BOSQUES_REALES, ESCENARIOS_REALES
        
        print(f"Total de bosques: {len(BOSQUES_REALES)}")
        print(f"Total de escenarios: {len(ESCENARIOS_REALES)}")
        
        # Mostrar primeros 3 bosques
        for i, bosque in enumerate(BOSQUES_REALES[:3]):
            print(f"\n  {i+1}. {bosque.nombre}")
            print(f"     País: {bosque.pais}")
            print(f"     Coordenadas: ({bosque.latitud:.4f}, {bosque.longitud:.4f})")
            print(f"     Área: {bosque.area_km2:.0f} km²")
        
        print(f"\n... ({len(BOSQUES_REALES) - 3} más)")
        
        print("\nEscenarios predefinidos:")
        for nombre in list(ESCENARIOS_REALES.keys())[:3]:
            print(f"  - {nombre}")
        
        print("\n✅ Bosques reales verificados correctamente\n")
        return True
    except Exception as e:
        print(f"\n❌ Error en bosques reales:\n{traceback.format_exc()}\n")
        return False

def test_gis_env():
    """Prueba la creación de un ambiente GIS"""
    print("=" * 60)
    print("TEST 3: Crear ambiente ForestFireGISEnv")
    print("=" * 60)
    
    try:
        from gis_locations import BOSQUES_REALES
        from forest_fire_gis import ForestFireGISEnv
        
        bosque = BOSQUES_REALES[0]
        print(f"Creando ambiente para: {bosque.nombre}")
        
        env = ForestFireGISEnv(
            bosque=bosque,
            grid_size=10,
            fire_spread_prob=0.15,
            initial_trees=0.65,
            initial_fires=3,
            num_agents=2
        )
        
        obs, info = env.reset()
        print(f"✓ Ambiente creado")
        print(f"✓ Grid shape: {obs.shape}")
        print(f"✓ Posiciones de agentes: {env.agent_positions}")
        
        # Pruebas de métodos GIS
        geo_positions = env.get_agent_geo_positions()
        print(f"✓ Posiciones geográficas: {geo_positions}")
        
        fires = env.get_fires_geo_positions()
        print(f"✓ Fuegos detectados: {len(fires)}")
        
        trees = env.get_trees_geo_positions()
        print(f"✓ Árboles detectados: {len(trees)}")
        
        bounds = env.get_grid_bounds()
        print(f"✓ Límites del grid: N={bounds['north']:.4f}, S={bounds['south']:.4f}")
        
        area = env.get_coverage_area_km2()
        print(f"✓ Área cubierta: {area:.2f} km²")
        
        print("\n✅ Ambiente GIS funcionando correctamente\n")
        return True
    except Exception as e:
        print(f"\n❌ Error en ambiente GIS:\n{traceback.format_exc()}\n")
        return False

def test_visualization():
    """Prueba la visualización GIS"""
    print("=" * 60)
    print("TEST 4: Crear visualización con Folium")
    print("=" * 60)
    
    try:
        from gis_locations import BOSQUES_REALES
        from forest_fire_gis import ForestFireGISEnv
        from gis_visualization import MapaForestGuardian
        
        bosque = BOSQUES_REALES[0]
        env = ForestFireGISEnv(bosque=bosque, grid_size=10)
        env.reset()
        
        print(f"Creando visualización para: {bosque.nombre}")
        
        visualizer = MapaForestGuardian(env, zoom_level=11)
        print("✓ Visualizador creado")
        
        # Crear mapa base
        mapa = visualizer.crear_mapa_base()
        print("✓ Mapa base creado")
        
        # Agregar elementos
        mapa = visualizer.agregar_informacion_bosque(mapa)
        print("✓ Información de bosque agregada")
        
        mapa = visualizer.agregar_drones(mapa)
        print("✓ Drones agregados")
        
        mapa = visualizer.agregar_limites_grid(mapa)
        print("✓ Límites del grid agregados")
        
        # Intentar crear mapa completo
        mapa_completo = visualizer.crear_mapa_completo(
            mostrar_heatmap=True,
            mostrar_grid=True,
            mostrar_drones=True,
            mostrar_fuegos=True,
            mostrar_arboles=True
        )
        print("✓ Mapa completo creado")
        
        print("\n✅ Visualización GIS funcionando correctamente\n")
        return True
    except Exception as e:
        print(f"\n❌ Error en visualización:\n{traceback.format_exc()}\n")
        return False

def test_streamlit_app():
    """Verifica que app.py puede importar todos los módulos"""
    print("=" * 60)
    print("TEST 5: Verificar app.py")
    print("=" * 60)
    
    try:
        # Solo verificar que el archivo existe y tiene sintaxis válida
        app_file = Path(__file__).parent / "app.py"
        
        if not app_file.exists():
            print(f"❌ archivo app.py no encontrado en {app_file}")
            return False
        
        print(f"✓ Archivo app.py encontrado")
        
        # Verificar sintaxis con Python AST
        import ast
        with open(app_file) as f:
            code = f.read()
        
        ast.parse(code)
        print("✓ Sintaxis de app.py válida")
        
        # Verificar que tiene los imports GIS
        if 'gis_locations' in code and 'forest_fire_gis' in code and 'gis_visualization' in code:
            print("✓ Imports GIS presentes en app.py")
        else:
            print("⚠️  Algunos imports GIS pueden estar ausentes")
        
        print("\n✅ app.py parece estar correctamente configurado\n")
        return True
    except Exception as e:
        print(f"\n❌ Error en app.py:\n{traceback.format_exc()}\n")
        return False

def main():
    """Ejecuta todos los tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  PRUEBA DE INTEGRACIÓN GIS - FOREST GUARDIAN RL  ".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = []
    
    results.append(("Importaciones", test_imports()))
    results.append(("Bosques Reales", test_bosques_reales()))
    results.append(("Ambiente GIS", test_gis_env()))
    results.append(("Visualización Folium", test_visualization()))
    results.append(("Archivo app.py", test_streamlit_app()))
    
    # Resumen
    print("=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("\n🎉 ¡INTEGRACIÓN GIS COMPLETAMENTE FUNCIONAL!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} prueba(s) fallida(s)")
        return 1

if __name__ == "__main__":
    exit(main())
