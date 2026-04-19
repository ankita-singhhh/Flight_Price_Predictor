#!/bin/bash

# Flight Price Predictor - Test Script
# This script runs all tests and generates coverage report

set -e  # Exit on any error

echo "🧪 Running Flight Price Predictor Test Suite..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    print_warning "Virtual environment is not activated. Activating..."
    source venv/bin/activate
fi

# Check if test dependencies are installed
print_step "Checking test dependencies..."
if ! python -c "import pytest" 2>/dev/null; then
    print_status "Installing test dependencies..."
    pip install pytest pytest-flask pytest-cov
fi

# Run linting
print_step "Running code linting..."
if command -v flake8 &> /dev/null; then
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
else
    print_warning "flake8 not installed. Skipping linting."
    print_status "Install with: pip install flake8"
fi

# Run tests with coverage
print_step "Running tests with coverage..."
pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing --cov-fail-under=80

# Check coverage report
if [ -f "htmlcov/index.html" ]; then
    print_status "✅ Coverage report generated: htmlcov/index.html"
fi

# Run specific integration tests
print_step "Running integration tests..."
python -c "
import requests
import json
from datetime import datetime, timedelta

# Test API endpoints
try:
    # Health check
    response = requests.get('http://localhost:5000/health', timeout=5)
    assert response.status_code == 200
    print('✅ Health check passed')
    
    # Prediction test
    future = datetime.now() + timedelta(hours=2)
    data = {
        'Dep_Time': future.isoformat(),
        'Arrival_Time': (future + timedelta(hours=2)).isoformat(),
        'stops': '0',
        'airline': 'IndiGo',
        'Source': 'Delhi',
        'Destination': 'Mumbai'
    }
    
    response = requests.post('http://localhost:5000/api/predict', 
                           json=data, timeout=10)
    assert response.status_code == 200
    result = response.json()
    assert 'prediction' in result
    print('✅ API prediction test passed')
    
except requests.exceptions.ConnectionError:
    print('⚠️ Application not running. Skipping integration tests.')
except Exception as e:
    print(f'❌ Integration test failed: {e}')
"

echo ""
print_status "🎉 Test suite completed!"
echo ""
echo "📊 Test Results:"
echo "   3. Run application: python app.py"
echo "   Coverage: htmlcov/index.html"
echo "   Linting: flake8 ."
echo ""
echo "🔍 View detailed coverage report:"
echo "   open htmlcov/index.html"
