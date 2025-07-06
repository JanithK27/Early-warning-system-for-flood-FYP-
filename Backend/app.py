from flask import Flask, request, jsonify, session, redirect, send_from_directory, url_for, render_template
from flask_cors import CORS
import os
import numpy as np
import joblib
from tensorflow.keras.models import load_model
import requests


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
    return send_from_directory(os.path.join(app.root_path, "Frontend", "HTML"), "welcome.html")

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
    location = data.get("location")
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
        'location': location,
        'password': password
    }

    # Log the user in (store email in session)
    session["email"] = email
    # Redirect to index.html (dashboard)
    return redirect("/index.html")

@app.route("/SignUp.html")
def signup_page():
    """Serves the SignUp.html page via GET."""
    return send_from_directory(os.path.join(app.root_path, "Frontend", "HTML"), "SignUp.html")

# ----------------------------------------------------------------
# (E) Sign In
# ----------------------------------------------------------------
@app.route("/signin", methods=["POST"])
def signin():
    """
    Expects JSON from SignIn.html fetch: { email, password }
    If valid => session['email'] = email => front-end then goes to index.html.
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No JSON in request."})

    email = data.get("email")
    password = data.get("password")

    user = USERS.get(email)
    if user and user["password"] == password:
        session["email"] = email
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Invalid credentials."})

@app.route("/SignIn.html")
def signin_page():
    return send_from_directory(os.path.join(app.root_path, "Frontend", "HTML"), "SignIn.html")


@app.route("/Frontend/HTML/index.html")
def redirect_legacy_index():
    return redirect("/index.html")



# ----------------------------------------------------------------
# (F) Google Sign-In (DEMO)
# ----------------------------------------------------------------
@app.route("/google_signin", methods=["POST"])
def google_signin():
    """
    Suppose your front-end calls /google_signin with { email } from Google.
    If email in USERS => log in => success
    Else => fail
    """
    data = request.get_json()
    google_email = data.get("email")
    if google_email in USERS:
        session["email"] = google_email
        return {"success": True}
    return {"success": False, "message": "User not registered."}

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

# ----------------------------------------------------------------
# (G) Dashboard (index.html)
# ----------------------------------------------------------------
@app.route("/index.html", methods=["GET", "POST"])
def dashboard():
    if "email" not in session:
        return redirect("/Frontend/HTML/welcome.html")

    discharge = rainfall = waterlevel = None
    predictions = None
    alerts = None
    # Get live data from API
    try:
        live_data = get_latest_water_level("I97")
        waterlevel = live_data["level"]
        alert = live_data["alert"] 
        alert_desc = live_data["alert_description"]
        location = live_data["location"]
        recorded_time = live_data["time"]
        #discharge =  ((10.034 *(live_data["level"])**2) - (90.809*live_data["level"]) + 419.1)
        discharge = ((0.1864 * (live_data["level"])**3) + (1.4103 * (live_data["level"])**2) + (15.63 * live_data["level"]) + 8.2621) #use all data to create equation
        rainfall = (live_data["level"] * 5)
        
        discharge_rate = float(request.form.get("discharge"))
        rainfall = float(request.form.get("rainfall"))
        water_level = float(request.form.get("waterlevel"))
        print("Received Data:", discharge_rate, rainfall, water_level)
        
        # Replace with actual prediction logic
        input_features = np.array([[discharge_rate, rainfall, water_level]])
        input_scaled = scaler_X.transform(input_features)
        # Reshape to (samples=1, time_steps=1, features=3)
        input_reshaped = input_scaled.reshape((1, 1, input_scaled.shape[1]))
        # Predict water levels
        predictions = model.predict(input_reshaped)[0].tolist()
        alerts = [generate_alert_message(p) for p in predictions]
        
    except Exception as e:
        print("Error fetching live water level:", e)
        live_data = None
        alert = alert_desc = location = recorded_time = None

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
# def dashboard():
#     if "email" not in session:
#         return redirect("/Frontend/HTML/welcome.html")

#     # Always define these variables before the POST block
#     discharge_rate = None
#     rainfall = None
#     water_level = None
#     predictions = None
#     alerts = None
    

#     if request.method == "POST":
#         try:
#             live_data = get_latest_water_level("I97")
#             waterlevel = live_data["level"]
#             alert = live_data["alert"]
#             alert_desc = live_data["alert_description"]
#             location = live_data["location"]
#             recorded_time = live_data["time"]
#             discharge_rate = float(request.form.get("discharge"))
#             rainfall = float(request.form.get("rainfall"))
#             water_level = float(request.form.get("waterlevel"))

#             print("Received Data:", discharge_rate, rainfall, water_level)

#             # Replace with actual prediction logic
#             input_features = np.array([[discharge_rate, rainfall, water_level]])
#             input_scaled = scaler_X.transform(input_features)

#             # Reshape to (samples=1, time_steps=1, features=3)
#             input_reshaped = input_scaled.reshape((1, 1, input_scaled.shape[1]))

#             # Predict water levels
#             predictions = model.predict(input_reshaped)[0].tolist()
#             alerts = [generate_alert_message(p) for p in predictions]

#         except Exception as e:
#             print("Error fetching live water level:", e)
#             live_data = None
#             alert = alert_desc = location = recorded_time = None

#     # return render_template("index.html",
#     #                        discharge=discharge_rate,
#     #                        rainfall=rainfall,
#     #                        waterlevel=water_level,
#     #                        predictions=predictions,
#     #                        alerts=alerts)
    
#     return render_template("index.html",
#                            discharge=discharge_rate,
#                            rainfall=rainfall,
#                            waterlevel=water_level,
#                            alert_desc=alert_desc,
#                            location=location,
#                            recorded_time=recorded_time,
#                            predictions=predictions,
#                            alerts=alerts)

# ----------------------------------------------------------------
# (H) Logout
# ----------------------------------------------------------------
@app.route("/logout")
def logout():
    """
    Clears session, returns user to welcome page.
    """
    session.clear()
    return redirect("/Frontend/HTML/welcome.html")

if __name__ == "__main__":
    app.run(debug=True)
