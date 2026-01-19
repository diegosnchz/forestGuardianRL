#!/usr/bin/env python3
"""
Script de demostración de Forest Guardian RL con GIS
Muestra cómo usar los módulos GIS para crear simulaciones de incendios forestales
en bosques reales del mundo.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from gis_locations import BOSQUES_REALES, ESCENARIOS_REALES
from forest_fire_gis import ForestFireGISEnv
from gis_visualization import MapaForestGuardian
import numpy as np


def demo_1_bosques_disponibles():
    """Demostración 1: Explorar bosques disponibles"""
    print("\n" + "="*70)
    print("DEMO 1: BOSQUES REALES DISPONIBLES")
    print("="*70)
    
    print(f"\nTotal de bosques en la base de datos: {len(BOSQUES_REALES)}\n")
    
    for i, bosque in enumerate(BOSQUES_REALES[:5], 1):
        print(f"{i}. {bosque.nombre}")
        print(f"   País: {bosque.pais}")
        print(f"   Coordenadas: ({bosque.latitud:.4f}°, {bosque.longitud:.4f}°)")
        print(f"   Área: {bosque.area_km2:,.0f} km²")
        print(f"   Amenazas: {', '.join(bosque.amenazas)}")
        print()


def demo_2_crear_simulacion_gis():
    """Demostración 2: Crear una simulación GIS básica"""
    print("\n" + "="*70)
    print("DEMO 2: CREAR SIMULACIÓN GIS")
    print("="*70)
    
    # Usar el primer bosque (Amazonas - Perú)
    bosque = BOSQUES_REALES[0]
    print(f"\n🌳 Creando simulación para: {bosque.nombre}")
    print(f"   País: {bosque.pais}")
    print(f"   Coordenadas: ({bosque.latitud:.4f}°, {bosque.longitud:.4f}°)")
    
    # Crear ambiente
    env = ForestFireGISEnv(
        bosque=bosque,
        grid_size=10,
        fire_spread_prob=0.15,
        initial_trees=0.65,
        initial_fires=3,
        num_agents=2
    )
    
    # Inicializar
    obs, info = env.reset()
    print(f"\n✓ Ambiente creado")
    print(f"✓ Grid: {obs.shape}")
    print(f"✓ Drones: {env.num_agents}")
    print(f"✓ Focos iniciales: {len(env.get_fires_geo_positions())}")
    print(f"✓ Árboles: {np.sum(obs == 1)}")


def demo_3_metodos_gis():
    """Demostración 3: Usar métodos GIS del ambiente"""
    print("\n" + "="*70)
    print("DEMO 3: MÉTODOS GIS DEL AMBIENTE")
    print("="*70)
    
    # Crear ambiente con Pantanal
    bosque = BOSQUES_REALES[1]  # Pantanal - Brasil
    env = ForestFireGISEnv(bosque=bosque, grid_size=10)
    obs, info = env.reset()
    
    print(f"\n🌳 Bosque: {bosque.nombre}\n")
    
    # 1. Posiciones geográficas de drones
    agent_geo = env.get_agent_geo_positions()
    print("📍 Posiciones de Drones (lat, lon):")
    for i, (lat, lon) in enumerate(agent_geo, 1):
        print(f"   Dron {i}: ({lat:.4f}°, {lon:.4f}°)")
    
    # 2. Posiciones de incendios
    fires_geo = env.get_fires_geo_positions()
    print(f"\n🔥 Incendios Activos: {len(fires_geo)}")
    for i, (lat, lon) in enumerate(fires_geo, 1):
        print(f"   Fuego {i}: ({lat:.4f}°, {lon:.4f}°)")
    
    # 3. Información del grid
    bounds = env.get_grid_bounds()
    print(f"\n📐 Límites del Grid:")
    print(f"   Norte: {bounds['north']:.4f}°")
    print(f"   Sur: {bounds['south']:.4f}°")
    print(f"   Este: {bounds['east']:.4f}°")
    print(f"   Oeste: {bounds['west']:.4f}°")
    
    # 4. Área cubierta
    area = env.get_coverage_area_km2()
    print(f"\n📊 Área Cubierta: {area:.2f} km²")
    
    # 5. Resumen de la misión
    summary = env.get_mission_summary()
    print(f"\n📋 Resumen:")
    print(f"   Densidad de árboles: {summary['densidad_arboles']:.2%}")
    print(f"   Focos activos: {summary['focos_activos']}")


def demo_4_escenarios_predefinidos():
    """Demostración 4: Usar escenarios predefinidos"""
    print("\n" + "="*70)
    print("DEMO 4: ESCENARIOS PREDEFINIDOS")
    print("="*70)
    
    print(f"\nEscenarios disponibles: {len(ESCENARIOS_REALES)}\n")
    
    for nombre, scenario in list(ESCENARIOS_REALES.items())[:3]:
        print(f"📌 {nombre}")
        bosque = scenario['bosque']
        print(f"   Bosque: {bosque.nombre}")
        print(f"   Ubicación: ({bosque.latitud:.4f}°, {bosque.longitud:.4f}°)")
        print(f"   Parámetros:")
        print(f"     - Focos iniciales: {scenario['initial_fires']}")
        print(f"     - Densidad árboles: {scenario['initial_trees']:.0%}")
        print(f"     - Propagación: {scenario['fire_spread_prob']:.2f}")
        print()


def demo_5_visualizacion():
    """Demostración 5: Crear y mostrar mapas"""
    print("\n" + "="*70)
    print("DEMO 5: CREAR VISUALIZACIÓN CON FOLIUM")
    print("="*70)
    
    # Sierra Nevada
    bosque = BOSQUES_REALES[2]
    print(f"\n🌳 Creando mapa para: {bosque.nombre}\n")
    
    # Crear ambiente
    env = ForestFireGISEnv(bosque=bosque, grid_size=10)
    obs, info = env.reset()
    
    # Crear visualizador
    visualizer = MapaForestGuardian(env, zoom_level=11)
    print("✓ Visualizador creado")
    
    # Crear diferentes tipos de mapas
    print("\nGenerando mapas:")
    
    # 1. Mapa base
    base_map = visualizer.crear_mapa_base()
    print("  ✓ Mapa base")
    
    # 2. Mapa con límites
    with_bounds = visualizer.agregar_limites_grid(base_map)
    print("  ✓ Límites del grid")
    
    # 3. Mapa con drones
    with_drones = visualizer.agregar_drones(with_bounds)
    print("  ✓ Marcadores de drones")
    
    # 4. Mapa completo
    full_map = visualizer.crear_mapa_completo(
        incluir_arboles=True,
        incluir_heatmap=True,
        incluir_grid=True,
        incluir_drones=True,
        incluir_info=True
    )
    print("  ✓ Mapa completo")
    
    # Salvar como archivo HTML
    output_file = Path(__file__).parent / f"demo_map_{bosque.nombre.lower().replace(' ', '_').replace('-', '_')}.html"
    full_map.save(str(output_file))
    print(f"\n💾 Mapa guardado en: {output_file}")


def demo_6_simulacion_paso_a_paso():
    """Demostración 6: Ejecutar pasos de simulación"""
    print("\n" + "="*70)
    print("DEMO 6: SIMULACIÓN PASO A PASO")
    print("="*70)
    
    bosque = BOSQUES_REALES[0]
    print(f"\n🌳 {bosque.nombre}\n")
    
    env = ForestFireGISEnv(
        bosque=bosque,
        grid_size=10,
        initial_fires=2,
        num_agents=1
    )
    
    obs, info = env.reset()
    
    print("Ejecutando 10 pasos de simulación:\n")
    print(f"{'Paso':<6} {'Fuegos':<10} {'Árboles':<10} {'Densidad':<10}")
    print("-" * 40)
    
    for step in range(10):
        # Acción aleatoria
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        
        fires = np.sum(obs == 2)
        trees = np.sum(obs == 1)
        density = trees / (env.grid_size ** 2)
        
        print(f"{step+1:<6} {fires:<10} {trees:<10} {density:<10.2%}")
        
        if terminated:
            print(f"\n✓ Simulación terminada: Todos los fuegos extinguidos")
            break
    
    # Mostrar resultados finales en coordenadas geográficas
    print(f"\n📍 Estado Final (Coordenadas Geográficas):")
    print(f"   Drones: {env.get_agent_geo_positions()}")
    print(f"   Fuegos: {env.get_fires_geo_positions()}")
    print(f"   Árboles salvados: {trees}/{env.grid_size**2}")


def main():
    """Ejecutar todas las demostraciones"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  DEMOSTRACIÓN: FOREST GUARDIAN RL CON GIS  ".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    # Ejecutar demos
    demo_1_bosques_disponibles()
    demo_2_crear_simulacion_gis()
    demo_3_metodos_gis()
    demo_4_escenarios_predefinidos()
    demo_5_visualizacion()
    demo_6_simulacion_paso_a_paso()
    
    print("\n" + "="*70)
    print("✅ TODAS LAS DEMOSTRACIONES COMPLETADAS")
    print("="*70)
    print("\n💡 Próximos pasos:")
    print("   1. Ejecuta 'streamlit run app.py' para usar la interfaz web")
    print("   2. Selecciona 'Bosques Reales' en la barra lateral")
    print("   3. Elige un bosque predefinido o personalizado")
    print("   4. Observa los mapas interactivos en tiempo real\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
