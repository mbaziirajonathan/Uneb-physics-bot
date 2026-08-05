FROM python:3.11.9-slim

WORKDIR /app

# Install system deps for PyMuPDF, pillow, matplotlib
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create folders for data persistence
RUN mkdir -p /data/assets/labels

# Tell streamlit to use /data for files
ENV STREAMLIT_DATA_PATH=/data

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
