# Reporting Service Test Guide

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Start the service**:

   ```bash
   cd /Users/forri/Github/Szoftarch/data_analysis
   docker compose up --build
   ```

2. **Test the API**:

   - Open browser: http://localhost:5000/docs (FastAPI auto-generated docs)
   - Or test with curl:
     ```bash
     curl -H "Authorization: Bearer test-api-key-12345" \
          http://localhost:5000/health
     ```

3. **Stop the service**:
   ```bash
   docker compose down
   ```

### Option 2: Using Docker directly

1. **Build the image**:

   ```bash
   cd /Users/forri/Github/Szoftarch/data_analysis/data_analysis
   docker build -t reporting-service .
   ```

2. **Run the container**:

   ```bash
   docker run -d \
     --name reporting-service \
     -p 5000:5000 \
     --env-file .env \
     reporting-service
   ```

3. **View logs**:

   ```bash
   docker logs -f reporting-service
   ```

4. **Stop and remove**:
   ```bash
   docker stop reporting-service
   docker rm reporting-service
   ```

### Option 3: Local Development (without Docker)

1. **Create virtual environment**:

   ```bash
   cd /Users/forri/Github/Szoftarch/data_analysis/data_analysis
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up .env file** (already created, edit if needed):

   ```bash
   nano .env
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

## Testing the API

### Check API documentation

Visit: http://localhost:5000/docs

### Test endpoints

**Health check** (if available):

```bash
curl http://localhost:5000/health
```

**Generate report** (example, adjust based on actual endpoints):

```bash
curl -X POST http://localhost:5000/api/reports/time-summary \
  -H "Authorization: Bearer test-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "start_date": "2025-01-01",
    "end_date": "2025-01-31"
  }'
```

## Connecting to Existing PostgreSQL

If you have the PostgreSQL database from the core-app running on port 5433:

- The service will connect automatically using `host.docker.internal:5433`
- Make sure the database is running: `docker ps | grep postgres`

## Troubleshooting

**Port already in use**:

```bash
# Change port in docker-compose.yml to "5001:5000"
```

**Database connection failed**:

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Test connection manually
psql -h localhost -p 5433 -U user -d workplanner
```

**WeasyPrint errors**:

- Already handled in Dockerfile with GTK dependencies
- If issues persist, check container logs: `docker logs reporting-service`

**Permission errors**:

```bash
# Create output directories with proper permissions
mkdir -p diagrams pdf_output templates
chmod 755 diagrams pdf_output templates
```
