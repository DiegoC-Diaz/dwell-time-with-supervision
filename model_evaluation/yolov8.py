import os
import supervision as sv
from inference import get_model
import cv2
from frame_loader import load_frames_from_folder
from scipy.io import loadmat
from utils.general import load_zones_config

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

def load_ground_truth_counts(gt_path="mall_dataset/mall_gt.mat"):
    """
    Load ground truth person counts from .mat file.
    
    Args:
        gt_path (str): Path to the ground truth .mat file
        
    Returns:
        list: List of person counts per frame
    """
    try:
        mall_gt = loadmat(gt_path)
        counts = []
        for index in range(mall_gt["frame"].size):
            persons = mall_gt['frame'][0][index][0][0][0]
            counts.append(len(persons))
        return counts
    except Exception as e:
        print(f"Warning: Could not load ground truth data: {e}")
        return []

def setup_zones(frame, zone_configuration_path):
    """
    Setup polygon zones from configuration.
    
    Args:
        frame: First frame to get resolution
        zone_configuration_path (str): Path to zone configuration
        
    Returns:
        list: List of PolygonZone objects
    """
    polygons = load_zones_config(file_path=zone_configuration_path)
    zones = [
        sv.PolygonZone(
            polygon=polygon,
            triggering_anchors=(sv.Position.CENTER,)
        )
        for polygon in polygons
    ]
    return zones

def count_persons_in_detections(detections):
    """
    Count the number of persons in detections.
    
    Args:
        detections: Supervision detections object
        
    Returns:
        int: Number of person detections
    """
    if not hasattr(detections, 'data') or 'class_name' not in detections.data:
        return 0
    
    return sum(1 for class_name in detections.data["class_name"] if class_name == "person")

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

def run_model(source_video_path: str, zone_configuration_path: str, model_id: str):
    """
    Run YOLOv8 model on video frames with zone-based detection.
    
    Args:
        source_video_path (str): Path to source video/frames
        zone_configuration_path (str): Path to zone configuration
        model_id (str): Roboflow model ID
    """
    # Validate API key
    api_key = validate_api_key()
    
    # Initialize model
    model = get_model(model_id=model_id, api_key=api_key)
    
    # Load frames
    frames = load_frames_from_folder(source_video_path)
    if not frames:
        raise ValueError(f"No frames found in {source_video_path}")
    
    # Setup zones
    zones = setup_zones(frames[0], zone_configuration_path)
    if not zones:
        raise ValueError("No zones configured")
    
    # Load ground truth data (optional)
    gt_counts = load_ground_truth_counts()
    
    # Initialize tracking variables
    last_detection_count = 0
    total_detections = 0
    
    # Process frames
    for frame_index, frame in enumerate(frames):
        # Run inference
        results = model.infer(
            frame,
            confidence=CONFIDENCE_THRESHOLD,
            iou_threshold=IOU_THRESHOLD
        )[0]
        
        # Convert to supervision detections
        detections = sv.Detections.from_inference(results)
        
        # Create annotated frame
        annotated_frame = frame.copy()
        
        # Draw polygon zone (using first zone only)
        primary_zone = zones[0]
        annotated_frame = sv.draw_polygon(
            scene=annotated_frame,
            polygon=primary_zone.polygon,
            thickness=1
            color=(0, 255, 0)
        )
        
        # Filter detections within zone
        detections_in_zone = detections[primary_zone.trigger(detections)]
        
        # Annotate detections
        annotated_frame = BOUNDING_BOX_ANNOTATOR.annotate(
            scene=annotated_frame,
            detections=detections_in_zone
        )
        annotated_frame = LABEL_ANNOTATOR.annotate(
            scene=annotated_frame,
            detections=detections_in_zone
        )
        
        # Count persons in current frame
        current_frame_detection_count = count_persons_in_detections(detections_in_zone)
        
        # Update total detections (only when count increases)
        if current_frame_detection_count > last_detection_count:
            difference = current_frame_detection_count - last_detection_count
            total_detections += difference
        
        # Update last detection count
        last_detection_count = current_frame_detection_count
        
        # Add text overlays
        add_text_overlay(
            annotated_frame,
            f"Detected: {current_frame_detection_count}",
            (5, 20)
        )


        
        
        # Add ground truth count if available
        if frame_index < len(gt_counts):
            add_text_overlay(
                annotated_frame,
                f"Ground Truth: {gt_counts[frame_index]}",
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
        print(f"Frame {frame_index}: Current={current_frame_detection_count}, "
              f"Total={total_detections}")
        
        # Display frame
        cv2.imshow("YOLOv8 Detection", annotated_frame)
        
        # Check for quit command
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Stopping detection...")
            break


        
    
    # Cleanup
    cv2.destroyAllWindows()
    print(f"Detection completed. Total detections: {total_detections}")

if __name__ == "__main__":
    # Example usage - modify these paths as needed
    SOURCE_VIDEO = "path/to/your/frames"
    ZONE_CONFIG = "path/to/zone/config.json"
    MODEL_ID = "your-model-id"
    
    try:
        run_model(SOURCE_VIDEO, ZONE_CONFIG, MODEL_ID)
    except Exception as e:
        print(f"Error running model: {e}")