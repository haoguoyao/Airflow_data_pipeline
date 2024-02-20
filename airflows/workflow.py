from datetime import datetime, timedelta
from airflow import DAG


# Airflow 2.0 and later
from airflow.operators.python import PythonOperator
from ml.retrieve_images import get_random_images,download_images

# Define the default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}
def get_random_images_task(numb_images, **kwargs):
    return get_random_images(numb_images)
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
    task2_result = kwargs['ti'].xcom_pull(task_ids='get_random_images_task_in_get_and_dowload_images_dag')
    print("Received from task2:", task2_result)
    download_images(task2_result,'ml_model/downloaded_images_dag/')

download_random_images_task_in_get_and_dowload_images_dag = PythonOperator(
    task_id='download_random_images_task_in_get_and_dowload_images_dag',
    python_callable=download_random_images_task,
    dag=get_and_dowload_images_dag
)
get_random_images_task_in_get_and_dowload_images_dag>>download_random_images_task_in_get_and_dowload_images_dag