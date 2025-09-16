import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os
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


def AverageTime(start_date_time, end_date_time):
    """
    Calcula el tiempo promedio de detección en un rango de fechas
    
    Args:
        start_date_time (str): Fecha y hora de inicio
        end_date_time (str): Fecha y hora de fin
    
    Returns:
        float: Tiempo promedio en segundos o None si hay error
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT AVG(EXTRACT(EPOCH FROM (end_time - start_time))) 
                FROM public.detection_times 
                WHERE start_time >= %s AND end_time <= %s;
            """
            cursor.execute(query, (start_date_time, end_date_time))
            result = cursor.fetchone()
            
            if result and result[0] is not None:
                return float(result[0])
            else:
                return None
    except Exception as e:
        print(f"❌ Error en AverageTime: {e}")
        return None
    finally:
        connection.close()



def getDetectionRegistries(start_date_time, end_date_time):
    """
    Obtiene los registros de detección en un rango de fechas
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT * FROM public.detection_times 
                WHERE start_time >= %s AND end_time <= %s;
            """
            cursor.execute(query, (start_date_time, end_date_time))
            result = cursor.fetchall()
            return result
    except Exception as e:
        print(f"❌ Error en getDetectionRegistries: {e}")
        return None
    finally:
        connection.close()

def getDetectionRegistriesPerZone(start_date_time, end_date_time, zone):
    """
    Obtiene los registros de detección en un rango de fechas por zona
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT * FROM public.detection_times 
                WHERE start_time >= %s AND end_time <= %s AND zone_id = %s;
            """
            cursor.execute(query, (start_date_time, end_date_time, zone))
            result = cursor.fetchall()
            return result
    except Exception as e:
        print(f"❌ Error en getDetectionRegistriesPerZone: {e}")
        return None
    finally:
        connection.close()




def PeakHour(start_date_time, end_date_time):
    """
    Obtiene la hora pico de detección en un rango de fechas
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            query = """
                SELECT * FROM public.detection_times 
                WHERE start_time >= %s AND end_time <= %s
                ORDER BY time_s DESC
                LIMIT 1;
            """
            cursor.execute(query, (start_date_time, end_date_time))
            result = cursor.fetchone()
            
            if result:
                return {
                    "hour": result['start_time'].hour, 
                    "date": result['start_time'].date()
                }
            else:
                return None
    except Exception as e:
        print(f"❌ Error en PeakHour: {e}")
        return None
    finally:
        connection.close()

def PeakHourPerZone(start_date_time, end_date_time, zone):
    """
    Obtiene la hora pico de detección en un rango de fechas por zona
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            query = """
                SELECT * FROM public.detection_times 
                WHERE start_time >= %s AND end_time <= %s AND zone_id = %s
                ORDER BY time_s DESC
                LIMIT 1;
            """
            cursor.execute(query, (start_date_time, end_date_time, zone))
            result = cursor.fetchone()
            
            if result:
                return {
                    "hour": result['start_time'].hour, 
                    "date": result['start_time'].date()
                }
            else:
                return None
    except Exception as e:
        print(f"❌ Error en PeakHourPerZone: {e}")
        return None
    finally:
        connection.close()

def AverageTimePerZone(start_date_time, end_date_time, zone):
    """
    Calcula el tiempo promedio de detección por zona en un rango de fechas
    
    Args:
        start_date_time (str): Fecha y hora de inicio
        end_date_time (str): Fecha y hora de fin
        zone (int): ID de la zona
    
    Returns:
        float: Tiempo promedio en segundos o None si hay error
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT AVG(EXTRACT(EPOCH FROM (end_time - start_time))) 
                FROM public.detection_times 
                WHERE start_time >= %s AND end_time <= %s AND zone_id = %s;
            """
            cursor.execute(query, (start_date_time, end_date_time, zone))
            result = cursor.fetchone()
            
            if result and result[0] is not None:
                return float(result[0])
            else:
                return None
    except Exception as e:
        print(f"❌ Error en AverageTimePerZone: {e}")
        return None
    finally:
        connection.close()



def TotalVisitorsPerZone(start_date_time, end_date_time,zone):
    """
    Calcula el total de visitantes únicos en un rango de fechas
    
    Args:
        start_date_time (str): Fecha y hora de inicio
        end_date_time (str): Fecha y hora de fin
    
    Returns:
        int: Número total de visitantes únicos o None si hay error
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT COUNT(DISTINCT id) 
                FROM public.detection_times 
                WHERE start_time >= %s AND end_time <= %s AND zone_id = %s;
            """
            cursor.execute(query, (start_date_time, end_date_time,zone))
            result = cursor.fetchone()
            
            if result and result[0] is not None:
                return int(result[0])
            else:
                return None
    except Exception as e:
        print(f"❌ Error en TotalVisitors: {e}")
        return None
    finally:
        connection.close()



def TotalVisitors(start_date_time, end_date_time):
    """
    Calcula el total de visitantes únicos en un rango de fechas
    
    Args:
        start_date_time (str): Fecha y hora de inicio
        end_date_time (str): Fecha y hora de fin
    
    Returns:
        int: Número total de visitantes únicos o None si hay error
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT COUNT(DISTINCT id) 
                FROM public.detection_times 
                WHERE start_time >= %s AND end_time <= %s;
            """
            cursor.execute(query, (start_date_time, end_date_time))
            result = cursor.fetchone()
            
            if result and result[0] is not None:
                return int(result[0])
            else:
                return None
    except Exception as e:
        print(f"❌ Error en TotalVisitors: {e}")
        return None
    finally:
        connection.close()



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
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            query = """
                INSERT INTO public.detection_times (zone_id, time_s, start_time, end_time) 
                VALUES (%s, %s, %s, %s) 
                RETURNING id;
            """
            cursor.execute(query, (zone_id, time_s, start_time, end_time))
            inserted_id = cursor.fetchone()[0]
            connection.commit()
            
            if inserted_id and inserted_id > 0:
                print(f"✅ Detection time insertado exitosamente con ID: {inserted_id}")
                return inserted_id
            else:
                print("❌ No se pudo obtener el ID del registro insertado")
                return None
    except Exception as e:
        print(f"❌ Error al insertar detection_time: {e}")
        connection.rollback()
        return None
    finally:
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
    connection = get_db_connection()
    if not connection:
        return 0
    
    try:
        with connection.cursor() as cursor:
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
            
            # Ejecutar inserción en lote usando executemany
            cursor.executemany(query, params_list)
            inserted_count = cursor.rowcount
            connection.commit()
            
            if inserted_count > 0:
                print(f"✅ Se insertaron {inserted_count} detection times exitosamente")
                return inserted_count
            else:
                print("❌ No se insertaron registros")
                return 0
            
    except Exception as e:
        print(f"❌ Error al insertar múltiples detection_times: {e}")
        connection.rollback()
        return 0
    finally:
        connection.close()


if __name__ == "__main__":
    print(AverageTime("2024-06-01 00:00:00","2025-06-30 23:59:59"))
    print(AverageTimePerZone("2024-06-01 00:00:00","2025-06-30 23:59:59",1))
    print(TotalVisitors("2024-06-01 00:00:00","2025-06-30 23:59:59"))

    print("✅ PostgreSQL está disponible")


