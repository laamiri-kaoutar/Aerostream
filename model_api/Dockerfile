# 1. Base Image
FROM python:3.10-slim

# 2. Set working directory
WORKDIR /app

# 3. Copy requirements
COPY requirements.txt .

# 4. Install dependencies with optimizations
# --default-timeout=1000: Prevents the "Read timed out" error
# We install the CPU version of torch FIRST to avoid downloading the huge 900MB GPU version
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --default-timeout=1000 torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# 5. Copy app code
COPY main.py .

# 6. Expose port
EXPOSE 8000

# 7. Run command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]