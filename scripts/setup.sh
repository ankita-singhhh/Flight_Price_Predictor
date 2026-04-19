#!/bin/bash

# Flight Price Predictor - Setup Script
# This script sets up the development environment

set -e  # Exit on any error

echo "🔧 Setting up Flight Price Predictor Development Environment..."

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

# Check Python version
print_step "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    print_status "✅ Python version $PYTHON_VERSION is compatible"
else
    print_error "❌ Python version $PYTHON_VERSION is too old. Required: $REQUIRED_VERSION+"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_step "Creating virtual environment..."
    python3 -m venv venv
    print_status "✅ Virtual environment created"
else
    print_status "✅ Virtual environment already exists"
fi

# Activate virtual environment
print_step "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_step "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_step "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
print_step "Creating necessary directories..."
mkdir -p logs
mkdir -p data
mkdir -p notebooks

# Set up environment file
if [ ! -f .env ]; then
    print_step "Creating environment file..."
    cp .env.example .env
    print_status "✅ Created .env file from template"
    print_warning "Please edit .env file with your configuration"
else
    print_status "✅ .env file already exists"
fi

# Run tests to verify setup
print_step "Running tests to verify setup..."
if pytest tests/ -v; then
    print_status "✅ All tests passed!"
else
    print_warning "Some tests failed. Please check the setup."
fi

# Display setup completion message
echo ""
print_status "🎉 Setup completed successfully!"
echo ""
echo "🚀 Next steps:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Edit .env file with your configuration"
echo "   3. Run application: python app.py"
echo "   4. Access the app: http://localhost:5000"
echo ""
echo "🧪 Development commands:"
echo "   Run tests:     pytest"
echo "   Run with coverage: pytest --cov=. --cov-report=html"
echo "   Format code:   black ."
echo "   Lint code:     flake8 ."
echo ""
print_status "Happy coding! 🚀"
