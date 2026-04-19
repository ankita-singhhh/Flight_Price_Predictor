"""
Serverless function for flight price prediction API
Optimized for Vercel deployment to reduce bundle size
"""

import json
import pickle
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# Add parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def model_predict(data):
    """Make prediction using the loaded model"""
    try:
        # Load model and columns
        model = pickle.load(open("../flight_price_model.pkl", "rb"))
        columns = pickle.load(open("../columns.pkl", "rb"))
        
        # Import feature engineering functions
        from app import build_row, parse_stops
        
        # Parse input data
        dep_dt = datetime.fromisoformat(data['Dep_Time'])
        arr_dt = datetime.fromisoformat(data['Arrival_Time'])
        stops = int(data['stops'])
        airline = data['airline']
        source = data['Source']
        destination = data['Destination']
        
        # Build feature row
        input_data = build_row(dep_dt, arr_dt, stops, airline, source, destination)
        
        # Make prediction
        prediction = model.predict(input_data)[0]
        
        return {
            "prediction": float(prediction),
            "formatted": f"₹ {prediction:,.0f}",
            "currency": "INR",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def handler(request):
    """Vercel serverless function handler"""
    try:
        # Enable CORS
        if request.method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type',
                }
            }
        
        # Parse request body
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['Dep_Time', 'Arrival_Time', 'stops', 'airline', 'Source', 'Destination']
        for field in required_fields:
            if field not in data:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Missing required field: {field}'})
                }
        
        # Make prediction
        result = model_predict(data)
        
        if 'error' in result:
            return {
                'statusCode': 500,
                'body': json.dumps(result)
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Prediction failed: {str(e)}'})
        }

# Vercel serverless entry point
def lambda_handler(event, context):
    """AWS Lambda handler for Vercel"""
    return handler(event)
