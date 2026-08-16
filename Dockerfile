FROM python:3.11.9-slim

WORKDIR /app

# System deps for PyMuPDF, pillow, matplotlib, reportlab, faiss
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Prevent Streamlit file watcher + auto reload. Fixes inotify limit on Render
ENV STREAMLIT_SERVER_FILE_WATCHER_TYPE=none
ENV STREAMLIT_SERVER_RUN_ON_SAVE=false
ENV STREAMLIT_SERVER_HEADLESS=true

# Tell app we are on CLOUD so it skips local LLM
ENV DEPLOY_ENV=cloud

# Install python deps first for caching
COPY requirements.txt .

# Install all deps EXCEPT llama-cpp-python which fails on Render
# We use grep -v to filter it out during cloud build
RUN pip install --no-cache-dir -r <(grep -v "llama-cpp-python" requirements.txt)

# Copy app code
COPY . .

# Create folder for persistent data on Render Disk
RUN mkdir -p /data/assets/labels

# Tell app to save files to /data
ENV STREAMLIT_DATA_PATH=/data

EXPOSE 8501

# Start command with no file watcher
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0", "--server.fileWatcherType", "none", "--server.runOnSave", "false", "--server.headless", "true"]
