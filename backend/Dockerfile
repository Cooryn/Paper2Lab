FROM python:3.11-slim

WORKDIR /workspace/backend

COPY backend/requirements.txt /workspace/backend/requirements.txt
RUN pip install --no-cache-dir -r /workspace/backend/requirements.txt

COPY backend /workspace/backend
COPY samples /workspace/samples
COPY scripts /workspace/scripts
COPY .env.example /workspace/.env.example

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

