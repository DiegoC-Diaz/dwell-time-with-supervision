#!/usr/bin/env python3
"""
Script de prueba para verificar el manejo de múltiples polígonos
"""

import requests
import json
from datetime import datetime

# Configuración
API_BASE_URL = "http://localhost:8000"

def test_multiple_polygons():
    """Prueba crear una zona con múltiples polígonos"""
    print("🔍 Probando creación de zona con múltiples polígonos...")
    
    # Datos de prueba con múltiples polígonos (como el ejemplo del usuario)
    test_zone_data = {
        "zone_name": f"Zona Múltiples Polígonos {datetime.now().strftime('%H%M%S')}",
        "zone_type": "detection",
        "coordinates": [
            # Primer polígono
            [[533, 94], [531, 621], [254, 615], [269, 128], [534, 97]],
            # Segundo polígono
            [[540, 95], [837, 104], [859, 618], [541, 619], [543, 94]]
        ]
    }
    
    print("📤 Datos enviados:")
    print(f"   Nombre: {test_zone_data['zone_name']}")
    print(f"   Tipo: {test_zone_data['zone_type']}")
    print(f"   Polígonos: {len(test_zone_data['coordinates'])}")
    for i, polygon in enumerate(test_zone_data['coordinates']):
        print(f"     Polígono {i+1}: {len(polygon)} puntos")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/zones",
            json=test_zone_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📥 Respuesta HTTP: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                zone_id = data.get('zone_id')
                print(f"✅ Zona creada exitosamente con ID: {zone_id}")
                
                # Verificar que se puede obtener la zona
                get_response = requests.get(f"{API_BASE_URL}/api/zones/{zone_id}")
                if get_response.status_code == 200:
                    zone_data = get_response.json()
                    print(f"✅ Zona obtenida: {zone_data.get('zone_name')}")
                    print(f"   - Coordenadas: {len(zone_data.get('coordinates', []))} polígonos")
                    
                    # Mostrar detalles de cada polígono
                    for i, polygon in enumerate(zone_data.get('coordinates', [])):
                        print(f"     Polígono {i+1}: {len(polygon)} puntos")
                    
                    # Limpiar zona de prueba
                    delete_response = requests.delete(f"{API_BASE_URL}/api/zones/{zone_id}")
                    if delete_response.status_code == 200:
                        print(f"✅ Zona de prueba eliminada")
                    else:
                        print(f"⚠️ No se pudo eliminar zona de prueba: {delete_response.status_code}")
                else:
                    print(f"❌ Error obteniendo zona: {get_response.status_code}")
                
                return True
            else:
                print(f"❌ Error en respuesta: {data.get('message', 'Error desconocido')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_single_polygon():
    """Prueba crear una zona con un solo polígono"""
    print("\n🔍 Probando creación de zona con un solo polígono...")
    
    test_zone_data = {
        "zone_name": f"Zona Un Solo Polígono {datetime.now().strftime('%H%M%S')}",
        "zone_type": "counting",
        "coordinates": [
            # Un solo polígono
            [[100, 100], [200, 100], [200, 200], [100, 200]]
        ]
    }
    
    print(f"📤 Polígonos: {len(test_zone_data['coordinates'])}")
    
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
                print(f"✅ Zona con un polígono creada exitosamente con ID: {zone_id}")
                
                # Limpiar zona de prueba
                requests.delete(f"{API_BASE_URL}/api/zones/{zone_id}")
                print(f"✅ Zona de prueba eliminada")
                return True
            else:
                print(f"❌ Error en respuesta: {data.get('message', 'Error desconocido')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_empty_polygons():
    """Prueba con coordenadas vacías"""
    print("\n🔍 Probando con coordenadas vacías...")
    
    test_zone_data = {
        "zone_name": "Prueba Vacía",
        "zone_type": "detection",
        "coordinates": []
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/zones",
            json=test_zone_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ Validación funciona - rechazó coordenadas vacías")
            return True
        else:
            print(f"❌ Se esperaba error 400, pero se recibió: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de múltiples polígonos")
    print("=" * 60)
    
    # Verificar que la API esté funcionando
    try:
        health_response = requests.get(f"{API_BASE_URL}/")
        if health_response.status_code != 200:
            print("❌ La API no está disponible")
            return
    except:
        print("❌ No se puede conectar a la API")
        return
    
    # Probar múltiples polígonos
    success1 = test_multiple_polygons()
    
    # Probar un solo polígono
    success2 = test_single_polygon()
    
    # Probar coordenadas vacías
    success3 = test_empty_polygons()
    
    print("\n" + "=" * 60)
    if success1 and success2 and success3:
        print("✅ Todas las pruebas pasaron correctamente")
        print("🎯 El sistema soporta múltiples polígonos por zona")
    else:
        print("❌ Algunas pruebas fallaron")

if __name__ == "__main__":
    main()
