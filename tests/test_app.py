import pytest
import json
from datetime import datetime, timedelta
from app import app, validate_input, parse_stops

@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test home page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'SkyFare' in response.data

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'model' in data
    assert 'features' in data

def test_predict_endpoint_valid(client):
    """Test prediction with valid data."""
    now = datetime.now()
    future = now + timedelta(hours=2)
    
    data = {
        'Dep_Time': future.isoformat(),
        'Arrival_Time': (future + timedelta(hours=2)).isoformat(),
        'stops': '0',
        'airline': 'IndiGo',
        'Source': 'Delhi',
        'Destination': 'Mumbai'
    }
    
    response = client.post('/predict', data=data)
    assert response.status_code == 200
    assert b'₹' in response.data

def test_predict_endpoint_invalid_dates(client):
    """Test prediction with invalid dates."""
    past = datetime.now() - timedelta(days=1)
    future = datetime.now() + timedelta(hours=2)
    
    data = {
        'Dep_Time': past.isoformat(),
        'Arrival_Time': future.isoformat(),
        'stops': '0',
        'airline': 'IndiGo',
        'Source': 'Delhi',
        'Destination': 'Mumbai'
    }
    
    response = client.post('/predict', data=data)
    assert response.status_code == 200
    assert b'⚠️' in response.data

def test_api_predict_valid(client):
    """Test API prediction with valid data."""
    now = datetime.now()
    future = now + timedelta(hours=2)
    
    data = {
        'Dep_Time': future.isoformat(),
        'Arrival_Time': (future + timedelta(hours=2)).isoformat(),
        'stops': '0',
        'airline': 'IndiGo',
        'Source': 'Delhi',
        'Destination': 'Mumbai'
    }
    
    response = client.post('/api/predict', 
                         data=json.dumps(data),
                         content_type='application/json')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert 'prediction' in result
    assert 'formatted' in result
    assert 'currency' in result

def test_parse_stops():
    """Test stops parsing function."""
    assert parse_stops("non-stop") == 0
    assert parse_stops("1 stop") == 1
    assert parse_stops("2 stops") == 2
    assert parse_stops("0") == 0
    assert parse_stops("3") == 3

def test_validate_input():
    """Test input validation function."""
    now = datetime.now()
    future = now + timedelta(hours=2)
    
    # Valid input
    errors = validate_input(future, future + timedelta(hours=2), 0, "IndiGo", "Delhi", "Mumbai")
    assert len(errors) == 0
    
    # Invalid: arrival before departure
    errors = validate_input(future, now, 0, "IndiGo", "Delhi", "Mumbai")
    assert len(errors) > 0
    assert any("after departure" in error for error in errors)
    
    # Invalid: same source and destination
    errors = validate_input(future, future + timedelta(hours=2), 0, "IndiGo", "Delhi", "Delhi")
    assert len(errors) > 0
    assert any("same" in error for error in errors)
