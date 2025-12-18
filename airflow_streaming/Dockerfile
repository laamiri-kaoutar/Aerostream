# 1. Start with the official Airflow image
FROM apache/airflow:2.7.1

# 2. Copy the requirements file
COPY requirements.txt .

# 3. Install the extra libraries
RUN pip install --no-cache-dir -r requirements.txt