from datetime import datetime, timedelta
from airflow.decorators import task, dag
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# with DAG(
#     dag_id="my_first_dag",
#     default_args=default_args,
#     description="My first DAG",
#     start_date=datetime(2023, 1, 1, 2),
#     schedule_interval='@daily'
# ) as dag:
#     task1 = BashOperator(
#         task_id='first_task',
#         bash_command="echo Hello World!"
#     )

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


def greet():
    print("Hello, Airflow!")


@dag(
    dag_id="my_second_dag",
    default_args=default_args,
    description="My second DAG",
    start_date=datetime(2023, 1, 1, 2),
    schedule_interval='@daily'
) 
def my_second_dag():
    task1 = PythonOperator(
        task_id='greet',
        python_callable=greet,
        #python_callable=lambda: print("Hello World!")
    )
my_second_dag = my_second_dag()
