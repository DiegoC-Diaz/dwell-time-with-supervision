#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión a PostgreSQL
"""

import os
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_connection():
    """Prueba la conexión a PostgreSQL"""
    print("🔧 Probando conexión a PostgreSQL...")
    
    try:
        # Mostrar configuración (sin password)
        print(f"   Host: {os.getenv('DB_HOST')}")
        print(f"   Database: {os.getenv('DB_NAME')}")
        print(f"   User: {os.getenv('DB_USER')}")
        print(f"   Port: {os.getenv('DB_PORT')}")
        
        # Intentar conexión
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=int(os.getenv("DB_PORT", 5432))
        )
        
        print("✅ Conexión exitosa!")
        
        # Probar consulta simple
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"   PostgreSQL version: {version}")
        
        # Verificar si la tabla detection_times existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'detection_times'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("✅ Tabla 'detection_times' existe")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM public.detection_times;")
            count = cursor.fetchone()[0]
            print(f"   Registros en detection_times: {count}")
            
            # Mostrar estructura de la tabla
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'detection_times' 
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            print("   Estructura de la tabla:")
            for col_name, col_type in columns:
                print(f"     - {col_name}: {col_type}")
                
        else:
            print("❌ Tabla 'detection_times' NO existe")
            print("   Necesitas ejecutar el script databaseDLL.sql primero")
        
        cursor.close()
        connection.close()
        
    except psycopg2.Error as e:
        print(f"❌ Error de PostgreSQL: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_insert():
    """Prueba una inserción simple"""
    print("\n🧪 Probando inserción...")
    
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=int(os.getenv("DB_PORT", 5432))
        )
        
        cursor = connection.cursor()
        
        # Datos de prueba
        query = """
            INSERT INTO public.detection_times (zone_id, time_s, start_time, end_time) 
            VALUES (%s, %s, %s, %s) 
            RETURNING id;
        """
        
        cursor.execute(query, (1, 120, "2024-01-15 10:00:00", "2024-01-15 10:02:00"))
        inserted_id = cursor.fetchone()[0]
        
        connection.commit()
        
        print(f"✅ Inserción exitosa! ID: {inserted_id}")
        
        cursor.close()
        connection.close()
        
    except psycopg2.Error as e:
        print(f"❌ Error de PostgreSQL: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    print("🚀 Diagnóstico de PostgreSQL")
    print("=" * 50)
    
    test_connection()
    test_insert()
    
    print("\n" + "=" * 50)
    print("✅ Diagnóstico completado")
