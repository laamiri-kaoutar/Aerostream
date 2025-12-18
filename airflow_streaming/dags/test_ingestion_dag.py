from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import requests
import random

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(seconds=30),
}

def run_sentiment_ingestion():
    # 1. Simulate fetching micro-batch tweets (You can link this to HF later)
    airlines = ["United", "Delta", "American", "Southwest", "US Airways"]
    sample_tweets = [
        "The flight was delayed for 3 hours, but the staff was very helpful.",
        "Worst experience ever. Lost my luggage and no one cares.",
        "Smooth flight, great snacks, and we landed 20 minutes early!",
        "I love the extra legroom on this aircraft. Great job!",
        "The cabin was freezing and the entertainment system didn't work."
    ]
    
    # 2. Call your FastAPI Model API
    # Note: We use the container name 'model_api' defined in your docker-compose
    api_url = "http://model_api:8000/predict"
    
    # We send the list of tweets to your /predict endpoint
    try:
        response = requests.post(api_url, json={"texts": sample_tweets})
        response.raise_for_status()
        predictions = response.json() # This returns [{'sentiment': '...', 'confidence': ...}, ...]
        
        # 3. Save to Postgres
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        for i, pred in enumerate(predictions):
            airline = random.choice(airlines)
            insert_query = """
                INSERT INTO sentiment_results (airline, original_text, sentiment, confidence)
                VALUES (%s, %s, %s, %s)
            """
            pg_hook.run(insert_query, parameters=(
                airline, 
                sample_tweets[i], 
                pred['sentiment'], 
                pred['confidence']
            ))
        print(f"Successfully processed {len(predictions)} tweets.")
        
    except Exception as e:
        print(f"Pipeline failed: {e}")
        raise

with DAG(
    'aerostream_sentiment_pipeline',
    default_args=default_args,
    schedule_interval='* * * * *', # This tells Airflow to run every minute
    catchup=False
) as dag:

    ingest_task = PythonOperator(
        task_id='ingest_and_predict_tweets',
        python_callable=run_sentiment_ingestion,
    )