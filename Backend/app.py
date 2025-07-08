from flask import Flask, request, jsonify, session, redirect, send_from_directory, url_for, render_template
from flask_cors import CORS
import os
import numpy as np
import joblib
from tensorflow.keras.models import load_model
import requests

import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd

app = Flask(__name__)
app.secret_key = "YOUR_SECRET_KEY"  # Session key
CORS(app)

# ----------------------------------------------------------------
# (A) In-Memory User Store (DEMO ONLY)
# ----------------------------------------------------------------
USERS = {}
"""
Structure:
USERS[email] = {
    'full_name': ...,
    'phone': ...,
    'address': ...,
    'location': ...,
    'password': ...,
}
"""

# ----------------------------------------------------------------
# (B) Load LSTM Model & Scaler
# ----------------------------------------------------------------
model = load_model("flood_model.h5")  # Make sure this file is in your project root
scaler_X = joblib.load("scaler_X.pkl")

def generate_alert_message(water_level):
    if water_level >= 10.5:
        return "🚨 Critical Flood Alert: Leave the area now."
    elif water_level >= 9.5:
        return "⚠️ Major Flood Alert: Be ready to leave soon!"
    elif water_level >= 7.5:
        return "🟠 Minor Flood Alert: Possible flood. Be ready."
    elif water_level >= 5.2:
        return "🟡 Flood Alert: Water rising. Stay alert."
    else:
        return "✅ No flood risk at the moment. Stay safe!." 
    
# ----------------------------------------------------------------
# (C) Serve Static HTML & CSS
# ----------------------------------------------------------------

@app.route("/Frontend/CSS/<path:filename>")
def serve_css(filename):
    """Serve your CSS files from Frontend/CSS folder."""
    return send_from_directory(os.path.join(app.root_path, "Frontend", "CSS"), filename)

@app.route("/Images/<path:filename>")
def serve_images(filename):
    """Serve images if needed from some images/ folder."""
    return send_from_directory(os.path.join(app.root_path, "Frontend", "HTML", "Images"), filename)

# Serve welcome.html as the root
@app.route("/")
def home():
    discharge = rainfall = waterlevel = None
    predictions = None
    alerts = None
    alerts = []
    # Get live data from API
    try:
        live_data = get_latest_water_level("I97")
        # live_data =  {'unit_id': 'I97', 'level': 0.72, 'location': 'Kalu Ganga (Ratnapura)', 'time': '2025-07-08 17:18:00', 'alert': 0, 'alert_description': 'No Alert', 'coords': {'latitude': 6.6792149, 'longitude': 80.3972954}}

        # print("Live Data:", live_data) 
        waterlevel = live_data["level"]
        alert = live_data["alert"] 
        alert_desc = live_data["alert_description"]
        location = live_data["location"]
        recorded_time = live_data["time"]
        #discharge =  ((10.034 *(live_data["level"])**2) - (90.809*live_data["level"]) + 419.1)
        discharge_eq = ((0.1864 * (waterlevel)**3) + (1.4103 * (waterlevel)**2) + (15.63 * waterlevel) + 8.2621) #use all data to create equation
        discharge = round(discharge_eq, 3)
        
        #Get live rainfall data from Open-Meteo
        weather = get_latest_weather_data()  # Uses the latitude and longitude you set
        if weather["current_rain"] == 0.0:
            rainfall = "0.0"
        else:
            rainfall = weather["current_rain"]
        
        
        
        if request.method == "GET":
            predictions = runModel(discharge, rainfall, waterlevel)
            for pred in predictions:
                alert_message = generate_alert_message(pred)
                alerts.append(alert_message)
       
        
    except Exception as e:
        print("Error fetching live water level:", e) # try and except. 
        live_data = None
        alert = alert_desc = None
    name = session.get("name", "User")
    return render_template("welcome.html",
                           discharge=discharge,
                           rainfall=rainfall,
                           waterlevel=waterlevel,
                           alert=alert,
                           alert_desc=alert_desc,
                           location=location,
                           recorded_time=recorded_time,
                           predictions=predictions,
                           alerts = alerts,
                           name=name

                        ) 


@app.route("/Frontend/HTML/<path:filename>")
def serve_html_files(filename):
    """Serve any HTML from Frontend/HTML folder, e.g. welcome.html, SignIn.html, SignUp.html."""
    return send_from_directory(os.path.join(app.root_path, "Frontend", "HTML"), filename)

# ----------------------------------------------------------------
# (D) Sign Up
# ----------------------------------------------------------------
@app.route("/signup", methods=["POST"])
def signup():
    """
    Handles sign-up form submission from SignUp.html (method="POST", action="/signup").
    Stores new user in USERS, logs them in, redirects to index.html.
    """
    data = request.form
    full_name = data.get("fullName")
    email = data.get("email")
    phone = data.get("phone")
    address = data.get("address")
    #location = data.get("location")
    password = data.get("password")
    confirm_password = data.get("confirmPassword")

    # Basic validation
    if password != confirm_password:
        return "Passwords do not match! <a href='/Frontend/HTML/SignUp.html'>Go Back</a>"
    if email in USERS:
        return "User already exists! <a href='/Frontend/HTML/SignIn.html'>Sign In</a>"

    USERS[email] = {
        'full_name': full_name,
        'phone': phone,
        'address': address,
        #'location': location,
        'password': password
    }

    # Log the user in (store email in session)
    session["email"] = email
    session["name"] = full_name  # Save full name in session
    # Redirect to index.html (dashboard)
    return redirect("/")


# ----------------------------------------------------------------
# (E) Sign In
# ----------------------------------------------------------------
@app.route("/signin", methods=["GET", "POST"])
def signin():
    """
    Handles both GET and POST requests for the sign-in process.
    - GET: Renders the login/signup page.
    - POST: Handles form submission with form data (not JSON).
    """
    if request.method == "GET":
        return render_template("SignIn.html")  # Ensure this template includes both tabs

    # POST: Handle form data
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return "Missing email or password. <a href='/signin'>Go back</a>"

    user = USERS.get(email)
    if user and user["password"] == password:
        session["email"] = email
        session["name"] = user["full_name"]  # Save full name in session

        return redirect("/")
    else:
        return "Invalid credentials. <a href='/signin'>Try again</a>"



## Api call- for live water level

def get_latest_water_level(device_id="I97"):
    # Step 1: Get token
    token_url = "https://www.warisoba.lk/services/api/salford/token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": "9f4cc8e7-ecc4-40d1-9402-acac9c574c72",
        "client_secret": "wIuP4BM4iJVaXjFKBxJcBCZzoOxVxbSLwqYgJL50",
        "scope": "*"
    }
    token_headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    token_response = requests.post(token_url, data=token_data, headers=token_headers)
    token_response.raise_for_status()
    access_token = token_response.json()["access_token"]

    # Step 2: Call level API
    data_url = f"https://www.warisoba.lk/services/api/salford/level/oxfamrg/latest/{device_id}"
    data_headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data_response = requests.get(data_url, headers=data_headers)
    data_response.raise_for_status()
    return data_response.json()["results"]

# Get weather API

def get_latest_weather_data(latitude=6.6858, longitude=80.4036):
    # Setup Open-Meteo client with cache and retry
    
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # API parameters
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "rain"],
        "current": "rain"
    }

    # Call the API
    responses = openmeteo.weather_api(weather_url, params=weather_params)
    response = responses[0]

    # Extract current rain
    current_rain = response.Current().Variables(0).Value()
    
    # Extract hourly data
    hourly = response.Hourly()
    hourly_temperature = hourly.Variables(0).ValuesAsNumpy()
    hourly_rain = hourly.Variables(1).ValuesAsNumpy()
    timestamps = pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )

    # Return as DataFrame
    weather_df = pd.DataFrame({
        "timestamp": timestamps,
        "temperature_2m": hourly_temperature,
        "rain": hourly_rain
    })

    return {
        "current_rain": current_rain,
        "hourly_weather": weather_df
    }


# real time data input the lstm

def runModel(discharge_rate, rainfall_IN, water_level):
    # Replace with actual prediction logic
    input_features = np.array([[discharge_rate, rainfall_IN, water_level]])
    input_scaled = scaler_X.transform(input_features)
        # Reshape to (samples=1, time_steps=1, features=3)
    input_reshaped = input_scaled.reshape((1, 1, input_scaled.shape[1]))
        # Predict water levels
    predictions = model.predict(input_reshaped)[0].tolist()
    
    
    return predictions


@app.route("/index", methods=["GET", "POST"])
def dashboard(): #manual input
    global count
    # if "email" not in session:
    #     return redirect("/Frontend/HTML/welcome.html")

    discharge = rainfall = waterlevel = None
    predictions = None
    alerts = None
    alerts = []
    # Get live data from API
    try:
        live_data = get_latest_water_level("I97")

        # live_data =  {'unit_id': 'I97', 'level': 0.72, 'location': 'Kalu Ganga (Ratnapura)', 'time': '2025-07-08 17:18:00', 'alert': 0, 'alert_description': 'No Alert', 'coords': {'latitude': 6.6792149, 'longitude': 80.3972954}}
        # print("Live Data:", live_data)  # Debug print statement
        waterlevel = live_data["level"]
        alert = live_data["alert"] 
        alert_desc = live_data["alert_description"]
        location = live_data["location"]
        recorded_time = live_data["time"]
        #discharge =  ((10.034 *(live_data["level"])**2) - (90.809*live_data["level"]) + 419.1)
        discharge_eq = ((0.1864 * (waterlevel)**3) + (1.4103 * (waterlevel)**2) + (15.63 * waterlevel) + 8.2621) #use all data to create equation
        discharge = round(discharge_eq, 3)
        
        #Get live rainfall data from Open-Meteo
        weather = get_latest_weather_data()  # Uses the latitude and longitude you set
        if weather["current_rain"] == 0.0:
            rainfall = "0.0"
        else:
            rainfall = weather["current_rain"]
        

        if request.method == "POST":
            print("Received POST request")
            discharge_rate = request.form.get("discharge")
            rainfall_IN = request.form.get("rainfall")
            water_level = request.form.get("waterlevel")
            predictions = runModel(discharge_rate, rainfall_IN, water_level)
            
            for pred in predictions:
                alert_message = generate_alert_message(pred)
                alerts.append(alert_message) 
            
        else:
            print("Received GET request")
            predictions = runModel(discharge, rainfall, waterlevel)
            
            for pred in predictions:
                alert_message = generate_alert_message(pred)
                alerts.append(alert_message) 
        
        # Debug print statements
        #print(f"Discharge Rate: {discharge_rate}")
        #print(f"Rainfall: {rainfall_IN}")
        #print(f"Water Level: {water_level}")
        # print("Received Data:", discharge_rate, rainfall_IN, water_level)    
        
        #predictions = runModel(discharge_rate, rainfall_IN, water_level)
        
        # Generate alerts based on the predictions
        
        
       
        
    except Exception as e:
        print("Error fetching live water level:", e) # try and except. 
        live_data = None
        alert = alert_desc = None

    return render_template("index.html",
                           discharge=discharge,
                           rainfall=rainfall,
                           waterlevel=waterlevel,
                           alert=alert,
                           alert_desc=alert_desc,
                           location=location,
                           recorded_time=recorded_time,
                           predictions=predictions,
                           alerts = alerts
                        ) 




@app.route("/profile")
def profile():
    # Redirect to sign-in page if user is not logged in
    if "email" not in session:
        return redirect(url_for("signin"))

    user_email = session.get("email")
    user = USERS.get(user_email)

    if not user:
        return "User not found", 404

    return render_template("profile.html", user=user, email=user_email)


# ----------------------------------------------------------------
# (H) Logout
# ----------------------------------------------------------------
@app.route("/logout")
def logout():
    """
    Clears session, returns user to welcome page.
    """
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)