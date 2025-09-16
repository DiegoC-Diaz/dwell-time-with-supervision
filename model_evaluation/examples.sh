#!/usr/bin/env bash
# Ejemplos de uso de la CLI de YOLOv8
# Este script demuestra diferentes formas de usar la aplicación CLI

echo "🚀 Ejemplos de uso de YOLOv8 CLI"
echo "================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "cli.py" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio model_evaluation/"
    exit 1
fi

echo ""
echo "1️⃣ Validar entorno"
echo "python cli.py validate"
python cli.py validate

echo ""
echo "2️⃣ Generar plantilla de configuración"
echo "python cli.py generate-template -m yolov8n-640 -o example_config.json"
python cli.py generate-template -m yolov8n-640 -o example_config.json

echo ""
echo "3️⃣ Mostrar ayuda"
echo "python cli.py --help"
python cli.py --help

echo ""
echo "4️⃣ Mostrar ayuda del comando run"
echo "python cli.py run --help"
python cli.py run --help

echo ""
echo "5️⃣ Ejemplo de ejecución básica (requiere frames y API key)"
echo "python cli.py run -s ./mall_dataset/frames -m yolov8n-640 -i 0.5 -c 0.5"
echo "💡 Nota: Este comando requiere que tengas frames y API key configurada"

echo ""
echo "6️⃣ Ejemplo de modo interactivo"
echo "python cli.py interactive"
echo "💡 Nota: Este comando te guiará paso a paso"

echo ""
echo "7️⃣ Ejemplo desde archivo de configuración"
echo "python cli.py run-from-config -f example_config.json"
echo "💡 Nota: Requiere que el archivo de configuración sea válido"

echo ""
echo "✅ Ejemplos completados!"
echo ""
echo "📖 Para más información, consulta README_CLI.md"
echo "🔧 Para configurar tu API key: export ROBOFLOW_API_KEY='tu_api_key'"
