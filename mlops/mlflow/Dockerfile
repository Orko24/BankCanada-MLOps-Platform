FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install MLflow and dependencies
RUN pip install --no-cache-dir \
    mlflow==2.9.2 \
    psycopg2-binary==2.9.9 \
    boto3==1.34.0 \
    azure-storage-blob==12.19.0

# Create artifacts directory
RUN mkdir -p /app/artifacts

# Expose MLflow port
EXPOSE 5000

# Set environment variables
ENV MLFLOW_BACKEND_STORE_URI=postgresql://admin:secure_password@postgres:5432/bankcanada_mlops
ENV MLFLOW_DEFAULT_ARTIFACT_ROOT=/app/artifacts
ENV MLFLOW_HOST=0.0.0.0
ENV MLFLOW_PORT=5000

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting MLflow tracking server..."\n\
mlflow server \\\n\
    --backend-store-uri $MLFLOW_BACKEND_STORE_URI \\\n\
    --default-artifact-root $MLFLOW_DEFAULT_ARTIFACT_ROOT \\\n\
    --host $MLFLOW_HOST \\\n\
    --port $MLFLOW_PORT \\\n\
    --workers 4\n\
' > /app/start.sh && chmod +x /app/start.sh

# Start MLflow server
CMD ["/app/start.sh"]
