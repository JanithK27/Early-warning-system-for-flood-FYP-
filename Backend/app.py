from flask import Flask, request, jsonify, session, redirect, send_from_directory, url_for
from flask_cors import CORS
import os
import numpy as np
import joblib
from tensorflow.keras.models import load_model

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
        return "🚨 Critical Flood Alert: Immediate evacuation recommended!"
    elif water_level >= 9.5:
        return "⚠️ Major Flood Alert: Severe flooding expected. Prepare for evacuation."
    elif water_level >= 7.5:
        return "🟠 Minor Flood Alert: Flooding expected. Stay alert and monitor updates."
    elif water_level >= 5.2:
        return "🟡 Flood Alert: Flood is likely to occur. Take necessary precautions!"
    else:
        return "✅ No immediate flood threat detected."

# ----------------------------------------------------------------
# (C) Serve Static HTML & CSS
# ----------------------------------------------------------------

@app.route("/Frontend/CSS/<path:filename>")
def serve_css(filename):
    """Serve your CSS files from Frontend/CSS folder."""
    return send_from_directory(os.path.join(app.root_path, "Frontend", "CSS"), filename)

@app.route("/images/<path:filename>")
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

@app.route("/Frontend/HTML/SignUp.html")
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

@app.route("/Frontend/HTML/SignIn.html")
def signin_page():
    """Serves the SignIn.html page."""
    return send_from_directory(os.path.join(app.root_path, "Frontend", "HTML"), "SignIn.html")

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

# ----------------------------------------------------------------
# (G) Dashboard (index.html)
# ----------------------------------------------------------------
@app.route("/index.html")
def dashboard():
    """
    Serve index.html if logged in.
    If not logged in => redirect to welcome.html.
    """
    if "email" not in session:
        return redirect("/Frontend/HTML/welcome.html")
    return send_from_directory(os.path.join(app.root_path), "index.html")

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

# ----------------------------------------------------------------
# (I) Predict (LSTM)
# ----------------------------------------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    """Flood prediction, requires user to be logged in."""
    if "email" not in session:
        return jsonify({"error": "Unauthorized user. Please sign in."}), 401
    try:
        data = request.json
        discharge_rate = float(data['discharge_rate'])
        rainfall = float(data['rainfall'])
        water_level = float(data['water_level'])

        X = np.array([[discharge_rate, rainfall, water_level]])
        X_scaled = scaler_X.transform(X)
        X_reshaped = X_scaled.reshape((1, 1, X_scaled.shape[1]))

        preds = model.predict(X_reshaped)[0].tolist()
        alerts = [generate_alert_message(p) for p in preds]

        return jsonify({
            "Next 1 Hour Water Level": preds[0],
            "Next 2 Hours Water Level": preds[1],
            "Next 3 Hours Water Level": preds[2],
            "Alert 1": alerts[0],
            "Alert 2": alerts[1],
            "Alert 3": alerts[2]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
