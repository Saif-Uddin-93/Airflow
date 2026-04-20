from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime

@dag(
    dag_id='postgres_to_postgres_etl',
    start_date=datetime(2026, 4, 1),
    schedule=None, # Manual trigger
    catchup=False,
    tags=['etl', 'multi_db']
)
def multi_db_etl():

    @task
    def extract_from_source():
        """Extracts data from mock_database"""
        src_hook = PostgresHook(postgres_conn_id='source_db_conn')
        # Returns list of tuples
        records = src_hook.get_records("SELECT order_id, customer_name, order_total FROM source_orders;")
        return records

    @task
    def transform_records(records):
        """Applies a 'VIP' status to orders over 200"""
        transformed = []
        for r_id, name, total in records:
            status = 'VIP' if float(total) > 200 else 'Standard'
            transformed.append((r_id, name, float(total), status))
        return transformed

    @task
    def load_to_destination(transformed_data):
        """Loads data into airflow_db"""
        dest_hook = PostgresHook(postgres_conn_id='my_postgres_conn')
        
        # Create target table
        dest_hook.run("""
            CREATE TABLE IF NOT EXISTS processed_orders (
                order_id INT PRIMARY KEY,
                customer_name VARCHAR(100),
                order_total NUMERIC,
                customer_tier VARCHAR(20)
            );
        """)

        # Upsert data
        for row in transformed_data:
            dest_hook.run("""
                INSERT INTO processed_orders (order_id, customer_name, order_total, customer_tier)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (order_id) DO UPDATE SET 
                    customer_tier = EXCLUDED.customer_tier,
                    order_total = EXCLUDED.order_total;
            """, parameters=row)

    # Execution Flow
    raw_data = extract_from_source()
    transformed_data = transform_records(raw_data)
    load_to_destination(transformed_data)

multi_db_etl()