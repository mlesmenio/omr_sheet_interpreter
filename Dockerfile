# Base image
FROM python:3.11-slim

# Install minimal system dependencies required for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    poppler-utils\
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && pip install \
    opencv-python \
    pdf2image \
    pillow \
    mido \
    pretty_midi \
    numpy \
    --no-cache-dir

# Set working directory
WORKDIR /app
#COPY /app .

# For interactive development
CMD ["bash"]