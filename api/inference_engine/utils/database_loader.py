"""
Database loader utilities for loading polygons and zone data
Utiliza el módulo store para conectar con PostgreSQL
"""

import json
import numpy as np
import sys
import os
from typing import List, Optional, Dict, Any

# Agregar el directorio store al path para importar PostgreSQLConnector
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'store'))

try:
    from postgresql import PostgreSQLConnector
    DB_AVAILABLE = True
except ImportError:
    print("⚠️ No se pudo importar PostgreSQLConnector. Verifica que el módulo store esté disponible.")
    DB_AVAILABLE = False

# Configuración de base de datos (misma que en la API)
DB_CONFIG = {
    'host': 'localhost',
    'database': 'vision_analytics', 
    'user': 'postgres',
    'password': 'VisionAnalytics2024!',
    'port': 5432
}

def get_db_connection() -> Optional[PostgreSQLConnector]:
    """
    Obtiene una conexión a la base de datos PostgreSQL usando store/postgresql.py
    
    Returns:
        PostgreSQLConnector instance o None si no se puede conectar
    """
    if not DB_AVAILABLE:
        print("❌ PostgreSQLConnector no disponible")
        return None
    
    try:
        db_connector = PostgreSQLConnector(**DB_CONFIG)
        if db_connector.connect():
            print("✅ Conectado a PostgreSQL usando store/postgresql.py")
            return db_connector
        else:
            print("❌ No se pudo conectar a PostgreSQL")
            return None
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def load_polygons(zone_id: int) -> List[np.ndarray]:
    """
    Carga los polígonos de una zona específica desde la base de datos
    
    Args:
        zone_id: ID de la zona en la base de datos
        
    Returns:
        List[np.ndarray]: Lista de polígonos como arrays de NumPy
        
    Raises:
        ValueError: Si la zona no existe o no está activa
        ConnectionError: Si no se puede conectar a la base de datos
    """
    print(f"🔍 Cargando polígonos para zona ID: {zone_id}")
    
    # Obtener conexión a la base de datos
    db = get_db_connection()
    if not db:
        raise ConnectionError("No se pudo conectar a la base de datos PostgreSQL")
    
    try:
        # Query para obtener la zona específica
        query = """
        SELECT id, zone_name, zone_type, coordinates, is_active, created_at, updated_at
        FROM vision_analytics.zones 
        WHERE id = %s AND is_active = true
        """
        
        result = db.execute_query(query, (zone_id,))
        
        if not result:
            raise ValueError(f"Zona con ID {zone_id} no encontrada o no está activa")
        
        zone_data = result[0]
        print(f"📍 Zona encontrada: '{zone_data['zone_name']}'")
        
        # Extraer coordenadas
        coordinates = zone_data.get('coordinates', {})
        if isinstance(coordinates, str):
            coordinates = json.loads(coordinates)
        
        # Obtener polígonos
        polygons_data = coordinates.get('polygons', [])
        if not polygons_data:
            raise ValueError(f"No hay polígonos definidos para la zona {zone_id}")
        
        # Convertir a formato NumPy (compatible con supervision)
        polygons = []
        for i, polygon_points in enumerate(polygons_data):
            if len(polygon_points) < 3:
                print(f"⚠️ Polígono {i+1} tiene menos de 3 puntos, ignorando...")
                continue
            
            # Convertir a NumPy array con dtype int32 (requerido por supervision)
            polygon_array = np.array(polygon_points, dtype=np.int32)
            polygons.append(polygon_array)
            print(f"✅ Polígono {i+1}: {len(polygon_points)} puntos")
        
        if not polygons:
            raise ValueError(f"No se pudieron cargar polígonos válidos para la zona {zone_id}")
        
        print(f"🎯 Cargados {len(polygons)} polígonos para la zona '{zone_data['zone_name']}'")
        
        return polygons
        
    except Exception as e:
        print(f"❌ Error cargando polígonos: {str(e)}")
        raise
    finally:
        # Cerrar conexión
        if db:
            db.disconnect()

def load_zone_info(zone_id: int) -> Optional[Dict[str, Any]]:
    """
    Carga información completa de una zona específica
    
    Args:
        zone_id: ID de la zona en la base de datos
        
    Returns:
        Dict con información de la zona o None si no existe
    """
    print(f"🔍 Cargando información de zona ID: {zone_id}")
    
    db = get_db_connection()
    if not db:
        print("❌ No se pudo conectar a la base de datos")
        return None
    
    try:
        query = """
        SELECT id, zone_name, zone_type, coordinates, is_active, created_at, updated_at
        FROM vision_analytics.zones 
        WHERE id = %s AND is_active = true
        """
        
        result = db.execute_query(query, (zone_id,))
        
        if not result:
            print(f"❌ Zona con ID {zone_id} no encontrada")
            return None
        
        zone_data = result[0]
        
        # Procesar coordenadas
        coordinates = zone_data.get('coordinates', {})
        if isinstance(coordinates, str):
            coordinates = json.loads(coordinates)
        
        zone_info = {
            'id': zone_data['id'],
            'zone_name': zone_data['zone_name'],
            'zone_type': zone_data['zone_type'],
            'polygons': coordinates.get('polygons', []),
            'description': coordinates.get('description', zone_data['zone_name']),
            'total_polygons': coordinates.get('total_polygons', len(coordinates.get('polygons', []))),
            'is_active': zone_data['is_active'],
            'created_at': zone_data['created_at'].isoformat() if zone_data['created_at'] else None,
            'updated_at': zone_data['updated_at'].isoformat() if zone_data['updated_at'] else None
        }
        
        print(f"✅ Información cargada para zona '{zone_info['zone_name']}'")
        return zone_info
        
    except Exception as e:
        print(f"❌ Error cargando información de zona: {str(e)}")
        return None
    finally:
        if db:
            db.disconnect()

def list_available_zones() -> List[Dict[str, Any]]:
    """
    Lista todas las zonas activas disponibles en la base de datos
    
    Returns:
        List[Dict]: Lista de zonas con información básica
    """
    print("🔍 Listando zonas disponibles...")
    
    db = get_db_connection()
    if not db:
        print("❌ No se pudo conectar a la base de datos")
        return []
    
    try:
        query = """
        SELECT id, zone_name, zone_type, coordinates, created_at
        FROM vision_analytics.zones 
        WHERE is_active = true
        ORDER BY created_at DESC
        """
        
        result = db.execute_query(query)
        
        zones = []
        for zone_data in result:
            coordinates = zone_data.get('coordinates', {})
            if isinstance(coordinates, str):
                coordinates = json.loads(coordinates)
            
            zone_info = {
                'id': zone_data['id'],
                'zone_name': zone_data['zone_name'],
                'zone_type': zone_data['zone_type'],
                'total_polygons': len(coordinates.get('polygons', [])),
                'description': coordinates.get('description', zone_data['zone_name']),
                'created_at': zone_data['created_at'].isoformat() if zone_data['created_at'] else None
            }
            zones.append(zone_info)
        
        print(f"✅ Encontradas {len(zones)} zonas activas")
        for zone in zones:
            print(f"   - ID: {zone['id']}, Nombre: '{zone['zone_name']}', Polígonos: {zone['total_polygons']}")
        
        return zones
        
    except Exception as e:
        print(f"❌ Error listando zonas: {str(e)}")
        return []
    finally:
        if db:
            db.disconnect()

# Función de compatibilidad con el código existente
def load_zones_config_from_db(zone_id: int) -> List[np.ndarray]:
    """
    Función de compatibilidad que mantiene la misma interfaz que load_zones_config
    pero carga desde la base de datos en lugar de archivo JSON
    
    Args:
        zone_id: ID de la zona en la base de datos
        
    Returns:
        List[np.ndarray]: Lista de polígonos como arrays de NumPy
    """
    return load_polygons(zone_id)
