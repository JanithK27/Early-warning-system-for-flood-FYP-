# Function to generate alert message based on water level
def generate_alert_message(water_level):
    if water_level >= 5:
        return "Critical Flood Alert: Immediate evacuation recommended!"
    elif water_level >= 4.5:
        return "Major Flood Alert: Severe flooding expected. Prepare for evacuation."
    elif water_level >= 4:
        return "Minor Flood Alert: Flooding expected. Stay alert and monitor updates."
    elif water_level >= 3.5:
        return "Flood Alert: Flood is likely to occur. Take necessary precautions!"
    else:
        return "No immediate flood threat detected."

# Example predicted water level
predicted_water_level = 3.6  # Example predicted water level

# Generate alert message based on predicted water level
alert_message = generate_alert_message(predicted_water_level)

# Function to write message to a file
def write_message(message, filename='message.txt'):
    with open(filename, 'w') as file:
        file.write(message)

if __name__ == "__main__":
    message = f'Predicted Water Level: {predicted_water_level}m - {alert_message}'
    write_message(message)
    #print(f"Message '{message}' written to file.")