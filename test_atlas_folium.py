#!/usr/bin/env python3
"""
Script de prueba rápida para atlas_folium_sync.py

Verifica que el módulo funciona correctamente sin necesidad
de conexión a MongoDB Atlas (modo demo).
"""

import sys
from pathlib import Path

print("\n" + "="*70)
print("🧪 PRUEBA RÁPIDA: ATLAS FOLIUM SYNC")
print("="*70 + "\n")

# ============================================================================
# 1. Verificar importaciones
# ============================================================================
print("1️⃣  Verificando importaciones...")

try:
    import folium
    print("   ✅ folium")
except ImportError:
    print("   ❌ folium - Instalar con: pip install folium")
    sys.exit(1)

try:
    from streamlit_folium import st_folium
    print("   ✅ streamlit_folium")
except ImportError:
    print("   ❌ streamlit_folium - Instalar con: pip install streamlit-folium")
    sys.exit(1)

try:
    from pymongo import MongoClient
    print("   ✅ pymongo")
except ImportError:
    print("   ❌ pymongo - Instalar con: pip install pymongo")
    sys.exit(1)

try:
    from atlas_folium_sync import (
        AtlasFoliumSync,
        create_atlas_folium_map,
        create_feature_tooltip,
        get_feature_color,
        calculate_center
    )
    print("   ✅ atlas_folium_sync")
except ImportError as e:
    print(f"   ❌ atlas_folium_sync - Error: {e}")
    sys.exit(1)

# ============================================================================
# 2. Verificar archivo GeoJSON
# ============================================================================
print("\n2️⃣  Verificando archivo GeoJSON...")

geojson_file = "zonas_forestales_ejemplo.geojson"

if not Path(geojson_file).exists():
    print(f"   ❌ {geojson_file} no encontrado")
    sys.exit(1)

try:
    import json
    with open(geojson_file, 'r') as f:
        geojson_data = json.load(f)
    
    features_count = len(geojson_data.get('features', []))
    print(f"   ✅ {geojson_file} válido ({features_count} features)")
except Exception as e:
    print(f"   ❌ Error al leer GeoJSON: {e}")
    sys.exit(1)

# ============================================================================
# 3. Probar creación de mapa sin conexión (modo demo)
# ============================================================================
print("\n3️⃣  Probando creación de mapa (modo demo)...")

try:
    # Convertir features de GeoJSON a formato esperado
    features = []
    for f in geojson_data.get('features', []):
        features.append({
            'location': f['geometry'],
            'properties': f.get('properties', {}),
            'tipo': f.get('properties', {}).get('tipo', 'default'),
            'nombre': f.get('properties', {}).get('nombre', 'Sin nombre')
        })
    
    print(f"   ℹ️  Procesados {len(features)} features")
    
    # Calcular centro
    center = calculate_center(features)
    print(f"   ℹ️  Centro calculado: {center}")
    
    # Crear mapa
    mapa = create_atlas_folium_map(
        features=features,
        center=center,
        zoom_start=13,
        show_heatmap=False
    )
    
    print("   ✅ Mapa creado exitosamente")
    
    # Guardar mapa HTML
    output_file = "test_map.html"
    mapa.save(output_file)
    print(f"   ✅ Mapa guardado en: {output_file}")
    
except Exception as e:
    print(f"   ❌ Error creando mapa: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# 4. Probar tooltips
# ============================================================================
print("\n4️⃣  Probando generación de tooltips...")

try:
    sample_feature = features[0]
    tooltip_html = create_feature_tooltip(sample_feature)
    
    if "<div" in tooltip_html and "</div>" in tooltip_html:
        print("   ✅ Tooltip HTML generado correctamente")
        print(f"   ℹ️  Longitud: {len(tooltip_html)} caracteres")
    else:
        print("   ❌ Tooltip HTML inválido")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Error generando tooltip: {e}")
    sys.exit(1)

# ============================================================================
# 5. Probar colores
# ============================================================================
print("\n5️⃣  Probando asignación de colores...")

try:
    for feature in features[:3]:
        color = get_feature_color(feature)
        nombre = feature.get('nombre', 'Sin nombre')
        tipo = feature.get('tipo', 'desconocido')
        print(f"   ✅ {nombre} ({tipo}): {color}")
        
except Exception as e:
    print(f"   ❌ Error asignando colores: {e}")
    sys.exit(1)

# ============================================================================
# 6. Probar AtlasFoliumSync (sin conexión)
# ============================================================================
print("\n6️⃣  Probando clase AtlasFoliumSync (sin conexión)...")

try:
    # Crear instancia sin URI (modo desconectado)
    sync = AtlasFoliumSync(uri=None)
    
    if not sync.connected:
        print("   ✅ Instancia creada en modo desconectado")
    else:
        print("   ⚠️  Se esperaba modo desconectado pero está conectado")
    
    sync.close()
    print("   ✅ Instancia cerrada correctamente")
    
except Exception as e:
    print(f"   ❌ Error con AtlasFoliumSync: {e}")
    sys.exit(1)

# ============================================================================
# RESUMEN FINAL
# ============================================================================
print("\n" + "="*70)
print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
print("="*70 + "\n")

print("📝 Archivos generados:")
print(f"   - {output_file} (mapa de prueba)")
print()
print("🚀 Próximos pasos:")
print("   1. Abre test_map.html en tu navegador para ver el mapa")
print("   2. Ejecuta 'streamlit run app.py' para usar en la interfaz")
print("   3. Configura MongoDB Atlas para modo completo (opcional)")
print()
print("📖 Documentación:")
print("   - FOLIUM_ATLAS_README.md")
print("   - MONGODB_ATLAS_SETUP.md")
print()
