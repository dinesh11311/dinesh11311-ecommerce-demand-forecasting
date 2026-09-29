# E-Commerce Product Demand Forecasting and Inventory Optimization System

An end-to-end Machine Learning web application designed to help e-commerce businesses forecast product demand, analyze sales trends, prevent stockouts, and optimize inventory reorder points.

## Architecture

User Interface (HTML5, Bootstrap 5, Chart.js)
       │
       ▼
Flask Backend REST API (app.py)
       │
       ├── Preprocessing & Feature Engineering Module
       ├── Machine Learning & Time-Series Engine (Scikit-Learn, XGBoost, SARIMA)
       ├── Inventory Optimization Calculator
       │
       ▼
SQLite Database Persistence (database.db)

## Tech Stack
- **Backend:** Python 3.11+, Flask 3.0
- **Data Science / ML:** Pandas, NumPy, Scikit-learn, XGBoost, Statsmodels, Joblib
- **Frontend:** Bootstrap 5, HTML5, CSS3, JavaScript (ES6), Chart.js
- **Database:** SQLite

## Installation & Setup Instructions

1. **Clone the Repository & Navigate to Directory:**
   ```bash
   git clone https://github.com/your-username/ecommerce-demand-forecasting.git
   cd ecommerce-demand-forecasting
   ```

2. **Create & Activate a Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Pytest Unit Tests:**
   ```bash
   pytest
   ```

5. **Start the Flask Application:**
   ```bash
   python app.py
   ```
   Open `http://127.0.0.1:5000` in your web browser.
