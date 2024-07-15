import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.preprocessing import StandardScaler

# Sample historical data for training
data = {
    'water_level': [3.5, 4.2, 5.1, 2.9, 6.0, 7.5, 3.0, 4.0, 5.5, 6.8, 4.5, 5.0, 3.2, 7.0, 5.8, 2.5, 4.7, 6.3, 5.3, 6.2],
    'flood': [0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1]  # 0 = No Flood, 1 = Flood
}

# Create a DataFrame
df = pd.DataFrame(data)

# Features and target variable
X = df[['water_level']]
y = df['flood']

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize the data (for models that require scaling)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Initialize models
models = {
    'Logistic Regression': LogisticRegression(),
    'Random Forest': RandomForestClassifier(),
    'Support Vector Machine': SVC(),
    'Artificial Neural Network': MLPClassifier(max_iter=1000)
}

# Train and evaluate models
accuracies = {}

for model_name, model in models.items():
    # For Linear Regression, we use a different evaluation metric (MSE) due to its nature
    if model_name == 'Linear Regression':
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        accuracies[model_name] = mse
    else:
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        accuracies[model_name] = accuracy

# Display accuracies of all models
#for model_name, accuracy in accuracies.items():
#    if model_name == 'Linear Regression':
#        print(f'{model_name} MSE: {accuracy:.4f}')
#    else:
#       print(f'{model_name} Accuracy: {accuracy * 100:.2f}%')

# Select the best model
best_model_name = max(accuracies, key=accuracies.get)
best_model = models[best_model_name]

#print(f'\nBest Model: {best_model_name}')

# Function to predict flood and provide alert message using the best model
def predict_flood(water_level, model):
    water_level_scaled = scaler.transform([[water_level]])
    prediction = model.predict(water_level_scaled)
    
    if water_level >= 10.5:
        return "Critical Flood Alert: Immediate evacuation recommended!"
    elif water_level >= 9.5:
        return "Major Flood Alert: Severe flooding expected. Prepare for evacuation."
    elif water_level >= 7.5:
        return "Minor Flood Alert: Flooding expected. Stay alert and monitor updates."
    elif water_level >= 5.2:
        return "Flood Alert: Flood is likely to occur. Take necessary precautions!"
    else:
        return "No immediate flood threat detected."

# Example usage with the best model
input_water_level = 6  # Example input
alert_message = predict_flood(input_water_level, best_model)
#print(f'Water Level: {input_water_level}m - {alert_message}')

#message send to user
def write_message(message, filename='message.txt'):
    with open(filename, 'w') as file:
        file.write(message)

if __name__ == "__main__":
    message = (f'Water Level: {input_water_level}m - {alert_message}')
    #message = "Hello from admin.py!"
    write_message(message)
    #print(f"Message '{message}' written to file.")
