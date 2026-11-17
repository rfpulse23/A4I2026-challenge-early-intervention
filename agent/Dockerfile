# Cloud Run & Agent Runtime Container for First Milestones Early Intervention Agents
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PORT=8080 \
    STATE_CODE=MS \
    STATE_FIPS=28 \
    BIGQUERY_DATASET=a4i_early_intervention

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/agent

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "agent.server:app", "--host", "0.0.0.0", "--port", "8080"]
