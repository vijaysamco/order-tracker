FROM node:22-slim AS copilot
RUN npm install --global @github/copilot

FROM python:3.12-slim
COPY --from=copilot /usr/local /usr/local
WORKDIR /responder
RUN pip install --no-cache-dir fastapi==0.115.12 httpx==0.28.1 uvicorn==0.34.0
COPY main.py ./main.py
ENV PYTHONUNBUFFERED=1 \
    COPILOT_CLI_COMMAND=copilot \
    COPILOT_HOME=/var/lib/copilot \
    INCIDENT_DATA_DIR=/var/lib/incident-response \
    INCIDENT_WORKSPACE=/workspace
EXPOSE 8001
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
