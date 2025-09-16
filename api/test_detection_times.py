#!/usr/bin/env python3
"""
Script de prueba para los endpoints de detection_times
"""

import requests
import json
from datetime import datetime, timedelta

# URL base del API
BASE_URL = "http://localhost:8000"

def test_single_detection_time():
    """Prueba el endpoint para insertar un solo detection_time"""
    print("🧪 Probando inserción de un solo detection_time...")
    
    # Datos de prueba
    detection_data = {
        "zone_id": 1,
        "time_s": 120,  # 2 minutos
        "start_time": "2024-01-15 10:00:00",
        "end_time": "2024-01-15 10:02:00"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/detection-times",
            json=detection_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Éxito: {result['message']}")
            print(f"   ID insertado: {result['inserted_id']}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al API. ¿Está ejecutándose?")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_multiple_detection_times():
    """Prueba el endpoint para insertar múltiples detection_times"""
    print("\n🧪 Probando inserción de múltiples detection_times...")
    
    # Generar datos de prueba para diferentes zonas y horarios
    base_time = datetime(2024, 1, 15, 10, 0, 0)
    detections = []
    
    for i in range(3):
        start_time = base_time + timedelta(minutes=i*5)
        end_time = start_time + timedelta(minutes=2)
        
        detections.append({
            "zone_id": i + 1,
            "time_s": 120,
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    bulk_data = {
        "detections": detections
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/detection-times/bulk",
            json=bulk_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Éxito: {result['message']}")
            print(f"   IDs insertados: {result['inserted_ids']}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al API. ¿Está ejecutándose?")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_dashboard_endpoint():
    """Prueba el endpoint del dashboard para ver si los datos se reflejan"""
    print("\n🧪 Probando endpoint del dashboard...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Dashboard funcionando correctamente")
            print(f"   Datos: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al API. ¿Está ejecutándose?")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_validation_errors():
    """Prueba los casos de error de validación"""
    print("\n🧪 Probando validaciones de error...")
    
    # Caso 1: Fecha inválida
    print("   Probando fecha inválida...")
    invalid_data = {
        "zone_id": 1,
        "time_s": 120,
        "start_time": "fecha-invalida",
        "end_time": "2024-01-15 10:02:00"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/detection-times",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("   ✅ Validación de fecha funcionando correctamente")
        else:
            print(f"   ❌ Error inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Caso 2: start_time >= end_time
    print("   Probando start_time >= end_time...")
    invalid_time_data = {
        "zone_id": 1,
        "time_s": 120,
        "start_time": "2024-01-15 10:02:00",
        "end_time": "2024-01-15 10:00:00"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/detection-times",
            json=invalid_time_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("   ✅ Validación de tiempo funcionando correctamente")
        else:
            print(f"   ❌ Error inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de detection_times API")
    print("=" * 50)
    
    # Ejecutar todas las pruebas
    test_single_detection_time()
    test_multiple_detection_times()
    test_dashboard_endpoint()
    test_validation_errors()
    
    print("\n" + "=" * 50)
    print("✅ Pruebas completadas")
    print("\n💡 Para ver la documentación interactiva del API:")
    print(f"   {BASE_URL}/docs")
