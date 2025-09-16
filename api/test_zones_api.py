#!/usr/bin/env python3
"""
Script de prueba para los endpoints de zonas de la API
"""

import requests
import json
import sys
from datetime import datetime

# Configuración
API_BASE_URL = "http://localhost:8000"

def test_api_health():
    """Prueba el endpoint de salud de la API"""
    print("🔍 Probando salud de la API...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API funcionando: {data.get('message', 'OK')}")
            return True
        else:
            print(f"❌ Error en API: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_get_zones():
    """Prueba obtener todas las zonas"""
    print("\n🔍 Probando GET /api/zones...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/zones")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Zonas obtenidas: {len(data.get('zones', []))} zonas encontradas")
            return data.get('zones', [])
        else:
            print(f"❌ Error obteniendo zonas: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return []

def test_create_zone():
    """Prueba crear una nueva zona"""
    print("\n🔍 Probando POST /api/zones...")
    
    # Datos de prueba - polígono similar al ejemplo del usuario
    # Formato correcto: List[List[List[int]]] (array de polígonos, cada polígono es array de puntos [x,y])
    test_zone_data = {
        "zone_name": f"Zona de Prueba {datetime.now().strftime('%H%M%S')}",
        "zone_type": "detection",
        "coordinates": [
            [[533, 94], [531, 621], [254, 615], [269, 128], [534, 97]],
            [[540, 95], [837, 104], [859, 618], [541, 619], [543, 94]]
        ]
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/zones",
            json=test_zone_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                zone_id = data.get('zone_id')
                print(f"✅ Zona creada exitosamente con ID: {zone_id}")
                return zone_id
            else:
                print(f"❌ Error creando zona: {data.get('message', 'Error desconocido')}")
                return None
        else:
            print(f"❌ Error HTTP: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def test_get_zone_by_id(zone_id):
    """Prueba obtener una zona específica por ID"""
    print(f"\n🔍 Probando GET /api/zones/{zone_id}...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/zones/{zone_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Zona obtenida: {data.get('zone_name', 'Sin nombre')}")
            print(f"   - Tipo: {data.get('zone_type', 'Sin tipo')}")
            print(f"   - Polígonos: {len(data.get('coordinates', []))}")
            return data
        else:
            print(f"❌ Error obteniendo zona: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def test_update_zone(zone_id):
    """Prueba actualizar una zona"""
    print(f"\n🔍 Probando PUT /api/zones/{zone_id}...")
    
    update_data = {
        "zone_name": f"Zona Actualizada {datetime.now().strftime('%H%M%S')}",
        "zone_type": "counting"
    }
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/api/zones/{zone_id}",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Zona actualizada exitosamente")
                return True
            else:
                print(f"❌ Error actualizando zona: {data.get('message', 'Error desconocido')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_delete_zone(zone_id):
    """Prueba eliminar una zona"""
    print(f"\n🔍 Probando DELETE /api/zones/{zone_id}...")
    try:
        response = requests.delete(f"{API_BASE_URL}/api/zones/{zone_id}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Zona eliminada exitosamente")
                return True
            else:
                print(f"❌ Error eliminando zona: {data.get('message', 'Error desconocido')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_validation_errors():
    """Prueba errores de validación"""
    print("\n🔍 Probando validaciones de errores...")
    
    # Prueba 1: Nombre vacío
    print("  - Probando nombre vacío...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/zones",
            json={"zone_name": "", "zone_type": "detection", "coordinates": [[[1, 1], [2, 2], [3, 3]]]},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 400:
            print("    ✅ Validación de nombre vacío funciona")
        else:
            print(f"    ❌ Validación falló: {response.status_code}")
    except Exception as e:
        print(f"    ❌ Error: {e}")
    
    # Prueba 2: Coordenadas vacías
    print("  - Probando coordenadas vacías...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/zones",
            json={"zone_name": "Test", "zone_type": "detection", "coordinates": []},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 400:
            print("    ✅ Validación de coordenadas vacías funciona")
        else:
            print(f"    ❌ Validación falló: {response.status_code}")
    except Exception as e:
        print(f"    ❌ Error: {e}")

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de API de Zonas")
    print("=" * 50)
    
    # Verificar que la API esté funcionando
    if not test_api_health():
        print("\n❌ La API no está disponible. Asegúrate de que esté ejecutándose en http://localhost:8000")
        sys.exit(1)
    
    # Obtener zonas existentes
    existing_zones = test_get_zones()
    
    # Crear una zona de prueba
    zone_id = test_create_zone()
    
    if zone_id:
        # Obtener la zona creada
        zone_data = test_get_zone_by_id(zone_id)
        
        if zone_data:
            # Actualizar la zona
            test_update_zone(zone_id)
            
            # Verificar la actualización
            test_get_zone_by_id(zone_id)
        
        # Eliminar la zona de prueba
        test_delete_zone(zone_id)
    
    # Probar validaciones
    test_validation_errors()
    
    # Verificar estado final
    final_zones = test_get_zones()
    
    print("\n" + "=" * 50)
    print("✅ Pruebas completadas")
    print(f"📊 Zonas al inicio: {len(existing_zones)}")
    print(f"📊 Zonas al final: {len(final_zones)}")

if __name__ == "__main__":
    main()
