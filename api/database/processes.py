"""
Funciones de base de datos para gestión de procesos de análisis de video
"""

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os
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


def GetProcesses() -> Optional[List[Dict]]:
    """
    Obtiene todos los procesos
    
    Returns:
        List[Dict]: Lista de procesos con sus datos
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            query = """
                SELECT p.id, p.zone_id, p.process_name, p.model_id, 
                       p.start_time, p.end_time, p.video_path, p.is_done,
                       z.zone_name, z.zone_type
                FROM public.processes p
                LEFT JOIN public.zones z ON p.zone_id = z.id
                ORDER BY p.start_time DESC;
            """
            cursor.execute(query)
            result = cursor.fetchall()
            
            if result:
                processes = []
                for row in result:
                    processes.append({
                        "id": row['id'],
                        "zone_id": row['zone_id'],
                        "process_name": row['process_name'],
                        "model_id": row['model_id'],
                        "start_time": row['start_time'].isoformat() if row['start_time'] else None,
                        "end_time": row['end_time'].isoformat() if row['end_time'] else None,
                        "video_path": row['video_path'],
                        "is_done": row['is_done'],
                        "zone_name": row['zone_name'],
                        "zone_type": row['zone_type']
                    })
                return processes
            else:
                return []
    except Exception as e:
        print(f"❌ Error al obtener procesos: {e}")
        return None
    finally:
        connection.close()


def GetProcessById(process_id: int) -> Optional[Dict]:
    """
    Obtiene un proceso específico por ID
    
    Args:
        process_id (int): ID del proceso
    
    Returns:
        Dict: Datos del proceso o None si no existe
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            query = """
                SELECT p.id, p.zone_id, p.process_name, p.model_id, 
                       p.start_time, p.end_time, p.video_path, p.is_done,
                       z.zone_name, z.zone_type
                FROM public.processes p
                LEFT JOIN public.zones z ON p.zone_id = z.id
                WHERE p.id = %s;
            """
            cursor.execute(query, (process_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    "id": result['id'],
                    "zone_id": result['zone_id'],
                    "process_name": result['process_name'],
                    "model_id": result['model_id'],
                    "start_time": result['start_time'].isoformat() if result['start_time'] else None,
                    "end_time": result['end_time'].isoformat() if result['end_time'] else None,
                    "video_path": result['video_path'],
                    "is_done": result['is_done'],
                    "zone_name": result['zone_name'],
                    "zone_type": result['zone_type']
                }
            else:
                return None
    except Exception as e:
        print(f"❌ Error al obtener proceso por ID: {e}")
        return None
    finally:
        connection.close()


def InsertProcess(
    zone_id: int,
    process_name: str,
    model_id: str,
    start_time: str,
    end_time: str,
    video_path: str
) -> Optional[int]:
    """
    Inserta un nuevo proceso
    
    Args:
        zone_id (int): ID de la zona
        process_name (str): Nombre del proceso
        model_id (str): ID del modelo a usar
        start_time (str): Hora de inicio en formato 'YYYY-MM-DD HH:MM:SS'
        end_time (str): Hora de fin en formato 'YYYY-MM-DD HH:MM:SS'
        video_path (str): Ruta del video
    
    Returns:
        int: ID del proceso insertado o None si hay error
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            query = """
                INSERT INTO public.processes (zone_id, process_name, model_id, start_time, end_time, video_path) 
                VALUES (%s, %s, %s, %s, %s, %s) 
                RETURNING id;
            """
            cursor.execute(query, (zone_id, process_name, model_id, start_time, end_time, video_path))
            inserted_id = cursor.fetchone()[0]
            connection.commit()
            
            if inserted_id and inserted_id > 0:
                print(f"✅ Proceso insertado exitosamente con ID: {inserted_id}")
                return inserted_id
            else:
                print("❌ No se pudo obtener el ID del proceso insertado")
                return None
    except Exception as e:
        print(f"❌ Error al insertar proceso: {e}")
        connection.rollback()
        return None
    finally:
        connection.close()


def UpdateProcess(
    process_id: int,
    process_name: str = None,
    model_id: str = None,
    start_time: str = None,
    end_time: str = None,
    video_path: str = None,
    is_done: bool = None
) -> bool:
    """
    Actualiza un proceso existente
    
    Args:
        process_id (int): ID del proceso a actualizar
        process_name (str, optional): Nuevo nombre del proceso
        model_id (str, optional): Nuevo ID del modelo
        start_time (str, optional): Nueva hora de inicio
        end_time (str, optional): Nueva hora de fin
        video_path (str, optional): Nueva ruta del video
        is_done (bool, optional): Estado de finalización
    
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
            
            if process_name is not None:
                update_fields.append("process_name = %s")
                params.append(process_name)
            
            if model_id is not None:
                update_fields.append("model_id = %s")
                params.append(model_id)
            
            if start_time is not None:
                update_fields.append("start_time = %s")
                params.append(start_time)
            
            if end_time is not None:
                update_fields.append("end_time = %s")
                params.append(end_time)
            
            if video_path is not None:
                update_fields.append("video_path = %s")
                params.append(video_path)
            
            if is_done is not None:
                update_fields.append("is_done = %s")
                params.append(is_done)
            
            # Agregar process_id al final de los parámetros
            params.append(process_id)
            
            query = f"""
                UPDATE public.processes 
                SET {', '.join(update_fields)}
                WHERE id = %s;
            """
            
            cursor.execute(query, params)
            affected_rows = cursor.rowcount
            connection.commit()
            
            if affected_rows > 0:
                print(f"✅ Proceso {process_id} actualizado exitosamente")
                return True
            else:
                print(f"❌ No se encontró proceso con ID {process_id}")
                return False
    except Exception as e:
        print(f"❌ Error al actualizar proceso: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()


def DeleteProcess(process_id: int) -> bool:
    """
    Elimina un proceso
    
    Args:
        process_id (int): ID del proceso a eliminar
    
    Returns:
        bool: True si se eliminó exitosamente, False en caso contrario
    """
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        with connection.cursor() as cursor:
            query = """
                DELETE FROM public.processes 
                WHERE id = %s;
            """
            cursor.execute(query, (process_id,))
            affected_rows = cursor.rowcount
            connection.commit()
            
            if affected_rows > 0:
                print(f"✅ Proceso {process_id} eliminado exitosamente")
                return True
            else:
                print(f"❌ No se encontró proceso con ID {process_id}")
                return False
    except Exception as e:
        print(f"❌ Error al eliminar proceso: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()


def GetProcessesByZone(zone_id: int) -> Optional[List[Dict]]:
    """
    Obtiene todos los procesos de una zona específica
    
    Args:
        zone_id (int): ID de la zona
    
    Returns:
        List[Dict]: Lista de procesos de la zona
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            query = """
                SELECT p.id, p.zone_id, p.process_name, p.model_id, 
                       p.start_time, p.end_time, p.video_path, p.is_done,
                       z.zone_name, z.zone_type
                FROM public.processes p
                LEFT JOIN public.zones z ON p.zone_id = z.id
                WHERE p.zone_id = %s
                ORDER BY p.start_time DESC;
            """
            cursor.execute(query, (zone_id,))
            result = cursor.fetchall()
            
            if result:
                processes = []
                for row in result:
                    processes.append({
                        "id": row['id'],
                        "zone_id": row['zone_id'],
                        "process_name": row['process_name'],
                        "model_id": row['model_id'],
                        "start_time": row['start_time'].isoformat() if row['start_time'] else None,
                        "end_time": row['end_time'].isoformat() if row['end_time'] else None,
                        "video_path": row['video_path'],
                        "is_done": row['is_done'],
                        "zone_name": row['zone_name'],
                        "zone_type": row['zone_type']
                    })
                return processes
            else:
                return []
    except Exception as e:
        print(f"❌ Error al obtener procesos por zona: {e}")
        return None
    finally:
        connection.close()


if __name__ == "__main__":
    # Pruebas de las funciones
    print("🔧 Probando funciones de procesos...")
    
    # Probar obtener procesos
    processes = GetProcesses()
    print(f"Procesos encontrados: {len(processes) if processes else 0}")
    
    # Probar insertar proceso de prueba
    process_id = InsertProcess(
        zone_id=1,
        process_name="Proceso de Prueba",
        model_id="yolo_v8",
        start_time="2024-01-01 10:00:00",
        end_time="2024-01-01 11:00:00",
        video_path="/path/to/video.mp4"
    )
    
    if process_id:
        print(f"✅ Proceso de prueba insertado con ID: {process_id}")
        
        # Probar obtener proceso por ID
        process = GetProcessById(process_id)
        if process:
            print(f"✅ Proceso obtenido: {process['process_name']}")
        
        # Probar actualizar proceso
        updated = UpdateProcess(process_id, process_name="Proceso Actualizado")
        if updated:
            print("✅ Proceso actualizado exitosamente")
        
        # Probar eliminar proceso
        deleted = DeleteProcess(process_id)
        if deleted:
            print("✅ Proceso eliminado exitosamente")
    
    print("✅ Pruebas de procesos completadas")
