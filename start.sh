#!/bin/bash

# ============================================================================
# Forest Guardian RL - Script de Inicio Rápido
# ============================================================================

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       🔥 FOREST GUARDIAN RL - CENTRO DE CONTROL 🔥            ║"
echo "║     Sistema Autónomo de Control de Incendios Forestales       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar Python
echo "✓ Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado. Por favor instála e intenta de nuevo."
    exit 1
fi
python3 --version

# Verificar/instalar dependencias
echo ""
echo "✓ Verificando dependencias..."

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "  → Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "  → Activando entorno virtual..."
source venv/bin/activate

# Instalar/actualizar paquetes
echo "  → Instalando paquetes desde requirements.txt..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "✓ Ambiente configurado correctamente"
echo ""

# Mostrar opciones
echo "════════════════════════════════════════════════════════════════"
echo "¿Qué deseas hacer?"
echo ""
echo "  1) Iniciar Streamlit (Interfaz web interactiva) [RECOMENDADO]"
echo "  2) Ejecutar misión de prueba (Terminal)"
echo "  3) Salir"
echo ""
read -p "Selecciona una opción (1-3): " choice

case $choice in
    1)
        echo ""
        echo "════════════════════════════════════════════════════════════════"
        echo "🚀 Iniciando Streamlit..."
        echo ""
        echo "La aplicación se abrirá automáticamente en:"
        echo "  → http://localhost:8501"
        echo ""
        echo "Presiona CTRL+C para detener el servidor"
        echo "════════════════════════════════════════════════════════════════"
        echo ""
        streamlit run app.py
        ;;
    2)
        echo ""
        echo "════════════════════════════════════════════════════════════════"
        echo "Ejecutando misión de prueba..."
        echo "════════════════════════════════════════════════════════════════"
        python3 train_and_test_refactored.py
        echo ""
        echo "✓ Misión completada. Revisa la carpeta GIF/ para ver resultados."
        ;;
    3)
        echo ""
        echo "👋 ¡Hasta luego!"
        exit 0
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac
