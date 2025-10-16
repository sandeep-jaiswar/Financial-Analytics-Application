# Continuous Integration (CI) Setup

This document describes the CI/CD pipeline setup for the Financial Analytics Application.

## Overview

The project uses GitHub Actions for Continuous Integration with automated build, test, code quality checks, and security scanning.

## Workflows

### 1. CI Pipeline (`ci.yml`)

The main CI workflow runs on every push and pull request to `main` and `develop` branches.

#### Jobs:

##### Build and Test
- **Purpose**: Compile all modules and run tests
- **Steps**:
  - Checkout code
  - Setup JDK 17
  - Build with Gradle
  - Run all tests
  - Generate and upload test reports

##### Code Quality & Linting
- **Purpose**: Run code quality checks
- **Steps**:
  - Checkout code
  - Setup JDK 17
  - Run Gradle check task
  - Upload build artifacts

##### Test Coverage
- **Purpose**: Generate and report code coverage metrics
- **Steps**:
  - Checkout code
  - Setup JDK 17
  - Run tests with JaCoCo coverage
  - Generate coverage badges
  - Upload coverage reports
- **Tools**: JaCoCo for coverage analysis

##### CodeQL Security Scan
- **Purpose**: Perform security and code quality analysis
- **Steps**:
  - Checkout code
  - Initialize CodeQL
  - Build project (without tests for faster analysis)
  - Analyze code for security vulnerabilities
- **Languages**: Java/Kotlin

### 2. SonarCloud Analysis (`sonarcloud.yml`)

Optional workflow for SonarCloud integration (disabled by default).

#### Setup Instructions:

1. Sign up at [SonarCloud](https://sonarcloud.io)
2. Create a new project for your repository
3. Add `SONAR_TOKEN` to repository secrets:
   - Go to repository Settings → Secrets and variables → Actions
   - Add a new secret named `SONAR_TOKEN`
4. Update the workflow file to uncomment the trigger events
5. (Optional) Customize the Sonar properties in the workflow

#### Configuration:

The workflow uses these SonarCloud parameters:
- `sonar.projectKey`: sandeep-jaiswar_Financial-Analytics-Application
- `sonar.organization`: sandeep-jaiswar
- `sonar.host.url`: https://sonarcloud.io

## Test Coverage

The project uses JaCoCo for code coverage analysis with the following configuration:

- Coverage reports are generated automatically with each test run
- Reports are available in multiple formats:
  - XML: `**/build/reports/jacoco/test/jacocoTestReport.xml`
  - HTML: `**/build/reports/jacoco/test/html/`
  - CSV: `**/build/reports/jacoco/test/jacocoTestReport.csv`

### Running Coverage Locally

```bash
# Run tests with coverage
./gradlew test jacocoTestReport

# View HTML report
open api/build/reports/jacoco/test/html/index.html
```

## Security Scanning

### CodeQL

CodeQL is configured to run automatically on every push and pull request. It analyzes:
- Java and Kotlin code
- Security vulnerabilities
- Code quality issues
- Common programming errors

Results are available in the GitHub Security tab.

### Enabling Advanced Security Features

For private repositories, you may need to enable GitHub Advanced Security:
1. Go to repository Settings → Code security and analysis
2. Enable "Dependency graph", "Dependabot alerts", and "Code scanning"

## Build Requirements

- **JDK**: 17 (Temurin distribution)
- **Build Tool**: Gradle 8.10.2+ (wrapper included)
- **Modules**: api, data-ingestion, analytics-core, ui

## Local Development

To run the same checks locally before pushing:

```bash
# Run all checks
./gradlew clean check

# Run tests
./gradlew test

# Generate coverage reports
./gradlew test jacocoTestReport

# Build all modules
./gradlew build
```

## Troubleshooting

### Build Failures

1. **Java Version Mismatch**: Ensure JDK 17 is installed
   ```bash
   java -version
   ```

2. **Gradle Daemon Issues**: Stop all daemons
   ```bash
   ./gradlew --stop
   ```

3. **Cache Issues**: Clean build cache
   ```bash
   ./gradlew clean --no-daemon
   ```

### Test Failures

- Check test reports in `**/build/reports/tests/test/index.html`
- Review logs in GitHub Actions workflow run

### Coverage Issues

- Ensure all modules have tests
- Check JaCoCo reports in `**/build/reports/jacoco/test/html/index.html`

## CI/CD Best Practices

1. **Always run tests locally** before pushing
2. **Keep builds fast** by using Gradle cache and `--no-daemon`
3. **Monitor coverage trends** to maintain code quality
4. **Review CodeQL alerts** promptly
5. **Use feature branches** and pull requests for all changes

## Future Enhancements

- [ ] Add integration tests with Docker Compose
- [ ] Add performance testing
- [ ] Set up deployment workflows
- [ ] Add code style enforcement (ktlint/checkstyle)
- [ ] Configure branch protection rules
- [ ] Add status badges to README
