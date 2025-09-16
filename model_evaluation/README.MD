# Model Evaluation CLI

This CLI application provides a comprehensive tool for evaluating YOLOv8 models on the Mall Dataset using distance-based matching techniques.

## Overview

The Mall Dataset evaluation system implements a sophisticated approach to person detection evaluation, using distance-based matching between detection centers and ground truth head coordinates instead of traditional IoU-based methods.

## Features

- **Distance-based Matching**: Uses euclidean distance between detection centers and ground truth points
- **Comprehensive Metrics**: Calculates Precision, Recall, F1-Score, and Average Error
- **Flexible Configuration**: Supports various hyperparameters and model configurations
- **Interactive Mode**: Step-by-step configuration with validation
- **Config Management**: Save and load evaluation configurations
- **Verbose Output**: Detailed logging and progress tracking

## Installation

### Prerequisites

```bash
# Install required packages
pip install click python-dotenv supervision inference opencv-python numpy scipy matplotlib
```

### Environment Setup

Create a `.env` file in the project root:

```env
ROBOFLOW_API_KEY=your_roboflow_api_key_here
```

## Usage

### Basic Usage

```bash
# Run evaluation with default parameters
python cli.py run

# Run with specific parameters
python cli.py run --source mall_dataset/frames --model-id yolov8s-640 --iou-threshold 0.5 --confidence-threshold 0.5 --class-ids 0
```

### Interactive Mode

```bash
# Launch interactive configuration
python cli.py interactive
```

### Configuration Management

```bash
# Generate template configuration
python cli.py generate-template

# Run from existing configuration
python cli.py run-from-config config.json
```

## Command Options

### `run` Command

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--source` | Path to frames directory | `mall_dataset/frames` | `--source data/frames` |
| `--model-id` | Roboflow model ID | `yolov8s-640` | `--model-id yolov8m-640` |
| `--iou-threshold` | IoU threshold for NMS | `0.5` | `--iou-threshold 0.3` |
| `--confidence-threshold` | Confidence threshold | `0.5` | `--confidence-threshold 0.7` |
| `--class-ids` | Class IDs to detect | `0` | `--class-ids 0,1,2` |
| `--verbose` | Enable verbose output | `False` | `--verbose` |

### `interactive` Command

Launches an interactive mode that guides you through configuration:

1. **Source Path**: Directory containing frames
2. **Model ID**: Roboflow model identifier
3. **IoU Threshold**: Non-Maximum Suppression threshold
4. **Confidence Threshold**: Detection confidence threshold
5. **Class IDs**: Comma-separated list of class IDs to detect

## How Evaluation Works

### 1. Data Loading

The system loads:
- **Frames**: Images from the specified directory
- **Ground Truth**: Person head coordinates from `mall_dataset/mall_gt.mat`
- **Model**: YOLOv8 model from Roboflow

### 2. Detection Process

For each frame:
1. **Inference**: Run YOLOv8 model on the frame
2. **Filtering**: Apply confidence and IoU thresholds
3. **Zone Processing**: Process all detections (no zone restriction)
4. **Counting**: Count detections for specified classes

### 3. Distance-Based Matching

The key innovation is the distance-based matching algorithm:

```python
# Calculate distance between detection center and ground truth points
detection_center = (bbox_x1 + bbox_x2) / 2, (bbox_y1 + bbox_y2) / 2
distance = sqrt((det_center_x - gt_x)² + (det_center_y - gt_y)²)

# Match if distance <= threshold (default: 100 pixels)
if distance <= distance_threshold:
    # This is a True Positive
```

### 4. Metrics Calculation

#### Precision
```
Precision = True Positives / (True Positives + False Positives)
```

#### Recall
```
Recall = True Positives / (True Positives + False Negatives)
```

#### F1-Score
```
F1-Score = 2 × (Precision × Recall) / (Precision + Recall)
```

#### Average Error
```
Average Error = (1/N_processed) × Σ|Detected_i - Ground_Truth_i|
```
Where N_processed is the number of processed frames (101), not total frames (2000).

## Dataset Structure

### Mall Dataset
- **Total Frames**: 2000
- **Resolution**: 640×480 pixels
- **Ground Truth**: Head coordinates (x, y) for each person
- **Format**: MATLAB .mat file with hierarchical structure

### Ground Truth Format
```python
# Access ground truth for frame i
gt_coordinates = mall_gt['frame'][0][i][0][0][0]
# Each person is represented as [x, y] coordinates
```

## Example Results

### Typical Output
```
=== MÉTRICAS REALES (TODAS LAS DETECCIONES) ===
Average Recall (per frame): 0.4971
Overall Precision: 0.9321
Overall Recall: 0.4835
F1-Score: 0.6367
Average Error: 13.7723
Error Statistics:
  - Max Error per frame: 31
  - Min Error per frame: 4
  - Error Standard Deviation: 6.1320
  - Frames with error > 5: 98.0% (99/101)
  - Frames with error > 10: 60.4% (61/101)
Valid frames for recall: 101/2000
Total detections across all frames: 1248
True Positives: 1276
False Positives: 93
False Negatives: 1363
```

### Result Interpretation

- **High Precision (93.21%)**: Model rarely detects false positives
- **Moderate Recall (48.35%)**: Model detects about half of real people
- **High Error (13.77)**: Significant counting challenges
- **High Variability**: Performance varies significantly across frames

## Configuration Files

### Example Configuration (`example_config.json`)
```json
{
  "source": "mall_dataset/frames",
  "model_id": "yolov8s-640",
  "iou_threshold": 0.5,
  "confidence_threshold": 0.5,
  "class_ids": [0],
  "distance_threshold": 100
}
```

## Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   Error: ROBOFLOW_API_KEY environment variable is not set
   ```
   **Solution**: Set your Roboflow API key in the `.env` file

2. **Model Loading Error**
   ```
   Error: Could not load model
   ```
   **Solution**: Check model ID and internet connection

3. **Ground Truth Loading Error**
   ```
   Warning: Could not load ground truth coordinates
   ```
   **Solution**: Ensure `mall_dataset/mall_gt.mat` exists

### Performance Tips

1. **Adjust Distance Threshold**: Lower values (50-75) for stricter matching, higher values (100-150) for more lenient matching
2. **Optimize Confidence Threshold**: Higher values reduce false positives but may decrease recall
3. **Class Selection**: Use `--class-ids 0` for person detection only

## Advanced Usage

### Custom Distance Threshold
Modify the distance threshold in the code:
```python
# In yolov8.py, line ~420
tp, fp, fn = match_detections_to_ground_truth(
    detections_in_zone, 
    gt_coords, 
    distance_threshold=75  # Custom threshold
)
```

### Batch Processing
```bash
# Process multiple configurations
for config in configs/*.json; do
    python cli.py run-from-config "$config"
done
```

## Contributing

When modifying the evaluation system:

1. **Maintain Distance-Based Matching**: Keep the core distance-based approach
2. **Update Documentation**: Update this README when adding new features
3. **Test Thoroughly**: Validate changes with the Mall Dataset
4. **Preserve Metrics**: Ensure all metrics remain mathematically correct

## References

- [Mall Dataset Paper](https://www.ee.cuhk.edu.hk/~xgwang/papers/zhangLWYtog09.pdf)
- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [Supervision Library](https://roboflow.github.io/supervision/)
- [Roboflow Inference](https://inference.roboflow.com/)

## License

This evaluation system is part of the time analysis project and follows the same licensing terms.
