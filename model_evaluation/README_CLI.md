# 🚀 YOLOv8 CLI - Interfaz de Línea de Comandos

Una aplicación CLI moderna y fácil de usar para evaluar modelos YOLOv8 con hiperparámetros configurables.

## 📋 Características

- ✅ **Interfaz intuitiva** con Click (la mejor librería CLI para Python)
- 🎯 **Hiperparámetros configurables** (IoU threshold, confidence threshold)
- 📄 **Configuración por archivos JSON** para reutilizar configuraciones
- 🎮 **Modo interactivo** para configuración paso a paso
- 🔍 **Validación de entorno** automática
- 📝 **Plantillas de configuración** predefinidas
- 🔑 **Soporte para API keys** de Roboflow

## 🛠️ Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Hacer ejecutable (Linux/Mac)
chmod +x cli.py
```

## 🚀 Uso Rápido

### Comando Básico
```bash
python cli.py run -s ./frames -m yolov8n-640 -i 0.5 -c 0.5
```

### Modo Interactivo (Recomendado para principiantes)
```bash
python cli.py interactive
```

### Desde Archivo de Configuración
```bash
python cli.py run-from-config -f config.json
```

## 📖 Comandos Disponibles

### `run` - Ejecutar Evaluación
Ejecuta la evaluación del modelo con parámetros específicos.

```bash
python cli.py run [OPTIONS]
```

**Opciones:**
- `-s, --source-video-path`: 📁 Ruta al directorio de frames o video (requerido)
- `-m, --model-id`: 🤖 ID del modelo Roboflow (requerido)
- `-i, --iou-threshold`: 🎯 Umbral IoU para NMS (0.0-1.0) [default: 0.5]
- `-c, --confidence-threshold`: 🎯 Umbral de confianza (0.0-1.0) [default: 0.5]
- `-k, --api-key`: 🔑 Clave API de Roboflow
- `-o, --output-dir`: 📤 Directorio de salida
- `-v, --verbose`: 🔍 Modo verboso
- `--save-config`: 💾 Guardar configuración actual

**Ejemplos:**
```bash
# Ejecución básica
python cli.py run -s ./mall_dataset/frames -m yolov8n-640

# Con parámetros personalizados
python cli.py run -s ./frames -m yolov8s-640 -i 0.7 -c 0.3 -v

# Guardando configuración
python cli.py run -s ./frames -m yolov8m-640 --save-config
```

### `interactive` - Modo Interactivo
Guía paso a paso para configurar y ejecutar la evaluación.

```bash
python cli.py interactive
```

### `run-from-config` - Ejecutar desde Configuración
Ejecuta la evaluación usando un archivo de configuración JSON.

```bash
python cli.py run-from-config -f config.json
```

### `validate` - Validar Entorno
Verifica que todas las dependencias y configuraciones estén correctas.

```bash
python cli.py validate
```

### `generate-template` - Generar Plantilla
Crea un archivo de configuración de ejemplo.

```bash
python cli.py generate-template -m yolov8n-640 -o my_config.json
```

## 📄 Archivos de Configuración

### Formato JSON
```json
{
  "source_video_path": "./frames",
  "model_id": "yolov8n-640",
  "iou_threshold": 0.5,
  "confidence_threshold": 0.5,
  "output_dir": "./output",
  "description": "Configuración de ejemplo",
  "notes": [
    "Ajusta source_video_path al directorio de tus frames",
    "Modifica model_id según tu modelo de Roboflow"
  ]
}
```

### Generar Plantilla
```bash
python cli.py generate-template
```

## 🔧 Configuración de API Key

### Opción 1: Variable de Entorno (Recomendado)
```bash
export ROBOFLOW_API_KEY="tu_api_key_aqui"
```

### Opción 2: Parámetro CLI
```bash
python cli.py run -s ./frames -m yolov8n-640 -k "tu_api_key_aqui"
```

### Opción 3: Archivo .env
```bash
echo "ROBOFLOW_API_KEY=tu_api_key_aqui" > .env
```

## 🎯 Hiperparámetros Explicados

### IoU Threshold (`-i, --iou-threshold`)
- **Rango**: 0.0 - 1.0
- **Default**: 0.5
- **Descripción**: Umbral para Non-Maximum Suppression (NMS)
- **Valores bajos (0.1-0.3)**: Más detecciones, posible duplicación
- **Valores altos (0.7-0.9)**: Menos detecciones, más precisión

### Confidence Threshold (`-c, --confidence-threshold`)
- **Rango**: 0.0 - 1.0
- **Default**: 0.5
- **Descripción**: Umbral mínimo de confianza para detecciones
- **Valores bajos (0.1-0.3)**: Más detecciones, más falsos positivos
- **Valores altos (0.7-0.9)**: Menos detecciones, más precisión

## 📊 Ejemplos de Uso Común

### Evaluación Rápida
```bash
python cli.py run -s ./mall_dataset/frames -m yolov8n-640
```

### Evaluación Precisión Alta
```bash
python cli.py run -s ./frames -m yolov8s-640 -i 0.7 -c 0.7
```

### Evaluación Sensibilidad Alta
```bash
python cli.py run -s ./frames -m yolov8m-640 -i 0.3 -c 0.3
```

### Configuración Personalizada
```bash
# Generar plantilla
python cli.py generate-template -m yolov8l-640 -o my_config.json

# Editar archivo
nano my_config.json

# Ejecutar
python cli.py run-from-config -f my_config.json
```

## 🐛 Solución de Problemas

### Error: "No se pudo importar el módulo yolov8"
```bash
# Asegúrate de estar en el directorio correcto
cd model_evaluation/
python cli.py validate
```

### Error: "ROBOFLOW_API_KEY environment variable is not set"
```bash
# Configurar API key
export ROBOFLOW_API_KEY="tu_api_key"
python cli.py validate
```

### Error: "No frames found"
```bash
# Verificar que el directorio existe y contiene frames
ls -la ./frames/
python cli.py run -s ./frames -m yolov8n-640 -v
```

## 🔍 Modo Verboso

Usa `-v, --verbose` para obtener información detallada:

```bash
python cli.py run -s ./frames -m yolov8n-640 -v
```

## 📈 Mejores Prácticas

1. **Siempre valida el entorno** antes de ejecutar:
   ```bash
   python cli.py validate
   ```

2. **Usa el modo interactivo** para aprender los parámetros:
   ```bash
   python cli.py interactive
   ```

3. **Guarda configuraciones exitosas**:
   ```bash
   python cli.py run -s ./frames -m yolov8n-640 --save-config
   ```

4. **Experimenta con diferentes umbrales**:
   ```bash
   # Prueba diferentes combinaciones
   python cli.py run -s ./frames -m yolov8n-640 -i 0.3 -c 0.3
   python cli.py run -s ./frames -m yolov8n-640 -i 0.7 -c 0.7
   ```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
