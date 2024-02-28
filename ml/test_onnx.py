import os
import numpy as np
import onnxruntime as ort
import cv2
import numpy as np
from ml.retrieve_images import get_images_local_folder
from ml.image_preprocessing import preprocess_image
from db.db_models import store_one_image_prediction,store_db_objects,Annotation_predictionDB
from s3.s3_access import upload_to_s3
import ml_model.model_settings as model_settings
from db.db_models import empty_prediction_tables
from s3.s3_settings import bucket_name,S3_withbox_FOLDER
from ml.image_postprocessing import postprocess_bbbox, postprocess_boxes, draw_bbox,generate_imagename_with_uuid,crop_and_save,nms

import json
original_coco_ids = list(range(1, 91))  # Example range, replace with actual COCO category IDs
# Simulate missing IDs to mimic the COCO categories' distribution
for missing_id in [12, 26, 29,30, 45, 66, 68, 69, 71, 83]:  # Example missing IDs, adjust as needed
    original_coco_ids.remove(missing_id)

# Create a mapping from original to new IDs
id_mapping = {new_id: original_id for new_id, original_id in enumerate(original_coco_ids, start=0)}

def convert_id(original_id):
    #convert to original_id
    return id_mapping.get(original_id, None)

def onnx_inference_local_folder():

    model_path = 'ml_model/yolov4.onnx'
    sess = ort.InferenceSession(model_path)
    outputs = sess.get_outputs()
    output_names = list(map(lambda output: output.name, outputs))
    input_name = sess.get_inputs()[0].name

    for image_url in get_images_local_folder(folder_path="ml_model/downloaded_images_dag/"):

        original_image_name = os.path.basename(image_url)
        if not original_image_name.endswith((".jpg", ".jpeg", ".tiff", ".cr2", ".nef")):
            continue

        print("Processing:", original_image_name)

        original_image = cv2.imread(image_url)
        original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        original_image_size = original_image.shape[:2]

        image_data = preprocess_image(np.copy(original_image), [model_settings.input_size, model_settings.input_size])
        detections = sess.run(output_names, {input_name: image_data})
        print("Output shape:", list(map(lambda detection: detection.shape, detections)))

        pred_bbox = postprocess_bbbox(detections, model_settings.ANCHORS, model_settings.STRIDES, model_settings.XYSCALE)
        bboxes = postprocess_boxes(pred_bbox, original_image_size,model_settings.input_size, 0.25)
        bboxes = nms(bboxes, 0.213, method='nms')

        original_image = cv2.cvtColor(original_image, cv2.COLOR_RGB2BGR)
        annotations = []
        for bbox in bboxes:
            coor = np.array(bbox[:4], dtype=np.int32)
            crop_name = generate_imagename_with_uuid()
            crop_and_save(original_image, coor,crop_name)
            annotation_prediction = {}
            annotation_prediction['category_id'] = convert_id(int(bbox[5]))
            annotation_prediction['crop_name'] = crop_name
            bbox_lst = bbox[:4].tolist()
            annotation_prediction['bbox'] = json.dumps([bbox_lst[0],bbox_lst[1],bbox_lst[2]-bbox_lst[0],bbox_lst[3]-bbox_lst[1]])
            annotation_prediction['confidence'] = bbox[4]
            annotation_prediction['image_name'] = os.path.basename(image_url)
            new_annotation_prediction = Annotation_predictionDB(
                category_id=annotation_prediction['category_id'],
                crop_name=annotation_prediction['crop_name'],
                bbox=annotation_prediction['bbox'],
                confidence=annotation_prediction['confidence'],
                image_name=annotation_prediction['image_name']
            )
            annotations.append(new_annotation_prediction)
        

        image_with_box = draw_bbox(original_image, bboxes)
        store_one_image_prediction({'file_name':os.path.basename(image_url),'prediction':bboxes})
        store_db_objects(annotations)


        image_local_path = 'ml_model/yolov4_output/'+os.path.basename(image_url)
        cv2.imwrite(image_local_path, image_with_box)
        upload_to_s3(image_local_path,bucket_name,S3_withbox_FOLDER+original_image_name)


if __name__ == "__main__":

    onnx_inference_local_folder()
