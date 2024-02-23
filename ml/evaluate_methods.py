from typing import List, Dict, Tuple
from scipy.optimize import linear_sum_assignment
import numpy as np
from coco.coco_models import AnnotationBox,Annotation, AnnotationPrediction

def calculate_iou(boxA: AnnotationBox, boxB: AnnotationBox) -> float:
    # Calculate the Intersection over Union (IoU) of two bounding boxes
    xA = max(boxA.x_min, boxB.x_min)
    yA = max(boxA.y_min, boxB.y_min)
    xB = min(boxA.x_min + boxA.width, boxB.x_min + boxB.width)
    yB = min(boxA.y_min + boxA.height, boxB.y_min + boxB.height)

    # Compute the area of intersection
    interArea = max(0, xB - xA) * max(0, yB - yA)

    # Compute the area of both bounding boxes
    boxAArea = boxA.width * boxA.height
    boxBArea = boxB.width * boxB.height

    # Compute the IoU
    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou
def match_predictions_to_ground_truth(ground_truths: List[Annotation], predictions: List[AnnotationPrediction]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    cost_matrix = np.zeros((len(ground_truths), len(predictions)))

    for i, gt in enumerate(ground_truths):
        for j, pred in enumerate(predictions):
            cost_matrix[i, j] = -calculate_iou(gt.bbox, pred.bbox)

    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    return row_ind, col_ind, -cost_matrix[row_ind, col_ind]
def calculate_confusion_matrix(ground_truths: List[Annotation], predictions: List[AnnotationPrediction], iou_threshold: float = 0.5):
    tp, fp, fn = 0, 0, len(ground_truths)
    matched_rows, matched_cols, ious = match_predictions_to_ground_truth(ground_truths, predictions)

    for iou in ious:
        if iou >= iou_threshold:
            tp += 1
            fn -= 1
        else:
            fp += 1

    # Assuming all unmatched predictions are false positives
    fp += (len(predictions) - len(matched_cols))

    return {"TP": tp, "FP": fp, "FN": fn}

def calculate_class_wise_iou(ground_truths: List[Annotation], predictions: List[AnnotationPrediction], class_id: int) -> np.ndarray:
    # Filter ground truths and predictions by class_id
    gt_filtered = [gt for gt in ground_truths if gt.category_id == class_id]
    pred_filtered = [pred for pred in predictions if pred.category_id == class_id]
    
    # Initialize cost matrix
    cost_matrix = np.zeros((len(gt_filtered), len(pred_filtered)))
    
    for i, gt in enumerate(gt_filtered):
        for j, pred in enumerate(pred_filtered):
            cost_matrix[i, j] = -calculate_iou(gt.bbox, pred.bbox)  # Assuming calculate_iou is defined as before
    
    return cost_matrix, gt_filtered, pred_filtered

def match_and_calculate_for_class(ground_truths: List[Annotation], predictions: List[AnnotationPrediction], class_id: int, iou_threshold: float = 0.5) -> Dict[str, int]:
    cost_matrix, gt_filtered, pred_filtered = calculate_class_wise_iou(ground_truths, predictions, class_id)
    
    if not cost_matrix.size:
        return {"TP": 0, "FP": 0, "FN": len(gt_filtered)}
    
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    matched_ious = -cost_matrix[row_ind, col_ind]
    
    tp = sum(iou >= iou_threshold for iou in matched_ious)
    fp = len(pred_filtered) - tp
    fn = len(gt_filtered) - tp
    
    return {"TP": tp, "FP": fp, "FN": fn}

def calculate_multi_class_confusion_matrix(ground_truths: List[Annotation], predictions: List[AnnotationPrediction], class_ids: List[int], iou_threshold: float = 0.5) -> Dict[int, Dict[str, int]]:
    results = {}
    for class_id in class_ids:
        results[class_id] = match_and_calculate_for_class(ground_truths, predictions, class_id, iou_threshold)
    return results