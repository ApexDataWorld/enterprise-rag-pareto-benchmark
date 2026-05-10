FROM python:3.13-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -e .

CMD ["python", "-m", "rag_pareto.cli", "run", "--config", "configs/default.yaml"]

