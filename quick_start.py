#!/usr/bin/env python3
"""
Forest Guardian RL - Script de Inicio Rápido
Facilita el inicio de la aplicación Streamlit o ejecución de misiones
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║       🔥 FOREST GUARDIAN RL - CENTRO DE CONTROL 🔥            ║")
    print("║     Sistema Autónomo de Control de Incendios Forestales       ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    # Verificar archivo de configuración
    if not Path("requirements.txt").exists():
        print("❌ Error: requirements.txt no encontrado")
        print("   Asegúrate de ejecutar este script desde la carpeta raíz del proyecto")
        sys.exit(1)
    
    print("✓ Verificando dependencias...")
    
    # Intentar importar módulos clave
    missing_packages = []
    packages_to_check = [
        ('streamlit', 'Streamlit'),
        ('plotly', 'Plotly'),
        ('gymnasium', 'Gymnasium'),
        ('numpy', 'NumPy'),
    ]
    
    for module_name, display_name in packages_to_check:
        try:
            __import__(module_name)
            print(f"  ✓ {display_name}")
        except ImportError:
            print(f"  ✗ {display_name} - FALTANTE")
            missing_packages.append(module_name)
    
    if missing_packages:
        print("\n⚠️  Faltan dependencias. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("\n" + "="*60)
    print("¿Qué deseas hacer?")
    print("")
    print("  1) 🌐 Iniciar Streamlit (Interfaz web interactiva)")
    print("     → La mejor opción para visualización y controles interactivos")
    print("")
    print("  2) 🧪 Ejecutar misión de prueba (Terminal)")
    print("     → Ejecuta una simulación rápida y genera un reporte HTML")
    print("")
    print("  3) 📖 Ver documentación")
    print("     → Abre el README en el navegador")
    print("")
    print("  4) 🚪 Salir")
    print("="*60 + "\n")
    
    try:
        choice = input("Selecciona una opción (1-4): ").strip()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
        sys.exit(0)
    
    if choice == "1":
        start_streamlit()
    elif choice == "2":
        run_test_mission()
    elif choice == "3":
        open_documentation()
    elif choice == "4":
        print("\n👋 ¡Hasta luego!")
        sys.exit(0)
    else:
        print("\n❌ Opción inválida")
        sys.exit(1)

def start_streamlit():
    """Inicia la aplicación Streamlit"""
    print("\n" + "="*60)
    print("🚀 Iniciando Streamlit...")
    print("="*60)
    print("\nLa aplicación se abrirá automáticamente en:")
    print("  → http://localhost:8501")
    print("\n💡 Tips:")
    print("  • Presiona CTRL+C para detener el servidor")
    print("  • Recarga la página (F5) si tienes problemas")
    print("  • Abre las Developer Tools (F12) para debugging")
    print("\n" + "="*60 + "\n")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n\n✓ Servidor detenido")
        sys.exit(0)

def run_test_mission():
    """Ejecuta una misión de prueba"""
    print("\n" + "="*60)
    print("🧪 Ejecutando misión de prueba...")
    print("="*60 + "\n")
    
    try:
        subprocess.run([sys.executable, "train_and_test_refactored.py"])
        print("\n✓ Misión completada.")
        print("   Revisa la carpeta GIF/ para ver los resultados (GIF y HTML)")
        print("="*60 + "\n")
    except KeyboardInterrupt:
        print("\n\n❌ Misión interrumpida por el usuario")
        sys.exit(0)

def open_documentation():
    """Abre la documentación en el navegador"""
    print("\n📖 Abriendo documentación...\n")
    
    import webbrowser
    
    # Intentar abrir el archivo markdown convertido a HTML
    doc_path = Path("STREAMLIT_README.md")
    
    if doc_path.exists():
        print(f"✓ Documentación encontrada en: {doc_path}")
        print("\nContenido de la documentación:\n")
        
        # Mostrar primeras líneas
        with open(doc_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:50]
            for line in lines:
                print(line.rstrip())
        
        print("\n...\n")
        print("Para leer el documento completo, abre STREAMLIT_README.md con tu editor de texto")
    else:
        print("❌ Documentación no encontrada")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
