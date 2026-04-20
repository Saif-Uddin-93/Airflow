from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta

# Default arguments for the DAG
default_args = {
    'owner': 'saif',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

@dag(
    dag_id='mock_postgres_etl_v1',
    default_args=default_args,
    start_date=datetime(2026, 4, 1),
    schedule_interval='@daily',
    catchup=False,
    tags=['learning', 'etl']
)
def etl_pipeline():

    @task()
    def extract_mock_data():
        """Mocking a data source (e.g., an external API or JSON file)"""
        data = [
            {"id": 101, "item": "Widget A", "price": 25.50},
            {"id": 102, "item": "Widget B", "price": 40.00},
            {"id": 103, "item": "Widget C", "price": 15.75},
        ]
        return data

    @task()
    def transform_data(raw_data):
        """Transforming data: adding a 10% tax to the price"""
        transformed = []
        for row in raw_data:
            row['total_price'] = round(row['price'] * 1.1, 2)
            transformed.append(row)
        return transformed

    @task()
    def load_to_postgres(final_data):
        """Loading the data into our airflow_db"""
        # This hook looks for a connection ID 'my_postgres_conn' in the Airflow UI
        pg_hook = PostgresHook(postgres_conn_id='my_postgres_conn')
        
        # 1. Create the table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS mock_sales (
            id INT PRIMARY KEY,
            item VARCHAR(50),
            price NUMERIC,
            total_price NUMERIC,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        pg_hook.run(create_table_query)

        # 2. Insert data (Upsert logic)
        for row in final_data:
            insert_query = """
            INSERT INTO mock_sales (id, item, price, total_price)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                total_price = EXCLUDED.total_price,
                processed_at = CURRENT_TIMESTAMP;
            """
            pg_hook.run(insert_query, parameters=(row['id'], row['item'], row['price'], row['total_price']))

    # Setting up the dependencies
    raw_data = extract_mock_data()
    clean_data = transform_data(raw_data)
    load_to_postgres(clean_data)

# Instantiate the DAG
etl_pipeline()