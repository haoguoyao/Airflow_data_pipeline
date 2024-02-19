from datetime import datetime, timedelta
from airflow import DAG


# Airflow 2.0 and later
from airflow.operators.python import PythonOperator

from ml.retrieve_images import get_random_images

# Define the default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'my_dag',
    default_args=default_args,
    description='A simple Airflow DAG',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False
)

# Define the PythonOperator
task = PythonOperator(
    task_id='get_random_imgaes',
    python_callable=get_random_images,
    dag=dag
)
