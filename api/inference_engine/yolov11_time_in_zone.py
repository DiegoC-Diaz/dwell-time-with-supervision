from ultralytics import YOLO
import supervision as sv
import cv2
import numpy as np
import requests
from datetime import datetime, timedelta
from inference_engine.utils.general import find_in_list
from inference_engine.utils.timers import FPSBasedTimer
COLORS = sv.ColorPalette.from_hex(["#E6194B", "#3CB44B", "#FFE119", "#3C76D1"])
COLOR_ANNOTATOR = sv.ColorAnnotator(color=COLORS)
LABEL_ANNOTATOR = sv.LabelAnnotator(
    color=COLORS, text_color=sv.Color.from_hex("#000000")
)

# Colores para diferentes zonas
colors = [
            (255, 0, 0),    # Rojo
            (0, 255, 0),    # Verde
            (0, 0, 255),    # Azul
            (255, 255, 0),  # Amarillo
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cian
        ]


class TrackedObject:
    """Clase para manejar información de objetos trackeados"""
    def __init__(self, tracker_id, zone_id, start_time):
        self.tracker_id = tracker_id
        self.zone_id = zone_id
        self.start_time = start_time
        self.end_time = None
        self.is_active = True
        
    def end_tracking(self, end_time):
        """Marca el fin del tracking del objeto"""
        self.end_time = end_time
        self.is_active = False
        
    def get_duration_seconds(self):
        """Calcula la duración en segundos"""
        if self.end_time and self.start_time:
            return int((self.end_time - self.start_time).total_seconds())
        return 0


class DetectionTimeManager:
    """Manejador para enviar detection times a la API"""
    def __init__(self, api_base_url="http://localhost:8000"):
        self.api_base_url = api_base_url
        
    def send_detection_time(self, zone_id, time_s, start_time, end_time):
        """Envía un detection time a la API"""
        try:
            url = f"{self.api_base_url}/api/detection-times"
            data = {
                "zone_id": zone_id,
                "time_s": time_s,
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            response = requests.post(url, json=data, timeout=5)
            if response.status_code == 200:
                print(f"✅ Detection time enviado: ID {data['zone_id']}, {time_s}s")
                return True
            else:
                print(f"❌ Error enviando detection time: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error en send_detection_time: {e}")
            return False


class TimeInZone():
    def __init__(self, polygons, start_time, weights_path="yolo11s.pt", classes: list[int] = [0], zone_id: int = 1):
        self.polygons = polygons
        self.start_time = start_time
        self.weights_path = weights_path
        self.zone_id = zone_id
        # Ajustar hiperparámetros para vista cenital (desde arriba)
        self.confidence = 0.5  # Threshold para detectar cabezas/personas desde arriba
        self.iou = 0.4  # IoU para mejor separación de personas cercanas
        self.classes = classes
        
        # Parámetros específicos para vista cenital
        self.min_detection_size = 20  # Tamaño mínimo de detección en píxeles
        self.max_detection_size = 200  # Tamaño máximo de detección en píxeles
        
        # Manager para enviar detection times
        self.detection_manager = DetectionTimeManager()
        
        # Diccionario para trackear objetos activos
        self.active_tracks = {}  # {tracker_id: TrackedObject}

    def init_model(self):
        """Inicializa el modelo YOLO con los pesos especificados"""
        if YOLO is None:
            raise ImportError("YOLO not available. Install ultralytics: pip install ultralytics")
        self.model = YOLO(self.weights_path)
        print(f"Modelo YOLO cargado: {self.weights_path}")
        print(f"Tiempo de inicio del video: {self.start_time}")

    def _get_start_datetime(self):
        """Convierte start_time a datetime object"""
        if isinstance(self.start_time, str):
            return datetime.strptime(self.start_time, "%Y-%m-%d %H:%M:%S")
        return self.start_time

    def handle_tracking_changes(self, current_tracker_ids, video_time):
        """Maneja los cambios en el tracking de objetos"""
        current_ids = set(current_tracker_ids) if current_tracker_ids is not None else set()
        previous_ids = set(self.active_tracks.keys())
        
        # Objetos nuevos (entraron al tracking)
        new_objects = current_ids - previous_ids
        for tracker_id in new_objects:
            if tracker_id is not None:
                tracked_obj = TrackedObject(tracker_id, self.zone_id, video_time)
                self.active_tracks[tracker_id] = tracked_obj
                print(f"🟢 Nuevo objeto trackeado: ID {tracker_id} en tiempo {video_time.strftime('%H:%M:%S')}")
        
        # Objetos que salieron del tracking
        lost_objects = previous_ids - current_ids
        for tracker_id in lost_objects:
            if tracker_id in self.active_tracks:
                tracked_obj = self.active_tracks[tracker_id]
                tracked_obj.end_tracking(video_time)
                
                # Enviar detection time a la API
                duration = tracked_obj.get_duration_seconds()
                if duration > 0:  # Solo enviar si duró más de 0 segundos
                    success = self.detection_manager.send_detection_time(
                        zone_id=self.zone_id,
                        time_s=duration,
                        start_time=tracked_obj.start_time,
                        end_time=tracked_obj.end_time
                    )
                    if success:
                        print(f"📊 Detection time registrado: ID {tracker_id}, {duration}s")
                
                # Remover del tracking activo
                del self.active_tracks[tracker_id]
                print(f"🔴 Objeto perdido del tracking: ID {tracker_id}")

    def cleanup_active_tracks(self, end_time):
        """Limpia todos los objetos activos al final del procesamiento"""
        for tracker_id, tracked_obj in list(self.active_tracks.items()):
            tracked_obj.end_tracking(end_time)
            
            # Enviar detection time a la API
            duration = tracked_obj.get_duration_seconds()
            if duration > 0:
                success = self.detection_manager.send_detection_time(
                    zone_id=self.zone_id,
                    time_s=duration,
                    start_time=tracked_obj.start_time,
                    end_time=tracked_obj.end_time
                )
                if success:
                    print(f"📊 Detection time final registrado: ID {tracker_id}, {duration}s")
        
        # Limpiar el diccionario
        self.active_tracks.clear()
        print("🧹 Tracking activo limpiado")

    def run_detections(self,video_path):
        video_info = sv.VideoInfo.from_video_path(video_path=video_path)
        tracker = sv.ByteTrack(
            minimum_matching_threshold=0.7,   # how strict to match detections with existing tracks
            lost_track_buffer=60,             # how many frames to keep "lost" tracks before deleting
            track_activation_threshold=0.60 ,  # detection confidence filter
            frame_rate=video_info.fps
       
        )
     
        frames_generator = sv.get_video_frames_generator(video_path)

        polygons = self.polygons
        zones = [
            sv.PolygonZone(
                polygon=polygon,
                triggering_anchors=(sv.Position.CENTER,),
            )
            for polygon in polygons
        ]
        timers = [FPSBasedTimer(video_info.fps) for _ in zones]
        
        # Variables para calcular tiempo del video
        frame_count = 0
        fps = video_info.fps

        for frame in frames_generator:
            # Calcular tiempo del video basado en FPS
            start_datetime = self._get_start_datetime()
            video_time = start_datetime + timedelta(seconds=frame_count / fps)
            frame_count += 1
            
            # Usar Ultralytics YOLO para inferencia
            results = self.model(frame, conf=self.confidence, iou=self.iou, verbose=False)[0]
            detections = sv.Detections.from_ultralytics(results)
            
            # Filtrar por clases deseadas (personas = clase 0)
            detections = detections[find_in_list(detections.class_id, self.classes)]
            if len(detections) > 0:
                detections = tracker.update_with_detections(detections)
            else:
                detections = sv.Detections.empty()
            
            # *** NUEVO: Filtrar detecciones para solo trackear las que están dentro de los polígonos ***
            # Esto evita que se trackeen objetos fuera de las zonas y se envíen datos incorrectos a la API
            detections_in_zones = sv.Detections.empty()
            if len(detections) > 0:
                zone_detections_list = []
                for zone in zones:
                    zone_detections = detections[zone.trigger(detections)]
                    if len(zone_detections) > 0:
                        zone_detections_list.append(zone_detections)
                
                # Combinar todas las detecciones de zonas usando numpy concatenate
                if zone_detections_list:
                    if len(zone_detections_list) == 1:
                        detections_in_zones = zone_detections_list[0]
                    else:
                        # Combinar múltiples detecciones usando concatenate
                        combined_xyxy = np.concatenate([d.xyxy for d in zone_detections_list])
                        combined_confidence = np.concatenate([d.confidence for d in zone_detections_list])
                        combined_class_id = np.concatenate([d.class_id for d in zone_detections_list])
                        
                        # Combinar tracker_ids si existen
                        combined_tracker_id = None
                        if all(hasattr(d, 'tracker_id') and d.tracker_id is not None for d in zone_detections_list):
                            combined_tracker_id = np.concatenate([d.tracker_id for d in zone_detections_list])
                        
                        detections_in_zones = sv.Detections(
                            xyxy=combined_xyxy,
                            confidence=combined_confidence,
                            class_id=combined_class_id,
                            tracker_id=combined_tracker_id
                        )
            
            # Manejar cambios en el tracking - SOLO para objetos dentro de zonas
            # Los objetos fuera de zonas NO serán trackeados ni enviados a la API
            if hasattr(detections_in_zones, 'tracker_id') and detections_in_zones.tracker_id is not None:
                self.handle_tracking_changes(detections_in_zones.tracker_id, video_time)
    
            annotated_frame = frame.copy()
            
            # *** Anotar TODAS las detecciones para visualización ***
            if len(detections) > 0:
                # Anotar todas las detecciones generales (bounding boxes) - usando nuevo annotator
                try:
                    bounding_box_annotator = sv.BoundingBoxAnnotator()
                    annotated_frame = bounding_box_annotator.annotate(
                        scene=annotated_frame,
                        detections=detections
                    )
                except AttributeError:
                    # Fallback para versiones anteriores
                    box_annotator = sv.BoxAnnotator()
                    annotated_frame = box_annotator.annotate(
                        scene=annotated_frame,
                        detections=detections
                    )
                
                # Anotar tracker IDs para todas las detecciones - SOLO si hay tracker_ids válidos
                if hasattr(detections, 'tracker_id') and detections.tracker_id is not None and len(detections.tracker_id) == len(detections):
                    # Verificar que todos los tracker_ids sean válidos (no None)
                    valid_tracker_ids = [tid for tid in detections.tracker_id if tid is not None]
                    if len(valid_tracker_ids) == len(detections.tracker_id):
                        tracker_labels = [f"ID: {tracker_id}" for tracker_id in detections.tracker_id]
                        label_annotator = sv.LabelAnnotator()
                        annotated_frame = label_annotator.annotate(
                            scene=annotated_frame,
                            detections=detections,
                            labels=tracker_labels
                        )
    
            for idx, zone in enumerate(zones):
                annotated_frame = sv.draw_polygon(
                    scene=annotated_frame, polygon=zone.polygon, color=COLORS.by_idx(idx)
                )
    
                if len(detections) > 0 and hasattr(detections, 'tracker_id') and len(detections.tracker_id) > 0:
                    detections_in_zone = detections[zone.trigger(detections)]
                else:
                    detections_in_zone = sv.Detections.empty()
                
                # Solo procesar timer si hay detecciones en la zona
                if len(detections_in_zone) > 0:
                    time_in_zone = timers[idx].tick(detections_in_zone)
                else:
                    time_in_zone = []
                custom_color_lookup = np.full(detections_in_zone.class_id.shape, idx)
    
                annotated_frame = COLOR_ANNOTATOR.annotate(
                    scene=annotated_frame,
                    detections=detections_in_zone,
                    custom_color_lookup=custom_color_lookup,
                )
                labels = [
                    f"#{tracker_id} {int(time // 60):02d}:{int(time % 60):02d}"
                    for tracker_id, time in zip(detections_in_zone.tracker_id, time_in_zone)
                    ] if len(detections_in_zone) > 0 and detections_in_zone.tracker_id is not None else []
                annotated_frame = LABEL_ANNOTATOR.annotate(
                    scene=annotated_frame,
                    detections=detections_in_zone,
                    labels=labels,
                    custom_color_lookup=custom_color_lookup,
                )
        
            cv2.imshow("Processed Video", annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        
        # Limpiar objetos activos al final del procesamiento
        start_datetime = self._get_start_datetime()
        final_video_time = start_datetime + timedelta(seconds=frame_count / fps)
        self.cleanup_active_tracks(final_video_time)
        cv2.destroyAllWindows()