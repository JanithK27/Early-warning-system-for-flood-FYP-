# 🌊 FloodGuard - Real-Time Flood Prediction System ⏰⚠️

Welcome to **FloodGuard**, an intelligent early warning system designed to **predict flood levels in the Kalu River Region** (Rathnapura area) using machine learning.  
This system aims to minimize flood-related risks by providing **timely alerts up to 3 hours in advance**! 🛑🏃‍♂️

---

## 🚀 Key Features

✅ Predicts water level for the next **1st, 2nd and 3rd hours**  
✅ Uses real-world data: **Water Level (m), Discharge Rate (cumecs), Rainfall (mm)**  
✅ Built with **LSTM, GRU, and Random Forest Regressor models**  
✅ Web-based UI with **Sign Up / Sign In / Dashboard**  
✅ Displays **alert levels** with appropriate messages  
✅ Supports **real-time prediction** using live APIs 🌐  
✅ Automatic login/session handling with Flask

---

## 🧠 Technologies Used

- 📌 **Frontend:** HTML5, CSS3 (no JavaScript for prediction)
- 🐍 **Backend:** Python + Flask  
- 🧠 **Machine Learning:** TensorFlow (LSTM, GRU), scikit-learn (Random Forest)
- 🧪 **Metrics:** MAE, MAPE, Accuracy
- 🔁 **API Integration:** Real-time rainfall and water level from Open-Meteo & Leecom Data API

---

## 📊 Model Performance

| Model           | 1st Hour Accuracy | 2nd Hour | 3rd Hour |
|----------------|-------------------|----------|----------|
| **LSTM**       | 96.39%            | 93.68%   | 90.58%   |
| **GRU**        | 96.09%            | 93.68%   | 91.03%   |
| **Random Forest** | 95.99%         | 92.63%   | 89.48%   |

---

## 📷 Dashboard Preview

![Dashboard Preview](Frontend/HTML/Images/flood_alert.png)

---

## 🛠️ How to Run Locally

1. 🔽 Clone the repo:
   ```bash
   git clone https://github.com/yourusername/FloodGuard.git
   cd FloodGuard
   ```

2. 🐍 Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. ▶️ Run the Flask server:
   ```bash
   python app.py
   ```

4. 🌐 Visit `http://127.0.0.1:5000` in your browser.

---

## 🔐 User Authentication

- ✅ **Sign Up:** Enter your name, email, phone, address, and password
- 🔑 **Sign In:** Authenticate to access the prediction dashboard
- 🚪 **Logout:** Securely ends the session

---

## ⚠️ API Credentials Notice

To access real-time water level data from the Irrigation Department of Sri Lanka, **you must obtain official permission.**  
The `client_id` and `client_secret` have been removed from `app.py` for privacy and security reasons.  
📩 Please contact the **Sri Lanka Irrigation Department** to get API access.

---

## 🙌 Acknowledgements

- 🏛️ University support  
- 📊 Sri Lanka Irrigation & Meteorology Departments  
- 👨‍🏫 Supervisors and academic mentors  

---

## 🤝 Contributors

- 👨‍💻 H. J. K. Hettiarachchi  
- 👨‍💻 D.M.R.Lakshika 

---

> 📢 _“Stay informed, stay safe – FloodGuard is here to alert you before the storm.”_
