FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for WeasyPrint and matplotlib
# WeasyPrint requires GTK, Pango, and other graphics libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Delete old generated protobuf files and regenerate with the installed protobuf version
RUN rm -f server/generated/report_pb2.py server/generated/report_pb2_grpc.py server/generated/report_pb2.pyi && \
    python -m grpc_tools.protoc \
    --proto_path=proto \
    --python_out=server/generated \
    --grpc_python_out=server/generated \
    proto/report.proto && \
    # Fix the import in the generated grpc file to use relative import
    sed -i 's/^import report_pb2/from . import report_pb2/' server/generated/report_pb2_grpc.py

# Create necessary output directories (but not data, which contains source code)
RUN mkdir -p /app/diagrams /app/pdf_output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port (adjust based on settings)
EXPOSE 5000

# Run the FastAPI application
CMD ["python", "main.py"]
