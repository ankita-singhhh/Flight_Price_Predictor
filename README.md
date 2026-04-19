# ✈️ SkyFare - Flight Price Predictor

A machine learning-powered flight price prediction system trained on Indian domestic flight data. Uses XGBoost regression to predict flight fares based on route, airline, timing, and other features.

## 🚀 Features

- **Accurate Predictions**: XGBoost model with 643 features
- **Real-time Processing**: Fast predictions (~236ms)
- **User-Friendly Interface**: Modern, responsive web UI
- **API Access**: RESTful API for integration
- **Production Ready**: Docker support, CI/CD pipeline
- **Comprehensive Validation**: Input validation and error handling

## 📊 Model Performance

- **Model Type**: XGBoost Regressor
- **Features**: 643 engineered features
- **Prediction Time**: ~236ms
- **Price Range**: ₹15,465 - ₹17,616 (based on test scenarios)
- **Key Features**: Business class, Jet Airways Business, route-specific features

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Machine Learning**: XGBoost, scikit-learn, pandas
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Docker, Gunicorn
- **CI/CD**: GitHub Actions

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/flight-price-predictor.git
   cd flight-price-predictor
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
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python improved_app.py
   ```

6. **Access the application**
   - Web Interface: http://localhost:5000
   - API: http://localhost:5000/api/predict
   - Health Check: http://localhost:5000/health

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Clone and navigate to the project**
   ```bash
   git clone https://github.com/yourusername/flight-price-predictor.git
   cd flight-price-predictor
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Web Interface: http://localhost
   - API: http://localhost/api/predict

### Using Docker Only

1. **Build the image**
   ```bash
   docker build -t flight-price-predictor .
   ```

2. **Run the container**
   ```bash
   docker run -p 5000:5000 flight-price-predictor
   ```

## 📡 API Usage

### Predict Flight Price

**Endpoint**: `POST /api/predict`

**Request Body**:
```json
{
  "Dep_Time": "2024-06-15T08:00:00",
  "Arrival_Time": "2024-06-15T10:30:00",
  "stops": "0",
  "airline": "IndiGo",
  "Source": "Delhi",
  "Destination": "Mumbai"
}
```

**Response**:
```json
{
  "prediction": 16945.0,
  "formatted": "₹ 16,945",
  "currency": "INR"
}
```

### Health Check

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "model": "XGBRegressor",
  "features": 643,
  "timestamp": "2024-06-15T08:00:00.000000"
}
```

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-flask pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### Test Coverage

The test suite includes:
- API endpoint testing
- Input validation testing
- Model prediction testing
- Error handling testing

## 📁 Project Structure

```
flight-price-predictor/
├── app.py                  # Production-ready Flask application
├── config.py               # Configuration management
├── wsgi.py                 # WSGI entry point
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore file
├── .dockerignore         # Docker ignore file
├── README.md             # This file
├── IMPROVEMENTS.md      # Detailed improvements documentation
├── static/               # Static assets
│   └── style.css        # Main stylesheet
├── templates/            # HTML templates
│   ├── home.html        # Original template
│   └── improved_home.html # Enhanced template
├── tests/               # Test suite
│   └── test_app.py     # Application tests
├── .github/             # GitHub workflows
│   └── workflows/
│       └── ci-cd.yml   # CI/CD pipeline
├── data/               # Training data (if available)
├── notebooks/          # Jupyter notebooks (if available)
├── flight_price_model.pkl # Trained model
├── columns.pkl         # Feature columns
└── logs/              # Application logs
```

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example`):

- `FLASK_ENV`: Environment (development/production)
- `SECRET_KEY`: Flask secret key
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 5000)
- `DEBUG`: Debug mode (default: False)
- `LOG_LEVEL`: Logging level (default: INFO)

### Model Configuration

- `MODEL_PATH`: Path to trained model file
- `COLUMNS_PATH`: Path to feature columns file

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-production-secret-key
   export DEBUG=False
   ```

2. **Using Gunicorn**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app
   ```

3. **Using Docker Compose**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

### Cloud Deployment

The application is ready for deployment on:
- **AWS**: ECS, EKS, or EC2 with Docker
- **Google Cloud**: Cloud Run or GKE
- **Azure**: Container Instances or AKS
- **Heroku**: Docker deployment
- **DigitalOcean**: App Platform or Droplets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation
- Use meaningful commit messages
- Ensure all tests pass before PR

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flight data source and preprocessing inspiration
- XGBoost library for powerful gradient boosting
- Flask framework for web development
- Open-source community for tools and libraries

## 📞 Support

For questions, issues, or contributions:

- 📧 Email: your-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/flight-price-predictor/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/flight-price-predictor/discussions)

---

**Built with ❤️ using Python, Flask, and XGBoost**
