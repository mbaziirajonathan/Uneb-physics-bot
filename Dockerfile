FROM python:3.11.9-slim

WORKDIR /app

# System deps for PyMuPDF, pillow, matplotlib, reportlab
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python deps first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Create folder for persistent data on Render Disk
RUN mkdir -p /data/assets/labels

# Tell app to save files to /data
ENV STREAMLIT_DATA_PATH=/data

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0", "--server.fileWatcherType", "none", "--server.runOnSave", "false"]
