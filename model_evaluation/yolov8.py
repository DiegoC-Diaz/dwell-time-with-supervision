import os
import supervision as sv
from inference import get_model
import cv2
import numpy as np 
from frame_loader import load_frames_from_folder
from scipy.io import loadmat

# Configuration constants
CONFIDENCE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.5
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")

# Initialize annotators once
BOUNDING_BOX_ANNOTATOR = sv.BoxAnnotator()
LABEL_ANNOTATOR = sv.LabelAnnotator()

def validate_api_key():
    """Validate that the Roboflow API key is available."""
    if not ROBOFLOW_API_KEY:
        raise ValueError("ROBOFLOW_API_KEY environment variable is not set. Please set it before running the script.")
    return ROBOFLOW_API_KEY

def load_ground_truth_coordinates(gt_path="mall_dataset/mall_gt.mat"):
    """
    Load ground truth person coordinates from .mat file.
    
    Args:
        gt_path (str): Path to the ground truth .mat file
        
    Returns:
        list: List of person coordinates per frame
    """
    try:
        mall_gt = loadmat(gt_path)
        coordinates_per_frame = []
        
        for index in range(mall_gt["frame"].size):
            try:
                frame_data = mall_gt['frame'][0][index]
                
                # Verificar si hay datos de personas en este frame
                if len(frame_data) > 0 and len(frame_data[0]) > 0:
                    # Intentar diferentes formas de acceder a las coordenadas
                    try:
                        persons = frame_data[0][0][0]
                        coordinates_per_frame.append(persons)
                    except (IndexError, TypeError):
                        # Si falla, intentar acceso directo
                        try:
                            persons = frame_data[0][0]
                            coordinates_per_frame.append(persons)
                        except (IndexError, TypeError):
                            # Si aún falla, usar lista vacía
                            coordinates_per_frame.append([])
                else:
                    coordinates_per_frame.append([])
                    
            except Exception as e:
                print(f"Warning: Error processing frame {index}: {e}")
                coordinates_per_frame.append([])
                
        return coordinates_per_frame
    except Exception as e:
        print(f"Warning: Could not load ground truth coordinates: {e}")
        return []

def coordinates_to_bounding_box(coordinates):
    """
    Convert person coordinates to bounding box.
    
    Args:
        coordinates: Array of (x, y) coordinates for a person
        
    Returns:
        tuple: (x_min, y_min, x_max, y_max) bounding box
    """
    if coordinates is None or len(coordinates) == 0:
        return None
    
    try:
        # Convertir a numpy array si no lo es
        coords = np.array(coordinates)
        
        # Verificar que tenga la forma correcta
        if coords.ndim == 1:
            # Si es 1D, puede ser una sola coordenada
            if len(coords) >= 2:
                return (coords[0], coords[1], coords[0], coords[1])
            else:
                return None
        elif coords.ndim == 2:
            # Si es 2D, extraer x e y
            if coords.shape[1] >= 2:
                x_coords = coords[:, 0]
                y_coords = coords[:, 1]
                
                x_min = np.min(x_coords)
                y_min = np.min(y_coords)
                x_max = np.max(x_coords)
                y_max = np.max(y_coords)
                
                return (x_min, y_min, x_max, y_max)
            else:
                return None
        else:
            return None
            
    except Exception as e:
        print(f"Warning: Error converting coordinates to bounding box: {e}")
        return None

def calculate_iou(box1, box2):
    """
    Calculate Intersection over Union (IoU) between two bounding boxes.
    
    Args:
        box1: (x_min, y_min, x_max, y_max) for first box
        box2: (x_min, y_min, x_max, y_max) for second box
        
    Returns:
        float: IoU value between 0 and 1
    """
    if box1 is None or box2 is None:
        return 0.0
    
    # Calculate intersection area
    x_left = max(box1[0], box2[0])
    y_top = max(box1[1], box2[1])
    x_right = min(box1[2], box2[2])
    y_bottom = min(box1[3], box2[3])
    
    if x_right < x_left or y_bottom < y_top:
        return 0.0
    
    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    
    # Calculate union area
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = area1 + area2 - intersection_area
    
    if union_area == 0:
        return 0.0
    
    return intersection_area / union_area

def point_in_bounding_box(point, bbox):
    """
    Check if a point is inside a bounding box.
    
    Args:
        point: (x, y) coordinates
        bbox: (x_min, y_min, x_max, y_max) bounding box
        
    Returns:
        bool: True if point is inside bbox
    """
    if bbox is None:
        return False
    
    x, y = point
    x_min, y_min, x_max, y_max = bbox
    
    return x_min <= x <= x_max and y_min <= y <= y_max

def match_detections_to_ground_truth(detections, gt_coordinates, distance_threshold=50):
    """
    Match detections to ground truth points using distance-based matching.
    
    Args:
        detections: Supervision detections object
        gt_coordinates: Array of person coordinates for current frame (shape: [n_persons, 2])
        distance_threshold: Maximum distance for a match (in pixels)
        
    Returns:
        tuple: (true_positives, false_positives, false_negatives)
    """
    if not hasattr(detections, 'xyxy') or len(detections.xyxy) == 0:
        # No detections, all ground truth are false negatives
        return 0, 0, len(gt_coordinates)
    
    if len(gt_coordinates) == 0:
        # No ground truth, all detections are false positives
        return 0, len(detections.xyxy), 0
    
    # Convert ground truth coordinates to points
    gt_points = []
    for person_coords in gt_coordinates:
        # person_coords es un array de shape [2] con (x, y)
        if len(person_coords) >= 2:
            gt_points.append((person_coords[0], person_coords[1]))
    
    if len(gt_points) == 0:
        return 0, len(detections.xyxy), 0
    
    # Calculate distance matrix between detections and ground truth points
    distance_matrix = np.zeros((len(detections.xyxy), len(gt_points)))
    for i, det_box in enumerate(detections.xyxy):
        # Calcular centro del bounding box de detección
        det_center_x = (det_box[0] + det_box[2]) / 2
        det_center_y = (det_box[1] + det_box[3]) / 2
        
        for j, gt_point in enumerate(gt_points):
            # Calcular distancia euclidiana
            distance = np.sqrt((det_center_x - gt_point[0])**2 + (det_center_y - gt_point[1])**2)
            distance_matrix[i, j] = distance
    
    # Find matches using greedy approach
    matched_detections = set()
    matched_gt = set()
    
    # Sort by distance ascending
    matches = []
    for i in range(len(detections.xyxy)):
        for j in range(len(gt_points)):
            if distance_matrix[i, j] <= distance_threshold:
                matches.append((distance_matrix[i, j], i, j))
    
    matches.sort()  # Sort by distance ascending
    
    # Assign matches greedily
    for distance, det_idx, gt_idx in matches:
        if det_idx not in matched_detections and gt_idx not in matched_gt:
            matched_detections.add(det_idx)
            matched_gt.add(gt_idx)
    
    true_positives = len(matched_detections)
    false_positives = len(detections.xyxy) - true_positives
    false_negatives = len(gt_points) - true_positives
    
    return true_positives, false_positives, false_negatives

def setup_zones(frame, zone_configuration_path):
    """
    Setup polygon zones from configuration.
    
    Args:
        frame: First frame to get resolution
        zone_configuration_path (str): Path to zone configuration
        
    Returns:
        list: List of PolygonZone objects
    """
    polygons = [
        np.array([[3, 292], [104, 205], [117, 180], [126, 145], [118, 80], [110, 43], [153, 32], [210, 27], [314, 21], [384, 24], [421, 47], [466, 73], [505, 100], [530, 120], [571, 165], [608, 246], [635, 320], [636, 417], [639, 457], [623, 478], [529, 480], [461, 480], [8, 476]])
    ]
    zones = [
        sv.PolygonZone(
            polygon=polygon,
            triggering_anchors=(sv.Position.CENTER,)
        )
        for polygon in polygons
    ]
    return zones

def count_classes(detections, class_ids):
    """
    Count the number of detections for specified class IDs.
    
    Args:
        detections: Supervision detections object
        class_ids: List of class IDs to count (e.g., [0, 1] for person and bicycle)
        
    Returns:
        int: Number of detections for the specified classes
    """
    if not hasattr(detections, 'data') or not detections.data:
        return 0
    
    # Intentar diferentes nombres de campo para class_id
    class_field = None
    if 'class_id' in detections.data:
        class_field = 'class_id'
    elif 'class_name' in detections.data:
        class_field = 'class_name'
    elif 'class' in detections.data:
        class_field = 'class'
    else:
        return 0
    
    # Mapeo de IDs numéricos a nombres de clase
    class_id_to_name = {
        0: 'person',
    }
    
    # Convertir class_ids numéricos a nombres de clase
    target_classes = []
    for class_id in class_ids:
        if class_id in class_id_to_name:
            target_classes.append(class_id_to_name[class_id])
    
    # Contar detecciones
    count = 0
    for detected_class in detections.data[class_field]:
        if detected_class in target_classes:
            count += 1
    
    return count

def add_text_overlay(frame, text, position, color=(255, 255, 255)):
    """
    Add text overlay to frame.
    
    Args:
        frame: Image frame
        text (str): Text to display
        position (tuple): (x, y) position
        color (tuple): RGB color values
    """
    cv2.putText(
        frame,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        color,
        1,
        cv2.LINE_AA
    )

def run_model(source_video_path: str, model_id: str, iou_threshold: float, confidence_threshold: float, class_ids: list = [0]):
    """
    Run YOLOv8 model on video frames with zone-based detection.
    
    Args:
        source_video_path (str): Path to source video/frames
        model_id (str): Roboflow model ID
        iou_threshold (float): IoU threshold for NMS
        confidence_threshold (float): Confidence threshold for detections
        class_ids (list): List of class IDs to count (default: [0] for person)
    """
    # Validate API key
    api_key = validate_api_key()
    
    # Initialize tracking variables
    last_detection_count = 0
    total_detections = 0
    
    # Initialize metrics variables
    recall_sum = 0
    error_sum = 0
    true_positives_sum = 0
    false_positives_sum = 0
    false_negatives_sum = 0
    valid_frames = 0
    error_per_frame = []  # Para calcular estadísticas detalladas
    
    # Initialize model
    model = get_model(model_id=model_id, api_key=api_key)
    
    # Load frames
    frames = load_frames_from_folder(source_video_path)
    if not frames:
        raise ValueError(f"No frames found in {source_video_path}")
    
    # Setup zones
    zones = setup_zones(frames[0], "")
    if not zones:
        raise ValueError("No zones configured")
    
    # Load ground truth data (optional)
    gt_coordinates = load_ground_truth_coordinates()
    
    # Initialize tracking variables
    last_detection_count = 0
    total_detections = 0
    
    # Process frames
    for frame_index, frame in enumerate(frames):
        # Run inference
        results = model.infer(
            frame,
            confidence=confidence_threshold,
            iou_threshold=iou_threshold
        )[0]
        
        # Convert to supervision detections
        detections = sv.Detections.from_inference(results)
      
        
        # Create annotated frame
        annotated_frame = frame.copy()
        
        # Draw polygon zone (using first zone only)
        primary_zone = zones[0]
        # Dibujar polígono usando OpenCV directamente
        cv2.polylines(
            annotated_frame,
            [primary_zone.polygon],
            isClosed=True,
            color=(0, 255, 0),
            thickness=1
        )
        
        # Use all detections (no zone filtering)
        detections_in_zone = detections
      
        # Annotate detections
        annotated_frame = BOUNDING_BOX_ANNOTATOR.annotate(
            scene=annotated_frame,
            detections=detections_in_zone
        )
        annotated_frame = LABEL_ANNOTATOR.annotate(
            scene=annotated_frame,
            detections=detections_in_zone
        )
        
        # Count detections for specified classes in current frame
        current_frame_detection_count = count_classes(detections_in_zone, class_ids)
        
        # Update total detections (count all detections, not just increases)
        total_detections += current_frame_detection_count
        
        # Calculate real metrics using distance-based matching
        if frame_index < len(gt_coordinates):
            gt_coords = gt_coordinates[frame_index]
            
            # Use real distance-based matching with more generous threshold
            tp, fp, fn = match_detections_to_ground_truth(detections_in_zone, gt_coords, distance_threshold=100)
            
            # Acumular métricas reales
            true_positives_sum += tp
            false_positives_sum += fp
            false_negatives_sum += fn
            
            # Calcular recall por frame
            gt_count = len(gt_coords)
            if gt_count > 0:
                frame_recall = tp / gt_count
                recall_sum += frame_recall
                valid_frames += 1
            
            # Calcular error absoluto (diferencia entre detectados y reales)
            frame_error = abs(current_frame_detection_count - gt_count)
            error_sum += frame_error
            error_per_frame.append(frame_error)
        # Update last detection count

        last_detection_count = current_frame_detection_count
        
        # Add text overlays
        add_text_overlay(
            annotated_frame,
            f"Detected: {current_frame_detection_count}",
            (5, 20)
        )


        
        
        # Add ground truth count if available
        if frame_index < len(gt_coordinates):
            gt_count = len(gt_coordinates[frame_index])
            add_text_overlay(
                annotated_frame,
                f"Ground Truth: {gt_count}",
                (5, 40),
                color=(0, 255, 0)  # Green color for ground truth
            )
        
        add_text_overlay(
            annotated_frame,
            f"Total: {total_detections}",
            (5, 60),
            color=(0, 0, 255)  # Red color for total
        )
        
        # Debug output (optional - can be removed for production)
        if frame_index < len(gt_coordinates):
            gt_count = len(gt_coordinates[frame_index])
            print(f"Frame {frame_index}: Detected={current_frame_detection_count}, "
                  f"GT={gt_count}, Total={total_detections} (All detections)")
        else:
            print(f"Frame {frame_index}: Current={current_frame_detection_count}, "
                  f"Total={total_detections} (All detections)")
        
        # Display frame
        cv2.imshow("YOLOv8 Detection", annotated_frame)
        
        # Check for quit command
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Stopping detection...")
            break


        
    
    # Cleanup
    cv2.destroyAllWindows()

    print(f"Detection completed. Total detections: {total_detections}")
    
    # Calculate final metrics with zero division protection
    if len(gt_coordinates) > 0:
        avg_recall = recall_sum / valid_frames if valid_frames > 0 else 0
        avg_error = error_sum / len(error_per_frame) if len(error_per_frame) > 0 else 0
        
        # Calcular precision y F1-score correctamente usando métricas reales
        precision = true_positives_sum / (true_positives_sum + false_positives_sum) if (true_positives_sum + false_positives_sum) > 0 else 0
        recall = true_positives_sum / (true_positives_sum + false_negatives_sum) if (true_positives_sum + false_negatives_sum) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Estadísticas detalladas del error
        if error_per_frame:
            max_error = max(error_per_frame)
            min_error = min(error_per_frame)
            std_error = np.std(error_per_frame)
            frames_with_high_error = sum(1 for e in error_per_frame if e > 5)
            frames_with_very_high_error = sum(1 for e in error_per_frame if e > 10)
            
            print(f"=== MÉTRICAS REALES (TODAS LAS DETECCIONES) ===")
            print(f"Average Recall (per frame): {avg_recall:.4f}")
            print(f"Overall Precision: {precision:.4f}")
            print(f"Overall Recall: {recall:.4f}")
            print(f"F1-Score: {f1_score:.4f}")
            print(f"Average Error: {avg_error:.4f}")
            print(f"Error Statistics:")
            print(f"  - Max Error per frame: {max_error}")
            print(f"  - Min Error per frame: {min_error}")
            print(f"  - Error Standard Deviation: {std_error:.4f}")
            print(f"  - Frames with error > 5: {frames_with_high_error}/{len(error_per_frame)} ({frames_with_high_error/len(error_per_frame)*100:.1f}%)")
            print(f"  - Frames with error > 10: {frames_with_very_high_error}/{len(error_per_frame)} ({frames_with_very_high_error/len(error_per_frame)*100:.1f}%)")
            print(f"Valid frames for recall: {valid_frames}/{len(gt_coordinates)}")
            print(f"Total detections across all frames: {total_detections}")
            print(f"True Positives: {true_positives_sum}")
            print(f"False Positives: {false_positives_sum}")
            print(f"False Negatives: {false_negatives_sum}")
        else:
            print("No error data available")
    else:
        print("No ground truth data available for metrics calculation")


if __name__ == "__main__":
    # Example usage - modify these paths as needed
    SOURCE_VIDEO = "path/to/your/frames"
    ZONE_CONFIG = "path/to/zone/config.json"
    MODEL_ID = "your-model-id"
    
    try:
        run_model(SOURCE_VIDEO, ZONE_CONFIG, MODEL_ID)
    except Exception as e:
        print(f"Error running model: {e}")