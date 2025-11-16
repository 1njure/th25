FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN mkdir -p temp logs

ENV PYTHONPATH=/app/src

RUN useradd -m -r botuser && \
    chown -R botuser:botuser /app
USER botuser

CMD ["python", "src/bot.py"]