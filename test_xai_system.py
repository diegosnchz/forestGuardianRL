"""
Script de prueba para el sistema XAI (Explainable AI).

Valida:
1. Inicialización del XAIExplainer
2. Generación de explicaciones de decisiones
3. Mapas de atención
4. Importancia de atributos
5. Razonamiento táctico
6. Visualizaciones

Autor: Forest Guardian RL Team
"""

import numpy as np
import matplotlib.pyplot as plt
from xai_explainer import XAIExplainer, AgentDecision
from xai_visualization import (
    create_attention_heatmap,
    create_importance_chart,
    create_decision_timeline,
    create_action_distribution_chart,
    create_confidence_vs_distance_scatter,
    create_tactical_reasoning_display,
    create_multi_agent_comparison,
    export_decision_report
)


def create_test_grid(size=10):
    """Crea un grid de prueba con fuegos y árboles"""
    grid = np.zeros((size, size), dtype=int)
    
    # Agregar árboles
    for _ in range(15):
        r, c = np.random.randint(0, size, 2)
        grid[r, c] = 1
    
    # Agregar fuegos
    fire_positions = [(2, 2), (7, 8), (5, 3)]
    for r, c in fire_positions:
        if 0 <= r < size and 0 <= c < size:
            grid[r, c] = 2
    
    return grid


def test_xai_initialization():
    """Test 1: Inicialización del XAIExplainer"""
    print("=" * 70)
    print("TEST 1: Inicialización del XAIExplainer")
    print("=" * 70)
    
    try:
        explainer = XAIExplainer(grid_size=10, enable_mongodb=False)
        print("✅ XAIExplainer inicializado correctamente")
        print(f"   - Grid size: {explainer.grid_size}")
        print(f"   - MongoDB: {explainer.enable_mongodb}")
        print(f"   - Historias de agentes: {len(explainer.histories)}")
        return explainer
    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        return None


def test_decision_explanation(explainer):
    """Test 2: Generación de explicación de decisión"""
    print("\n" + "=" * 70)
    print("TEST 2: Generación de Explicación de Decisión")
    print("=" * 70)
    
    try:
        # Crear grid de prueba
        grid = create_test_grid(10)
        
        # Generar decisión para agente ALPHA
        decision = explainer.explain_decision(
            agent_id="ALPHA",
            agent_role="nearest",
            position=(5, 5),
            action=1,  # Move down
            grid_state=grid,
            obs={'step': 0},
            water_level=999
        )
        
        print("✅ Decisión generada correctamente")
        print(f"   - Agente: {decision.agent_id} ({decision.agent_role})")
        print(f"   - Posición: {decision.position}")
        print(f"   - Acción: {decision.action_name}")
        print(f"   - Distancia al objetivo: {decision.distance_to_target:.2f}")
        print(f"   - Confianza: {decision.confidence:.2f}")
        print(f"   - Importancia de atributos: {len(decision.importance_scores)} factores")
        print(f"   - Alternativas: {len(decision.alternative_actions)} opciones")
        
        print("\n📊 Top 3 Factores de Importancia:")
        sorted_factors = sorted(decision.importance_scores.items(), 
                               key=lambda x: x[1], reverse=True)
        for i, (factor, score) in enumerate(sorted_factors[:3], 1):
            print(f"   {i}. {factor}: {score*100:.1f}%")
        
        return decision
    except Exception as e:
        print(f"❌ Error generando decisión: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_attention_map(decision):
    """Test 3: Mapa de atención"""
    print("\n" + "=" * 70)
    print("TEST 3: Mapa de Atención")
    print("=" * 70)
    
    try:
        attention_map = decision.attention_map
        print(f"✅ Mapa de atención generado: {attention_map.shape}")
        print(f"   - Valor mínimo: {attention_map.min():.3f}")
        print(f"   - Valor máximo: {attention_map.max():.3f}")
        print(f"   - Valor promedio: {attention_map.mean():.3f}")
        
        # Crear visualización
        fig = create_attention_heatmap(
            attention_map,
            decision.grid_state,
            decision.position,
            "Test: Mapa de Atención"
        )
        
        # Guardar
        plt.savefig("test_attention_map.png", dpi=150, bbox_inches='tight')
        print("   - Visualización guardada: test_attention_map.png")
        plt.close(fig)
        
        return True
    except Exception as e:
        print(f"❌ Error generando mapa de atención: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_importance_chart(decision):
    """Test 4: Gráfico de importancia"""
    print("\n" + "=" * 70)
    print("TEST 4: Gráfico de Importancia de Atributos")
    print("=" * 70)
    
    try:
        fig = create_importance_chart(
            decision.importance_scores,
            "Test: Importancia de Atributos"
        )
        
        print(f"✅ Gráfico de importancia generado")
        print(f"   - Factores analizados: {len(decision.importance_scores)}")
        
        # Guardar
        fig.write_html("test_importance_chart.html")
        print("   - Visualización guardada: test_importance_chart.html")
        
        return True
    except Exception as e:
        print(f"❌ Error generando gráfico de importancia: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tactical_reasoning(decision):
    """Test 5: Razonamiento táctico"""
    print("\n" + "=" * 70)
    print("TEST 5: Razonamiento Táctico")
    print("=" * 70)
    
    try:
        print("✅ Razonamiento táctico disponible")
        print("\n📝 Explicación:")
        print("-" * 70)
        print(decision.explanation)
        print("-" * 70)
        
        print("\n⚔️ Razonamiento Táctico:")
        print("-" * 70)
        print(decision.tactical_reasoning)
        print("-" * 70)
        
        return True
    except Exception as e:
        print(f"❌ Error accediendo al razonamiento: {e}")
        return False


def test_multiple_decisions(explainer):
    """Test 6: Múltiples decisiones y análisis temporal"""
    print("\n" + "=" * 70)
    print("TEST 6: Múltiples Decisiones y Análisis Temporal")
    print("=" * 70)
    
    try:
        decisions = []
        grid = create_test_grid(10)
        
        # Simular 10 pasos
        positions = [(5, 5), (5, 4), (5, 3), (4, 3), (3, 3), 
                    (3, 2), (2, 2), (2, 2), (2, 2), (2, 2)]
        actions = [1, 1, 0, 0, 1, 5, 5, 6, 6, 6]  # Movimientos y apagar
        
        for step, (pos, action) in enumerate(zip(positions, actions)):
            decision = explainer.explain_decision(
                agent_id="ALPHA",
                agent_role="nearest",
                position=pos,
                action=action,
                grid_state=grid.copy(),
                obs={'step': step},
                water_level=999 - step * 10
            )
            decisions.append(decision)
        
        print(f"✅ {len(decisions)} decisiones generadas")
        
        # Timeline
        fig_timeline = create_decision_timeline(decisions, 'distance_to_target')
        fig_timeline.write_html("test_timeline.html")
        print("   - Timeline guardado: test_timeline.html")
        
        # Distribución de acciones
        fig_actions = create_action_distribution_chart(decisions)
        fig_actions.write_html("test_action_distribution.html")
        print("   - Distribución guardada: test_action_distribution.html")
        
        # Confianza vs Distancia
        fig_scatter = create_confidence_vs_distance_scatter(decisions)
        fig_scatter.write_html("test_confidence_scatter.html")
        print("   - Scatter guardado: test_confidence_scatter.html")
        
        return decisions
    except Exception as e:
        print(f"❌ Error en análisis temporal: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_multi_agent_comparison(explainer):
    """Test 7: Comparación multi-agente"""
    print("\n" + "=" * 70)
    print("TEST 7: Comparación Multi-Agente")
    print("=" * 70)
    
    try:
        grid = create_test_grid(10)
        
        decisions_dict = {}
        
        # Simular decisiones para ALPHA (nearest)
        alpha_decisions = []
        for step in range(5):
            pos = (5 - step, 5)
            decision = explainer.explain_decision(
                agent_id="ALPHA",
                agent_role="nearest",
                position=pos,
                action=0,  # Move up
                grid_state=grid.copy(),
                obs={'step': step},
                water_level=999
            )
            alpha_decisions.append(decision)
        decisions_dict["ALPHA"] = alpha_decisions
        
        # Simular decisiones para BRAVO (farthest)
        bravo_decisions = []
        for step in range(5):
            pos = (5, 5 + step)
            decision = explainer.explain_decision(
                agent_id="BRAVO",
                agent_role="farthest",
                position=pos,
                action=3,  # Move right
                grid_state=grid.copy(),
                obs={'step': step},
                water_level=999
            )
            bravo_decisions.append(decision)
        decisions_dict["BRAVO"] = bravo_decisions
        
        print(f"✅ Decisiones multi-agente generadas")
        print(f"   - ALPHA: {len(alpha_decisions)} decisiones")
        print(f"   - BRAVO: {len(bravo_decisions)} decisiones")
        
        # Comparación
        fig_comparison = create_multi_agent_comparison(decisions_dict)
        fig_comparison.write_html("test_multi_agent_comparison.html")
        print("   - Comparación guardada: test_multi_agent_comparison.html")
        
        return True
    except Exception as e:
        print(f"❌ Error en comparación multi-agente: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_export_report(decision):
    """Test 8: Exportación de reporte"""
    print("\n" + "=" * 70)
    print("TEST 8: Exportación de Reporte")
    print("=" * 70)
    
    try:
        filename = "test_xai_report.html"
        export_decision_report(decision, filename)
        
        print(f"✅ Reporte exportado: {filename}")
        
        # Verificar que el archivo existe
        import os
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"   - Tamaño: {size} bytes")
            return True
        else:
            print(f"❌ Archivo no encontrado")
            return False
    except Exception as e:
        print(f"❌ Error exportando reporte: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_history_export(explainer):
    """Test 9: Exportación de historial JSON"""
    print("\n" + "=" * 70)
    print("TEST 9: Exportación de Historial JSON")
    print("=" * 70)
    
    try:
        # Primero generar algunas decisiones para tener historial
        grid = create_test_grid(10)
        for step in range(3):
            explainer.explain_decision(
                agent_id="ALPHA",
                agent_role="nearest",
                position=(5, 5 - step),
                action=0,
                grid_state=grid.copy(),
                obs={'step': step},
                water_level=999
            )
        
        # Ahora exportar
        filename = "test_xai_history.json"
        explainer.export_history(filename)
        
        print(f"✅ Historial exportado: {filename}")
        
        # Verificar contenido
        import json
        with open(filename, 'r') as f:
            data = json.load(f)
        
        print(f"   - Historias de agentes: {len(data.get('histories', {}))}")
        if 'ALPHA' in data.get('histories', {}):
            print(f"   - Decisiones ALPHA: {len(data['histories']['ALPHA'])}")
        
        return True
    except Exception as e:
        print(f"❌ Error exportando historial: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "=" * 70)
    print("🧪 SUITE DE PRUEBAS XAI - Forest Guardian RL")
    print("=" * 70)
    print()
    
    results = {
        'passed': 0,
        'failed': 0,
        'total': 9
    }
    
    # Test 1: Inicialización
    explainer = test_xai_initialization()
    if explainer:
        results['passed'] += 1
    else:
        results['failed'] += 1
        return results  # Si falla la inicialización, no continuar
    
    # Test 2: Explicación de decisión
    decision = test_decision_explanation(explainer)
    if decision:
        results['passed'] += 1
    else:
        results['failed'] += 1
        return results
    
    # Test 3: Mapa de atención
    if test_attention_map(decision):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 4: Gráfico de importancia
    if test_importance_chart(decision):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 5: Razonamiento táctico
    if test_tactical_reasoning(decision):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 6: Múltiples decisiones
    decisions = test_multiple_decisions(explainer)
    if decisions:
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 7: Comparación multi-agente
    if test_multi_agent_comparison(explainer):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 8: Exportación de reporte
    if test_export_report(decision):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 9: Exportación de historial
    if test_history_export(explainer):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 70)
    print(f"✅ Pruebas exitosas: {results['passed']}/{results['total']}")
    print(f"❌ Pruebas fallidas: {results['failed']}/{results['total']}")
    
    if results['failed'] == 0:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
    else:
        print(f"\n⚠️ {results['failed']} prueba(s) fallaron")
    
    print("\n📁 Archivos generados:")
    print("   - test_attention_map.png")
    print("   - test_importance_chart.html")
    print("   - test_timeline.html")
    print("   - test_action_distribution.html")
    print("   - test_confidence_scatter.html")
    print("   - test_multi_agent_comparison.html")
    print("   - test_xai_report.html")
    print("   - test_xai_history.json")
    
    return results


if __name__ == "__main__":
    np.random.seed(42)  # Para reproducibilidad
    results = run_all_tests()
    
    # Exit code basado en resultados
    import sys
    sys.exit(0 if results['failed'] == 0 else 1)
