FROM python:3.11.9-slim

WORKDIR /app

# Install deps first for cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code - FIXED: need source + destination
COPY . .

# Create tmp folder for free tier cache
RUN mkdir -p /tmp

# Expose Streamlit port
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
