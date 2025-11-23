FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DEBUG=false
ENV SEED_VALUE=""

CMD ["python", "src/game/main.py"]
