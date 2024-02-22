from datetime import datetime, timedelta
from airflow import DAG
from s3.s3_access import empty_s3_predictions

# Airflow 2.0 and later
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from ml.retrieve_images import download_images
from db.db_operations import get_random_objects_from_db
from db.db_models import empty_prediction_tables
from ml.test_onnx import onnx_inference_local_folder
import ml.statistics_images as statistics_images
import cv2
import os
import onnxruntime as ort
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=1),
}
onnx_inference_local_folder_dag = DAG(
    'onnx_inference_local_folder_dag',
    default_args=default_args,
    description='empty prediction tables and images, and then inference everything images in local folder using onnx model and store the result',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False
)

# Define the PythonOperator
onnx_inference_local_folder_task = BashOperator(
    task_id='onnx_inference_local_folder_task',
    bash_command='cd /Users/hao/Desktop/github/Airflow_data_pipeline && python -m ml.test_onnx',
    dag=onnx_inference_local_folder_dag
)

# onnx_inference_local_folder_task = PythonOperator(
#     task_id='onnx_inference_local_folder_task',
#     python_callable=onnx_inference_local_folder,
#     op_kwargs={},
#     dag=onnx_inference_local_folder_dag
# )
empty_prediction_tables_task = PythonOperator(
    task_id='empty_prediction_tables_task',
    python_callable=empty_prediction_tables,
    op_kwargs={},
    dag=onnx_inference_local_folder_dag
)
empty_prediction_images_task = PythonOperator(
    task_id='empty_prediction_images_task',
    python_callable=empty_s3_predictions,
    op_kwargs={},
    dag=onnx_inference_local_folder_dag
)
empty_prediction_images_task>>onnx_inference_local_folder_task
empty_prediction_tables_task>>onnx_inference_local_folder_task