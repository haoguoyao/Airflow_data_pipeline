import os
import numpy as np
import onnxruntime as ort
import cv2
from scipy import special
import colorsys
import random
import numpy as np
from ml.retrieve_images import get_images_local_folder
from ml.image_preprocessing import preprocess_image
from db.db_models import store_one_image_prediction
from s3.s3_access import upload_to_s3
import ml_model.model_settings as model_settings
from s3.s3_settings import bucket_name,S3_withbox_FOLDER
from ml.image_postprocessing import postprocess_bbbox, postprocess_boxes, draw_bbox,generate_imagename_with_uuid,crop_and_save,nms



def onnx_inference_local_folder():

    model_path = 'ml_model/yolov4.onnx'
    sess = ort.InferenceSession(model_path)
    outputs = sess.get_outputs()
    output_names = list(map(lambda output: output.name, outputs))
    input_name = sess.get_inputs()[0].name

    for image_url in get_images_local_folder(folder_path="ml_model/downloaded_images"):

        original_image_name = os.path.basename(image_url)
        original_image = cv2.imread(image_url)
        original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        original_image_size = original_image.shape[:2]

        image_data = preprocess_image(np.copy(original_image), [model_settings.input_size, model_settings.input_size])
        # image_data = image_data[np.newaxis, ...].astype(np.float32)
        detections = sess.run(output_names, {input_name: image_data})
        print("Output shape:", list(map(lambda detection: detection.shape, detections)))

        pred_bbox = postprocess_bbbox(detections, model_settings.ANCHORS, model_settings.STRIDES, model_settings.XYSCALE)
        bboxes = postprocess_boxes(pred_bbox, original_image_size,model_settings.input_size, 0.25)
        bboxes = nms(bboxes, 0.213, method='nms')

        original_image = cv2.cvtColor(original_image, cv2.COLOR_RGB2BGR)

        for bbox in bboxes:
            coor = np.array(bbox[:4], dtype=np.int32)
            crop_name = generate_imagename_with_uuid()
            crop_and_save(original_image, coor,crop_name)

        image_with_box = draw_bbox(original_image, bboxes)

        store_one_image_prediction({'file_name':os.path.basename(image_url),'prediction':bboxes})
        image_local_path = 'ml_model/yolov4_output/'+os.path.basename(image_url)
        cv2.imwrite(image_local_path, image_with_box)
        upload_to_s3(image_local_path,bucket_name,S3_withbox_FOLDER+original_image_name)

        break

if __name__ == "__main__":
    onnx_inference_local_folder()
