from datetime import datetime, timedelta
from airflow.decorators import dag
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

@dag(
    dag_id="my_first_dag",
    default_args=default_args,
    description="My first DAG",
    start_date=datetime(2023, 1, 1, 2),
    schedule_interval='@daily'
) 
def my_first_dag():
    task1 = BashOperator(
        task_id='first_task',
        bash_command="echo Hello World!"
    )
my_first_dag = my_first_dag()