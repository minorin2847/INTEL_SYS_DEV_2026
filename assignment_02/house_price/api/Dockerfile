# API image for the house-price service.
FROM python:3.12-slim

WORKDIR /app

COPY api/requirements.txt ./api/requirements.txt
RUN pip install --default-timeout=100 --no-cache-dir -r api/requirements.txt

COPY api ./api
COPY model ./model

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
