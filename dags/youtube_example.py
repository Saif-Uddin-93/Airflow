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


def greet(age, ti):
    first_name = ti.xcom_pull(task_ids='get_name', key='first_name')
    last_name = ti.xcom_pull(task_ids='get_name', key='last_name')
    print(f"Hello, {first_name} {last_name}! You are {age}.")

def get_name(ti):
    ti.xcom_push(key='first_name', value="Saif")
    ti.xcom_push(key='last_name', value="Uddin")

@dag(
    dag_id="my_second_dag",
    default_args=default_args,
    description="My second DAG",
    start_date=datetime(2023, 1, 1, 2),
    schedule_interval='@daily'
) 
def my_second_dag():
    task1 = PythonOperator(
        task_id='greet_v2',
        python_callable=greet,
        op_kwargs={'age': 30}
        #python_callable=lambda: print("Hello World!")
    )
my_second_dag = my_second_dag()
