import torchvision.transforms as T
from PIL import Image
import numpy as np
from coco.coco_models import Annotation, AnnotationBox
from typing import List, Tuple
import cv2

def preprocess_image(image, target_size, gt_boxes=None):

    ih, iw = target_size
    h, w, _ = image.shape

    scale = min(iw/w, ih/h)
    nw, nh = int(scale * w), int(scale * h)
    image_resized = cv2.resize(image, (nw, nh))

    image_padded = np.full(shape=[ih, iw, 3], fill_value=128.0)
    dw, dh = (iw - nw) // 2, (ih-nh) // 2
    image_padded[dh:nh+dh, dw:nw+dw, :] = image_resized
    image_padded = image_padded / 255.

    if gt_boxes is None:
        return image_padded

    else:
        gt_boxes[:, [0, 2]] = gt_boxes[:, [0, 2]] * scale + dw
        gt_boxes[:, [1, 3]] = gt_boxes[:, [1, 3]] * scale + dh
        return image_padded, gt_boxes


def adjust_annotation_boxes(image: Image, target_size: Tuple[int, int]) -> List[Annotation]:

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