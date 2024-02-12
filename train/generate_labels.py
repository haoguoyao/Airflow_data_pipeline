from typing import List
from coco.coco_models import Image

def generate_yolo_labels(image: Image) -> List[str]:
    """
    Generate YOLO formatted labels for each annotation in an image.
    
    Args:
    - image: An instance of the Image model with annotations.
    
    Returns:
    - A list of strings, each representing a YOLO formatted label for an annotation.
    """
    # Example usage
    # Assuming `image_with_annotations` is an instance of Image populated with annotations
    #yolo_labels = generate_yolo_labels(image_with_annotations)
    
    yolo_labels = []
    for annotation in image.annotations:
        # Convert COCO format to YOLO format
        # COCO format: [x_min, y_min, width, height]
        x_min, y_min, width, height = annotation.bbox.x_min, annotation.bbox.y_min, annotation.bbox.width, annotation.bbox.height
        
        # Calculate the center of the box
        center_x = x_min + width / 2
        center_y = y_min + height / 2
        
        # Normalize the coordinates and dimensions
        norm_center_x = center_x / image.width
        norm_center_y = center_y / image.height
        norm_width = width / image.width
        norm_height = height / image.height
        
        # YOLO format: [class_id center_x center_y width height]
        yolo_label = f"{annotation.category_id} {norm_center_x} {norm_center_y} {norm_width} {norm_height}"
        yolo_labels.append(yolo_label)
    
    return yolo_labels

