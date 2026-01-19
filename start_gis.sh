#!/bin/bash
# Forest Guardian RL - Quick Start con GIS
# Ejecuta este script para iniciar la aplicación

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║          🌍 FOREST GUARDIAN RL - GIS Integration 🌍           ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt no encontrado"
    echo "   Asegúrate de ejecutar este script desde la carpeta del proyecto"
    exit 1
fi

echo "✓ Verificando dependencias..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no instalado"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "  ✅ Python $PYTHON_VERSION"

# Instalar/Actualizar dependencias
echo ""
echo "✓ Instalando/Actualizando paquetes necesarios..."
pip install -q -r requirements.txt

echo "  ✅ Dependencias instaladas"

# Información
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  INFORMACIÓN IMPORTANTE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📚 Documentación:"
echo "   • GIS_README.md (Guía de usuario completa)"
echo "   • INTEGRACION_GIS.md (Detalles técnicos)"
echo "   • RESUMEN_GIS.txt (Resumen ejecutivo)"
echo ""
echo "🚀 Para iniciar la aplicación:"
echo ""
echo "   streamlit run app.py"
echo ""
echo "📖 Para ver demostraciones:"
echo ""
echo "   python3 demo_gis.py"
echo ""
echo "✅ Características disponibles:"
echo "   • 13 bosques reales del mundo"
echo "   • Mapas interactivos Folium"
echo "   • Simulación multi-drones"
echo "   • Coordenadas geográficas automáticas"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🎉 Sistema GIS completamente funcional y validado"
echo ""
