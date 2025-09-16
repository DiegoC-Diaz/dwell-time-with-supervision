#!/usr/bin/env python3
"""
Script de prueba para verificar la integración del motor de inferencia
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuración
API_BASE_URL = "http://localhost:8000"

def test_process_with_inference():
    """Prueba crear un proceso que ejecute el motor de inferencia"""
    
    print("🧪 Probando integración del motor de inferencia...")
    
    # Datos de prueba para un proceso
    test_process = {
        "zone_id": 1,  # Asumiendo que existe una zona con ID 1
        "process_name": "Prueba de Inferencia",
        "model_id": "yolo_v8",
        "start_time": "2024-01-01 10:00:00",
        "end_time": "2024-01-01 11:00:00",
        "video_path": "/test/video.mp4"  # Ruta de prueba
    }
    
    try:
        # 1. Crear el proceso
        print("\n1. Creando proceso de prueba...")
        response = requests.post(
            f"{API_BASE_URL}/api/processes",
            json=test_process,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            process_id = data.get('process_id')
            print(f"   ✅ Proceso creado con ID: {process_id}")
            print(f"   📝 Mensaje: {data.get('message')}")
            
            # 2. Verificar el estado del proceso
            print(f"\n2. Verificando estado del proceso {process_id}...")
            
            for i in range(5):  # Verificar 5 veces con intervalos
                time.sleep(2)  # Esperar 2 segundos
                
                response = requests.get(f"{API_BASE_URL}/api/processes/{process_id}/status")
                
                if response.status_code == 200:
                    status_data = response.json()
                    print(f"   Estado: {status_data.get('status')}")
                    print(f"   Completado: {status_data.get('is_done')}")
                    
                    if status_data.get('is_done'):
                        print(f"   ✅ Proceso completado!")
                        break
                else:
                    print(f"   ❌ Error al verificar estado: {response.text}")
            
            # 3. Obtener detalles del proceso
            print(f"\n3. Obteniendo detalles del proceso {process_id}...")
            response = requests.get(f"{API_BASE_URL}/api/processes/{process_id}")
            
            if response.status_code == 200:
                process_data = response.json()
                print(f"   ✅ Proceso obtenido:")
                print(f"      Nombre: {process_data.get('process_name')}")
                print(f"      Zona: {process_data.get('zone_name')}")
                print(f"      Video: {process_data.get('video_path')}")
                print(f"      Completado: {process_data.get('is_done')}")
            else:
                print(f"   ❌ Error: {response.text}")
        
        else:
            print(f"   ❌ Error al crear proceso: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor API")
        print("   Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    print("\n✅ Prueba completada")

def test_inference_engine_availability():
    """Verifica si el motor de inferencia está disponible"""
    
    print("🔧 Verificando disponibilidad del motor de inferencia...")
    
    try:
        # Hacer una petición simple para verificar si el servidor responde
        response = requests.get(f"{API_BASE_URL}/")
        
        if response.status_code == 200:
            print("✅ Servidor API disponible")
            
            # Intentar crear un proceso para ver si el motor está disponible
            test_process = {
                "zone_id": 999,  # Zona que no existe para probar el manejo de errores
                "process_name": "Test",
                "model_id": "yolo_v8",
                "start_time": "2024-01-01 10:00:00",
                "end_time": "2024-01-01 11:00:00",
                "video_path": "/test/video.mp4"
            }
            
            response = requests.post(
                f"{API_BASE_URL}/api/processes",
                json=test_process,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 404:
                print("✅ Motor de inferencia disponible (zona no encontrada como esperado)")
            elif response.status_code == 200:
                print("⚠️ Proceso creado (verificar si el motor está realmente disponible)")
            else:
                print(f"⚠️ Respuesta inesperada: {response.status_code}")
        else:
            print(f"❌ Servidor no disponible: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de integración...")
    
    # Primero verificar disponibilidad
    test_inference_engine_availability()
    
    print("\n" + "="*50)
    
    # Luego probar la funcionalidad completa
    test_process_with_inference()
