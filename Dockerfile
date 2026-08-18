FROM python:3.11.9-slim

WORKDIR /app

# Runtime deps for PyMuPDF, pillow, matplotlib, python-docx, reportlab, pypdf
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    gcc \
    poppler-utils \ # ADDED: for better PDF text extraction
    && rm -rf /var/lib/apt/lists/*

# Streamlit settings for Render
ENV STREAMLIT_SERVER_FILE_WATCHER_TYPE=none
ENV STREAMLIT_SERVER_RUN_ON_SAVE=false
ENV STREAMLIT_SERVER_HEADLESS=true

# Tell app this is CLOUD so it skips local LLM and uses OPENROUTER
ENV DEPLOY_ENV=cloud

# Install python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Create folder for persistent data on Render Disk
RUN mkdir -p /data/assets/labels

# Tell app to save files to /data
ENV STREAMLIT_DATA_PATH=/data

EXPOSE 8501

# Start Streamlit
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0", "--server.fileWatcherType", "none", "--server.runOnSave", "false", "--server.headless", "true"]
