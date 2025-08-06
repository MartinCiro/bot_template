FROM python:3.10-slim

# Instala dependencias necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    gnupg \
    ca-certificates \
    firefox-esr \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libxt6 \
    libxrender1 \
    libxrandr2 \
    libasound2 \
    libnss3 \
    libxss1 \
    libglib2.0-0 \
    xauth \
    xvfb \
    unzip \
    libavif-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /app/plugins/clip/
RUN ln -s /usr/local/lib/python3.10/site-packages/clip/bpe_simple_vocab_16e6.txt.gz /app/plugins/clip/

COPY . .

