from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
from tensorflow.keras.models import load_model

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Load trained LSTM model and scaler
model = load_model("flood_model.h5")
scaler_X = joblib.load("scaler_X.pkl")

# Function to generate flood alert message
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

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Extract data from request
        data = request.json
        print("Received Data:", data)

        # Parse input values
        discharge_rate = float(data['discharge_rate'])
        rainfall = float(data['rainfall'])
        water_level = float(data['water_level'])

        # Normalize input using the saved scaler
        input_features = np.array([[discharge_rate, rainfall, water_level]])
        input_scaled = scaler_X.transform(input_features)

        # Reshape to (samples=1, time_steps=1, features=3)
        input_reshaped = input_scaled.reshape((1, 1, input_scaled.shape[1]))

        # Predict water levels
        prediction = model.predict(input_reshaped)[0].tolist()

        # Generate alert messages for each predicted water level
        alerts = [generate_alert_message(pred) for pred in prediction]

        # Return predictions along with alert messages
        return jsonify({
            "Next 1 Hour Water Level": prediction[0],
            "Next 2 Hours Water Level": prediction[1],
            "Next 3 Hours Water Level": prediction[2],
            "Alert 1": alerts[0],
            "Alert 2": alerts[1],
            "Alert 3": alerts[2]
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
