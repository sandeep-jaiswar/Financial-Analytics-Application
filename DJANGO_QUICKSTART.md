# Django Quick Start Guide

Get the Django version of Financial Analytics Application running in 5 minutes!

## Prerequisites

- Python 3.12 or higher
- Docker and Docker Compose (for ClickHouse and Redis)

## Option 1: Docker Compose (Recommended)

The easiest way to run everything:

```bash
# Clone the repository
git clone https://github.com/sandeep-jaiswar/Financial-Analytics-Application.git
cd Financial-Analytics-Application

# Start all services
docker compose up
```

That's it! Access:
- Web UI: http://localhost:8000
- API: http://localhost:8000/api/stocks/
- Admin: http://localhost:8000/admin/

## Option 2: Local Development

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Start Supporting Services

```bash
# Start ClickHouse and Redis
docker compose up -d clickhouse redis

# Initialize ClickHouse schema
./db/init-schema.sh
```

### 3. Run Django

```bash
# Run migrations
python manage.py migrate

# Start Django server
python manage.py runserver
```

### 4. Start Celery (Optional, for scheduled tasks)

In separate terminals:

```bash
# Terminal 2: Start Celery worker
celery -A financial_analytics worker -l info

# Terminal 3: Start Celery beat
celery -A financial_analytics beat -l info
```

## Test the Application

### Web Interface

Open http://localhost:8000 in your browser

### API Endpoints

```bash
# Get stock quote
curl http://localhost:8000/api/stocks/AAPL/quote/

# Get historical data
curl "http://localhost:8000/api/stocks/AAPL/history/?from=2024-01-01&to=2024-01-31"

# Get multiple quotes
curl -X POST http://localhost:8000/api/stocks/quotes/ \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "GOOGL", "MSFT"]}'
```

### Management Commands

```bash
# Ingest historical data (30 days for AAPL)
python manage.py ingest_historical --symbols AAPL --days 30

# Ingest current quotes
python manage.py ingest_current --symbols AAPL,GOOGL,MSFT
```

## Run Tests

```bash
python manage.py test
```

## Configuration

Copy `.env.django.example` to `.env` and customize:

```bash
cp .env.django.example .env
# Edit .env with your settings
```

Key settings:
- `INGESTION_SYMBOLS` - Stock symbols to track
- `CLICKHOUSE_HOST` - ClickHouse server host
- `CELERY_BROKER_URL` - Redis URL for Celery

## Troubleshooting

### Port Already in Use
```bash
# Change Django port
python manage.py runserver 8001
```

### Can't Connect to ClickHouse
```bash
# Check if ClickHouse is running
docker ps | grep clickhouse

# Start ClickHouse
docker compose up -d clickhouse
```

### Celery Tasks Not Running
```bash
# Check if Redis is running
docker ps | grep redis

# Start Redis
docker compose up -d redis
```

## Next Steps

- Read [README_DJANGO.md](README_DJANGO.md) for detailed documentation
- Check [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for Spring Boot comparison
- Explore the admin interface at http://localhost:8000/admin/

## Need Help?

- Check logs in the `logs/` directory
- Run `python manage.py check` to verify configuration
- See full documentation in [README_DJANGO.md](README_DJANGO.md)

---

Enjoy your Django Financial Analytics Application! 🚀
