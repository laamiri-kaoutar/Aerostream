from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from airflow.providers.postgres.hooks.postgres import PostgresHook
import requests
import pendulum
import json

default_args = {
    'owner': 'airflow',
    'start_date': pendulum.today('UTC').add(days=-1), 
    'retries': 1,
}

@dag(
    dag_id='aerostream_realtime_etl',
    default_args=default_args,
    schedule_interval='* * * * *',  
    catchup=False,                  
    tags=['aerostream', 'sentiment']
)
def sentiment_pipeline():

    @task()
    def fetch_tweets():
        url = "http://tweet_generator:8001/batch?batch_size=10"
        
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            tweets = response.json()
            print(f"Successfully fetched {len(tweets)} tweets.")
            return tweets
        except Exception as e:
            print(f"Error fetching tweets: {e}")
            return []

    @task()
    def predict_sentiment(raw_tweets: list):
        if not raw_tweets:
            print("No tweets to process.")
            return []

        texts = [t['text'] for t in raw_tweets]
        
        api_url = "http://aerostream_api:8000/predict"
        
        try:
            response = requests.post(api_url, json={"texts": texts}, timeout=5)
            response.raise_for_status()
            predictions = response.json()
            
            processed_data = []
            
            for original, pred in zip(raw_tweets, predictions):
                combined_record = {
                    'airline': original.get('airline', 'Unknown'),
                    'original_text': original.get('text', ''),
                    'sentiment': pred.get('sentiment'),
                    'confidence': pred.get('confidence'),
                    # Note: Source API uses 'negativereason', DB uses 'negative_reason'
                    'negative_reason': original.get('negativereason'), 
                    'external_created_at': original.get('tweet_created')
                }
                processed_data.append(combined_record)
                
            print(f"Successfully generated predictions for {len(processed_data)} tweets.")
            return processed_data

        except Exception as e:
            print(f"Error calling Model API: {e}")
            raise e

    @task()
    def load_to_postgres(processed_data: list):
        if not processed_data:
            print("No data to save.")
            return

        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        insert_query = """
            INSERT INTO sentiment_results 
            (airline, original_text, sentiment, confidence, negative_reason, external_created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        rows_to_insert = []
        for row in processed_data:
            rows_to_insert.append((
                row['airline'],
                row['original_text'],
                row['sentiment'],
                row['confidence'],
                row['negative_reason'],
                row['external_created_at']
            ))
            
        connection = pg_hook.get_conn()
        cursor = connection.cursor()
        cursor.executemany(insert_query, rows_to_insert)
        connection.commit()
        cursor.close()
        connection.close()
        
        print(f"Successfully inserted {len(rows_to_insert)} rows into Database.")

    # TaskFlow
    raw_data = fetch_tweets()
    analyzed_data = predict_sentiment(raw_data)
    load_to_postgres(analyzed_data)

# the Dag
dag_instance = sentiment_pipeline()