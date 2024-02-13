import torchvision.transforms as T
from PIL import Image
import numpy as np
from coco.coco_models import Annotation, AnnotationBox
from typing import List, Tuple

def preprocess_image(image_path, target_size: Tuple[int, int]):
    """
    Preprocess an image: resize, normalize, and convert to tensor.
    """
    # Load the image
    image = Image.open(image_path).convert("RGB")
    
    # Define transformations
    transform = T.Compose([
        T.Resize(target_size),  # Resize the image
        T.ToTensor(),  # Convert the image to a PyTorch tensor
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalize to ImageNet stats
    ])
    
    # Apply transformations
    processed_image = transform(image)
    return processed_image

def adjust_annotation_boxes(image: Image, target_size: Tuple[int, int]) -> List[Annotation]:
    """
    Adjusts the bounding boxes of annotations based on the resize target for the given image.

    Args:
    - image: An instance of Image containing original dimensions.
    - annotations: A list of Annotation instances to be adjusted.
    - target_size: A tuple (target_width, target_height) specifying the resize target dimensions.

    Returns:
    - A list of adjusted Annotation instances.
    """
    original_width, original_height = image.width, image.height
    target_width, target_height = target_size

    scale_x = target_width / original_width
    scale_y = target_height / original_height

    adjusted_annotations = []

    for annotation in image.annotations:
        # Scale the bounding box coordinates
        adjusted_bbox = AnnotationBox(
            x_min=annotation.bbox.x_min * scale_x,
            y_min=annotation.bbox.y_min * scale_y,
            width=annotation.bbox.width * scale_x,
            height=annotation.bbox.height * scale_y
        )

        # Create a new adjusted Annotation instance
        adjusted_annotation = annotation.copy(update={"bbox": adjusted_bbox})
        adjusted_annotations.append(adjusted_annotation)

    return adjusted_annotations