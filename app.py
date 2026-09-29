import os
import pandas as pd
from flask import Flask, render_template, request, jsonify
from config import Config
from src.database import init_db, save_sales_data_to_db, load_sales_data_from_db
from src.preprocessing import validate_csv, preprocess_data, get_preprocessing_stats
from src.feature_engineering import create_time_series_features
from src.train_model import train_and_compare_models
from src.forecasting import forecast_demand
from src.inventory import calculate_inventory_metrics, classify_demand_level

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database schema
init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/analysis')
def analysis_page():
    return render_template('analysis.html')

@app.route('/training')
def training_page():
    return render_template('training.html')

@app.route('/forecast')
def forecast_page():
    return render_template('forecast.html')

@app.route('/inventory')
def inventory_page():
    return render_template('inventory.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

# REST API Endpoints
@app.route('/api/upload', methods=['POST'])
def api_upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file and file.filename.endswith('.csv'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_dataset.csv')
        file.save(file_path)

        raw_df = pd.read_csv(file_path)
        is_valid, msg = validate_csv(raw_df)
        if not is_valid:
            return jsonify({"error": msg}), 400

        cleaned_df = preprocess_data(raw_df)
        save_sales_data_to_db(cleaned_df)

        stats = get_preprocessing_stats(raw_df, cleaned_df)
        preview = cleaned_df.head(10).to_dict(orient='records')

        return jsonify({
            "message": "File uploaded and processed successfully",
            "stats": stats,
            "preview": preview
        }), 200

    return jsonify({"error": "Invalid file format. Please upload a CSV file."}), 400

@app.route('/api/data-summary', methods=['GET'])
def api_data_summary():
    df = load_sales_data_from_db()
    if df.empty:
        return jsonify({"error": "No dataset uploaded yet."}), 404

    top_products = df.groupby('Product Name')['Total Sales'].sum().nlargest(10).to_dict()
    bottom_products = df.groupby('Product Name')['Total Sales'].sum().nsmallest(10).to_dict()
    category_sales = df.groupby('Category')['Total Sales'].sum().to_dict()
    region_sales = df.groupby('Region')['Total Sales'].sum().to_dict()
    profit_category = df.groupby('Category')['Profit'].sum().to_dict()
    monthly_sales = df.groupby(df['Order Date'].dt.strftime('%Y-%m'))['Total Sales'].sum().to_dict()

    return jsonify({
        "summary": {
            "total_orders": int(df['Order ID'].nunique()),
            "total_products": int(df['Product ID'].nunique()),
            "total_revenue": round(float(df['Total Sales'].sum()), 2),
            "total_quantity": int(df['Quantity'].sum()),
            "avg_order_value": round(float(df['Total Sales'].mean()), 2),
            "highest_selling_product": str(df.groupby('Product Name')['Quantity'].sum().idxmax())
        },
        "charts": {
            "top_products": top_products,
            "bottom_products": bottom_products,
            "category_sales": category_sales,
            "region_sales": region_sales,
            "profit_category": profit_category,
            "monthly_sales": monthly_sales
        }
    })

@app.route('/api/products', methods=['GET'])
def api_products():
    df = load_sales_data_from_db()
    if df.empty:
        return jsonify([])
    products = df[['Product ID', 'Product Name', 'Category']].drop_duplicates().to_dict(orient='records')
    return jsonify(products)

@app.route('/api/categories', methods=['GET'])
def api_categories():
    df = load_sales_data_from_db()
    if df.empty:
        return jsonify([])
    categories = df['Category'].unique().tolist()
    return jsonify(categories)

@app.route('/api/train', methods=['POST'])
def api_train():
    df = load_sales_data_from_db()
    if df.empty:
        return jsonify({"error": "No dataset found for training."}), 404

    try:
        df_features = create_time_series_features(df)
        results = train_and_compare_models(df_features)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Training failed: {e}"}), 500

    return jsonify(results)

@app.route('/api/forecast', methods=['POST'])
def api_forecast():
    data = request.get_json(silent=True) or {}
    product_id = data.get('product_id')
    category = data.get('category')
    try:
        forecast_days = int(data.get('forecast_days', 30))
    except (TypeError, ValueError):
        forecast_days = 30
    forecast_days = max(1, min(forecast_days, 365))

    df = load_sales_data_from_db()
    if df.empty:
        return jsonify({"error": "No dataset uploaded."}), 404

    result = forecast_demand(df, product_id=product_id, category=category, forecast_days=forecast_days)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)

def _safe_int(value, default):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default

@app.route('/api/inventory', methods=['POST'])
def api_inventory():
    data = request.get_json(silent=True) or {}
    product_id = data.get('product_id')
    lead_time = _safe_int(data.get('lead_time', 7), 7)
    safety_days = _safe_int(data.get('safety_days', 5), 5)
    current_stock = _safe_int(data.get('current_stock', 50), 50)

    df = load_sales_data_from_db()
    if df.empty:
        return jsonify({"error": "No dataset uploaded."}), 404

    if product_id:
        prod_df = df[df['Product ID'] == product_id]
    else:
        prod_df = df

    if prod_df.empty:
        return jsonify({"error": "Product not found."}), 404

    daily_demand = prod_df.groupby('Order Date')['Quantity'].sum().mean()
    
    prod_demands = df.groupby('Product ID')['Quantity'].sum()
    p75 = prod_demands.quantile(0.75)
    p25 = prod_demands.quantile(0.25)
    total_prod_qty = prod_df['Quantity'].sum()
    
    demand_cat = classify_demand_level(total_prod_qty, p75, p25)
    
    metrics = calculate_inventory_metrics(
        avg_daily_demand=daily_demand,
        lead_time_days=lead_time,
        safety_stock_days=safety_days,
        current_stock=current_stock
    )
    metrics["demand_category"] = demand_cat

    return jsonify(metrics)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
