#!/usr/bin/env python3
"""
Script de prueba para el endpoint de procesos
"""

import requests
import json
from datetime import datetime, timedelta

# Configuración
API_BASE_URL = "http://localhost:8000"

def test_processes_endpoints():
    """Prueba todos los endpoints de procesos"""
    
    print("🧪 Iniciando pruebas de endpoints de procesos...")
    
    # Datos de prueba
    test_process = {
        "zone_id": 1,  # Asumiendo que existe una zona con ID 1
        "process_name": "Prueba de Proceso",
        "model_id": "yolo_v8",
        "start_time": "2024-01-01 10:00:00",
        "end_time": "2024-01-01 11:00:00",
        "video_path": "/test/video.mp4"
    }
    
    try:
        # 1. Probar GET /api/processes
        print("\n1. Probando GET /api/processes...")
        response = requests.get(f"{API_BASE_URL}/api/processes")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Procesos encontrados: {len(data.get('processes', []))}")
        else:
            print(f"   ❌ Error: {response.text}")
        
        # 2. Probar POST /api/processes
        print("\n2. Probando POST /api/processes...")
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
            
            # 3. Probar GET /api/processes/{id}
            print(f"\n3. Probando GET /api/processes/{process_id}...")
            response = requests.get(f"{API_BASE_URL}/api/processes/{process_id}")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Proceso obtenido: {data.get('process_name')}")
            else:
                print(f"   ❌ Error: {response.text}")
            
            # 4. Probar PUT /api/processes/{id}
            print(f"\n4. Probando PUT /api/processes/{process_id}...")
            update_data = {
                "process_name": "Proceso Actualizado",
                "is_done": True
            }
            response = requests.put(
                f"{API_BASE_URL}/api/processes/{process_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Proceso actualizado exitosamente")
            else:
                print(f"   ❌ Error: {response.text}")
            
            # 5. Probar GET /api/processes/zone/{zone_id}
            print(f"\n5. Probando GET /api/processes/zone/{test_process['zone_id']}...")
            response = requests.get(f"{API_BASE_URL}/api/processes/zone/{test_process['zone_id']}")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Procesos de zona encontrados: {len(data.get('processes', []))}")
            else:
                print(f"   ❌ Error: {response.text}")
            
            # 6. Probar DELETE /api/processes/{id}
            print(f"\n6. Probando DELETE /api/processes/{process_id}...")
            response = requests.delete(f"{API_BASE_URL}/api/processes/{process_id}")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ Proceso eliminado exitosamente")
            else:
                print(f"   ❌ Error: {response.text}")
        
        else:
            print(f"   ❌ Error al crear proceso: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor API")
        print("   Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    
    print("\n✅ Pruebas completadas")

if __name__ == "__main__":
    test_processes_endpoints()
