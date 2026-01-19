#!/usr/bin/env python3
"""
Script de validación rápida para la integración MongoDB Atlas.

Verifica que todos los archivos necesarios estén presentes y
que las dependencias estén instaladas correctamente.

Autor: Forest Guardian RL Team
"""

import sys
from pathlib import Path
from typing import List, Dict

# Colores para terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def check_file_exists(file_path: str) -> bool:
    """Verifica si un archivo existe."""
    return Path(file_path).exists()


def check_python_version() -> bool:
    """Verifica que Python sea >= 3.8."""
    version = sys.version_info
    return version.major == 3 and version.minor >= 8


def check_dependencies() -> Dict[str, bool]:
    """Verifica que las dependencias estén instaladas."""
    dependencies = {}
    
    try:
        import pymongo
        dependencies['pymongo'] = True
    except ImportError:
        dependencies['pymongo'] = False
    
    try:
        import requests
        dependencies['requests'] = True
    except ImportError:
        dependencies['requests'] = False
    
    try:
        import json
        dependencies['json'] = True
    except ImportError:
        dependencies['json'] = False
    
    return dependencies


def validate_geojson(file_path: str) -> bool:
    """Valida que el archivo GeoJSON sea válido."""
    try:
        import json
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if 'type' not in data:
            return False
        
        if data['type'] not in ['FeatureCollection', 'Feature']:
            return False
        
        return True
    except Exception:
        return False


def main():
    """Función principal de validación."""
    print("\n" + "="*70)
    print(f"{BLUE}🔍 VALIDACIÓN DE INTEGRACIÓN MONGODB ATLAS{RESET}")
    print("="*70 + "\n")
    
    all_ok = True
    
    # ========================================================================
    # 1. Verificar Python
    # ========================================================================
    print(f"{BLUE}1. Versión de Python{RESET}")
    print("-" * 70)
    
    if check_python_version():
        version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        print(f"   {GREEN}✓{RESET} Python {version} (>= 3.8 requerido)")
    else:
        version = f"{sys.version_info.major}.{sys.version_info.minor}"
        print(f"   {RED}✗{RESET} Python {version} (Se requiere >= 3.8)")
        all_ok = False
    
    # ========================================================================
    # 2. Verificar archivos
    # ========================================================================
    print(f"\n{BLUE}2. Archivos del Proyecto{RESET}")
    print("-" * 70)
    
    required_files = [
        ("upload_geojson_to_atlas.py", "Script de carga"),
        ("query_geospatial_examples.py", "Ejemplos de consultas"),
        ("zonas_forestales_ejemplo.geojson", "Datos de ejemplo"),
        ("MONGODB_ATLAS_SETUP.md", "Documentación completa"),
        ("MONGODB_INTEGRATION_SUMMARY.md", "Resumen ejecutivo"),
        ("requirements.txt", "Dependencias"),
    ]
    
    for file_path, description in required_files:
        if check_file_exists(file_path):
            print(f"   {GREEN}✓{RESET} {file_path:<40} ({description})")
        else:
            print(f"   {RED}✗{RESET} {file_path:<40} (FALTANTE)")
            all_ok = False
    
    # ========================================================================
    # 3. Verificar dependencias
    # ========================================================================
    print(f"\n{BLUE}3. Dependencias de Python{RESET}")
    print("-" * 70)
    
    deps = check_dependencies()
    
    for dep_name, installed in deps.items():
        if installed:
            print(f"   {GREEN}✓{RESET} {dep_name}")
        else:
            print(f"   {RED}✗{RESET} {dep_name} (FALTANTE - instalar con: pip install {dep_name})")
            all_ok = False
    
    # ========================================================================
    # 4. Validar GeoJSON de ejemplo
    # ========================================================================
    print(f"\n{BLUE}4. Validación de GeoJSON{RESET}")
    print("-" * 70)
    
    geojson_file = "zonas_forestales_ejemplo.geojson"
    if check_file_exists(geojson_file):
        if validate_geojson(geojson_file):
            print(f"   {GREEN}✓{RESET} {geojson_file} es válido")
            
            # Contar features
            try:
                import json
                with open(geojson_file, 'r') as f:
                    data = json.load(f)
                features_count = len(data.get('features', []))
                print(f"   {BLUE}ℹ{RESET}  {features_count} features encontradas")
            except:
                pass
        else:
            print(f"   {RED}✗{RESET} {geojson_file} tiene formato inválido")
            all_ok = False
    else:
        print(f"   {RED}✗{RESET} {geojson_file} no encontrado")
        all_ok = False
    
    # ========================================================================
    # 5. Verificar scripts ejecutables
    # ========================================================================
    print(f"\n{BLUE}5. Permisos de Ejecución{RESET}")
    print("-" * 70)
    
    scripts = [
        "upload_geojson_to_atlas.py",
        "query_geospatial_examples.py"
    ]
    
    for script in scripts:
        path = Path(script)
        if path.exists():
            # En Unix/Linux, verificar si es ejecutable
            import os
            if os.name != 'nt':  # No Windows
                is_executable = os.access(str(path), os.X_OK)
                if is_executable:
                    print(f"   {GREEN}✓{RESET} {script} es ejecutable")
                else:
                    print(f"   {YELLOW}⚠{RESET} {script} no es ejecutable (ejecutar: chmod +x {script})")
            else:
                print(f"   {BLUE}ℹ{RESET}  {script} (Windows detectado)")
    
    # ========================================================================
    # Resumen final
    # ========================================================================
    print("\n" + "="*70)
    if all_ok:
        print(f"{GREEN}✅ VALIDACIÓN COMPLETA - TODO CORRECTO{RESET}")
        print("="*70 + "\n")
        print(f"{BLUE}📖 Próximos pasos:{RESET}")
        print("   1. Lee MONGODB_ATLAS_SETUP.md para configurar MongoDB Atlas")
        print("   2. Obtén tu URI de conexión desde MongoDB Atlas")
        print("   3. Edita upload_geojson_to_atlas.py con tu URI")
        print("   4. Ejecuta: python upload_geojson_to_atlas.py")
        print("   5. Prueba consultas: python query_geospatial_examples.py\n")
    else:
        print(f"{RED}❌ VALIDACIÓN FALLIDA - REVISAR ERRORES{RESET}")
        print("="*70 + "\n")
        print(f"{YELLOW}💡 Soluciones:{RESET}")
        print("   - Instalar dependencias faltantes: pip install -r requirements.txt")
        print("   - Verificar que todos los archivos estén presentes")
        print("   - Revisar versión de Python (>= 3.8 requerido)\n")
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}⚠️  Validación interrumpida por el usuario{RESET}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}❌ Error durante la validación: {e}{RESET}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
