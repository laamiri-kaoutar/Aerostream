FROM python:3.9-slim

WORKDIR /app

# Install system tools needed for the database connection
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Expose the port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "Home.py", "--server.address=0.0.0.0"]