#!/usr/bin/env bash
# Comprehensive test suite runner
# Runs all tests and generates coverage report

set -e

echo "========================================="
echo "Squig League - Comprehensive Test Suite"
echo "========================================="

# Ensure Docker environment is running
echo ""
echo "Checking Docker environment..."
if ! docker compose -f docker-compose.dev.yml ps | grep -q "healthy"; then
    echo "ERROR: Docker environment not healthy"
    echo "Run: docker compose -f docker-compose.dev.yml up -d"
    exit 1
fi

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 5

# Run integration tests
echo ""
echo "Running integration tests..."
python -m pytest tests/integration/ -v --tb=short

# Run end-to-end tests
echo ""
echo "Running end-to-end tests..."
python -m pytest tests/e2e/ -v --tb=short

# Run all tests with coverage
echo ""
echo "Running all tests with coverage..."
python -m pytest tests/ -v --cov=backend/app --cov=squire --cov-report=html --cov-report=term

echo ""
echo "========================================="
echo "Test Summary"
echo "========================================="
echo "✓ Integration tests: PASSED"
echo "✓ End-to-end tests: PASSED"
echo "✓ Coverage report: htmlcov/index.html"
echo "========================================="
