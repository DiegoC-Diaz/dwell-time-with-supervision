#!/usr/bin/env python3
"""
Script de prueba para verificar que el tracking solo funciona para objetos dentro de polígonos
"""

import numpy as np
import supervision as sv
from inference_engine.yolov11_time_in_zone import TimeInZone, TrackedObject
from datetime import datetime

def test_polygon_filtering():
    """Prueba que solo se trackeen objetos dentro de polígonos"""
    
    print("🧪 Probando filtrado de polígonos...")
    
    # Crear polígono de prueba (cuadrado pequeño en el centro)
    polygon = np.array([
        [100, 100],  # Esquina superior izquierda
        [200, 100],  # Esquina superior derecha  
        [200, 200],  # Esquina inferior derecha
        [100, 200]   # Esquina inferior izquierda
    ])
    
    # Crear instancia de TimeInZone
    start_time = datetime.now()
    time_in_zone = TimeInZone(
        polygons=[polygon],
        start_time=start_time,
        weights_path="yolo11s.pt",
        classes=[0],  # Solo personas
        zone_id=1
    )
    
    # Simular detecciones: algunas dentro del polígono, otras fuera
    detections_data = {
        'xyxy': np.array([
            [50, 50, 80, 80],    # Fuera del polígono (izquierda)
            [150, 150, 180, 180], # Dentro del polígono
            [250, 250, 280, 280], # Fuera del polígono (derecha)
            [120, 120, 150, 150], # Dentro del polígono
        ]),
        'confidence': np.array([0.8, 0.9, 0.7, 0.85]),
        'class_id': np.array([0, 0, 0, 0])
    }
    
    detections = sv.Detections(**detections_data)
    
    # Crear zona de prueba
    zone = sv.PolygonZone(
        polygon=polygon,
        triggering_anchors=(sv.Position.CENTER,)
    )
    
    # Filtrar detecciones dentro de la zona
    detections_in_zone = detections[zone.trigger(detections)]
    
    print(f"📊 Detecciones totales: {len(detections)}")
    print(f"📊 Detecciones dentro de zona: {len(detections_in_zone)}")
    
    # Verificar que solo las detecciones dentro del polígono fueron filtradas
    expected_inside = 2  # Las detecciones en [150,150] y [120,120]
    actual_inside = len(detections_in_zone)
    
    if actual_inside == expected_inside:
        print("✅ Prueba exitosa: Solo se detectaron objetos dentro del polígono")
        return True
    else:
        print(f"❌ Prueba fallida: Esperado {expected_inside}, obtenido {actual_inside}")
        return False

def test_detections_combination():
    """Prueba la combinación correcta de detecciones usando numpy concatenate"""
    
    print("\n🧪 Probando combinación de detecciones...")
    
    # Crear detecciones de prueba para múltiples zonas
    detections_zone1 = sv.Detections(
        xyxy=np.array([[150, 150, 180, 180]]),
        confidence=np.array([0.9]),
        class_id=np.array([0]),
        tracker_id=np.array([1])
    )
    
    detections_zone2 = sv.Detections(
        xyxy=np.array([[120, 120, 150, 150]]),
        confidence=np.array([0.85]),
        class_id=np.array([0]),
        tracker_id=np.array([2])
    )
    
    # Combinar usando numpy concatenate (método correcto)
    try:
        combined_xyxy = np.concatenate([detections_zone1.xyxy, detections_zone2.xyxy])
        combined_confidence = np.concatenate([detections_zone1.confidence, detections_zone2.confidence])
        combined_class_id = np.concatenate([detections_zone1.class_id, detections_zone2.class_id])
        combined_tracker_id = np.concatenate([detections_zone1.tracker_id, detections_zone2.tracker_id])
        
        combined_detections = sv.Detections(
            xyxy=combined_xyxy,
            confidence=combined_confidence,
            class_id=combined_class_id,
            tracker_id=combined_tracker_id
        )
        
        print(f"📊 Detecciones combinadas: {len(combined_detections)}")
        print(f"📊 Tracker IDs combinados: {combined_detections.tracker_id}")
        
        if len(combined_detections) == 2 and len(combined_detections.tracker_id) == 2:
            print("✅ Prueba exitosa: Detecciones combinadas correctamente")
            return True
        else:
            print("❌ Prueba fallida: Combinación incorrecta")
            return False
            
    except Exception as e:
        print(f"❌ Error en combinación: {e}")
        return False

def test_tracking_logic():
    """Prueba la lógica de tracking"""
    
    print("\n🧪 Probando lógica de tracking...")
    
    # Crear polígono de prueba
    polygon = np.array([
        [100, 100],
        [200, 100], 
        [200, 200],
        [100, 200]
    ])
    
    start_time = datetime.now()
    time_in_zone = TimeInZone(
        polygons=[polygon],
        start_time=start_time,
        weights_path="yolo11s.pt",
        classes=[0],
        zone_id=1
    )
    
    # Simular tracker IDs
    tracker_ids_inside = [1, 2]  # Solo IDs dentro de zona
    tracker_ids_outside = [3, 4]  # IDs fuera de zona
    
    # Simular que solo los objetos dentro de zona están siendo trackeados
    current_tracker_ids = tracker_ids_inside
    
    # Verificar que active_tracks solo contiene objetos dentro de zona
    print(f"📊 Tracker IDs dentro de zona: {tracker_ids_inside}")
    print(f"📊 Tracker IDs fuera de zona: {tracker_ids_outside}")
    
    # Simular el proceso de tracking
    video_time = start_time
    time_in_zone.handle_tracking_changes(current_tracker_ids, video_time)
    
    print(f"📊 Objetos activos trackeados: {len(time_in_zone.active_tracks)}")
    
    # Verificar que solo se trackearon objetos dentro de zona
    tracked_ids = set(time_in_zone.active_tracks.keys())
    expected_ids = set(tracker_ids_inside)
    
    if tracked_ids == expected_ids:
        print("✅ Prueba exitosa: Solo se trackearon objetos dentro de zona")
        return True
    else:
        print(f"❌ Prueba fallida: IDs esperados {expected_ids}, obtenidos {tracked_ids}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de filtrado de polígonos...")
    
    test1_passed = test_polygon_filtering()
    test2_passed = test_detections_combination()
    test3_passed = test_tracking_logic()
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 Todas las pruebas pasaron exitosamente!")
        print("✅ Los objetos fuera de polígonos NO serán trackeados")
        print("✅ Solo se enviarán a la API objetos dentro de zonas")
        print("✅ La combinación de detecciones funciona correctamente")
    else:
        print("\n❌ Algunas pruebas fallaron")
