FROM pytorch/pytorch:2.9.1-cuda12.6-cudnn9-runtime

RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN chown -R 42420:42420 /app
ENV HOME=/app

RUN pip install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p downloads separated && chown -R 42420:42420 /app

EXPOSE 8501

CMD ["streamlit", "run", "project.py", "--server.port=8501", "--server.address=0.0.0.0"]