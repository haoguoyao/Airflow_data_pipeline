from typing import List, Dict, Tuple
from scipy.optimize import linear_sum_assignment
import numpy as np
from coco.coco_models import AnnotationBox,Annotation, AnnotationPrediction
from db.db_operations import query_images_by_filenames,get_random_objects_from_db
from db.db_models import Image_predictionDB
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

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

def find_correct_predictions(ground_truths: List[Annotation], predictions: List[AnnotationPrediction]) -> List[Annotation]:
    correct_predictions = []
    
    for gt in ground_truths:
        for pred in predictions:

            if gt.category_id == pred.category_id:

                iou = calculate_iou(gt.bbox, pred.bbox)
                if iou > 0.5:
                    
                    correct_predictions.append((gt,pred))
    
    return correct_predictions

def evaluate_width_regression(evaluate_size: int = 200):
    image_predictions = get_random_objects_from_db(Image_predictionDB, evaluate_size)
    image_names = []
 
    for image in image_predictions:
        image_names.append(image.id)
    images_truth = query_images_by_filenames(image_names)
    image_predictions.sort(key=lambda image_prediction: image_prediction.id)
    images_truth.sort(key=lambda image: image.file_name)
    truth_width = []
    predicted_width = []
    for i in range(len(image_predictions)):

        correct_predictions = find_correct_predictions(images_truth[i].annotations, image_predictions[i].annotations_prediction)
        for j in range(len(correct_predictions)):
            truth_width.append(correct_predictions[j][0].bbox.width)
            predicted_width.append(correct_predictions[j][1].bbox.width)
    plt.figure(figsize=(10, 10))
    plt.scatter(truth_width, predicted_width, alpha=0.5)
    plt.title('Scatter plot between width ground truth and predicted')
    plt.xlabel('truth_width')
    plt.ylabel('predicted_width')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('ml_model/statistics_plots/scatter_validation_width.png')
    plt.close()

def evaluate_classification(evaluate_size: int = 200):
    image_predictions = get_random_objects_from_db(Image_predictionDB, evaluate_size)
    image_names = []
 
    for image in image_predictions:
        image_names.append(image.id)
    images_truth = query_images_by_filenames(image_names)
    image_predictions.sort(key=lambda image_prediction: image_prediction.id)
    images_truth.sort(key=lambda image: image.file_name)
    tp = 0
    fp = 0
    fn = 0
    for i in range(len(image_predictions)):
        confusion_matrix = calculate_confusion_matrix(images_truth[i].annotations, image_predictions[i].annotations_prediction)
        tp += confusion_matrix['TP']
        fp += confusion_matrix['FP']
        fn += confusion_matrix['FN']
    precision = tp/(tp+fp)
    recall = tp/(tp+fn)
    f1_score = 2*precision*recall/(precision+recall)
    print("Precision:",precision)
    print("Recall:",recall)
    print("F1 Score:",f1_score)

if __name__ == "__main__":
    evaluate_width_regression()
    evaluate_classification()

