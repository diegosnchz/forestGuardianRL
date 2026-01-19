#!/usr/bin/env python3
"""
Test del Modelo de Rothermel en ForestFireEnv
Valida propagación direccional del viento, efecto de humedad y asimilación MongoDB
"""

import numpy as np
import sys
from forest_fire_env import ForestFireEnv

def test_wind_directional_propagation():
    """Test 1: Verificar que el fuego se propaga a favor del viento"""
    print("\n" + "="*60)
    print("🔥 TEST 1: Propagación Direccional del Viento")
    print("="*60)
    
    env = ForestFireEnv(grid_size=30, fire_spread_prob=0.15)
    env.reset()
    
    # Configurar viento fuerte hacia el Este (90°)
    env.wind_speed = 20.0
    env.wind_direction = 90.0
    
    print(f"   Viento configurado: {env.wind_speed} km/h hacia {env.wind_direction}°")
    
    # Limpiar grid y colocar fuego en centro
    env.grid[:, :] = 0  # Limpiar todo
    center = env.grid_size // 2
    
    # Crear línea vertical de árboles
    for i in range(center - 5, center + 6):
        for j in range(center - 1, center + 10):
            env.grid[i, j] = 1  # Árboles
    
    # Fuego en el centro-izquierdo
    env.grid[center, center] = 2
    
    initial_fire_pos = np.argwhere(env.grid == 2)
    print(f"   Posición inicial del fuego: {initial_fire_pos[0]}")
    
    # Simular 30 pasos sin agentes
    for step in range(30):
        env.step([4, 4, 4])  # Todos idle
    
    # Analizar propagación
    fire_positions = np.argwhere(env.grid == 2)
    
    if len(fire_positions) > 1:
        # Calcular centro de masa del fuego
        mean_row = np.mean(fire_positions[:, 0])
        mean_col = np.mean(fire_positions[:, 1])
        
        print(f"   Centro de masa del fuego después de 30 pasos: ({mean_row:.1f}, {mean_col:.1f})")
        print(f"   Desplazamiento horizontal: {mean_col - center:.1f} celdas")
        
        # Verificar que se propagó hacia el Este (columnas mayores)
        if mean_col > center + 1.0:
            print("   ✅ TEST PASADO: Fuego se propagó a favor del viento (hacia el Este)")
            return True
        else:
            print("   ❌ TEST FALLIDO: Fuego no se propagó suficientemente hacia el Este")
            return False
    else:
        print("   ⚠️ TEST INCONCLUSO: Fuego no se propagó")
        return False


def test_fuel_moisture_effect():
    """Test 2: Verificar que la humedad reduce la propagación"""
    print("\n" + "="*60)
    print("💧 TEST 2: Efecto de Humedad del Combustible")
    print("="*60)
    
    # Caso A: Combustible muy seco
    print("\n   🔥 Caso A: Combustible MUY SECO (5%)")
    env_dry = ForestFireEnv(grid_size=25, fire_spread_prob=0.15)
    env_dry.reset()
    env_dry.fuel_moisture[:, :] = 5.0  # Muy seco
    
    # Configurar escenario estándar
    env_dry.wind_speed = 10.0
    env_dry.wind_direction = 0.0
    env_dry.grid[:, :] = 1  # Todo árboles
    center = env_dry.grid_size // 2
    env_dry.grid[center, center] = 2  # Fuego central
    
    # Simular 40 pasos
    for _ in range(40):
        env_dry.step([4, 4, 4])
    
    fires_dry = np.sum(env_dry.grid == 2)
    print(f"   Fuegos activos después de 40 pasos: {fires_dry}")
    
    # Caso B: Combustible muy húmedo
    print("\n   💧 Caso B: Combustible MUY HÚMEDO (30%)")
    env_wet = ForestFireEnv(grid_size=25, fire_spread_prob=0.15)
    env_wet.reset()
    env_wet.fuel_moisture[:, :] = 30.0  # Muy húmedo
    
    # Mismo escenario
    env_wet.wind_speed = 10.0
    env_wet.wind_direction = 0.0
    env_wet.grid[:, :] = 1
    env_wet.grid[center, center] = 2
    
    # Simular 40 pasos
    for _ in range(40):
        env_wet.step([4, 4, 4])
    
    fires_wet = np.sum(env_wet.grid == 2)
    print(f"   Fuegos activos después de 40 pasos: {fires_wet}")
    
    # Comparar
    ratio = fires_dry / (fires_wet + 1)  # +1 para evitar división por 0
    print(f"\n   Ratio de propagación (seco/húmedo): {ratio:.2f}x")
    
    if ratio > 2.0:
        print(f"   ✅ TEST PASADO: Humedad reduce significativamente la propagación ({ratio:.1f}x)")
        return True
    else:
        print(f"   ❌ TEST FALLIDO: Efecto de humedad insuficiente ({ratio:.1f}x, esperado > 2.0x)")
        return False


def test_slope_effect():
    """Test 3: Verificar que el fuego sube más rápido cuesta arriba"""
    print("\n" + "="*60)
    print("⛰️  TEST 3: Efecto de Pendiente (Slope)")
    print("="*60)
    
    env = ForestFireEnv(grid_size=30, fire_spread_prob=0.1)
    env.reset()
    
    # Crear pendiente artificial: elevación aumenta hacia el Norte
    for i in range(env.grid_size):
        for j in range(env.grid_size):
            env.elevation[i, j] = (env.grid_size - i) / env.grid_size
    
    print("   Terreno configurado: pendiente ascendente hacia el Norte")
    print(f"   Elevación Sur (fila 29): {env.elevation[29, 15]:.2f}")
    print(f"   Elevación Norte (fila 0): {env.elevation[0, 15]:.2f}")
    
    # Colocar fuego en el Sur (fila alta)
    env.grid[:, :] = 1  # Todo árboles
    env.grid[25, 15] = 2  # Fuego en el Sur
    
    # Sin viento para aislar efecto de pendiente
    env.wind_speed = 0.0
    
    # Simular 50 pasos
    for _ in range(50):
        env.step([4, 4, 4])
    
    # Analizar propagación
    fire_positions = np.argwhere(env.grid == 2)
    
    if len(fire_positions) > 1:
        mean_row = np.mean(fire_positions[:, 0])
        print(f"\n   Fila promedio del fuego: {mean_row:.1f}")
        print(f"   Desplazamiento hacia el Norte: {25 - mean_row:.1f} celdas")
        
        if mean_row < 25:  # Cualquier desplazamiento hacia el Norte
            print("   ✅ TEST PASADO: Fuego se propagó cuesta arriba (hacia el Norte)")
            return True
        else:
            print("   ❌ TEST FALLIDO: Fuego no se propagó significativamente cuesta arriba")
            return False
    else:
        print("   ⚠️ TEST INCONCLUSO: Fuego no se propagó")
        return False


def test_rothermel_probability_calculation():
    """Test 4: Verificar cálculo de probabilidad de Rothermel"""
    print("\n" + "="*60)
    print("📐 TEST 4: Cálculo de Probabilidad de Rothermel")
    print("="*60)
    
    env = ForestFireEnv(grid_size=20)
    env.reset()
    
    # Configurar condiciones extremas
    env.wind_speed = 20.0
    env.wind_direction = 0.0  # Norte
    env.fuel_moisture[:, :] = 5.0  # Muy seco
    
    # Crear pendiente fuerte hacia el Norte
    for i in range(env.grid_size):
        env.elevation[i, :] = (env.grid_size - i) / env.grid_size
    
    print("\n   Condiciones configuradas:")
    print(f"   - Viento: {env.wind_speed} km/h hacia {env.wind_direction}°")
    print(f"   - Humedad: {env.fuel_moisture[10, 10]:.1f}%")
    print(f"   - Pendiente: {env.elevation[5, 10] - env.elevation[10, 10]:.2f}")
    
    # Caso 1: A favor del viento, cuesta arriba, seco (peor caso)
    from_pos = (10, 10)
    to_pos = (9, 10)  # Norte (a favor del viento + cuesta arriba)
    
    prob_worst = env._calculate_fire_spread_probability(from_pos, to_pos)
    print(f"\n   Peor caso (viento+pendiente+seco): {prob_worst:.4f}")
    
    # Caso 2: Contra el viento, cuesta abajo, húmedo (mejor caso)
    env.wind_direction = 180.0  # Sur
    env.fuel_moisture[:, :] = 30.0  # Húmedo
    to_pos = (11, 10)  # Sur (contra viento + cuesta abajo)
    
    prob_best = env._calculate_fire_spread_probability(from_pos, to_pos)
    print(f"   Mejor caso (contra viento+abajo+húmedo): {prob_best:.4f}")
    
    # Verificar rango
    dynamic_range = prob_worst / (prob_best + 1e-6)
    print(f"\n   Rango dinámico: {dynamic_range:.1f}x")
    
    if prob_worst > prob_best * 10:
        print(f"   ✅ TEST PASADO: Modelo tiene alto rango dinámico ({dynamic_range:.0f}x)")
        return True
    else:
        print(f"   ❌ TEST FALLIDO: Rango dinámico insuficiente ({dynamic_range:.1f}x)")
        return False


def test_mongodb_updates():
    """Test 5: Verificar actualizaciones de humedad en MongoDB"""
    print("\n" + "="*60)
    print("🛰️  TEST 5: Asimilación de Datos UAV (MongoDB)")
    print("="*60)
    
    env = ForestFireEnv(grid_size=20)
    env.reset()
    
    if not env.mongodb_enabled:
        print("   ⚠️ MongoDB no configurado - TEST OMITIDO")
        print("   💡 Configura MONGODB_URI para habilitar este test")
        return None
    
    print(f"   ✅ MongoDB conectado")
    print(f"   Database: forestguardian")
    print(f"   Collection: fuel_moisture_updates")
    
    # Contar documentos antes
    count_before = env.mongodb_collection.count_documents({})
    print(f"\n   Documentos antes: {count_before}")
    
    # Mover agentes para generar actualizaciones
    initial_pos = env.agent_positions.copy()
    
    for step in range(10):
        # Mover aleatoriamente
        actions = [np.random.randint(0, 4) for _ in range(env.num_agents)]
        env.step(actions)
    
    # Contar documentos después
    count_after = env.mongodb_collection.count_documents({})
    print(f"   Documentos después: {count_after}")
    
    updates = count_after - count_before
    print(f"\n   Actualizaciones generadas: {updates}")
    print(f"   Contador interno: {env.moisture_updates_count}")
    
    if updates > 0:
        # Obtener una actualización de ejemplo
        sample = env.mongodb_collection.find_one({'step': {'$exists': True}})
        
        if sample:
            print(f"\n   Ejemplo de documento:")
            print(f"   - Agente: {sample.get('agent_id')}")
            print(f"   - Paso: {sample.get('step')}")
            print(f"   - Posición: {sample.get('position')}")
            print(f"   - Humedad: {sample.get('fuel_moisture', {}).get('value'):.1f}%")
            print(f"   - Viento: {sample.get('environmental_data', {}).get('wind_speed'):.1f} km/h")
        
        print("\n   ✅ TEST PASADO: Actualizaciones guardadas correctamente en MongoDB")
        return True
    else:
        print("\n   ❌ TEST FALLIDO: No se guardaron actualizaciones en MongoDB")
        return False


def test_fuel_moisture_stats():
    """Test 6: Verificar estadísticas de humedad"""
    print("\n" + "="*60)
    print("📊 TEST 6: Estadísticas de Humedad del Combustible")
    print("="*60)
    
    env = ForestFireEnv(grid_size=30)
    env.reset()
    
    stats = env.get_fuel_moisture_stats()
    
    print(f"\n   Estadísticas iniciales:")
    print(f"   - Media: {stats['mean']:.2f}%")
    print(f"   - Mínimo: {stats['min']:.2f}%")
    print(f"   - Máximo: {stats['max']:.2f}%")
    print(f"   - Desv. Std: {stats['std']:.2f}%")
    print(f"   - Actualizaciones: {stats['updates_count']}")
    
    # Verificar rango realista
    if 5.0 <= stats['min'] <= 35.0 and 5.0 <= stats['max'] <= 35.0:
        print("\n   ✅ TEST PASADO: Valores de humedad en rango realista (5-35%)")
        return True
    else:
        print(f"\n   ❌ TEST FALLIDO: Valores fuera de rango esperado")
        return False


def main():
    """Ejecutar todos los tests"""
    print("\n" + "="*60)
    print("🧪 SUITE DE TESTS: MODELO DE ROTHERMEL")
    print("="*60)
    print("Validación de propagación direccional, humedad y MongoDB")
    print()
    
    results = {}
    
    try:
        results['wind'] = test_wind_directional_propagation()
    except Exception as e:
        print(f"   ❌ ERROR en test de viento: {e}")
        results['wind'] = False
    
    try:
        results['moisture'] = test_fuel_moisture_effect()
    except Exception as e:
        print(f"   ❌ ERROR en test de humedad: {e}")
        results['moisture'] = False
    
    try:
        results['slope'] = test_slope_effect()
    except Exception as e:
        print(f"   ❌ ERROR en test de pendiente: {e}")
        results['slope'] = False
    
    try:
        results['probability'] = test_rothermel_probability_calculation()
    except Exception as e:
        print(f"   ❌ ERROR en test de probabilidad: {e}")
        results['probability'] = False
    
    try:
        results['mongodb'] = test_mongodb_updates()
    except Exception as e:
        print(f"   ❌ ERROR en test de MongoDB: {e}")
        results['mongodb'] = False
    
    try:
        results['stats'] = test_fuel_moisture_stats()
    except Exception as e:
        print(f"   ❌ ERROR en test de estadísticas: {e}")
        results['stats'] = False
    
    # Resumen
    print("\n" + "="*60)
    print("📋 RESUMEN DE TESTS")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASADO" if result is True else ("❌ FALLIDO" if result is False else "⚠️ OMITIDO")
        print(f"   {test_name:20s}: {status}")
    
    print(f"\n   Total: {passed}/{total - skipped} tests pasados")
    
    if skipped > 0:
        print(f"   ({skipped} tests omitidos por falta de configuración)")
    
    print("="*60)
    
    # Exit code
    if failed == 0:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        return 0
    else:
        print(f"\n⚠️  {failed} tests fallaron")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrumpidos por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
