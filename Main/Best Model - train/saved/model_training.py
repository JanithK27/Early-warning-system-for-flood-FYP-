import pandas as pd
import numpy as np
import joblib  # For saving the scaler
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

#  Load the dataset
file_path = "F:/FYP project/FYP(Flood)/Real Data/Flood_fyp_data.csv"  # Update the path as needed
data = pd.read_csv(file_path)

#  Handle missing values (forward fill or interpolation)
data.fillna(method='ffill', inplace=True)

# Drop non-numeric columns if they exist (like Date and Hour)
data.drop(columns=['Date', 'Hour'], errors='ignore', inplace=True)

# Define input (X) and targets (y) for 3-hour predictions
X = data[['Discharge Rate (cumecs)', 'Rainfall Data (mm)', 'Water Level (m)']].values
y = data[['Next 1 Hour Water Level (m)', 
          'Next 2 Hours Water Level (m)', 
          'Next 3 Hours Water Level (m)']].values

# Scale input features to [0,1]
scaler_X = MinMaxScaler()
X_scaled = scaler_X.fit_transform(X)

# Save the scaler for future use
joblib.dump(scaler_X, "scaler_X.pkl")

# Reshape the data to be 3D for LSTM input: (samples, time_steps=1, features=3)
X_scaled = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))  # 3D shape for LSTM (number of rows,time steps,number of input features)

# Split dataset into training (70%), validation (15%), and testing (15%)
X_train, X_temp, y_train, y_temp = train_test_split(X_scaled, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

# Initialize the LSTM model
model = Sequential()

# LSTM layers
model.add(LSTM(units=64, return_sequences=False, input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(Dense(units=64, activation='relu'))
model.add(Dense(units=3))  

model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
print(model.summary())

# 8. Train the model
model.fit(X_train, y_train, 
          epochs=50, 
          batch_size=32, 
          validation_data=(X_val, y_val), 
          verbose=1)

# 9. Save the trained model
model.save("flood_model.h5")
print("Model training completed and saved as flood_model.h5.")
