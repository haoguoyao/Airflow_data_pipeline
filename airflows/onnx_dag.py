from datetime import datetime, timedelta
from airflow import DAG
from s3.s3_access import empty_s3_predictions

# Airflow 2.0 and later
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from db.db_models import empty_prediction_tables
from airflows.workflow import default_args
from airflow.operators.trigger_dagrun import TriggerDagRunOperator


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
trigger_validate_reg_dag = TriggerDagRunOperator(
    task_id='trigger_validate_reg_dag',
    trigger_dag_id='validate_reg_dag',  # Specify the ID of the DAG you want to trigger
    dag=onnx_inference_local_folder_dag,
)
trigger_generate_sample_statistics_dag = TriggerDagRunOperator(
    task_id='trigger_generate_sample_statistics_dag',
    trigger_dag_id='generate_sample_statistics_dag',  # Specify the ID of the DAG you want to trigger
    dag=onnx_inference_local_folder_dag,
)
# Define tasks and dependencies in dag1 as needed
# End dag1 with the TriggerDagRunOperator
trigger_validate_reg_dag
trigger_generate_sample_statistics_dag
empty_prediction_images_task>>onnx_inference_local_folder_task
empty_prediction_tables_task>>onnx_inference_local_folder_task