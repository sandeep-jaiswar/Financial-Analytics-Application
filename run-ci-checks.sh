#!/bin/bash
# Local CI Validation Script
# This script runs the same checks that GitHub Actions will run

set -e

echo "============================================"
echo "Running Local CI Pipeline Validation"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1${NC}"
        exit 1
    fi
}

echo "Step 1: Clean build directory..."
./gradlew clean --no-daemon
print_status "Clean completed"
echo ""

echo "Step 2: Building all modules..."
./gradlew build --no-daemon
print_status "Build completed"
echo ""

echo "Step 3: Running ktlint checks..."
./gradlew ktlintCheck --no-daemon
print_status "Code style checks passed"
echo ""

echo "Step 4: Running tests..."
./gradlew test --no-daemon
print_status "All tests passed"
echo ""

echo "Step 5: Generating coverage reports..."
./gradlew jacocoTestReport --no-daemon
print_status "Coverage reports generated"
echo ""

echo "============================================"
echo -e "${GREEN}All CI checks passed successfully!${NC}"
echo "============================================"
echo ""
echo "Coverage reports available at:"
echo "  - api/build/reports/jacoco/test/html/index.html"
echo "  - data-ingestion/build/reports/jacoco/test/html/index.html"
echo "  - analytics-core/build/reports/jacoco/test/html/index.html"
echo ""
echo "Test reports available at:"
echo "  - api/build/reports/tests/test/index.html"
echo "  - data-ingestion/build/reports/tests/test/index.html"
echo "  - analytics-core/build/reports/tests/test/index.html"
echo ""
