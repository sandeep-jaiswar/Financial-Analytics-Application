# Financial Analytics Application

A comprehensive financial analytics platform that pulls market data from YahooFinance API, stores it in ClickHouse, and enables quantitative analysis through pluggable algorithmic modules.

## Architecture

This is a Gradle multi-module project with the following components:

### Modules

- **api** - REST API layer for YahooFinance integration
  - Fetches quotes, fundamentals, historical data, and news
  - Exposes REST endpoints for data access
  - Spring Boot application

- **data-ingestion** - Data synchronization service
  - Ingests financial data from the API layer
  - Stores data in ClickHouse
  - Keeps datasets updated
  - Spring Boot application

- **analytics-core** - Analytics engine
  - Pluggable algorithmic modules
  - Statistical models, ML models, quantitative strategies
  - Trend detection, mean reversion, etc.
  - Reusable library (not a standalone application)

- **ui** - Web frontend
  - Data exploration and visualization
  - Strategy execution interface
  - Display and compare market insights
  - Spring Boot application with Thymeleaf

## Technology Stack

- **Language**: Kotlin
- **Build Tool**: Gradle (Kotlin DSL)
- **Framework**: Spring Boot 3.2.2
- **Database**: ClickHouse (optimized for analytical queries)
- **Data Source**: YahooFinance API
- **JDK**: Java 17+

## Getting Started

### Prerequisites

- JDK 17 or higher
- Gradle 8.5+ (wrapper included)
- Docker and Docker Compose (for local ClickHouse instance)
- ClickHouse instance (for data-ingestion module)

### Building the Project

```bash
# Build all modules
./gradlew build

# Build a specific module
./gradlew :api:build
./gradlew :data-ingestion:build
./gradlew :analytics-core:build
./gradlew :ui:build
```

### Setting Up ClickHouse Database

```bash
# Start ClickHouse with Docker
docker compose up -d clickhouse

# Verify schema is created
./db/verify-schema.sh

# Or manually initialize
docker exec -it financial-analytics-clickhouse clickhouse-client --multiquery < db/schema/001_create_market_data_table.sql
```

For more details on database setup, see [db/README.md](db/README.md).

### Running Tests

```bash
# Run all tests
./gradlew test

# Run tests for a specific module
./gradlew :api:test
```

### Running Applications

```bash
# Run the API service
./gradlew :api:bootRun

# Run the data ingestion service
./gradlew :data-ingestion:bootRun

# Run the UI application
./gradlew :ui:bootRun
```

## Project Structure

```
financial-analytics-application/
├── api/                          # REST API module
│   ├── src/
│   │   ├── main/
│   │   │   ├── kotlin/
│   │   │   └── resources/
│   │   └── test/
│   └── build.gradle.kts
├── data-ingestion/               # Data ingestion module
│   ├── src/
│   │   ├── main/
│   │   │   ├── kotlin/
│   │   │   └── resources/
│   │   └── test/
│   └── build.gradle.kts
├── analytics-core/               # Analytics library
│   ├── src/
│   │   ├── main/
│   │   │   ├── kotlin/
│   │   │   └── resources/
│   │   └── test/
│   └── build.gradle.kts
├── ui/                           # Web UI module
│   ├── src/
│   │   ├── main/
│   │   │   ├── kotlin/
│   │   │   └── resources/
│   │   └── test/
│   └── build.gradle.kts
├── db/                           # Database schemas and scripts
│   ├── schema/                   # SQL migration scripts
│   │   ├── 001_create_market_data_table.sql
│   │   ├── 002_create_market_data_table_replicated.sql
│   │   └── README.md
│   ├── init-schema.sh            # Schema initialization
│   ├── verify-schema.sh          # Schema verification
│   └── README.md
├── buildSrc/                     # Gradle convention plugins
│   ├── src/main/kotlin/
│   │   └── Dependencies.kt
│   └── build.gradle.kts
├── clickhouse-config/            # ClickHouse configuration
│   └── custom.xml
├── docker-compose.yml            # Docker services
├── build.gradle.kts              # Root build configuration
├── settings.gradle.kts           # Multi-module settings
├── gradle.properties             # Gradle properties
├── gradlew                       # Gradle wrapper (Unix)
├── gradlew.bat                   # Gradle wrapper (Windows)
└── README.md                     # This file
```

## Development Guidelines

### Code Quality

- Write modular, well-documented code
- Use clear, descriptive function and variable names
- Favor configuration-driven designs
- Maintain robust error handling especially around API calls and DB operations
- All business logic should be testable and reusable in isolation

### Testing

- Write unit tests for all business logic
- Integration tests for API endpoints
- Test data ingestion and model logic
- Maintain high test coverage

### Security

- Keep secrets/configs out of the codebase
- Validate all API and DB payloads
- Use environment variables for sensitive configuration

### Performance

- Aim for high throughput and reliability
- Use asynchronous programming for I/O operations
- Optimize database queries for analytical workloads

## Feature Roadmap

- [x] Initial monorepo structure
- [ ] API Layer: YahooFinance integration
- [x] Database Layer: ClickHouse schema for time series data
- [ ] Data Sync: Automated data ingestion pipeline
- [ ] Analytics Engine: Model pipeline framework
- [ ] Web UI: Dashboard and visualization
- [ ] Extensibility: Plugin system for custom strategies
- [ ] Error Monitoring: Logging, alerts, health endpoints
- [ ] Testing: Comprehensive test suite

## Contributing

1. Follow the coding guidelines
2. Write concise, comprehensible commits
3. Document all functions and modules with KDoc
4. Ensure all tests pass before submitting

## License

[Specify your license here]
