CREATE TABLE IF NOT EXISTS sentiment_results (
    id SERIAL PRIMARY KEY,
    airline VARCHAR(100),
    original_text TEXT,
    sentiment VARCHAR(20),
    confidence FLOAT,
    negative_reason TEXT,
    external_created_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE VIEW airline_sentiment_kpis AS
SELECT 
    airline,
    COUNT(*) AS total_tweets,
    SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) AS positive_tweets,
    SUM(CASE WHEN sentiment = 'neutral' THEN 1 ELSE 0 END) AS neutral_tweets
    SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) AS negative_tweets,
    ROUND(CAST(SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) AS NUMERIC) / NULLIF(COUNT(*), 0) * 100, 2) AS satisfaction_score
FROM sentiment_results
GROUP BY airline;

CREATE OR REPLACE VIEW global_sentiment_stats AS
SELECT 
    COUNT(*) AS total_tweets,
    COUNT(DISTINCT airline) AS total_airlines,
    ROUND(CAST(SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) AS NUMERIC) / NULLIF(COUNT(*), 0) * 100, 2) AS pct_negative
FROM sentiment_results;

CREATE OR REPLACE VIEW negative_reason_analysis AS
SELECT 
    airline,
    negative_reason,
    COUNT(*) AS reason_count
FROM sentiment_results
WHERE sentiment = 'negative' 
  AND negative_reason IS NOT NULL
GROUP BY airline, negative_reason
ORDER BY airline, reason_count DESC;