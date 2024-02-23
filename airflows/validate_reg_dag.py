from datetime import datetime, timedelta
from airflow import DAG
from s3.s3_access import empty_s3_predictions

# Airflow 2.0 and later
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflows.workflow import default_args

validate_reg_dag = DAG(
    'validate_reg_dag',
    default_args=default_args,
    description='generate a scatter plot for predicted bbox width and ground truth bbox width',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False
)

# Define the PythonOperator
validate_reg_task = BashOperator(
    task_id='validate_reg_task',
    bash_command='cd /Users/hao/Desktop/github/Airflow_data_pipeline && python -m ml.evaluate_methods',
    dag=validate_reg_dag
)
