import pandas as pd
import numpy as np
import joblib  # For saving the scaler
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

# 1. Load the dataset
file_path = "F:/FYP project/FYP(Flood)/Real Data/Flood_fyp_data.csv"  # Update the path as needed
data = pd.read_csv(file_path)

# 2. Handle missing values (forward fill or interpolation)
data.fillna(method='ffill', inplace=True)

# Drop non-numeric columns if they exist (like Date and Hour)
data.drop(columns=['Date', 'Hour'], errors='ignore', inplace=True)

# 3. Define input (X) and targets (y) for 3-hour predictions
X = data[['Discharge Rate (cumecs)', 'Rainfall Data (mm)', 'Water Level (m)']].values
y = data[['Next 1 Hour Water Level (m)', 
          'Next 2 Hours Water Level (m)', 
          'Next 3 Hours Water Level (m)']].values

# 4. Scale input features to [0,1]
scaler_X = MinMaxScaler()
X_scaled = scaler_X.fit_transform(X)

# Save the scaler for future use
joblib.dump(scaler_X, "scaler_X.pkl")

# 5. Reshape input for LSTM: (samples, time_steps=1, features=3)
X_scaled = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))

# 6. Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

# 7. Build LSTM model
model = Sequential([
    LSTM(64, return_sequences=False, input_shape=(1, X_train.shape[2])),
    Dropout(0.2),
    Dense(64, activation='relu'),
    Dropout(0.2),
    Dense(3)  # Output = [Next 1 Hour, Next 2 Hours, Next 3 Hours]
])

model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
print(model.summary())

# 8. Train the model
model.fit(X_train, y_train, 
          epochs=50, 
          batch_size=32, 
          validation_data=(X_test, y_test), 
          verbose=1)

# 9. Save the trained model
model.save("flood_model.h5")
print("Model training completed and saved as flood_model.h5.")
