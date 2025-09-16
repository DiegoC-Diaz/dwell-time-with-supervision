
from dotenv import load_dotenv
import psycopg2
import os
load_dotenv()
def InsertDetectionTime(zone_id, time_s, start_time, end_time):
    """
    Inserta un nuevo registro en detection_times usando psycopg2 directamente
    
    Args:
        zone_id (int): ID de la zona
        time_s (int): Tiempo en segundos
        start_time (str): Fecha y hora de inicio (formato: 'YYYY-MM-DD HH:MM:SS')
        end_time (str): Fecha y hora de fin (formato: 'YYYY-MM-DD HH:MM:SS')
    
    Returns:
        int: ID del registro insertado o None si hay error
    """

    
    connection = None
    cursor = None
    
    try:
        # Conexión directa a PostgreSQL
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=int(os.getenv("DB_PORT", 5432))
        )
        
        cursor = connection.cursor()
        
        query = """
            INSERT INTO public.detection_times (zone_id, time_s, start_time, end_time) 
            VALUES (%s, %s, %s, %s) 
            RETURNING id;
        """
        
        cursor.execute(query, (zone_id, time_s, start_time, end_time))
        inserted_id = cursor.fetchone()[0]
        
        # Confirmar la transacción
        connection.commit()
        
        print(f"✅ Detection time insertado exitosamente con ID: {inserted_id}")
        
        return inserted_id
        
    except Exception as e:
        print(f"❌ Error al insertar detection_time: {e}")
        if connection:
            connection.rollback()
        return None
    finally:
        # Cerrar cursor y conexión
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def InsertMultipleDetectionTimes(detection_data_list):
    """
    Inserta múltiples registros en detection_times usando psycopg2 directamente
    
    Args:
        detection_data_list (list): Lista de diccionarios con los datos:
            [{"zone_id": int, "time_s": int, "start_time": str, "end_time": str}, ...]
    
    Returns:
        int: Número de registros insertados exitosamente
    """
    import psycopg2
    
    connection = None
    cursor = None
    
    try:
        # Conexión directa a PostgreSQL
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=int(os.getenv("DB_PORT", 5432))
        )
        
        cursor = connection.cursor()
        
        query = """
            INSERT INTO public.detection_times (zone_id, time_s, start_time, end_time) 
            VALUES (%s, %s, %s, %s);
        """
        
        # Preparar lista de parámetros para batch insert
        params_list = []
        for data in detection_data_list:
            params_list.append((
                data["zone_id"], 
                data["time_s"], 
                data["start_time"], 
                data["end_time"]
            ))
        
        # Ejecutar inserción en lote
        cursor.executemany(query, params_list)
        inserted_count = cursor.rowcount
        
        # Confirmar la transacción
        connection.commit()
        
        print(f"✅ Se insertaron {inserted_count} detection times exitosamente")
        
        return inserted_count
        
    except Exception as e:
        print(f"❌ Error al insertar múltiples detection_times: {e}")
        if connection:
            connection.rollback()
        return 0
    finally:
        # Cerrar cursor y conexión
        if cursor:
            cursor.close()
        if connection:
            connection.close()
