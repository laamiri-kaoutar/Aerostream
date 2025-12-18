from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime

with DAG(
    'test_postgres_connection',
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:

    # This task will try to insert a dummy row into your new table
    test_insert = PostgresOperator(
        task_id='insert_test_row',
        postgres_conn_id='postgres_default',
        sql="""
            INSERT INTO sentiment_results (airline, original_text, sentiment, confidence)
            VALUES ('TestAir', 'This is a test tweet', 'neutral', 0.99);
        """
    )