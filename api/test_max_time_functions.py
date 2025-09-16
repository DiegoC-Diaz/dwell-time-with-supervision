#!/usr/bin/env python3
"""
Script de prueba para las nuevas funciones de tiempo máximo por persona
"""

import sys
import os
from datetime import datetime, timedelta

# Agregar el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.kpis import MaxTimePerPerson, MaxTimePerPersonPerZone

def test_max_time_functions():
    """
    Prueba las funciones de tiempo máximo por persona
    """
    print("🧪 Probando funciones de tiempo máximo por persona...")
    
    # Usar fechas de prueba (últimos 30 días)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    start_datetime = start_date.strftime("%Y-%m-%d %H:%M:%S")
    end_datetime = end_date.strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"📅 Rango de fechas: {start_datetime} - {end_datetime}")
    
    # Probar función general
    print("\n🔍 Probando MaxTimePerPerson (general)...")
    try:
        result = MaxTimePerPerson(start_datetime, end_datetime)
        if result:
            print(f"✅ Tiempo máximo encontrado:")
            print(f"   - Duración: {result['duration_minutes']} minutos ({result['max_time_s']} segundos)")
            print(f"   - Zona: {result['zone_id']}")
            print(f"   - Inicio: {result['start_time']}")
            print(f"   - Fin: {result['end_time']}")
        else:
            print("ℹ️  No se encontraron datos para el rango de fechas")
    except Exception as e:
        print(f"❌ Error en MaxTimePerPerson: {e}")
    
    # Probar función por zona específica
    print("\n🔍 Probando MaxTimePerPersonPerZone (zona 1)...")
    try:
        result = MaxTimePerPersonPerZone(start_datetime, end_datetime, 1)
        if result:
            print(f"✅ Tiempo máximo en zona 1:")
            print(f"   - Duración: {result['duration_minutes']} minutos ({result['max_time_s']} segundos)")
            print(f"   - Zona: {result['zone_id']}")
            print(f"   - Inicio: {result['start_time']}")
            print(f"   - Fin: {result['end_time']}")
        else:
            print("ℹ️  No se encontraron datos para la zona 1 en el rango de fechas")
    except Exception as e:
        print(f"❌ Error en MaxTimePerPersonPerZone: {e}")
    
    print("\n✅ Pruebas completadas")

if __name__ == "__main__":
    test_max_time_functions()
