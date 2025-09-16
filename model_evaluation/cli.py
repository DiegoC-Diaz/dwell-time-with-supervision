#!/usr/bin/env python3
"""
CLI Application for YOLOv8 Model Evaluation
Interfaz de línea de comandos para evaluar modelos YOLOv8 con hiperparámetros configurables
"""

import click
import os
import sys
from pathlib import Path
from typing import Optional
import json
import dotenv
dotenv.load_dotenv()
# Importar el módulo yolov8
try:
    from yolov8 import run_model, validate_api_key
except ImportError:
    click.echo("❌ Error: No se pudo importar el módulo yolov8. Asegúrate de que esté en el mismo directorio.", err=True)
    sys.exit(1)


@click.group()
@click.version_option(version="1.0.0", prog_name="YOLOv8 CLI")
def cli():
    """
    🚀 YOLOv8 Model Evaluation CLI
    
    Herramienta de línea de comandos para evaluar modelos YOLOv8 con hiperparámetros configurables.
    """
    pass


@cli.command()
@click.option(
    '--source-video-path', '-s',
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help='📁 Ruta al directorio de frames o archivo de video'
)
@click.option(
    '--model-id', '-m',
    required=True,
    help='🤖 ID del modelo Roboflow (ej: yolov8n-640)'
)
@click.option(
    '--iou-threshold', '-i',
    default=0.5,
    type=float,
    help='🎯 Umbral IoU para NMS (0.0-1.0) [default: 0.5]'
)
@click.option(
    '--confidence-threshold', '-c',
    default=0.5,
    type=float,
    help='🎯 Umbral de confianza para detecciones (0.0-1.0) [default: 0.5]'
)
@click.option(
    '--api-key', '-k',
    envvar='ROBOFLOW_API_KEY',
    help='🔑 Clave API de Roboflow (también se puede configurar con variable de entorno ROBOFLOW_API_KEY)'
)
@click.option(
    '--output-dir', '-o',
    type=click.Path(path_type=Path),
    help='📤 Directorio de salida para resultados (opcional)'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='🔍 Modo verboso para mostrar información detallada'
)
@click.option(
    '--save-config', '--save',
    is_flag=True,
    help='💾 Guardar configuración actual como archivo JSON'
)
@click.option(
    '--class-ids', '--classes',
    default='0',
    help='🎯 IDs de clases a detectar separados por comas (ej: 0,1,2) [default: 0]'
)
def run(
    source_video_path: Path,
    model_id: str,
    iou_threshold: float,
    confidence_threshold: float,
    api_key: Optional[str],
    output_dir: Optional[Path],
    verbose: bool,
    save_config: bool,
    class_ids: str
):
    """
    🏃 Ejecutar evaluación del modelo YOLOv8
    
    Ejemplo de uso:
    python cli.py run -s ./frames -m yolov8n-640 -i 0.5 -c 0.5 --classes 0,1,2
    """
    
    # Validar parámetros
    if not (0.0 <= iou_threshold <= 1.0):
        click.echo("❌ Error: El umbral IoU debe estar entre 0.0 y 1.0", err=True)
        sys.exit(1)
    
    if not (0.0 <= confidence_threshold <= 1.0):
        click.echo("❌ Error: El umbral de confianza debe estar entre 0.0 y 1.0", err=True)
        sys.exit(1)
    
    # Configurar API key si se proporciona
    if api_key:
        os.environ['ROBOFLOW_API_KEY'] = api_key
    
    # Procesar class_ids
    try:
        class_ids_list = [int(x.strip()) for x in class_ids.split(',')]
    except ValueError:
        click.echo("❌ Error: Los IDs de clases deben ser números enteros separados por comas", err=True)
        sys.exit(1)
    
    # Mostrar configuración
    if verbose:
        click.echo("🔧 Configuración:")
        click.echo(f"   📁 Ruta de origen: {source_video_path}")
        click.echo(f"   🤖 Modelo: {model_id}")
        click.echo(f"   🎯 IoU Threshold: {iou_threshold}")
        click.echo(f"   🎯 Confidence Threshold: {confidence_threshold}")
        click.echo(f"   🎯 Class IDs: {class_ids_list}")
        click.echo(f"   📤 Directorio de salida: {output_dir or 'No especificado'}")
        click.echo(f"   🔑 API Key: {'Configurada' if os.getenv('ROBOFLOW_API_KEY') else 'No configurada'}")
    
    # Guardar configuración si se solicita
    if save_config:
        config = {
            "source_video_path": str(source_video_path),
            "model_id": model_id,
            "iou_threshold": iou_threshold,
            "confidence_threshold": confidence_threshold,
            "class_ids": class_ids_list,
            "output_dir": str(output_dir) if output_dir else None
        }
        
        config_file = Path("yolov8_config.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        click.echo(f"💾 Configuración guardada en: {config_file}")
    
    # Ejecutar modelo
    try:
        click.echo("🚀 Iniciando evaluación del modelo...")
        run_model(
            source_video_path=str(source_video_path),
            model_id=model_id,
            iou_threshold=iou_threshold,
            confidence_threshold=confidence_threshold,
            class_ids=class_ids_list
        )
        click.echo("✅ Evaluación completada exitosamente!")
        
    except ValueError as e:
        click.echo(f"❌ Error de validación: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error inesperado: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    '--config-file', '-f',
    type=click.Path(exists=True, path_type=Path),
    help='📄 Archivo de configuración JSON'
)
def run_from_config(config_file: Path):
    """
    🔄 Ejecutar evaluación desde archivo de configuración
    
    Ejemplo de uso:
    python cli.py run-from-config -f yolov8_config.json
    """
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        click.echo(f"📄 Cargando configuración desde: {config_file}")
        
        # Validar configuración requerida
        required_keys = ['source_video_path', 'model_id', 'iou_threshold', 'confidence_threshold']
        for key in required_keys:
            if key not in config:
                click.echo(f"❌ Error: Falta la clave '{key}' en el archivo de configuración", err=True)
                sys.exit(1)
        
        # Obtener class_ids con valor por defecto
        class_ids = config.get('class_ids', [0])
        
        # Validar que el directorio de origen existe
        source_path = Path(config['source_video_path'])
        if not source_path.exists():
            click.echo(f"❌ Error: El directorio de origen no existe: {source_path}", err=True)
            sys.exit(1)
        
        # Ejecutar con configuración cargada
        click.echo("🚀 Iniciando evaluación desde configuración...")
        run_model(
            source_video_path=config['source_video_path'],
            model_id=config['model_id'],
            iou_threshold=config['iou_threshold'],
            confidence_threshold=config['confidence_threshold'],
            class_ids=class_ids
        )
        click.echo("✅ Evaluación completada exitosamente!")
        
    except json.JSONDecodeError as e:
        click.echo(f"❌ Error al parsear JSON: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error inesperado: {e}", err=True)
        sys.exit(1)


@cli.command()
def validate():
    """
    ✅ Validar configuración del entorno
    
    Verifica que todas las dependencias y configuraciones estén correctas.
    """
    
    click.echo("🔍 Validando configuración del entorno...")
    
    # Verificar API key
    try:
        api_key = validate_api_key()
        click.echo("✅ API Key de Roboflow configurada correctamente")
    except ValueError as e:
        click.echo(f"❌ Error con API Key: {e}", err=True)
        click.echo("💡 Solución: Configura la variable de entorno ROBOFLOW_API_KEY o usa --api-key", err=True)
        return
    
    # Verificar dependencias
    dependencies = [
        ('supervision', 'sv'),
        ('inference', 'get_model'),
        ('cv2', 'cv2'),
        ('numpy', 'np'),
        ('scipy.io', 'loadmat')
    ]
    
    missing_deps = []
    for dep_name, import_name in dependencies:
        try:
            __import__(import_name)
            click.echo(f"✅ {dep_name} disponible")
        except ImportError:
            missing_deps.append(dep_name)
            click.echo(f"❌ {dep_name} no encontrado")
    
    if missing_deps:
        click.echo(f"\n❌ Dependencias faltantes: {', '.join(missing_deps)}", err=True)
        click.echo("💡 Instala las dependencias con: pip install supervision inference opencv-python numpy scipy", err=True)
        return
    
    click.echo("\n🎉 ¡Todas las validaciones pasaron! El entorno está listo.")


@cli.command()
@click.option(
    '--model-id', '-m',
    default='yolov8n-640',
    help='🤖 Modelo base para generar configuración [default: yolov8n-640]'
)
@click.option(
    '--output-file', '-o',
    default='yolov8_config_template.json',
    help='📄 Archivo de salida para la plantilla [default: yolov8_config_template.json]'
)
def generate_template(model_id: str, output_file: str):
    """
    📝 Generar plantilla de configuración
    
    Crea un archivo de configuración de ejemplo con valores por defecto.
    """
    
    template_config = {
        "source_video_path": "./frames",
        "model_id": model_id,
        "iou_threshold": 0.5,
        "confidence_threshold": 0.5,
        "class_ids": [0],
        "output_dir": "./output",
        "description": "Configuración de ejemplo para YOLOv8",
        "notes": [
            "Ajusta source_video_path al directorio de tus frames",
            "Modifica model_id según tu modelo de Roboflow",
            "Ajusta los umbrales según tus necesidades",
            "Modifica class_ids para las clases que quieres detectar (0=persona, 1=bicicleta, etc.)"
        ]
    }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(template_config, f, indent=2, ensure_ascii=False)
        
        click.echo(f"📝 Plantilla de configuración creada: {output_file}")
        click.echo("💡 Edita el archivo y usa 'run-from-config' para ejecutar")
        
    except Exception as e:
        click.echo(f"❌ Error al crear plantilla: {e}", err=True)
        sys.exit(1)


@cli.command()
def interactive():
    """
    🎮 Modo interactivo
    
    Guía paso a paso para configurar y ejecutar la evaluación.
    """
    
    click.echo("🎮 Modo Interactivo - Configuración de YOLOv8")
    click.echo("=" * 50)
    
    # Solicitar parámetros paso a paso
    source_path = click.prompt(
        "📁 Ingresa la ruta al directorio de frames o video",
        type=click.Path(exists=True, path_type=Path)
    )
    
    model_id = click.prompt(
        "🤖 Ingresa el ID del modelo Roboflow",
        default="yolov8n-640"
    )
    
    iou_threshold = click.prompt(
        "🎯 Ingresa el umbral IoU (0.0-1.0)",
        type=float,
        default=0.5
    )
    
    confidence_threshold = click.prompt(
        "🎯 Ingresa el umbral de confianza (0.0-1.0)",
        type=float,
        default=0.5
    )
    
    class_ids_input = click.prompt(
        "🎯 Ingresa los IDs de clases separados por comas (ej: 0,1,2)",
        default="0"
    )
    
    # Procesar class_ids
    try:
        class_ids_list = [int(x.strip()) for x in class_ids_input.split(',')]
    except ValueError:
        click.echo("❌ Error: Los IDs de clases deben ser números enteros separados por comas", err=True)
        return
    
    save_config = click.confirm("💾 ¿Guardar esta configuración?", default=True)
    
    # Mostrar resumen
    click.echo("\n📋 Resumen de configuración:")
    click.echo(f"   📁 Ruta: {source_path}")
    click.echo(f"   🤖 Modelo: {model_id}")
    click.echo(f"   🎯 IoU: {iou_threshold}")
    click.echo(f"   🎯 Confianza: {confidence_threshold}")
    click.echo(f"   🎯 Clases: {class_ids_list}")
    
    if not click.confirm("\n🚀 ¿Proceder con la evaluación?"):
        click.echo("❌ Evaluación cancelada")
        return
    
    # Ejecutar evaluación
    try:
        click.echo("\n🚀 Iniciando evaluación...")
        run_model(
            source_video_path=str(source_path),
            model_id=model_id,
            iou_threshold=iou_threshold,
            confidence_threshold=confidence_threshold,
            class_ids=class_ids_list
        )
        click.echo("✅ Evaluación completada exitosamente!")
        
        # Guardar configuración si se solicitó
        if save_config:
            config = {
                "source_video_path": str(source_path),
                "model_id": model_id,
                "iou_threshold": iou_threshold,
                "confidence_threshold": confidence_threshold,
                "class_ids": class_ids_list
            }
            
            config_file = Path("yolov8_interactive_config.json")
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            click.echo(f"💾 Configuración guardada en: {config_file}")
        
    except Exception as e:
        click.echo(f"❌ Error durante la evaluación: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
