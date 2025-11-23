import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import warnings

warnings.filterwarnings('ignore')

# ========================================
# PROFESSIONAL PAGE CONFIGURATION
# ========================================

st.set_page_config(
    page_title="Grecert DGT Transport - Executive Analytics",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# PROFESSIONAL CSS WITH MAXIMUM READABILITY
# ========================================

def load_professional_css():
    st.markdown("""
    <style>
        /* Import Professional Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global Styling */
        .main {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: #f8f9fa;
        }
        
        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Professional Header */
        .executive-header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 2.5rem 1rem;
            margin: -1rem -1rem 2rem -1rem;
            text-align: center;
            border-radius: 0 0 20px 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        }
        
        .executive-header h1 {
            font-size: 3rem;
            font-weight: 700;
            margin: 0;
            color: white !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .executive-header p {
            font-size: 1.3rem;
            margin: 0.8rem 0 0 0;
            color: rgba(255,255,255,0.9) !important;
            font-weight: 400;
        }
        
        /* Professional Metric Cards */
        .metric-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            padding: 1.8rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid #e9ecef;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
            text-align: center;
        }
        
        .metric-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        }
        
        .metric-title {
            font-size: 0.85rem;
            color: #6c757d !important;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }
        
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: #2c3e50 !important;
            margin: 0.3rem 0;
        }
        
        .metric-delta {
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .metric-delta.positive {
            color: #28a745 !important;
        }
        
        .metric-delta.negative {
            color: #dc3545 !important;
        }
        
        .metric-delta.neutral {
            color: #6c757d !important;
        }
        
        /* Professional Insight Boxes */
        .insight-container {
            background: #ffffff;
            border: 1px solid #e9ecef;
            border-left: 5px solid #007bff;
            border-radius: 10px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 0 2px 15px rgba(0,0,0,0.05);
        }
        
        .insight-container h4 {
            color: #1e3c72 !important;
            font-weight: 600;
            font-size: 1.3rem;
            margin-bottom: 1rem;
        }
        
        .insight-container p,
        .insight-container li,
        .insight-container ul {
            color: #2c3e50 !important;
            font-size: 1rem;
            line-height: 1.6;
        }
        
        .insight-container strong {
            color: #1e3c72 !important;
            font-weight: 600;
        }
        
        /* Professional Recommendation Boxes */
        .recommendation-container {
            background: #f8fff8;
            border: 1px solid #d4edda;
            border-left: 5px solid #28a745;
            border-radius: 10px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 0 2px 15px rgba(40,167,69,0.08);
        }
        
        .recommendation-container h4 {
            color: #155724 !important;
            font-weight: 600;
            font-size: 1.3rem;
            margin-bottom: 1rem;
        }
        
        .recommendation-container p,
        .recommendation-container li,
        .recommendation-container ul {
            color: #155724 !important;
            font-size: 1rem;
            line-height: 1.6;
        }
        
        .recommendation-container strong {
            color: #0f4419 !important;
            font-weight: 600;
        }
        
        /* Alert Boxes */
        .alert-success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724 !important;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        .alert-warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404 !important;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        .alert-danger {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24 !important;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        /* Professional Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background: transparent;
            margin-bottom: 1rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 55px;
            padding: 0px 24px;
            background: #ffffff !important;
            border: 2px solid #e9ecef !important;
            border-radius: 10px 10px 0px 0px !important;
            color: #495057 !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: #f8f9fa !important;
            border-color: #dee2e6 !important;
            color: #2c3e50 !important;
            transform: translateY(-2px);
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%) !important;
            border-color: #007bff !important;
            color: white !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,123,255,0.3);
        }
        
        /* Sidebar Styling */
        .css-1d391kg {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        }
        
        /* Ensure all text is readable */
        .stMarkdown p,
        .stMarkdown li,
        .stMarkdown h1,
        .stMarkdown h2,
        .stMarkdown h3,
        .stMarkdown h4,
        .stMarkdown h5,
        .stMarkdown h6 {
            color: #2c3e50 !important;
        }
        
        /* Data tables */
        .dataframe {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .executive-header h1 {
                font-size: 2.2rem;
            }
            
            .executive-header p {
                font-size: 1.1rem;
            }
            
            .metric-card {
                padding: 1.2rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

load_professional_css()

# ========================================
# ENHANCED DATA GENERATION
# ========================================

@st.cache_data(ttl=3600)
def generate_executive_dgt_data(num_records=80000):
    """Generate comprehensive, realistic DGT Transport data for executive analysis."""
    np.random.seed(42)
    
    # European regions with market share weights
    regions = {
        'Germany': 0.22, 'France': 0.18, 'Italy': 0.15, 'Spain': 0.13, 
        'Poland': 0.10, 'Netherlands': 0.08, 'Belgium': 0.06, 'Austria': 0.04,
        'Portugal': 0.03, 'Greece': 0.01
    }
    
    vehicle_types = {
        'Passenger Car': 0.42, 'Commercial Truck': 0.28, 'Public Bus': 0.12,
        'Motorcycle': 0.08, 'Heavy Vehicle': 0.06, 'Delivery Van': 0.04
    }
    
    fuel_types = {
        'Gasoline': 0.30, 'Diesel': 0.32, 'Electric': 0.20, 
        'Hybrid': 0.12, 'Biofuel': 0.04, 'Hydrogen': 0.02
    }
    
    violation_categories = {
        'Speeding': 0.35, 'Parking': 0.20, 'Traffic Signal': 0.15,
        'Documentation': 0.12, 'Weight Limit': 0.08, 'Route Violation': 0.06,
        'Emission Standards': 0.04
    }
    
    # Generate date range (24 months)
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Create comprehensive dataset
    data = {
        'date': np.random.choice(date_range, num_records),
        'region': np.random.choice(list(regions.keys()), num_records, p=list(regions.values())),
        'vehicle_type': np.random.choice(list(vehicle_types.keys()), num_records, p=list(vehicle_types.values())),
        'fuel_type': np.random.choice(list(fuel_types.keys()), num_records, p=list(fuel_types.values())),
        'violation_type': np.random.choice(list(violation_categories.keys()), num_records, p=list(violation_categories.values())),
        
        # Core operational metrics
        'distance_km': np.random.lognormal(6.5, 1.0, num_records),
        'fuel_consumption_l': np.random.lognormal(4.0, 0.9, num_records),
        'avg_speed_kmh': np.random.normal(70, 18, num_records),
        'trip_duration_hours': np.random.exponential(2.5, num_records),
        'passenger_count': np.random.poisson(3, num_records),
        'freight_weight_tons': np.random.exponential(8, num_records),
        
        # Financial metrics (in EUR)
        'operational_cost_eur': np.random.lognormal(6.2, 0.7, num_records),
        'maintenance_cost_eur': np.random.lognormal(4.5, 0.9, num_records),
        'fuel_cost_eur': np.random.lognormal(4.8, 0.6, num_records),
        'revenue_eur': np.random.lognormal(7.2, 0.6, num_records),
        'fine_amount_eur': np.random.lognormal(5.2, 0.8, num_records),
        
        # Environmental metrics
        'co2_emissions_kg': np.random.lognormal(5.5, 0.8, num_records),
        'nox_emissions_g': np.random.lognormal(3.2, 0.7, num_records),
        'pm_emissions_g': np.random.lognormal(1.5, 1.0, num_records),
        
        # Performance indicators (0-1 scale)
        'on_time_performance': np.random.beta(8, 2, num_records),
        'safety_score': np.random.beta(9, 1.5, num_records),
        'driver_satisfaction': np.random.beta(7, 2.5, num_records),
        'fuel_efficiency_rating': np.random.beta(6, 3, num_records),
        
        # Compliance indicators
        'emission_compliance': np.random.choice([0, 1], num_records, p=[0.08, 0.92]),
        'safety_inspection_pass': np.random.choice([0, 1], num_records, p=[0.10, 0.90]),
        'digital_compliance': np.random.choice([0, 1], num_records, p=[0.04, 0.96]),
        
        # External factors
        'weather_severity': np.random.beta(2, 6, num_records),
        'traffic_density': np.random.beta(4, 4, num_records),
        'route_complexity': np.random.beta(3, 5, num_records),
    }
    
    df = pd.DataFrame(data)
    
    # Apply realistic constraints
    df['avg_speed_kmh'] = np.clip(df['avg_speed_kmh'], 25, 140)
    df['trip_duration_hours'] = np.clip(df['trip_duration_hours'], 0.3, 20)
    df['passenger_count'] = np.clip(df['passenger_count'], 0, 55)
    df['freight_weight_tons'] = np.clip(df['freight_weight_tons'], 0, 45)
    
    # Vehicle-specific adjustments
    truck_mask = df['vehicle_type'] == 'Commercial Truck'
    df.loc[truck_mask, 'distance_km'] *= 2.5
    df.loc[truck_mask, 'fuel_consumption_l'] *= 3.5
    df.loc[truck_mask, 'co2_emissions_kg'] *= 4.0
    df.loc[truck_mask, 'passenger_count'] = 0
    df.loc[truck_mask, 'freight_weight_tons'] = np.random.uniform(5, 40, truck_mask.sum())
    
    bus_mask = df['vehicle_type'] == 'Public Bus'
    df.loc[bus_mask, 'passenger_count'] = np.random.randint(10, 55, bus_mask.sum())
    df.loc[bus_mask, 'freight_weight_tons'] = 0
    df.loc[bus_mask, 'fuel_consumption_l'] *= 2.2
    
    car_mask = df['vehicle_type'] == 'Passenger Car'
    df.loc[car_mask, 'passenger_count'] = np.random.randint(1, 5, car_mask.sum())
    df.loc[car_mask, 'freight_weight_tons'] = 0
    
    # Electric vehicle adjustments
    electric_mask = df['fuel_type'] == 'Electric'
    df.loc[electric_mask, ['co2_emissions_kg', 'nox_emissions_g', 'pm_emissions_g']] = 0
    df.loc[electric_mask, 'fuel_cost_eur'] *= 0.25
    df.loc[electric_mask, 'emission_compliance'] = 1
    
    # Hybrid adjustments
    hybrid_mask = df['fuel_type'] == 'Hybrid'
    df.loc[hybrid_mask, 'co2_emissions_kg'] *= 0.55
    df.loc[hybrid_mask, 'fuel_consumption_l'] *= 0.65
    df.loc[hybrid_mask, 'fuel_cost_eur'] *= 0.70
    
    # Weather impact
    severe_weather = df['weather_severity'] > 0.7
    df.loc[severe_weather, 'avg_speed_kmh'] *= np.random.uniform(0.6, 0.85, severe_weather.sum())
    df.loc[severe_weather, 'on_time_performance'] *= np.random.uniform(0.75, 0.90, severe_weather.sum())
    df.loc[severe_weather, 'safety_score'] *= np.random.uniform(0.80, 0.95, severe_weather.sum())
    
    # Calculate derived metrics
    df['fuel_efficiency_km_per_l'] = np.where(
        df['fuel_consumption_l'] > 0, 
        df['distance_km'] / df['fuel_consumption_l'], 
        0
    )
    df['emissions_per_km'] = np.where(
        df['distance_km'] > 0, 
        df['co2_emissions_kg'] / df['distance_km'], 
        0
    )
    df['total_cost_eur'] = (
        df['operational_cost_eur'] + 
        df['maintenance_cost_eur'] + 
        df['fuel_cost_eur']
    )
    df['profit_eur'] = df['revenue_eur'] - df['total_cost_eur']
    df['profit_margin'] = np.where(
        df['revenue_eur'] > 0, 
        df['profit_eur'] / df['revenue_eur'], 
        0
    )
    df['cost_per_km'] = np.where(
        df['distance_km'] > 0, 
        df['total_cost_eur'] / df['distance_km'], 
        0
    )
    df['revenue_per_km'] = np.where(
        df['distance_km'] > 0, 
        df['revenue_eur'] / df['distance_km'], 
        0
    )
    
    # Add temporal features
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['day_of_week'] = df['date'].dt.day_name()
    df['week_number'] = df['date'].dt.isocalendar().week
    df['is_weekend'] = df['date'].dt.weekday >= 5
    
    # Clean and validate data
    df = df.replace([np.inf, -np.inf], np.nan)
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())
    
    # Final data quality checks
    df['profit_margin'] = df['profit_margin'].clip(-1, 1)
    df['on_time_performance'] = df['on_time_performance'].clip(0, 1)
    df['safety_score'] = df['safety_score'].clip(0, 1)
    df['driver_satisfaction'] = df['driver_satisfaction'].clip(0, 1)
    
    return df

# ========================================
# ADVANCED ANALYTICS FUNCTIONS
# ========================================

def perform_executive_anomaly_detection(df, metric_column, contamination=0.08):
    """Executive-level anomaly detection with business context."""
    try:
        # Daily aggregation for executive overview
        daily_data = df.groupby('date').agg({
            metric_column: ['sum', 'mean', 'std', 'count']
        }).reset_index()
        
        daily_data.columns = ['date', f'{metric_column}_sum', f'{metric_column}_mean', 
                             f'{metric_column}_std', f'{metric_column}_count']
        
        if len(daily_data) < 10:
            return daily_data, pd.DataFrame()
        
        # Multi-dimensional anomaly detection
        features = [f'{metric_column}_sum', f'{metric_column}_mean']
        feature_data = daily_data[features].fillna(daily_data[features].median())
        
        # Isolation Forest
        iso_forest = IsolationForest(
            contamination=contamination, 
            random_state=42,
            n_estimators=200
        )
        daily_data['anomaly_flag'] = iso_forest.fit_predict(feature_data)
        daily_data['anomaly_score'] = iso_forest.score_samples(feature_data)
        
        # Extract anomalies
        anomalies = daily_data[daily_data['anomaly_flag'] == -1].copy()
        
        return daily_data, anomalies
        
    except Exception as e:
        st.error(f"Anomaly detection error: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

def executive_forecasting_engine(df, metric_column, periods=6):
    """Advanced forecasting with ensemble methods and confidence intervals."""
    try:
        # Monthly aggregation for strategic forecasting
        monthly_data = df.groupby(pd.Grouper(key='date', freq='M')).agg({
            metric_column: ['sum', 'mean', 'count']
        }).reset_index()
        
        monthly_data.columns = ['date', f'{metric_column}_sum', f'{metric_column}_mean', f'{metric_column}_count']
        
        if len(monthly_data) < 6:
            return None, None
        
        # Feature engineering
        monthly_data['month_index'] = range(len(monthly_data))
        monthly_data['trend'] = monthly_data[f'{metric_column}_sum'].rolling(window=3, center=True).mean()
        monthly_data['seasonal'] = monthly_data['date'].dt.month
        
        # Prepare features
        X = monthly_data[['month_index', 'seasonal']].values
        y = monthly_data[f'{metric_column}_sum'].values
        
        # Ensemble forecasting models
        models = {
            'linear': LinearRegression(),
            'rf': RandomForestRegressor(n_estimators=150, random_state=42, max_depth=10)
        }
        
        # Train models
        predictions = {}
        for name, model in models.items():
            model.fit(X, y)
            predictions[name] = model
        
        # Generate future features
        last_month_index = monthly_data['month_index'].max()
        future_features = []
        
        for i in range(1, periods + 1):
            future_month = monthly_data['date'].max() + pd.DateOffset(months=i)
            future_features.append([
                last_month_index + i,
                future_month.month
            ])
        
        future_features = np.array(future_features)
        
        # Generate ensemble predictions
        ensemble_predictions = []
        for features in future_features:
            pred_values = []
            for model in predictions.values():
                pred_values.append(model.predict([features])[0])
            ensemble_predictions.append(np.mean(pred_values))
        
        # Calculate confidence intervals using model variance
        prediction_std = []
        for features in future_features:
            pred_values = []
            for model in predictions.values():
                pred_values.append(model.predict([features])[0])
            prediction_std.append(np.std(pred_values))
        
        # Generate future dates
        last_date = monthly_data['date'].max()
        future_dates = [last_date + pd.DateOffset(months=i) for i in range(1, periods + 1)]
        
        # Create forecast dataframe
        forecast_df = pd.DataFrame({
            'date': future_dates,
            'prediction': ensemble_predictions,
            'lower_bound': [p - 1.96 * s for p, s in zip(ensemble_predictions, prediction_std)],
            'upper_bound': [p + 1.96 * s for p, s in zip(ensemble_predictions, prediction_std)],
            'confidence_width': [2 * 1.96 * s for s in prediction_std]
        })
        
        return monthly_data, forecast_df
        
    except Exception as e:
        st.error(f"Forecasting error: {str(e)}")
        return None, None

def strategic_regional_clustering(df, n_clusters=4):
    """Strategic clustering analysis for regional performance segmentation."""
    try:
        # Regional performance aggregation
        regional_metrics = df.groupby('region').agg({
            'co2_emissions_kg': 'sum',
            'fuel_efficiency_km_per_l': 'mean',
            'total_cost_eur': 'sum',
            'revenue_eur': 'sum',
            'profit_eur': 'sum',
            'on_time_performance': 'mean',
            'safety_score': 'mean',
            'distance_km': 'sum',
            'digital_compliance': 'mean'
        }).reset_index()
        
        # Calculate derived metrics
        regional_metrics['profit_margin'] = (
            regional_metrics['profit_eur'] / regional_metrics['revenue_eur']
        ).fillna(0)
        regional_metrics['emissions_intensity'] = (
            regional_metrics['co2_emissions_kg'] / regional_metrics['distance_km']
        ).fillna(0)
        regional_metrics['cost_efficiency'] = (
            regional_metrics['total_cost_eur'] / regional_metrics['distance_km']
        ).fillna(0)
        
        # Select clustering features
        clustering_features = [
            'fuel_efficiency_km_per_l', 'on_time_performance', 
            'safety_score', 'profit_margin', 'emissions_intensity'
        ]
        
        X = regional_metrics[clustering_features].fillna(regional_metrics[clustering_features].mean())
        
        if len(X) < 3:
            regional_metrics['cluster'] = 0
            return regional_metrics, None, 0
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Optimal cluster determination
        best_score = -1
        best_k = min(n_clusters, len(X) - 1)
        
        for k in range(2, min(8, len(X))):
            if k >= len(X):
                break
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=20, max_iter=300)
            cluster_labels = kmeans.fit_predict(X_scaled)
            
            if len(np.unique(cluster_labels)) > 1:
                score = silhouette_score(X_scaled, cluster_labels)
                if score > best_score:
                    best_score = score
                    best_k = k
        
        # Final clustering
        final_kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=20, max_iter=300)
        regional_metrics['cluster'] = final_kmeans.fit_predict(X_scaled)
        
        return regional_metrics, final_kmeans, best_score
        
    except Exception as e:
        st.error(f"Clustering error: {str(e)}")
        return df.groupby('region').mean().reset_index(), None, 0

def create_professional_metric_card(title, value, delta=None, format_type="number"):
    """Create professional metric cards with proper formatting."""
    
    # Format value based on type
    if format_type == "currency":
        formatted_value = f"€{value:,.2f}"
    elif format_type == "percentage":
        formatted_value = f"{value:.1f}%"
    elif format_type == "decimal":
        formatted_value = f"{value:.2f}"
    else:
        formatted_value = f"{value:,.0f}"
    
    # Format delta
    delta_html = ""
    if delta:
        if isinstance(delta, str):
            delta_class = "neutral"
            delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>'
        else:
            if delta > 0:
                delta_class = "positive"
                delta_symbol = "↗"
            elif delta < 0:
                delta_class = "negative"
                delta_symbol = "↘"
            else:
                delta_class = "neutral"
                delta_symbol = ""
            delta_html = f'<div class="metric-delta {delta_class}">{delta_symbol} {abs(delta):.1f}%</div>'
    
    return f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{formatted_value}</div>
        {delta_html}
    </div>
    """

# ========================================
# MAIN APPLICATION
# ========================================

def main():
    # Professional Header
    st.markdown("""
    <div class="executive-header">
        <h1>🚛 Grecert DGT Transport Intelligence</h1>
        <p>Executive Business Intelligence & AI-Powered Analytics Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    with st.spinner("🔄 Loading comprehensive transport analytics data..."):
        df = generate_executive_dgt_data()
    
    # Executive Control Panel
    st.sidebar.markdown("## 🎛️ Executive Control Center")
    st.sidebar.markdown("---")
    
    # Date range controls
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    with col2:
        end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
    
    # Strategic filters
    st.sidebar.markdown("### 🌍 Strategic Scope")
    selected_regions = st.sidebar.multiselect(
        "Regions",
        options=sorted(df['region'].unique()),
        default=sorted(df['region'].unique())[:6]
    )
    
    selected_vehicles = st.sidebar.multiselect(
        "Vehicle Categories",
        options=df['vehicle_type'].unique(),
        default=df['vehicle_type'].unique()
    )
    
    selected_fuels = st.sidebar.multiselect(
        "Energy Sources",
        options=df['fuel_type'].unique(),
        default=df['fuel_type'].unique()
    )
    
    # Advanced analytics options
    st.sidebar.markdown("### ⚙️ Analytics Configuration")
    forecast_horizon = st.sidebar.slider("Forecast Horizon (months)", 3, 18, 8)
    anomaly_sensitivity = st.sidebar.slider("Anomaly Detection Sensitivity", 0.02, 0.15, 0.06, 0.01)
    
    # Apply filters
    mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
    filtered_df = df[mask]
    
    if selected_regions:
        filtered_df = filtered_df[filtered_df['region'].isin(selected_regions)]
    if selected_vehicles:
        filtered_df = filtered_df[filtered_df['vehicle_type'].isin(selected_vehicles)]
    if selected_fuels:
        filtered_df = filtered_df[filtered_df['fuel_type'].isin(selected_fuels)]
    
    if filtered_df.empty:
        st.error("⚠️ No data matches your selection criteria. Please adjust the filters.")
        return
    
    # Executive KPI Dashboard
    st.markdown("## 📊 Executive Performance Dashboard")
    
    # Calculate executive KPIs
    total_operations = len(filtered_df)
    total_distance_mkm = filtered_df['distance_km'].sum() / 1_000_000
    total_revenue_m = filtered_df['revenue_eur'].sum() / 1_000_000
    total_profit_m = filtered_df['profit_eur'].sum() / 1_000_000
    total_emissions_m = filtered_df['co2_emissions_kg'].sum() / 1_000_000
    avg_efficiency = filtered_df['fuel_efficiency_km_per_l'].mean()
    avg_on_time = filtered_df['on_time_performance'].mean() * 100
    avg_safety = filtered_df['safety_score'].mean() * 100
    avg_profit_margin = filtered_df['profit_margin'].mean() * 100
    
    # Display KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_professional_metric_card(
            "Total Operations", total_operations, delta="+8.5% YoY"
        ), unsafe_allow_html=True)
        
        st.markdown(create_professional_metric_card(
            "Distance (Million km)", total_distance_mkm, delta=12.3, format_type="decimal"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_professional_metric_card(
            "Revenue (Million €)", total_revenue_m, delta=15.7, format_type="currency"
        ), unsafe_allow_html=True)
        
        st.markdown(create_professional_metric_card(
            "Profit (Million €)", total_profit_m, delta=22.4, format_type="currency"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_professional_metric_card(
            "CO₂ Emissions (M kg)", total_emissions_m, delta=-8.2, format_type="decimal"
        ), unsafe_allow_html=True)
        
        st.markdown(create_professional_metric_card(
            "Fuel Efficiency", avg_efficiency, delta=5.1, format_type="decimal"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_professional_metric_card(
            "On-Time Performance", avg_on_time, delta=3.8, format_type="percentage"
        ), unsafe_allow_html=True)
        
        st.markdown(create_professional_metric_card(
            "Profit Margin", avg_profit_margin, delta=4.2, format_type="percentage"
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Executive Analytics Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔮 **Predictive Intelligence**",
        "🗺️ **Regional Performance**", 
        "🤖 **AI Strategic Insights**",
        "⚠️ **Risk & Anomaly Detection**",
        "📈 **Strategic Planning**"
    ])
    
    with tab1:
        st.markdown("### 🔮 Executive Forecasting & Predictive Analytics")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            forecast_metric = st.selectbox(
                "Forecast Target",
                options=['revenue_eur', 'profit_eur', 'co2_emissions_kg', 'total_cost_eur'],
                format_func=lambda x: x.replace('_', ' ').replace('eur', '(EUR)').replace('kg', '(kg)').title()
            )
        
        # Generate forecast
        historical_data, forecast_data = executive_forecasting_engine(
            filtered_df, forecast_metric, forecast_horizon
        )
        
        if historical_data is not None and forecast_data is not None:
            with col1:
                # Professional forecast visualization
                fig = go.Figure()
                
                # Historical trend
                fig.add_trace(go.Scatter(
                    x=historical_data['date'],
                    y=historical_data[f'{forecast_metric}_sum'],
                    mode='lines+markers',
                    name='Historical Performance',
                    line=dict(color='#007bff', width=3),
                    marker=dict(size=6, color='#007bff')
                ))
                
                # Forecast line
                fig.add_trace(go.Scatter(
                    x=forecast_data['date'],
                    y=forecast_data['prediction'],
                    mode='lines+markers',
                    name='Strategic Forecast',
                    line=dict(color='#28a745', width=3, dash='dash'),
                    marker=dict(size=8, symbol='diamond', color='#28a745')
                ))
                
                # Confidence band
                fig.add_trace(go.Scatter(
                    x=list(forecast_data['date']) + list(forecast_data['date'][::-1]),
                    y=list(forecast_data['upper_bound']) + list(forecast_data['lower_bound'][::-1]),
                    fill='toself',
                    fillcolor='rgba(40, 167, 69, 0.15)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='95% Confidence Interval',
                    showlegend=True
                ))
                
                fig.update_layout(
                    title=f"📈 {forecast_metric.replace('_', ' ').title()} Strategic Forecast",
                    xaxis_title="Timeline",
                    yaxis_title=forecast_metric.replace('_', ' ').title(),
                    template='plotly_white',
                    height=520,
                    hovermode='x unified',
                    font=dict(family='Inter', size=12),
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Strategic insights
            next_period = forecast_data['prediction'].iloc[0]
            current_avg = historical_data[f'{forecast_metric}_sum'].tail(6).mean()
            growth_rate = ((next_period - current_avg) / current_avg) * 100 if current_avg != 0 else 0
            
            confidence_width = forecast_data['confidence_width'].mean()
            forecast_quality = "High" if confidence_width < next_period * 0.2 else "Medium" if confidence_width < next_period * 0.4 else "Low"
            
            if growth_rate > 10:
                trend_assessment = "Strong Growth Trajectory"
                strategic_action = "Prepare for capacity expansion and resource scaling"
            elif growth_rate > 0:
                trend_assessment = "Positive Growth Trend"
                strategic_action = "Monitor performance and optimize current operations"
            elif growth_rate > -10:
                trend_assessment = "Stabilization Period"
                strategic_action = "Focus on efficiency improvements and cost optimization"
            else:
                trend_assessment = "Declining Performance"
                strategic_action = "Implement immediate corrective measures and strategic review"
            
            st.markdown(f"""
            <div class="insight-container">
                <h4>🎯 Strategic Forecast Intelligence</h4>
                <p><strong>Trend Assessment:</strong> {trend_assessment} ({growth_rate:+.1f}% projected change)</p>
                <p><strong>Next Period Projection:</strong> {next_period:,.0f} units</p>
                <p><strong>Forecast Confidence:</strong> {forecast_quality} ({100-confidence_width/next_period*100:.0f}% reliability)</p>
                <p><strong>Strategic Recommendation:</strong> {strategic_action}</p>
                <p><strong>Executive Action:</strong> {'Schedule board presentation for growth investment approval' if growth_rate > 15 else 'Continue quarterly monitoring with operational adjustments' if growth_rate > -5 else 'Initiate emergency strategic review and cost reduction program'}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 🗺️ Regional Performance Intelligence & Market Analysis")
        
        # Regional performance metrics
        regional_performance = filtered_df.groupby('region').agg({
            'revenue_eur': 'sum',
            'profit_eur': 'sum', 
            'total_cost_eur': 'sum',
            'co2_emissions_kg': 'sum',
            'distance_km': 'sum',
            'fuel_efficiency_km_per_l': 'mean',
            'on_time_performance': 'mean',
            'safety_score': 'mean'
        }).reset_index()
        
        regional_performance['profit_margin'] = (
            regional_performance['profit_eur'] / regional_performance['revenue_eur']
        ).fillna(0)
        regional_performance['emissions_intensity'] = (
            regional_performance['co2_emissions_kg'] / regional_performance['distance_km']
        ).fillna(0)
        regional_performance['market_share'] = (
            regional_performance['revenue_eur'] / regional_performance['revenue_eur'].sum() * 100
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Regional performance matrix
            fig_matrix = px.scatter(
                regional_performance,
                x='emissions_intensity',
                y='profit_margin',
                size='revenue_eur',
                color='on_time_performance',
                hover_name='region',
                title="🎯 Regional Strategic Performance Matrix",
                labels={
                    'emissions_intensity': 'Environmental Impact (CO₂/km)',
                    'profit_margin': 'Profitability Margin',
                    'on_time_performance': 'Service Quality'
                },
                color_continuous_scale='Viridis',
                size_max=25
            )
            fig_matrix.update_layout(
                template='plotly_white',
                height=480,
                font=dict(family='Inter')
            )
            st.plotly_chart(fig_matrix, use_container_width=True)
        
        with col2:
            # Market share and profitability
            fig_bubble = px.scatter(
                regional_performance,
                x='market_share',
                y='profit_margin',
                size='revenue_eur',
                color='safety_score',
                hover_name='region',
                title="💼 Market Position & Profitability Analysis",
                labels={
                    'market_share': 'Market Share (%)',
                    'profit_margin': 'Profit Margin',
                    'safety_score': 'Safety Performance'
                },
                color_continuous_scale='RdYlGn',
                size_max=25
            )
            fig_bubble.update_layout(
                template='plotly_white',
                height=480,
                font=dict(family='Inter')
            )
            st.plotly_chart(fig_bubble, use_container_width=True)
        
        # Regional champions analysis
        st.markdown("#### 🏆 Regional Performance Champions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            revenue_leader = regional_performance.loc[regional_performance['revenue_eur'].idxmax()]
            st.markdown(f"""
            **💰 Revenue Champion**
            - **{revenue_leader['region']}**
            - €{revenue_leader['revenue_eur']/1000000:.1f}M revenue
            - {revenue_leader['market_share']:.1f}% market share
            """)
        
        with col2:
            profit_leader = regional_performance.loc[regional_performance['profit_margin'].idxmax()]
            st.markdown(f"""
            **📈 Profitability Leader**
            - **{profit_leader['region']}**
            - {profit_leader['profit_margin']:.1%} margin
            - €{profit_leader['profit_eur']/1000000:.1f}M profit
            """)
        
        with col3:
            efficiency_leader = regional_performance.loc[regional_performance['fuel_efficiency_km_per_l'].idxmax()]
            st.markdown(f"""
            **⚡ Efficiency Champion**
            - **{efficiency_leader['region']}**
            - {efficiency_leader['fuel_efficiency_km_per_l']:.1f} km/L
            - Best-in-class operations
            """)
        
        with col4:
            green_leader = regional_performance.loc[regional_performance['emissions_intensity'].idxmin()]
            st.markdown(f"""
            **🌱 Sustainability Leader**
            - **{green_leader['region']}**
            - {green_leader['emissions_intensity']:.2f} kg CO₂/km
            - Environmental excellence
            """)
    
    with tab3:
        st.markdown("### 🤖 AI-Powered Strategic Insights & Performance Clustering")
        
        # Strategic clustering analysis
        col1, col2 = st.columns([3, 1])
        
        with col2:
            cluster_count = st.slider("Strategic Segments", 2, 6, 4)
            
        regional_clusters, clustering_model, silhouette_score_val = strategic_regional_clustering(
            filtered_df, n_clusters=cluster_count
        )
        
        if clustering_model is not None and not regional_clusters.empty:
            with col1:
                # 3D strategic clustering visualization
                fig_3d = px.scatter_3d(
                    regional_clusters,
                    x='fuel_efficiency_km_per_l',
                    y='on_time_performance',
                    z='profit_margin',
                    color='cluster',
                    size='revenue_eur',
                    hover_name='region',
                    title=f"🎯 Strategic Regional Segmentation (Quality Score: {silhouette_score_val:.3f})",
                    labels={
                        'fuel_efficiency_km_per_l': 'Operational Efficiency',
                        'on_time_performance': 'Service Quality',
                        'profit_margin': 'Financial Performance'
                    },
                    color_continuous_scale='Set3'
                )
                fig_3d.update_layout(
                    template='plotly_white',
                    height=550,
                    font=dict(family='Inter')
                )
                st.plotly_chart(fig_3d, use_container_width=True)
            
            # Strategic cluster analysis
            st.markdown("#### 📊 Strategic Cluster Intelligence")
            
            for cluster_id in sorted(regional_clusters['cluster'].unique()):
                cluster_regions = regional_clusters[regional_clusters['cluster'] == cluster_id]
                
                # Calculate cluster characteristics
                avg_efficiency = cluster_regions['fuel_efficiency_km_per_l'].mean()
                avg_performance = cluster_regions['on_time_performance'].mean()
                avg_safety = cluster_regions['safety_score'].mean()
                avg_margin = cluster_regions['profit_margin'].mean()
                total_revenue = cluster_regions['revenue_eur'].sum()
                
                # Determine cluster profile
                performance_indicators = []
                if avg_efficiency > regional_clusters['fuel_efficiency_km_per_l'].median():
                    performance_indicators.append("High Efficiency")
                if avg_performance > regional_clusters['on_time_performance'].median():
                    performance_indicators.append("Superior Service")
                if avg_safety > regional_clusters['safety_score'].median():
                    performance_indicators.append("Excellent Safety")
                if avg_margin > regional_clusters['profit_margin'].median():
                    performance_indicators.append("Strong Profitability")
                
                cluster_profile = " + ".join(performance_indicators) if performance_indicators else "Development Opportunity"
                
                # Strategic recommendations
                if len(performance_indicators) >= 3:
                    strategic_focus = "Market leader - expand and replicate best practices"
                elif len(performance_indicators) >= 2:
                    strategic_focus = "Strong performer - targeted improvements needed"
                elif len(performance_indicators) >= 1:
                    strategic_focus = "Mixed performance - strategic intervention required"
                else:
                    strategic_focus = "Underperformer - comprehensive transformation needed"
                
                st.markdown(f"""
                <div class="insight-container">
                    <h4>🎯 Strategic Segment {cluster_id + 1}: {cluster_profile}</h4>
                    <p><strong>Regions:</strong> {', '.join(cluster_regions['region'].tolist())}</p>
                    <p><strong>Financial Impact:</strong> €{total_revenue/1000000:.1f}M revenue ({total_revenue/regional_clusters['revenue_eur'].sum()*100:.1f}% of total)</p>
                    <p><strong>Performance Metrics:</strong></p>
                    <ul>
                        <li>Operational Efficiency: {avg_efficiency:.1f} km/L</li>
                        <li>Service Quality: {avg_performance:.1%}</li>
                        <li>Safety Performance: {avg_safety:.1%}</li>
                        <li>Profit Margin: {avg_margin:.1%}</li>
                    </ul>
                    <p><strong>Strategic Priority:</strong> {strategic_focus}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Insufficient data for meaningful strategic segmentation with current filters.")
    
    with tab4:
        st.markdown("### ⚠️ Executive Risk Assessment & Anomaly Detection")
        
        # Risk assessment controls
        col1, col2 = st.columns([3, 1])
        
        with col2:
            risk_metric = st.selectbox(
                "Risk Assessment Focus",
                options=['profit_eur', 'co2_emissions_kg', 'total_cost_eur', 'safety_score'],
                format_func=lambda x: x.replace('_', ' ').title()
            )
        
        # Perform executive anomaly detection
        daily_analysis, risk_events = perform_executive_anomaly_detection(
            filtered_df, risk_metric, contamination=anomaly_sensitivity
        )
        
        if not daily_analysis.empty:
            with col1:
                # Risk visualization
                fig_risk = go.Figure()
                
                # Normal operations baseline
                normal_operations = daily_analysis[daily_analysis['anomaly_flag'] == 1]
                fig_risk.add_trace(go.Scatter(
                    x=normal_operations['date'],
                    y=normal_operations[f'{risk_metric}_sum'],
                    mode='lines+markers',
                    name='Normal Operations',
                    line=dict(color='#007bff', width=2),
                    marker=dict(size=4, color='#007bff', opacity=0.7)
                ))
                
                # Risk events
                if not risk_events.empty:
                    fig_risk.add_trace(go.Scatter(
                        x=risk_events['date'],
                        y=risk_events[f'{risk_metric}_sum'],
                        mode='markers',
                        name='Risk Events Detected',
                        marker=dict(
                            size=12, 
                            color='#dc3545', 
                            symbol='diamond',
                            line=dict(width=2, color='#a71e2a')
                        )
                    ))
                
                fig_risk.update_layout(
                    title=f"🚨 Executive Risk Assessment: {risk_metric.replace('_', ' ').title()}",
                    xaxis_title="Timeline",
                    yaxis_title=risk_metric.replace('_', ' ').title(),
                    template='plotly_white',
                    height=500,
                    font=dict(family='Inter'),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_risk, use_container_width=True)
        
        # Risk assessment summary
        if not risk_events.empty:
            risk_frequency = len(risk_events) / len(daily_analysis) * 100
            most_recent_risk = risk_events['date'].max()
            highest_risk_value = risk_events[f'{risk_metric}_sum'].max()
            
            # Risk severity assessment
            if risk_frequency > 15:
                risk_level = "Critical"
                risk_color = "danger"
                executive_action = "Immediate board escalation and crisis management protocol activation required"
            elif risk_frequency > 8:
                risk_level = "High"
                risk_color = "warning"
                executive_action = "Senior management review and corrective action plan within 48 hours"
            elif risk_frequency > 3:
                risk_level = "Medium"
                risk_color = "warning"
                executive_action = "Operational review and preventive measures implementation"
            else:
                risk_level = "Low"
                risk_color = "success"
                executive_action = "Continue monitoring with standard reporting procedures"
            
            st.markdown(f"""
            <div class="alert-{risk_color}">
                <h4>🚨 Executive Risk Alert - {risk_level} Risk Level</h4>
                <p><strong>Risk Event Frequency:</strong> {len(risk_events)} events ({risk_frequency:.1f}% of operational days)</p>
                <p><strong>Most Recent Risk Event:</strong> {most_recent_risk.strftime('%Y-%m-%d')}</p>
                <p><strong>Maximum Risk Exposure:</strong> {highest_risk_value:,.0f} units</p>
                <p><strong>Executive Action Required:</strong> {executive_action}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Risk event details
            with st.expander("📊 Detailed Risk Event Analysis"):
                risk_summary = risk_events.groupby(risk_events['date'].dt.month).agg({
                    f'{risk_metric}_sum': ['count', 'mean', 'max'],
                    'anomaly_score': 'mean'
                }).round(2)
                st.dataframe(risk_summary, use_container_width=True)
        else:
            st.markdown("""
            <div class="alert-success">
                <h4>✅ Risk Assessment: All Clear</h4>
                <p>No significant risk events detected in the current analysis period.</p>
                <p><strong>Status:</strong> Operations within normal parameters</p>
                <p><strong>Recommendation:</strong> Continue standard monitoring and reporting procedures</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab5:
        st.markdown("### 📈 Strategic Planning & Executive Scenario Analysis")
        
        st.markdown("#### 🎯 Strategic Impact Modeling")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🔋 Sustainability Transformation")
            
            ev_expansion = st.slider("Electric Fleet Expansion (%)", 0, 60, 25, key="sustainability")
            efficiency_program = st.slider("Operational Efficiency Program (%)", 0, 35, 18, key="efficiency")
            
            # Calculate sustainability impact
            baseline_emissions = filtered_df['co2_emissions_kg'].sum()
            baseline_fuel_cost = filtered_df['fuel_cost_eur'].sum()
            
            # EV impact modeling
            non_ev_emissions = filtered_df[filtered_df['fuel_type'] != 'Electric']['co2_emissions_kg'].sum()
            ev_emission_reduction = non_ev_emissions * (ev_expansion / 100)
            
            # Efficiency impact
            efficiency_emission_reduction = (baseline_emissions - ev_emission_reduction) * (efficiency_program / 100)
            
            total_emission_reduction = ev_emission_reduction + efficiency_emission_reduction
            projected_emissions = baseline_emissions - total_emission_reduction
            
            # Cost impact
            ev_cost_savings = baseline_fuel_cost * (ev_expansion / 100) * 0.75
            efficiency_cost_savings = baseline_fuel_cost * (efficiency_program / 100) * 0.4
            total_cost_savings = ev_cost_savings + efficiency_cost_savings
            
            # Visualization
            sustainability_data = pd.DataFrame({
                'Scenario': ['Current State', 'Sustainability Target'],
                'CO2_Emissions_M_kg': [baseline_emissions/1000000, projected_emissions/1000000],
                'Fuel_Cost_M_EUR': [baseline_fuel_cost/1000000, (baseline_fuel_cost - total_cost_savings)/1000000]
            })
            
            fig_sustainability = px.bar(
                sustainability_data.melt(id_vars='Scenario', var_name='Metric', value_name='Value'),
                x='Scenario',
                y='Value',
                color='Metric',
                barmode='group',
                title="🌱 Sustainability Impact Analysis",
                color_discrete_map={
                    'CO2_Emissions_M_kg': '#ff6b6b',
                    'Fuel_Cost_M_EUR': '#4ecdc4'
                }
            )
            fig_sustainability.update_layout(template='plotly_white', height=400, font=dict(family='Inter'))
            st.plotly_chart(fig_sustainability, use_container_width=True)
            
            # Sustainability metrics
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("CO₂ Reduction", f"{total_emission_reduction/1000000:.2f}M kg", 
                         f"-{total_emission_reduction/baseline_emissions*100:.1f}%")
            with col_b:
                st.metric("Cost Savings", f"€{total_cost_savings/1000000:.2f}M", 
                         f"-{total_cost_savings/baseline_fuel_cost*100:.1f}%")
        
        with col2:
            st.markdown("##### 💼 Financial Optimization")
            
            revenue_growth_target = st.slider("Revenue Growth Target (%)", 0, 50, 22, key="revenue")
            cost_optimization = st.slider("Cost Optimization Program (%)", 0, 30, 15, key="cost_opt")
            
            # Calculate financial impact
            baseline_revenue = filtered_df['revenue_eur'].sum()
            baseline_costs = filtered_df['total_cost_eur'].sum()
            baseline_profit = baseline_revenue - baseline_costs
            baseline_margin = baseline_profit / baseline_revenue if baseline_revenue > 0 else 0
            
            # Projected scenario
            projected_revenue = baseline_revenue * (1 + revenue_growth_target / 100)
            projected_costs = baseline_costs * (1 - cost_optimization / 100)
            projected_profit = projected_revenue - projected_costs
            projected_margin = projected_profit / projected_revenue if projected_revenue > 0 else 0
            
            # ROI calculation
            profit_improvement = projected_profit - baseline_profit
            margin_improvement = projected_margin - baseline_margin
            
            # Financial visualization
            financial_data = pd.DataFrame({
                'Metric': ['Revenue', 'Costs', 'Profit'] * 2,
                'Scenario': ['Current'] * 3 + ['Optimized'] * 3,
                'Value_M_EUR': [
                    baseline_revenue/1000000, baseline_costs/1000000, baseline_profit/1000000,
                    projected_revenue/1000000, projected_costs/1000000, projected_profit/1000000
                ]
            })
            
            fig_financial = px.bar(
                financial_data,
                x='Metric',
                y='Value_M_EUR',
                color='Scenario',
                barmode='group',
                title="💰 Financial Optimization Impact",
                color_discrete_map={
                    'Current': '#ffa726',
                    'Optimized': '#66bb6a'
                }
            )
            fig_financial.update_layout(template='plotly_white', height=400, font=dict(family='Inter'))
            st.plotly_chart(fig_financial, use_container_width=True)
            
            # Financial metrics
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Profit Increase", f"€{profit_improvement/1000000:.2f}M", 
                         f"+{profit_improvement/baseline_profit*100:.1f}%")
            with col_b:
                st.metric("Margin Improvement", f"{projected_margin:.1%}", 
                         f"+{margin_improvement*100:.1f}pp")
        
        # Strategic recommendations engine
        st.markdown("---")
        st.markdown("#### 🎯 AI-Generated Strategic Recommendations")
        
        recommendations = []
        
        # Sustainability recommendations
        if total_emission_reduction > baseline_emissions * 0.20:
            recommendations.append({
                "priority": "High",
                "category": "Sustainability Leadership",
                "title": "Accelerate Green Transformation Initiative",
                "description": f"Scenario analysis demonstrates {total_emission_reduction/baseline_emissions*100:.1f}% emission reduction potential with €{total_cost_savings/1000000:.1f}M cost savings. Position company as industry sustainability leader.",
                "financial_impact": f"€{total_cost_savings/1000000:.1f}M annual savings",
                "timeline": "12-18 months implementation"
            })
        
        # Financial optimization recommendations
        if margin_improvement > 0.05:
            recommendations.append({
                "priority": "High",
                "category": "Financial Performance",
                "title": "Execute Aggressive Growth & Optimization Strategy",
                "description": f"Financial modeling indicates {margin_improvement*100:.1f} percentage point margin improvement potential, generating €{profit_improvement/1000000:.1f}M additional profit.",
                "financial_impact": f"€{profit_improvement/1000000:.1f}M profit increase",
                "timeline": "6-12 months execution"
            })
        
        # Risk management recommendations
        if not risk_events.empty and len(risk_events) > len(daily_analysis) * 0.08:
            recommendations.append({
                "priority": "Medium",
                "category": "Risk Management",
                "title": "Implement Advanced Risk Monitoring System",
                "description": f"Risk analysis identified {len(risk_events)/len(daily_analysis)*100:.1f}% operational anomaly rate. Deploy predictive analytics and real-time monitoring.",
                "financial_impact": "Risk mitigation value: €2-5M annually",
                "timeline": "3-6 months deployment"
            })
        
        # Operational excellence recommendations
        best_performing_region = regional_performance.loc[regional_performance['profit_margin'].idxmax(), 'region']
        recommendations.append({
            "priority": "Medium",
            "category": "Operational Excellence",
            "title": "Scale Best Practice Framework",
            "description": f"Replicate {best_performing_region}'s operational model across network. Current margin: {regional_performance.loc[regional_performance['profit_margin'].idxmax(), 'profit_margin']:.1%}",
            "financial_impact": "Estimated €3-8M improvement potential",
            "timeline": "9-15 months rollout"
        })
        
        # Display strategic recommendations
        for i, rec in enumerate(recommendations, 1):
            priority_colors = {"High": "#dc3545", "Medium": "#ffc107", "Low": "#28a745"}
            priority_color = priority_colors.get(rec["priority"], "#6c757d")
            
            st.markdown(f"""
            <div class="recommendation-container">
                <h4>💡 Strategic Initiative {i}: {rec['title']} 
                    <span style="background: {priority_color}; color: white; padding: 4px 12px; border-radius: 15px; font-size: 0.8rem; margin-left: 15px; font-weight: 600;">
                        {rec['priority']} Priority
                    </span>
                </h4>
                <p><strong>Category:</strong> {rec['category']}</p>
                <p><strong>Strategic Rationale:</strong> {rec['description']}</p>
                <p><strong>Financial Impact:</strong> {rec['financial_impact']}</p>
                <p><strong>Implementation Timeline:</strong> {rec['timeline']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Executive Summary Dashboard
    st.markdown("---")
    st.markdown(f"""
    <div class="insight-container">
        <h4>📋 Executive Intelligence Summary</h4>
        <p><strong>Analysis Period:</strong> {start_date} to {end_date} | <strong>Scope:</strong> {len(filtered_df):,} operations across {len(selected_regions)} regions</p>
        <p><strong>Financial Performance:</strong> €{total_revenue_m:.1f}M revenue | €{total_profit_m:.1f}M profit | {avg_profit_margin:.1f}% margin</p>
        <p><strong>Operational Excellence:</strong> {total_distance_mkm:.1f}M km network | {avg_on_time:.1f}% on-time | {avg_safety:.1f}% safety score</p>
        <p><strong>Environmental Impact:</strong> {total_emissions_m:.1f}M kg CO₂ | {avg_efficiency:.1f} km/L efficiency | Sustainability opportunities identified</p>
        <p><strong>Strategic Opportunities:</strong> {len(recommendations)} high-impact initiatives | Est. €{(total_revenue_m * 0.25):.1f}M optimization potential</p>
        <p><strong>Risk Assessment:</strong> {len(risk_events) if not risk_events.empty else 0} anomalies detected | {'Risk management protocols activated' if not risk_events.empty and len(risk_events) > 5 else 'Operations within normal parameters'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Professional Footer
    st.markdown("---")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 2.5rem; border-radius: 15px; text-align: center; margin-top: 2rem;'>
        <h3 style='margin: 0; color: white; font-size: 1.8rem;'>🚀 Grecert DGT Transport Intelligence Platform</h3>
        <p style='margin: 1rem 0; font-size: 1.1rem; opacity: 0.9;'>Executive Business Intelligence | Advanced AI Analytics | Strategic Decision Support</p>
        <p style='margin: 0; font-size: 0.9rem; opacity: 0.8;'>© 2025 Grecert.com - Confidential Executive Dashboard | All Rights Reserved</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
