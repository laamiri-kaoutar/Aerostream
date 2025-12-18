from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List  # <--- Added this
import joblib
import re
from sentence_transformers import SentenceTransformer

app = FastAPI()

class TweetBatchRequest(BaseModel):
    texts: List[str]

embedding_model = None
sentiment_model = None

@app.on_event("startup")
def load_models():
    global embedding_model, sentiment_model
    
    embedding_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    sentiment_model = joblib.load("/app/models/sentiment_model.pkl")
    
    print("Our models loaded successfully!")

def clean_tweet(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

@app.post("/predict")
def predict(request: TweetBatchRequest):
    cleaned_texts = [clean_tweet(t) for t in request.texts]
    
    vectors = embedding_model.encode(cleaned_texts)
    
    predictions = sentiment_model.predict(vectors)
    all_probs = sentiment_model.predict_proba(vectors)
    
    results = []
    for i, original_text in enumerate(request.texts):
        confidence = float(max(all_probs[i]))
        
        results.append({
            "original_text": original_text,
            "sentiment": predictions[i],
            "confidence": confidence
        })

    return results