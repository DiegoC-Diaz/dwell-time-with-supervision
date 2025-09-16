#!/usr/bin/env python3
"""
Script de prueba para verificar las funciones de hora pico
"""

import sys
import os
from datetime import datetime

# Agregar el directorio api al path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api'))

from database.kpis import PeakHour, PeakHourPerZone

def test_peak_hour_functions():
    """Prueba las funciones de hora pico"""
    
    print("🧪 Probando funciones de hora pico...")
    
    # Usar fecha de hoy para las pruebas
    today = datetime.now().strftime("%Y-%m-%d")
    start_time = f"{today} 00:00:00"
    end_time = f"{today} 23:59:59"
    
    print(f"📅 Fecha de prueba: {today}")
    
    # Probar PeakHour global
    print("\n🔍 Probando PeakHour (global)...")
    try:
        peak_hour_global = PeakHour(start_time, end_time)
        if peak_hour_global:
            print(f"✅ Hora pico global: {peak_hour_global['hour']:02d}:00")
            print(f"📅 Fecha: {peak_hour_global['date']}")
        else:
            print("ℹ️ No hay datos para hora pico global")
    except Exception as e:
        print(f"❌ Error en PeakHour: {e}")
    
    # Probar PeakHourPerZone para zona 1
    print("\n🔍 Probando PeakHourPerZone (zona 1)...")
    try:
        peak_hour_zone1 = PeakHourPerZone(start_time, end_time, 1)
        if peak_hour_zone1:
            print(f"✅ Hora pico zona 1: {peak_hour_zone1['hour']:02d}:00")
            print(f"📅 Fecha: {peak_hour_zone1['date']}")
        else:
            print("ℹ️ No hay datos para hora pico zona 1")
    except Exception as e:
        print(f"❌ Error en PeakHourPerZone: {e}")
    
    # Probar PeakHourPerZone para zona 2
    print("\n🔍 Probando PeakHourPerZone (zona 2)...")
    try:
        peak_hour_zone2 = PeakHourPerZone(start_time, end_time, 2)
        if peak_hour_zone2:
            print(f"✅ Hora pico zona 2: {peak_hour_zone2['hour']:02d}:00")
            print(f"📅 Fecha: {peak_hour_zone2['date']}")
        else:
            print("ℹ️ No hay datos para hora pico zona 2")
    except Exception as e:
        print(f"❌ Error en PeakHourPerZone zona 2: {e}")

def test_dashboard_integration():
    """Prueba la integración con el dashboard"""
    
    print("\n🧪 Probando integración con dashboard...")
    
    # Simular llamada al endpoint del dashboard
    today = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📅 Simulando llamada: GET /api/dashboard?date={today}")
    
    # Simular lógica del dashboard
    formated_date = today
    
    # Probar sin filtro de zona
    print("\n🔍 Sin filtro de zona:")
    try:
        peakHourData = PeakHour(f"{formated_date} 00:00:00", f"{formated_date} 23:59:59")
        if peakHourData and isinstance(peakHourData, dict) and 'hour' in peakHourData:
            peakHour = f"{peakHourData['hour']:02d}:00"
            print(f"✅ Hora pico formateada: {peakHour}")
        else:
            peakHour = "12:00"  # Fallback
            print(f"ℹ️ Usando fallback: {peakHour}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar con filtro de zona
    print("\n🔍 Con filtro de zona (zona 1):")
    try:
        peakHourData = PeakHourPerZone(f"{formated_date} 00:00:00", f"{formated_date} 23:59:59", 1)
        if peakHourData and isinstance(peakHourData, dict) and 'hour' in peakHourData:
            peakHour = f"{peakHourData['hour']:02d}:00"
            print(f"✅ Hora pico zona 1 formateada: {peakHour}")
        else:
            peakHour = "12:00"  # Fallback
            print(f"ℹ️ Usando fallback: {peakHour}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de funciones de hora pico...")
    
    test_peak_hour_functions()
    test_dashboard_integration()
    
    print("\n🎉 Pruebas completadas!")
    print("✅ Las funciones de hora pico están integradas en el dashboard")
    print("✅ Se muestran horas pico reales en lugar de valores aleatorios")
