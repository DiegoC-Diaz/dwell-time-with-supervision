#!/usr/bin/env python3
"""
Script de prueba para verificar la conversión de coordenadas entre frontend y backend
"""

import requests
import json
from datetime import datetime

# Configuración
API_BASE_URL = "http://localhost:8000"

def test_coordinate_conversion():
    """Prueba la conversión de coordenadas desde el formato frontend al backend"""
    print("🔍 Probando conversión de coordenadas...")
    
    # Datos de prueba en el formato que envía el frontend (después de conversión)
    test_zone_data = {
        "zone_name": f"Prueba Conversión {datetime.now().strftime('%H%M%S')}",
        "zone_type": "detection",
        "coordinates": [
            [[533, 94], [531, 621], [254, 615], [269, 128], [534, 97]],
            [[540, 95], [837, 104], [859, 618], [541, 619], [543, 94]]
        ]
    }
    
    print("📤 Datos enviados:")
    print(json.dumps(test_zone_data, indent=2))
    
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

def test_invalid_coordinates():
    """Prueba con coordenadas inválidas"""
    print("\n🔍 Probando coordenadas inválidas...")
    
    # Datos con formato incorrecto
    invalid_data = {
        "zone_name": "Prueba Inválida",
        "zone_type": "detection",
        "coordinates": "esto no es un array"  # Formato incorrecto
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/zones",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 422:
            print("✅ Validación funciona correctamente - rechazó coordenadas inválidas")
            return True
        else:
            print(f"❌ Se esperaba error 422, pero se recibió: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de conversión de coordenadas")
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
    
    # Probar conversión válida
    success1 = test_coordinate_conversion()
    
    # Probar coordenadas inválidas
    success2 = test_invalid_coordinates()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ Todas las pruebas pasaron correctamente")
    else:
        print("❌ Algunas pruebas fallaron")

if __name__ == "__main__":
    main()
