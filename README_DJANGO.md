# Financial Analytics Application - Django Migration

This application has been migrated from Spring Boot (Java) to Django (Python) while preserving all existing features and functionality.

## Overview

A comprehensive financial analytics platform that pulls market data from YahooFinance API, stores it in ClickHouse, and enables quantitative analysis through Django REST Framework.

## Architecture

This is a Django project with the following apps:

### Apps

- **api_service** - REST API layer for YahooFinance integration
  - Fetches quotes, fundamentals, historical data
  - Exposes REST endpoints for data access
  - Django REST Framework application

- **data_ingestion** - Data synchronization service
  - Ingests financial data from Yahoo Finance API
  - Stores data in ClickHouse with deduplication
  - Scheduled updates via Celery (daily and intraday)
  - Retry strategy with exponential backoff
  - Alert logging for failures

- **analytics_core** - Analytics engine
  - Pluggable algorithmic modules
  - Statistical models, ML models, quantitative strategies
  - Reusable library

- **ui_app** - Web frontend
  - Data exploration and visualization
  - Django templates
  - Display market insights

## Technology Stack

- **Language**: Python 3.12
- **Framework**: Django 5.0.1
- **REST API**: Django REST Framework 3.14.0
- **Task Queue**: Celery 5.3.6 with Redis
- **Database**: ClickHouse (optimized for analytical queries)
- **Data Source**: YahooFinance API (via yfinance)
- **CI/CD**: GitHub Actions (to be updated)

## Migrated Features

All features from the Spring Boot application have been migrated:

✅ **API Layer**
- GET /api/stocks/{symbol}/quote/ - Real-time stock quotes
- GET /api/stocks/{symbol}/history/ - Historical data with date range
- POST /api/stocks/quotes/ - Batch quote retrieval

✅ **Rate Limiting**
- Configurable rate limiter (default: 5 requests/second)
- Rate limit exception handling

✅ **Data Ingestion**
- Historical data ingestion with configurable days
- Current quote ingestion
- Batch processing for multiple symbols
- ClickHouse integration with native driver

✅ **Scheduled Tasks**
- Daily historical data ingestion (6 PM)
- Intraday quote updates (every 15 minutes during market hours)
- Celery Beat for scheduling

✅ **Retry Logic**
- Automatic retry with exponential backoff
- Configurable max attempts
- Recovery methods for failures

✅ **Alert System**
- Separate ALERT logger for critical failures
- Failure threshold tracking
- High failure rate alerts

✅ **Error Handling**
- Custom exceptions (YahooFinanceException, RateLimitExceededException)
- Comprehensive logging
- Graceful degradation

✅ **Web UI**
- Home dashboard
- Stock quotes page
- Modern, responsive design

## Getting Started

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Docker and Docker Compose (for ClickHouse and Redis)
- ClickHouse instance
- Redis instance (for Celery)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/sandeep-jaiswar/Financial-Analytics-Application.git
cd Financial-Analytics-Application
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.django.example .env
# Edit .env with your configuration
```

5. **Start ClickHouse and Redis**
```bash
docker compose up -d clickhouse redis
```

6. **Initialize database schema**
```bash
./db/init-schema.sh
```

7. **Run Django migrations**
```bash
python manage.py migrate
```

8. **Create superuser (optional)**
```bash
python manage.py createsuperuser
```

### Running the Application

#### Option 1: Local Development

**Start Django server:**
```bash
python manage.py runserver
```

**Start Celery worker (in another terminal):**
```bash
celery -A financial_analytics worker -l info
```

**Start Celery beat scheduler (in another terminal):**
```bash
celery -A financial_analytics beat -l info
```

#### Option 2: Docker Compose

```bash
docker compose up
```

This will start all services:
- Django web server (port 8000)
- Celery worker
- Celery beat scheduler
- ClickHouse (ports 8123, 9000)
- Redis (port 6379)

### Accessing the Application

- **Web UI**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **API Endpoints**: http://localhost:8000/api/stocks/

### Testing API Endpoints

**Get real-time quote:**
```bash
curl http://localhost:8000/api/stocks/AAPL/quote/
```

**Get historical data:**
```bash
curl "http://localhost:8000/api/stocks/AAPL/history/?from=2024-01-01&to=2024-01-31"
```

**Get multiple quotes:**
```bash
curl -X POST http://localhost:8000/api/stocks/quotes/ \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "GOOGL", "MSFT"]}'
```

## Data Ingestion

### Management Commands

**Ingest historical data:**
```bash
python manage.py ingest_historical --symbols AAPL,GOOGL --days 30
```

**Ingest current quotes:**
```bash
python manage.py ingest_current --symbols AAPL,GOOGL
```

### Scheduled Tasks

The application uses Celery Beat for scheduled tasks:

- **Daily Historical Ingestion**: Runs at 6 PM daily (configurable in `financial_analytics/celery.py`)
- **Intraday Quote Ingestion**: Runs every 15 minutes during market hours (9 AM - 4 PM, Mon-Fri)

To modify schedules, edit `financial_analytics/celery.py`.

## Configuration

### Environment Variables

See `.env.django.example` for all available configuration options:

- `DJANGO_SECRET_KEY`: Django secret key
- `DJANGO_DEBUG`: Debug mode (True/False)
- `CLICKHOUSE_HOST`: ClickHouse host
- `CLICKHOUSE_PORT`: ClickHouse port
- `CELERY_BROKER_URL`: Redis URL for Celery
- `INGESTION_SYMBOLS`: Comma-separated list of stock symbols
- `INGESTION_HISTORY_DAYS`: Number of days of historical data to fetch
- `YAHOO_FINANCE_RATE_LIMIT`: API rate limit (requests per second)

### Django Settings

Main settings are in `financial_analytics/settings.py`:
- REST Framework configuration
- CORS settings
- Celery configuration
- Logging configuration
- ClickHouse connection settings

## Project Structure

```
financial-analytics-application/
├── financial_analytics/        # Django project settings
│   ├── settings.py            # Main settings
│   ├── urls.py                # URL routing
│   ├── celery.py              # Celery configuration
│   └── wsgi.py                # WSGI application
├── api_service/               # REST API app
│   ├── models.py              # Data models (StockQuote, HistoricalQuote)
│   ├── services.py            # Yahoo Finance service
│   ├── views.py               # API views
│   └── urls.py                # API routing
├── data_ingestion/            # Data ingestion app
│   ├── models.py              # MarketData model
│   ├── service.py             # Ingestion service
│   ├── repository.py          # ClickHouse repository
│   ├── tasks.py               # Celery tasks
│   └── management/commands/   # Management commands
│       ├── ingest_historical.py
│       └── ingest_current.py
├── analytics_core/            # Analytics library (to be implemented)
├── ui_app/                    # Web UI app
│   ├── views.py               # UI views
│   ├── urls.py                # UI routing
│   └── templates/ui_app/      # Django templates
│       ├── base.html
│       ├── home.html
│       └── stocks.html
├── db/                        # Database schemas and scripts
│   ├── schema/
│   └── init-schema.sh
├── logs/                      # Application logs
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── Dockerfile.django          # Docker configuration
├── docker-compose.yml         # Docker Compose services
└── README_DJANGO.md          # This file
```

## Migration from Spring Boot

### Key Changes

1. **Framework**: Spring Boot → Django
2. **Language**: Java/Kotlin → Python
3. **REST Framework**: Spring Web → Django REST Framework
4. **Task Scheduling**: Spring @Scheduled → Celery Beat
5. **Rate Limiting**: Resilience4j → Custom Python implementation
6. **Database Driver**: ClickHouse JDBC → clickhouse-driver (Python)
7. **Build Tool**: Gradle → pip/requirements.txt
8. **Templates**: Thymeleaf → Django Templates

### API Compatibility

The REST API endpoints remain compatible with the Spring Boot version:
- Same URL structure
- Same request/response formats
- Same error handling approach

### Notable Differences

1. **Rate Limiting**: Implemented as a decorator instead of Resilience4j
2. **Scheduling**: Celery Beat instead of Spring @Scheduled
3. **Configuration**: Environment variables and Django settings instead of application.yml
4. **Dependency Injection**: Django's apps and service pattern instead of Spring beans

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test api_service
python manage.py test data_ingestion
```

## Development Guidelines

### Code Quality

- Follow PEP 8 style guide
- Use type hints where applicable
- Write docstrings for all functions and classes
- Maintain modular, testable code

### Testing

- Write unit tests for all business logic
- Integration tests for API endpoints
- Test data ingestion and model logic

### Security

- Keep secrets in environment variables
- Validate all API and DB inputs
- Use Django's built-in security features

## Deployment

### Production Settings

1. Set `DJANGO_DEBUG=False`
2. Use strong `DJANGO_SECRET_KEY`
3. Configure `DJANGO_ALLOWED_HOSTS`
4. Use production WSGI server (Gunicorn)
5. Set up proper logging
6. Configure HTTPS

### Using Gunicorn

```bash
gunicorn financial_analytics.wsgi:application --bind 0.0.0.0:8000
```

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure virtual environment is activated
2. **Database connection**: Verify ClickHouse is running and accessible
3. **Celery not starting**: Check Redis connection
4. **API rate limiting**: Adjust `YAHOO_FINANCE_RATE_LIMIT` setting

### Logs

Check logs in the `logs/` directory:
- `financial_analytics.log`: General application logs
- `alerts.log`: Critical alerts and failures

## Contributing

1. Follow Python and Django best practices
2. Write clear, descriptive commits
3. Document all functions with docstrings
4. Ensure all tests pass before submitting

## License

[Specify your license here]
