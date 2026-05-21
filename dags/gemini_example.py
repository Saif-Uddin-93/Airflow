import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Airflow specific imports
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

# ---------------------------------------------------------
# 1. EXTRACT: Scrape website and save to raw CSV
# ---------------------------------------------------------
def extract_data():
    url = 'https://books.toscrape.com/'
    print(f"Fetching data from {url}...")
    
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    books_data = []
    
    articles = soup.find_all('article', class_='product_pod')
    
    for article in articles:
        books_data.append({
            'Title': article.h3.a['title'],
            'Price': article.find('p', class_='price_color').text,
            'Availability': article.find('p', class_='instock availability').text.strip()
        })
        
    df = pd.DataFrame(books_data)
    
    # Save the raw data
    raw_output_path = '/tmp/raw_scraped_books.csv'
    df.to_csv(raw_output_path, index=False, encoding='utf-8')
    
    print(f"Successfully scraped {len(books_data)} books.")
    
    # Return the file path so XCom can pass it to the Transform task
    return raw_output_path

# ---------------------------------------------------------
# 2. TRANSFORM: Clean the data and save to a new CSV
# ---------------------------------------------------------
def transform_data(ti):
    # Pull the raw file path from the Extract task
    input_path = ti.xcom_pull(task_ids='extract_data')
    df = pd.read_csv(input_path)
    
    # This Regex removes everything except numbers and decimals, then converts to float.
    df['Price'] = df['Price'].str.replace(r'[^\d.]', '', regex=True).astype(float)
    
    # Clean Availability: Convert string like "In stock" to a standard Boolean
    df['Availability'] = df['Availability'].apply(lambda x: True if 'In stock' in str(x) else False)
    
    # Rename columns to fit PostgreSQL friendly schema (lowercase, no spaces)
    df.rename(columns={
        'Title': 'title', 
        'Price': 'price', 
        'Availability': 'is_in_stock'
    }, inplace=True)
    
    # Save the cleaned data
    clean_output_path = '/tmp/cleaned_books.csv'
    df.to_csv(clean_output_path, index=False, encoding='utf-8')
    
    # Return the new file path for the Load task
    return clean_output_path

# ---------------------------------------------------------
# 3. LOAD: Insert the cleaned data into PostgreSQL
# ---------------------------------------------------------
def load_data(ti):
    # Pull the cleaned file path from the Transform task
    input_path = ti.xcom_pull(task_ids='transform_data')
    df = pd.read_csv(input_path)
    
    # Connect to your database
    pg_hook = PostgresHook(postgres_conn_id='my_postgres_conn')
    
    # Create the table using the autocommit fix we established earlier
    create_table_query = """
    CREATE TABLE IF NOT EXISTS scraped_books (
        title TEXT,
        price NUMERIC,
        is_in_stock BOOLEAN,
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    pg_hook.run(create_table_query, autocommit=True)
    
    # Convert DataFrame to a list of tuples for bulk insertion
    records = list(df.to_records(index=False))
    
    # Airflow's PostgresHook has a built-in method for bulk inserting rows efficiently!
    pg_hook.insert_rows(
        table="scraped_books", 
        rows=records, 
        target_fields=['title', 'price', 'is_in_stock']
    )
    
    print(f"Successfully loaded {len(records)} rows into PostgreSQL.")

# ---------------------------------------------------------
# 4. Define the DAG Default Arguments & Instantiation
# ---------------------------------------------------------
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 5, 20),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    'books_scraper_etl_pipeline',
    default_args=default_args,
    description='Extract, Transform, and Load Books Data',
    schedule_interval='@daily',
    catchup=False,
    tags=['scraping', 'etl'],
) as dag:

    # 5. Define Tasks
    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
    )

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
    )

    load_task = PythonOperator(
        task_id='load_data',
        python_callable=load_data,
    )

    # 6. Set Task Dependencies (The Pipeline Flow)
    extract_task >> transform_task >> load_task