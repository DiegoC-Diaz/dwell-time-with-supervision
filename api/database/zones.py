"""
Funciones de base de datos para gestión de zonas de detección
"""

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os
import json
from typing import List, Dict, Optional

load_dotenv()


def get_db_connection():
    """
    Crea y retorna una conexión a PostgreSQL
    
    Returns:
        psycopg2.connection: Conexión a la base de datos
    """
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        return connection
    except Exception as e:
        print(f"❌ Error al conectar con PostgreSQL: {e}")
        return None


def GetZones() -> Optional[List[Dict]]:
    """
    Obtiene todas las zonas activas
    
    Returns:
        List[Dict]: Lista de zonas con sus datos
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            query = """
                SELECT id, zone_name, zone_type, coordinates, is_active, created_at, updated_at 
                FROM public.zones 
                WHERE is_active = true 
                ORDER BY created_at DESC;
            """
            cursor.execute(query)
            result = cursor.fetchall()
            
            if result:
                zones = []
                for row in result:
                    zones.append({
                        "id": row['id'],
                        "zone_name": row['zone_name'],
                        "zone_type": row['zone_type'],
                        "coordinates": row['coordinates'],  # Ya es un dict/JSON
                        "is_active": row['is_active'],
                        "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                        "updated_at": row['updated_at'].isoformat() if row['updated_at'] else None
                    })
                return zones
            else:
                return []
    except Exception as e:
        print(f"❌ Error al obtener zonas: {e}")
        return None
    finally:
        connection.close()


def GetZoneById(zone_id: int) -> Optional[Dict]:
    """
    Obtiene una zona específica por ID
    
    Args:
        zone_id (int): ID de la zona
    
    Returns:
        Dict: Datos de la zona o None si no existe
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            query = """
                SELECT id, zone_name, zone_type, coordinates, is_active, created_at, updated_at 
                FROM public.zones 
                WHERE id = %s;
            """
            cursor.execute(query, (zone_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    "id": result['id'],
                    "zone_name": result['zone_name'],
                    "zone_type": result['zone_type'],
                    "coordinates": result['coordinates'],  # Ya es un dict/JSON
                    "is_active": result['is_active'],
                    "created_at": result['created_at'].isoformat() if result['created_at'] else None,
                    "updated_at": result['updated_at'].isoformat() if result['updated_at'] else None
                }
            else:
                return None
    except Exception as e:
        print(f"❌ Error al obtener zona por ID: {e}")
        return None
    finally:
        connection.close()


def InsertZone(zone_name: str, zone_type: str, coordinates: List[List[List[int]]]) -> Optional[int]:
    """
    Inserta una nueva zona
    
    Args:
        zone_name (str): Nombre de la zona
        zone_type (str): Tipo de zona (ej: 'detection', 'counting')
        coordinates (List[List[List[int]]]): Coordenadas del polígono en formato [[[x1,y1], [x2,y2], ...]]
    
    Returns:
        int: ID de la zona insertada o None si hay error
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            # Convertir coordenadas a JSON
            coordinates_json = json.dumps(coordinates)
            
            query = """
                INSERT INTO public.zones (zone_name, zone_type, coordinates) 
                VALUES (%s, %s, %s) 
                RETURNING id;
            """
            cursor.execute(query, (zone_name, zone_type, coordinates_json))
            inserted_id = cursor.fetchone()[0]
            connection.commit()
            
            if inserted_id and inserted_id > 0:
                print(f"✅ Zona insertada exitosamente con ID: {inserted_id}")
                return inserted_id
            else:
                print("❌ No se pudo obtener el ID de la zona insertada")
                return None
    except Exception as e:
        print(f"❌ Error al insertar zona: {e}")
        connection.rollback()
        return None
    finally:
        connection.close()


def UpdateZone(zone_id: int, zone_name: str = None, zone_type: str = None, coordinates: List[List[List[int]]] = None) -> bool:
    """
    Actualiza una zona existente
    
    Args:
        zone_id (int): ID de la zona a actualizar
        zone_name (str, optional): Nuevo nombre de la zona
        zone_type (str, optional): Nuevo tipo de zona
        coordinates (List[List[List[int]]], optional): Nuevas coordenadas
    
    Returns:
        bool: True si se actualizó exitosamente, False en caso contrario
    """
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            # Construir query dinámicamente basado en los parámetros proporcionados
            update_fields = []
            params = []
            
            if zone_name is not None:
                update_fields.append("zone_name = %s")
                params.append(zone_name)
            
            if zone_type is not None:
                update_fields.append("zone_type = %s")
                params.append(zone_type)
            
            if coordinates is not None:
                update_fields.append("coordinates = %s")
                params.append(json.dumps(coordinates))
            
            # Siempre actualizar updated_at
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            
            # Agregar zone_id al final de los parámetros
            params.append(zone_id)
            
            query = f"""
                UPDATE public.zones 
                SET {', '.join(update_fields)}
                WHERE id = %s;
            """
            
            cursor.execute(query, params)
            affected_rows = cursor.rowcount
            connection.commit()
            
            if affected_rows > 0:
                print(f"✅ Zona {zone_id} actualizada exitosamente")
                return True
            else:
                print(f"❌ No se encontró zona con ID {zone_id}")
                return False
    except Exception as e:
        print(f"❌ Error al actualizar zona: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()


def DeleteZone(zone_id: int) -> bool:
    """
    Elimina una zona (soft delete - marca como inactiva)
    
    Args:
        zone_id (int): ID de la zona a eliminar
    
    Returns:
        bool: True si se eliminó exitosamente, False en caso contrario
    """
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            query = """
                UPDATE public.zones 
                SET is_active = false, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s;
            """
            cursor.execute(query, (zone_id,))
            affected_rows = cursor.rowcount
            connection.commit()
            
            if affected_rows > 0:
                print(f"✅ Zona {zone_id} eliminada exitosamente")
                return True
            else:
                print(f"❌ No se encontró zona con ID {zone_id}")
                return False
    except Exception as e:
        print(f"❌ Error al eliminar zona: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()


def CheckZoneNameExists(zone_name: str, exclude_id: int = None) -> bool:
    """
    Verifica si ya existe una zona con el nombre dado
    
    Args:
        zone_name (str): Nombre de la zona a verificar
        exclude_id (int, optional): ID de zona a excluir de la búsqueda (para updates)
    
    Returns:
        bool: True si el nombre ya existe, False en caso contrario
    """
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            if exclude_id:
                query = """
                    SELECT COUNT(*) FROM public.zones 
                    WHERE zone_name = %s AND id != %s AND is_active = true;
                """
                cursor.execute(query, (zone_name, exclude_id))
            else:
                query = """
                    SELECT COUNT(*) FROM public.zones 
                    WHERE zone_name = %s AND is_active = true;
                """
                cursor.execute(query, (zone_name,))
            
            result = cursor.fetchone()
            return result[0] > 0 if result else False
    except Exception as e:
        print(f"❌ Error al verificar nombre de zona: {e}")
        return False
    finally:
        connection.close()


if __name__ == "__main__":
    # Pruebas de las funciones
    print("🔧 Probando funciones de zonas...")
    
    # Probar obtener zonas
    zones = GetZones()
    print(f"Zonas encontradas: {len(zones) if zones else 0}")
    
    # Probar insertar zona de prueba
    test_coordinates = [[[533, 94], [531, 621], [254, 615], [269, 128], [534, 97]]]
    zone_id = InsertZone("Zona de Prueba", "detection", test_coordinates)
    if zone_id:
        print(f"✅ Zona de prueba insertada con ID: {zone_id}")
        
        # Probar obtener zona por ID
        zone = GetZoneById(zone_id)
        if zone:
            print(f"✅ Zona obtenida: {zone['zone_name']}")
        
        # Probar actualizar zona
        updated = UpdateZone(zone_id, zone_name="Zona Actualizada")
        if updated:
            print("✅ Zona actualizada exitosamente")
        
        # Probar eliminar zona
        deleted = DeleteZone(zone_id)
        if deleted:
            print("✅ Zona eliminada exitosamente")
    
    print("✅ Pruebas de zonas completadas")
