# API image for the customer-behaviour (Sephora product-recommendation) service.
# Build context is customer_behaviour/ (so both api/ and model/ are available):
#     docker build -f api/Dockerfile -t cb-api .
# Compose does this for you.
FROM python:3.12-slim

WORKDIR /app

COPY api/requirements.txt ./api/requirements.txt
RUN pip install --default-timeout=100 --no-cache-dir -r api/requirements.txt

# code + the persisted pipeline (config.py resolves model/ as APP_DIR/model)
COPY api ./api
COPY model ./model

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
