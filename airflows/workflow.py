from datetime import datetime, timedelta
from airflow import DAG


# Airflow 2.0 and later
from airflow.operators.python import PythonOperator
from ml.retrieve_images import download_images
from db.db_operations import get_random_objects_from_db
from db.db_models import ImageDB
import ml.test_onnx as test_onnx
import ml.statistics_images as statistics_images
# Define the default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=1),
}
def get_random_images_task(numb_images, **kwargs):
    return get_random_objects_from_db(ImageDB,numb_images)
# Define the DAG
get_random_images_dag = DAG(
    'get_random_images_dag',
    default_args=default_args,
    description='get_random_images_dag',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False
)
# Define the PythonOperator
get_random_images_task_in_get_random_images_dag = PythonOperator(
    task_id='get_random_images_task_in_get_random_images_dag',
    python_callable=get_random_images_task,
    op_kwargs={'numb_images':100},
    dag=get_random_images_dag
)


get_and_dowload_images_dag = DAG(
    'get_and_dowload_images_dag',
    default_args=default_args,
    description='get_and_dowload_images_dag, test using xcom_pull',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False
)

get_random_images_task_in_get_and_dowload_images_dag = PythonOperator(
    task_id='get_random_images_task_in_get_and_dowload_images_dag',
    python_callable=get_random_images_task,
    op_kwargs={'numb_images':100},
    dag=get_and_dowload_images_dag
)


def download_random_images_task(**kwargs):
    task_get_random_images_result = kwargs['ti'].xcom_pull(task_ids='get_random_images_task_in_get_and_dowload_images_dag')
    # print("Received from task2:", task2_result)
    download_images(task_get_random_images_result,'ml_model/downloaded_images_dag/')

download_random_images_task_in_get_and_dowload_images_dag = PythonOperator(
    task_id='download_random_images_task_in_get_and_dowload_images_dag',
    python_callable=download_random_images_task,
    dag=get_and_dowload_images_dag
)
get_random_images_task_in_get_and_dowload_images_dag>>download_random_images_task_in_get_and_dowload_images_dag





generate_sample_statistics_dag = DAG(
    'generate_sample_statistics_dag',
    default_args=default_args,
    description='inference everything images in local folder using onnx model and store the result to database and s3 bucket',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False
)
# Define the PythonOperator
generate_sample_statistics_dag_task = PythonOperator(
    task_id='generate_sample_statistics_dag_task',
    python_callable=statistics_images.plot_areas_histogram,
    op_kwargs={},
    dag=generate_sample_statistics_dag
)