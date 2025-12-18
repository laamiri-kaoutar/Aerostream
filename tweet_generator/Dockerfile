FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# We use port 8001 to avoid conflict with your Model API on 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]