from flask import Flask, request, render_template, jsonify
import pickle
import pandas as pd
import numpy as np
from scipy.special import boxcox1p
from scipy.stats import boxcox_normmax
import logging
from datetime import datetime, timedelta
import time

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Load model & columns ──────────────────────────────────────────────────────
try:
    model = pickle.load(open("flight_price_model.pkl", "rb"))
    columns = pickle.load(open("columns.pkl", "rb"))
    logger.info(f"Model loaded successfully: {type(model).__name__}")
    logger.info(f"Training columns: {len(columns)}")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    raise

# ── Performance optimization: Cache column mapping ───────────────────────────────
COLUMN_MAPPING = {
    'numeric': {
        'Duration': 'Duration_0',
        'Depart_Time_Hour': 'Depart_Time_Hour_1', 
        'Depart_Time_Minutes': 'Depart_Time_Minutes_2',
        'Arr_Time_Hour': 'Arr_Time_Hour_3',
        'Arr_Time_Minutes': 'Arr_Time_Minutes_4',
        'weekday_journey': 'weekday_journey_5',
        'weekday_arrival': 'weekday_arrival_6',
        'Year': 'Year_7',
        'month_of_journey': 'month_of_journey_8',
        'month_of_Arrival': 'month_of_Arrival_9',
        'day_of_Arrival': 'day_of_Arrival_10',
        'day_of_Journey': 'day_of_Journey_11',
    },
    'airline': {
        'AirAsia': 'Airline_AirAsia_17',
        'AirIndia': 'Airline_AirIndia_18', 
        'GoAir': 'Airline_GoAir_19',
        'IndiGo': 'Airline_IndiGo_20',
        'JetAirways': 'Airline_JetAirways_21',
        'JetAirwaysBusiness': 'Airline_JetAirwaysBusiness_22',
        'Multiplecarriers': 'Airline_Multiplecarriers_23',
        'MultiplecarriersPremiumeconomy': 'Airline_MultiplecarriersPremiumeconomy_24',
        'SpiceJet': 'Airline_SpiceJet_25',
        'Trujet': 'Airline_Trujet_26',
        'Vistara': 'Airline_Vistara_27',
        'VistaraPremiumeconomy': 'Airline_VistaraPremiumeconomy_28',
    },
    'source': {
        'Banglore': 'Source_Banglore_29',
        'Chennai': 'Source_Chennai_30',
        'Delhi': 'Source_Delhi_31',
        'Kolkata': 'Source_Kolkata_32',
        'Mumbai': 'Source_Mumbai_33',
    },
    'destination': {
        'Banglore': 'Destination_Banglore_34',
        'Cochin': 'Destination_Cochin_35',
        'Delhi': 'Destination_Delhi_36',
        'Hyderabad': 'Destination_Hyderabad_37',
        'Kolkata': 'Destination_Kolkata_38',
        'NewDelhi': 'Destination_NewDelhi_39',
    },
    'class': {
        'Business': 'Class_Business_634',
        'Economy': 'Class_Economy_635',
        'PremiumEconomy': 'Class_PremiumEconomy_636',
    },
    'booking': {
        'Ecocnomy': 'Booking_Class_Ecocnomy_640',
        'Economy': 'Booking_Class_Economy_641',
        'PremiumEconomy': 'Booking_Class_PremiumEconomy_642',
    },
    'info': {
        '1Longlayover': 'Additional_Info_1Longlayover_624',
        '1Shortlayover': 'Additional_Info_1Shortlayover_625',
        '2Longlayover': 'Additional_Info_2Longlayover_626',
        'Businessclass': 'Additional_Info_Businessclass_627',
        'Changeairports': 'Additional_Info_Changeairports_628',
        'Inflightmealnotincluded': 'Additional_Info_Inflightmealnotincluded_629',
        'NoInfo': 'Additional_Info_NoInfo_630',
        'Nocheckinbaggageincluded': 'Additional_Info_Nocheckinbaggageincluded_631',
        'Noinfo': 'Additional_Info_Noinfo_632',
        'Redeyeflight': 'Additional_Info_Redeyeflight_633',
    },
    'travel': {
        '0days000000': 'Same_day_travel_0days000000_637',
        '1days000000': 'Same_day_travel_1days000000_638',
        '2days000000': 'Same_day_travel_2days000000_639',
    }
}

# ── Input validation ───────────────────────────────────────────────────────────
VALID_AIRLINES = list(COLUMN_MAPPING['airline'].keys())
VALID_SOURCES = list(COLUMN_MAPPING['source'].keys())
VALID_DESTINATIONS = list(COLUMN_MAPPING['destination'].keys())

def validate_input(dep_dt, arr_dt, total_stops, airline, source, destination):
    """Validate user inputs and return error message if invalid."""
    errors = []
    
    # Date validation
    if arr_dt <= dep_dt:
        errors.append("Arrival time must be after departure time")
    
    if dep_dt < datetime.now() - timedelta(days=1):
        errors.append("Departure time cannot be in the past")
    
    if (arr_dt - dep_dt).days > 7:
        errors.append("Flight duration cannot exceed 7 days")
    
    # Route validation
    if source == destination:
        errors.append("Source and destination cannot be the same")
    
    # Airline validation
    sanitized_airline = airline.replace(' ', '').replace('&', '').replace('-', '')
    if sanitized_airline not in VALID_AIRLINES:
        errors.append(f"Invalid airline: {airline}")
    
    # Location validation
    if source not in VALID_SOURCES:
        errors.append(f"Invalid source: {source}")
    
    if destination not in VALID_DESTINATIONS:
        errors.append(f"Invalid destination: {destination}")
    
    # Stops validation
    if not isinstance(total_stops, int) or total_stops < 0 or total_stops > 4:
        errors.append("Number of stops must be between 0 and 4")
    
    return errors

# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_stops(raw: str) -> int:
    """Convert stop string / integer to int."""
    if isinstance(raw, str):
        mapping = {"non-stop": 0, "1 stop": 1, "2 stops": 2, "3 stops": 3, "4 stops": 4}
        return mapping.get(raw.strip().lower(), int(''.join(filter(str.isdigit, raw)) or 0))
    return int(raw)

def get_class(airline: str) -> str:
    """Replicate the notebook's Class derivation from airline name."""
    upper = airline.upper()
    if "BUSINESS" in upper:
        return "Business"
    if "PREMIUM" in upper:
        return "Premium Economy"
    return "Economy"

BOOKING_CLASS_MAP = {
    "IndiGo":                            "Economy",
    "GoAir":                             "Economy",
    "Vistara":                           "Economy",
    "Air Asia":                          "Economy",
    "Vistara Premium economy":           "Premium Economy",
    "Trujet":                            "Economy",
    "Jet Airways":                       "Ecocnomy",   # intentional typo – matches training data
    "SpiceJet":                          "Economy",
    "Jet Airways Business":              "Business",
    "Air India":                         "Economy",
    "Multiple carriers":                 "Economy",
    "Multiple carriers Premium economy": "Premium Economy",
}

def build_row_optimized(dep_dt, arr_dt, total_stops, airline, source, destination,
                        additional_info="No info", route=None) -> pd.DataFrame:
    """
    Optimized version of build_row with better error handling and performance.
    """
    try:
        # Duration in minutes
        duration_min = int((arr_dt - dep_dt).total_seconds() / 60)

        # Date calculations
        date_of_journey  = dep_dt.date()
        date_of_arrival  = arr_dt.date()

        # Time parts
        dep_hour  = dep_dt.hour
        dep_min   = dep_dt.minute
        arr_hour  = arr_dt.hour
        arr_min   = arr_dt.minute

        # Weekday
        weekday_journey  = dep_dt.weekday()
        weekday_arrival  = arr_dt.weekday()

        # Year/month/day
        year             = dep_dt.year
        month_journey    = dep_dt.month
        month_arrival    = arr_dt.month
        day_arrival      = arr_dt.day
        day_journey      = dep_dt.day

        # Same-day travel
        delta_days       = (date_of_arrival - date_of_journey).days
        same_day_travel  = f"{delta_days} days 00:00:00"

        # Class & Booking Class
        flight_class     = get_class(airline)
        booking_class    = BOOKING_CLASS_MAP.get(airline, "Economy")

        # Default route
        if route is None:
            src_codes  = {"Delhi": "DEL", "Mumbai": "BOM", "Kolkata": "CCU",
                          "Chennai": "MAA", "Banglore": "BLR"}
            dst_codes  = {"Cochin": "COK", "Delhi": "DEL", "Hyderabad": "HYD",
                          "Kolkata": "CCU", "New Delhi": "DEL", "New_Delhi": "DEL",
                          "Banglore": "BLR"}
            s = src_codes.get(source, source[:3].upper())
            d = dst_codes.get(destination, destination[:3].upper())
            route = f"{s} → {d}" if total_stops == 0 else f"{s} → ??? → {d}"

        # Build raw row
        raw = pd.DataFrame([{
            "Airline":          airline,
            "Source":           source,
            "Destination":      destination,
            "Route":            route,
            "Duration":         float(duration_min),
            "Total_Stops":      float(total_stops),
            "Additional_Info":  additional_info,
            "Depart_Time_Hour": float(dep_hour),
            "Depart_Time_Minutes": float(dep_min),
            "Arr_Time_Hour":    float(arr_hour),
            "Arr_Time_Minutes": float(arr_min),
            "weekday_journey":  float(weekday_journey),
            "weekday_arrival":  float(weekday_arrival),
            "Year":             float(year),
            "month_of_journey": float(month_journey),
            "month_of_Arrival": float(month_arrival),
            "day_of_Arrival":   float(day_arrival),
            "day_of_Journey":   float(day_journey),
            "Class":            flight_class,
            "Booking_Class":    booking_class,
            "Same_day_travel":  same_day_travel,
        }])

        # BoxCox transformation
        numeric_cols = ["Duration", "Total_Stops", "Depart_Time_Hour",
                        "Depart_Time_Minutes", "Arr_Time_Hour", "Arr_Time_Minutes",
                        "weekday_journey", "weekday_arrival", "Year",
                        "month_of_journey", "month_of_Arrival",
                        "day_of_Arrival", "day_of_Journey"]

        for col in numeric_cols:
            val = raw[col].iloc[0]
            try:
                lam = boxcox_normmax(np.array([val + 1e-6, val + 1]))
                raw[col] = boxcox1p(raw[col], lam)
            except Exception:
                pass   # if boxcox fails (e.g. constant), leave as-is

        # One-hot encode
        raw = raw.drop(columns=["Dep_Time", "Arrival_Time"], errors="ignore")
        dummies = pd.get_dummies(raw)

        # Sanitize column names
        dummies.columns = dummies.columns.str.replace('[^A-Za-z0-9_]+', '', regex=True)

        # Create final DataFrame with correct column names
        final_data = pd.DataFrame(0, index=[0], columns=columns)
        
        # Map each feature to the correct training column
        for col in dummies.columns:
            value = dummies[col].iloc[0]
            
            # Try to map to training columns
            if col in COLUMN_MAPPING['numeric']:
                final_data[COLUMN_MAPPING['numeric'][col]] = value
            elif col in COLUMN_MAPPING['airline']:
                final_data[COLUMN_MAPPING['airline'][col]] = value
            elif col in COLUMN_MAPPING['source']:
                final_data[COLUMN_MAPPING['source'][col]] = value
            elif col in COLUMN_MAPPING['destination']:
                final_data[COLUMN_MAPPING['destination'][col]] = value
            elif col in COLUMN_MAPPING['class']:
                final_data[COLUMN_MAPPING['class'][col]] = value
            elif col in COLUMN_MAPPING['booking']:
                final_data[COLUMN_MAPPING['booking'][col]] = value
            elif col in COLUMN_MAPPING['info']:
                final_data[COLUMN_MAPPING['info'][col]] = value
            elif col in COLUMN_MAPPING['travel']:
                final_data[COLUMN_MAPPING['travel'][col]] = value
            else:
                # Try to find partial matches for route columns
                for training_col in columns:
                    if 'Route_' in training_col and col.replace('→', '').replace(' ', '') in training_col:
                        final_data[training_col] = value
                        break

        return final_data
        
    except Exception as e:
        logger.error(f"Error in build_row_optimized: {e}")
        raise ValueError(f"Feature engineering failed: {str(e)}")

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/predict", methods=["POST"])
def predict():
    start_time = time.time()
    
    try:
        # Parse form inputs
        dep_dt = pd.to_datetime(request.form["Dep_Time"])
        arr_dt = pd.to_datetime(request.form["Arrival_Time"])
        total_stops = parse_stops(request.form["stops"])
        airline = request.form["airline"]
        source = request.form["Source"]
        destination = request.form["Destination"]
        
        # Validate inputs
        validation_errors = validate_input(dep_dt, arr_dt, total_stops, airline, source, destination)
        if validation_errors:
            return render_template("home.html", 
                                   prediction_text=f"⚠️ {'; '.join(validation_errors)}")
        
        # Build feature row
        input_data = build_row_optimized(dep_dt, arr_dt, total_stops, airline, source, destination)
        
        # Predict
        prediction = model.predict(input_data)[0]
        output = round(float(prediction), 2)
        
        # Performance logging
        prediction_time = (time.time() - start_time) * 1000
        logger.info(f"Prediction completed in {prediction_time:.2f}ms: ₹{output:,.0f}")
        
        return render_template("home.html",
                               prediction_text=f"₹ {output:,.0f}")

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return render_template("home.html",
                               prediction_text=f"Error: {str(e)}")

@app.route("/api/predict", methods=["POST"])
def api_predict():
    """API endpoint for programmatic access"""
    try:
        data = request.get_json()
        
        # Parse inputs
        dep_dt = pd.to_datetime(data["Dep_Time"])
        arr_dt = pd.to_datetime(data["Arrival_Time"])
        total_stops = parse_stops(data["stops"])
        airline = data["airline"]
        source = data["Source"]
        destination = data["Destination"]
        
        # Validate inputs
        validation_errors = validate_input(dep_dt, arr_dt, total_stops, airline, source, destination)
        if validation_errors:
            return jsonify({"error": validation_errors}), 400
        
        # Build feature row and predict
        input_data = build_row_optimized(dep_dt, arr_dt, total_stops, airline, source, destination)
        prediction = model.predict(input_data)[0]
        output = round(float(prediction), 2)
        
        return jsonify({
            "prediction": output,
            "formatted": f"₹ {output:,.0f}",
            "currency": "INR"
        })
        
    except Exception as e:
        logger.error(f"API prediction error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model": type(model).__name__,
        "features": len(columns),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
