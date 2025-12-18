
#  AeroStream: Real-time Airline Sentiment Analysis

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![Airflow](https://img.shields.io/badge/Apache%20Airflow-Orchestration-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)

**AeroStream** is an intelligent, end-to-end MLOps system designed to classify customer reviews for airlines in real-time. By leveraging **Natural Language Processing (NLP)** and **Data Engineering** best practices, the system analyzes customer sentiment to provide actionable insights via an interactive dashboard.

---

##  Project Context & Objectives
AeroStream aims to automate the analysis of customer feedback to monitor satisfaction levels.
- **Goal:** Develop a real-time classification system for airline reviews.
- **Input:** Customer tweets and textual reviews.
- **Output:** Sentiment analysis, satisfaction KPIs, and negative feedback root cause analysis.

---

##  System Architecture

The project is divided into two main pipelines:

### 1. Batch Pipeline (Training & Data Science)
Focuses on data preparation and model creation.
- **Data Source:** US Airlines Dataset (`7Xan7der7/usairlinesentiment` from Hugging Face).
- **EDA & Cleaning:** Deduplication, Regex cleaning (URLs, mentions), and normalization.
- **Embeddings:** Text-to-Vector conversion using **Sentence Transformers** (`paraphrase-multilingual-MiniLM-L12-v2`).
- **Vector Storage:** Embeddings stored in **ChromaDB** (Training & Test collections).
- **Model:** Classification model trained on embeddings and saved as a `.pkl` artifact.

### 2. Streaming Pipeline (Inference & Visualization)
Handles real-time data flow and user interface.
- **Ingestion:** Micro-batch data collection via API/Tweet Generator.
- **Processing:** Data cleaning and sentiment prediction via the Model API.
- **Storage:** Predictions and metadata stored in **PostgreSQL**.
- **Orchestration:** **Apache Airflow** DAGs running every minute to manage the workflow.
- **Visualization:** **Streamlit** dashboard displaying live KPIs:
  - Total Tweet Volume & Airline Count.
  - Sentiment Distribution (Positive/Neutral/Negative).
  - Real-time Satisfaction Rates.

---

##  Tech Stack

| Domain | Technologies |
|--------|--------------|
| **Orchestration** | Apache Airflow |
| **Containerization** | Docker, Docker Compose |
| **Database** | PostgreSQL (Relational), ChromaDB (Vector) |
| **Machine Learning** | Hugging Face, Scikit-learn, Sentence Transformers |
| **API & Backend** | Python (FastAPI/Flask integration) |
| **Frontend** | Streamlit |

---

##  Project Structure

```bash
Aerostream/
├── airflow_streaming/      # Airflow DAGs and configuration
├── chroma_db/              # Vector database storage (Embeddings)
├── dashboard/              # Streamlit application (Frontend)
├── data/                   # Raw and processed datasets (CSV)
├── init-db/                # SQL scripts for PostgreSQL initialization
├── model_api/              # REST API for model inference
├── models/                 # Serialized models (sentiment_model.pkl)
├── notebooks/              # Data Science Lifecycle (EDA, Cleaning, Embedding, Training)
├── tweet_generator/        # Service to simulate streaming tweet data
└── docker-compose.yaml     # Container orchestration config
```

---

##  Installation & Usage

### Prerequisites
- Docker Desktop installed and running.
- Git.

### Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/laamiri-kaoutar/Aerostream.git
   cd Aerostream
   ```

2. **Build and Run Containers:**
   ```bash
   docker-compose up --build -d
   ```

3. **Access the Services:**
   - **Streamlit Dashboard:** `http://localhost:8501`
   - **Airflow Webserver:** `http://localhost:8080`
   - **Model API:** Port `5000` (internal)
   - **PostgreSQL:** Port `5432`

---

## Dashboard Features
The Streamlit dashboard automatically updates when new data is ingested:
- **Metrics:** Total number of tweets, percentage of negative tweets.
- **Charts:** Bar charts for sentiment distribution per airline.
- **Analysis:** Identification of main reasons for negative feedback.

---
*Created by [Laamiri Kaoutar](https://github.com/laamiri-kaoutar)*
```
