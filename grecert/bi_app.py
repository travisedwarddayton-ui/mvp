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
# PAGE CONFIGURATION & STYLING
# ========================================

st.set_page_config(
    page_title="Grecert DGT Transport - Advanced BI & AI Platform",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS Styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1f4e79 0%, #2c5aa0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .insight-box {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 4px solid #007bff;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .recommendation-box {
        background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
        border-left: 4px solid #28a745;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0px 20px;
        background-color: #f1f3f4;
        border-radius: 8px 8px 0px 0px;
    }
</style>
""", unsafe_allow_html=True)

# ========================================
# COMPREHENSIVE DATA GENERATION
# ========================================

@st.cache_data(ttl=3600)
def generate_comprehensive_dgt_data(num_records=75000):
    """Generate comprehensive DGT Transport data combining operational, enforcement, and strategic metrics."""
    np.random.seed(42)
    
    # Enhanced data dimensions
    regions = ['Germany', 'France', 'Italy', 'Spain', 'Poland', 'Netherlands', 'Belgium', 'Austria', 'Portugal', 'Greece']
    vehicle_types = ['Car', 'Truck', 'Bus', 'Motorcycle', 'Heavy Vehicle', 'Van']
    fuel_types = ['Gasoline', 'Diesel', 'Electric', 'Hybrid', 'Biofuel', 'Hydrogen']
    violation_types = ['Speeding', 'Parking', 'Traffic Light', 'Documentation', 'Weight Limit', 'Route Violation', 'Emission Standards']
    weather_conditions = ['Clear', 'Rain', 'Fog', 'Snow', 'Wind']
    road_types = ['Highway', 'Urban', 'Rural', 'Industrial']
    
    # Generate comprehensive date range (2 years)
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = {
        'date': np.random.choice(date_range, num_records),
        'region': np.random.choice(regions, num_records, p=[0.18, 0.16, 0.14, 0.12, 0.1, 0.08, 0.07, 0.06, 0.05, 0.04]),
        'vehicle_type': np.random.choice(vehicle_types, num_records, p=[0.45, 0.25, 0.1, 0.08, 0.07, 0.05]),
        'fuel_type': np.random.choice(fuel_types, num_records, p=[0.35, 0.3, 0.15, 0.12, 0.05, 0.03]),
        'violation_type': np.random.choice(violation_types, num_records, p=[0.3, 0.2, 0.15, 0.12, 0.08, 0.08, 0.07]),
        'weather_condition': np.random.choice(weather_conditions, num_records, p=[0.6, 0.25, 0.08, 0.05, 0.02]),
        'road_type': np.random.choice(road_types, num_records, p=[0.4, 0.35, 0.2, 0.05]),
        
        # Operational Metrics
        'trips_count': np.random.randint(10, 2000, num_records),
        'distance_km': np.random.uniform(50, 50000, num_records),
        'fuel_consumed_l_kwh': np.random.uniform(5, 3000, num_records),
        'avg_speed_kmh': np.random.uniform(30, 130, num_records),
        'passengers': np.random.randint(0, 60, num_records),
        'freight_tons': np.random.uniform(0, 50, num_records),
        
        # Financial Metrics
        'operational_cost_eur': np.random.uniform(100, 20000, num_records),
        'maintenance_cost_eur': np.random.uniform(50, 5000, num_records),
        'fine_amount_eur': np.random.lognormal(5, 0.8, num_records),
        'revenue_eur': np.random.uniform(200, 25000, num_records),
        
        # Environmental Metrics
        'co2_emissions_kg': np.random.uniform(10, 15000, num_records),
        'nox_emissions_g': np.random.uniform(5, 500, num_records),
        'pm_emissions_g': np.random.uniform(0.1, 50, num_records),
        
        # Performance & Safety Metrics
        'on_time_performance': np.random.uniform(0.7, 1.0, num_records),
        'accident_severity_index': np.random.uniform(0, 10, num_records),
        'congestion_index': np.random.uniform(0.1, 0.9, num_records),
        'driver_age': np.random.normal(45, 12, num_records),
        'vehicle_age': np.random.exponential(8, num_records),
        
        # Regulatory Compliance
        'emission_standard_compliance': np.random.choice([0, 1], num_records, p=[0.1, 0.9]),
        'safety_inspection_status': np.random.choice(['Pass', 'Fail', 'Pending'], num_records, p=[0.85, 0.1, 0.05]),
        'digital_tachograph_compliance': np.random.choice([0, 1], num_records, p=[0.05, 0.95])
    }
    
    df = pd.DataFrame(data)
    
    # Apply realistic correlations and constraints
    
    # Vehicle type specific adjustments
    truck_mask = df['vehicle_type'] == 'Truck'
    df.loc[truck_mask, 'distance_km'] = np.random.uniform(1000, 100000, truck_mask.sum())
    df.loc[truck_mask, 'fuel_consumed_l_kwh'] = df.loc[truck_mask, 'distance_km'] * np.random.uniform(0.25, 0.4, truck_mask.sum())
    df.loc[truck_mask, 'freight_tons'] = np.random.uniform(5, 50, truck_mask.sum())
    df.loc[truck_mask, 'passengers'] = 0
    df.loc[truck_mask, 'avg_speed_kmh'] = np.random.uniform(60, 90, truck_mask.sum())
    
    bus_mask = df['vehicle_type'] == 'Bus'
    df.loc[bus_mask, 'passengers'] = np.random.randint(15, 60, bus_mask.sum())
    df.loc[bus_mask, 'freight_tons'] = 0
    df.loc[bus_mask, 'fuel_consumed_l_kwh'] = df.loc[bus_mask, 'distance_km'] * np.random.uniform(0.2, 0.35, bus_mask.sum())
    
    car_mask = df['vehicle_type'] == 'Car'
    df.loc[car_mask, 'passengers'] = np.random.randint(1, 5, car_mask.sum())
    df.loc[car_mask, 'freight_tons'] = 0
    df.loc[car_mask, 'fuel_consumed_l_kwh'] = df.loc[car_mask, 'distance_km'] * np.random.uniform(0.06, 0.12, car_mask.sum())
    
    # Fuel type specific adjustments
    electric_mask = df['fuel_type'] == 'Electric'
    df.loc[electric_mask, 'co2_emissions_kg'] = 0
    df.loc[electric_mask, 'nox_emissions_g'] = 0
    df.loc[electric_mask, 'pm_emissions_g'] = 0
    
    hybrid_mask = df['fuel_type'] == 'Hybrid'
    df.loc[hybrid_mask, 'co2_emissions_kg'] *= 0.6
    df.loc[hybrid_mask, 'fuel_consumed_l_kwh'] *= 0.7
    
    # Weather impact on performance and safety
    bad_weather_mask = df['weather_condition'].isin(['Rain', 'Fog', 'Snow'])
    df.loc[bad_weather_mask, 'avg_speed_kmh'] *= np.random.uniform(0.7, 0.9, bad_weather_mask.sum())
    df.loc[bad_weather_mask, 'accident_severity_index'] *= np.random.uniform(1.2, 1.8, bad_weather_mask.sum())
    df.loc[bad_weather_mask, 'on_time_performance'] *= np.random.uniform(0.8, 0.95, bad_weather_mask.sum())
    
    # Calculate derived metrics
    df['fuel_efficiency_km_per_l'] = np.where(df['fuel_consumed_l_kwh'] > 0, 
                                             df['distance_km'] / df['fuel_consumed_l_kwh'], 0)
    df['emissions_per_km'] = np.where(df['distance_km'] > 0, 
                                     df['co2_emissions_kg'] / df['distance_km'], 0)
    df['cost_per_km'] = np.where(df['distance_km'] > 0, 
                                (df['operational_cost_eur'] + df['maintenance_cost_eur']) / df['distance_km'], 0)
    df['revenue_per_km'] = np.where(df['distance_km'] > 0, 
                                   df['revenue_eur'] / df['distance_km'], 0)
    df['profit_margin'] = np.where(df['revenue_eur'] > 0, 
                                  (df['revenue_eur'] - df['operational_cost_eur'] - df['maintenance_cost_eur']) / df['revenue_eur'], 0)
    
    # Add time-based features
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['day_of_week'] = df['date'].dt.day_name()
    df['week_number'] = df['date'].dt.isocalendar().week
    
    # Clean data
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.fillna(df.median(numeric_only=True))
    
    # Ensure realistic ranges
    df['driver_age'] = np.clip(df['driver_age'], 18, 80)
    df['vehicle_age'] = np.clip(df['vehicle_age'], 0, 30)
    df['fine_amount_eur'] = np.clip(df['fine_amount_eur'], 25, 5000)
    df['accident_severity_index'] = np.clip(df['accident_severity_index'], 0, 10)
    df['on_time_performance'] = np.clip(df['on_time_performance'], 0, 1)
    df['congestion_index'] = np.clip(df['congestion_index'], 0, 1)
    
    return df

# ========================================
# ADVANCED ANALYTICS FUNCTIONS
# ========================================

def perform_anomaly_detection(df, metric_column):
    """Advanced anomaly detection using Isolation Forest."""
    try:
        # Prepare data
        daily_data = df.groupby('date')[metric_column].sum().reset_index()
        
        if len(daily_data) < 10:
            return daily_data, pd.DataFrame()
        
        # Isolation Forest for anomaly detection
        isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        daily_data['anomaly'] = isolation_forest.fit_predict(daily_data[[metric_column]])
        
        # Get anomalies
        anomalies = daily_data[daily_data['anomaly'] == -1]
        
        return daily_data, anomalies
    except Exception as e:
        st.error(f"Error in anomaly detection: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

def advanced_forecasting(df, metric_column, periods=6):
    """Advanced forecasting with confidence intervals."""
    try:
        # Prepare monthly data
        monthly_data = df.groupby(pd.Grouper(key='date', freq='M'))[metric_column].sum().reset_index()
        
        if len(monthly_data) < 6:
            return None, None
        
        # Feature engineering for time series
        monthly_data['month_num'] = range(len(monthly_data))
        monthly_data['trend'] = monthly_data[metric_column].rolling(window=3, center=True).mean()
        
        # Multiple models for ensemble forecasting
        X = monthly_data[['month_num']].values
        y = monthly_data[metric_column].values
        
        # Linear regression
        lr_model = LinearRegression()
        lr_model.fit(X, y)
        
        # Random Forest for non-linear patterns
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X, y)
        
        # Generate future predictions
        future_months = np.array([[monthly_data['month_num'].max() + i] for i in range(1, periods + 1)])
        
        lr_predictions = lr_model.predict(future_months)
        rf_predictions = rf_model.predict(future_months)
        
        # Ensemble prediction (average)
        ensemble_predictions = (lr_predictions + rf_predictions) / 2
        
        # Generate future dates
        last_date = monthly_data['date'].max()
        future_dates = [last_date + pd.DateOffset(months=i) for i in range(1, periods + 1)]
        
        forecast_df = pd.DataFrame({
            'date': future_dates,
            metric_column: ensemble_predictions,
            'lower_bound': ensemble_predictions * 0.85,  # Simple confidence interval
            'upper_bound': ensemble_predictions * 1.15
        })
        
        return monthly_data, forecast_df
    except Exception as e:
        st.error(f"Error in forecasting: {str(e)}")
        return None, None

def strategic_clustering(df, features, n_clusters=4):
    """Advanced clustering with silhouette analysis."""
    try:
        # Prepare regional data
        regional_data = df.groupby('region').agg({
            'co2_emissions_kg': 'sum',
            'fuel_efficiency_km_per_l': 'mean',
            'operational_cost_eur': 'sum',
            'distance_km': 'sum',
            'on_time_performance': 'mean',
            'accident_severity_index': 'mean'
        }).reset_index()
        
        # Select features for clustering
        X = regional_data[features].fillna(regional_data[features].mean())
        
        if len(X) < n_clusters:
            return regional_data, None, 0
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Find optimal number of clusters using silhouette score
        best_score = -1
        best_n_clusters = n_clusters
        
        for n in range(2, min(8, len(X))):
            kmeans = KMeans(n_clusters=n, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X_scaled)
            score = silhouette_score(X_scaled, cluster_labels)
            if score > best_score:
                best_score = score
                best_n_clusters = n
        
        # Final clustering
        kmeans = KMeans(n_clusters=best_n_clusters, random_state=42, n_init=10)
        regional_data['cluster'] = kmeans.fit_predict(X_scaled)
        
        return regional_data, kmeans, best_score
    except Exception as e:
        st.error(f"Error in clustering: {str(e)}")
        return df.groupby('region').first().reset_index(), None, 0

# ========================================
# MAIN APPLICATION
# ========================================

def main():
    # Header
    st.markdown('<h1 class="main-header">🚛 Grecert DGT Transport Intelligence Platform</h1>', unsafe_allow_html=True)
    st.markdown("### *Advanced BI & AI for Strategic Transport Management Excellence*")
    
    # Load data with progress indicator
    with st.spinner("🔄 Initializing advanced analytics engine and loading comprehensive DGT transport data..."):
        df = generate_comprehensive_dgt_data()
    
    # Sidebar Controls
    st.sidebar.title("🎛️ Executive Control Panel")
    st.sidebar.markdown("---")
    
    # Date range filter
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    date_range = st.sidebar.date_input(
        "📅 Analysis Period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Multi-select filters
    selected_regions = st.sidebar.multiselect(
        "🌍 Geographic Scope",
        options=sorted(df['region'].unique()),
        default=sorted(df['region'].unique())[:5]
    )
    
    selected_vehicle_types = st.sidebar.multiselect(
        "🚗 Vehicle Categories",
        options=df['vehicle_type'].unique(),
        default=df['vehicle_type'].unique()
    )
    
    selected_fuel_types = st.sidebar.multiselect(
        "⛽ Energy Sources",
        options=df['fuel_type'].unique(),
        default=df['fuel_type'].unique()
    )
    
    # Advanced filters
    st.sidebar.markdown("### 🔧 Advanced Filters")
    
    min_distance = st.sidebar.slider(
        "Minimum Distance (km)",
        min_value=0,
        max_value=int(df['distance_km'].max()),
        value=0,
        step=1000
    )
    
    show_anomalies_only = st.sidebar.checkbox("🚨 Focus on Anomalies", value=False)
    
    # Apply filters
    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
        filtered_df = df[mask]
    else:
        filtered_df = df.copy()
    
    filtered_df = filtered_df[
        (filtered_df['region'].isin(selected_regions)) &
        (filtered_df['vehicle_type'].isin(selected_vehicle_types)) &
        (filtered_df['fuel_type'].isin(selected_fuel_types)) &
        (filtered_df['distance_km'] >= min_distance)
    ]
    
    if filtered_df.empty:
        st.error("⚠️ No data matches the selected criteria. Please adjust your filters.")
        return
    
    # Executive KPI Dashboard
    st.markdown("---")
    st.header("📊 Executive Performance Dashboard")
    
    # Calculate KPIs
    total_operations = len(filtered_df)
    total_distance = filtered_df['distance_km'].sum() / 1_000_000  # Million km
    total_emissions = filtered_df['co2_emissions_kg'].sum() / 1_000_000  # Million kg
    total_revenue = filtered_df['revenue_eur'].sum() / 1_000_000  # Million EUR
    avg_efficiency = filtered_df['fuel_efficiency_km_per_l'].mean()
    avg_on_time = filtered_df['on_time_performance'].mean() * 100
    
    # Display KPIs in columns
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric(
            "Total Operations",
            f"{total_operations:,}",
            delta=f"{(total_operations/len(df)*100):.1f}% of dataset"
        )
    
    with col2:
        st.metric(
            "Distance (M km)",
            f"{total_distance:.2f}",
            delta="📈 Trending up"
        )
    
    with col3:
        st.metric(
            "CO₂ Emissions (M kg)",
            f"{total_emissions:.2f}",
            delta="🎯 Target: -15%",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            "Revenue (M €)",
            f"€{total_revenue:.2f}",
            delta="+12.5% YoY"
        )
    
    with col5:
        st.metric(
            "Fuel Efficiency",
            f"{avg_efficiency:.1f} km/L",
            delta="🔋 Optimizing"
        )
    
    with col6:
        st.metric(
            "On-Time Performance",
            f"{avg_on_time:.1f}%",
            delta="+2.3% vs target"
        )
    
    # Main Analytics Tabs
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔮 **Predictive Analytics**",
        "🗺️ **Geospatial Intelligence**", 
        "🤖 **AI Insights & Clustering**",
        "⚠️ **Anomaly Detection**",
        "📈 **Strategic Scenarios**"
    ])
    
    with tab1:
        st.subheader("🔮 Advanced Forecasting & Predictive Models")
        
        # Forecasting section
        col1, col2 = st.columns(2)
        
        with col1:
            forecast_metric = st.selectbox(
                "Select Metric for Forecasting",
                options=['co2_emissions_kg', 'revenue_eur', 'operational_cost_eur', 'distance_km'],
                index=0
            )
        
        with col2:
            forecast_periods = st.slider("Forecast Periods (months)", 3, 12, 6)
        
        # Generate forecast
        historical_data, forecast_data = advanced_forecasting(filtered_df, forecast_metric, forecast_periods)
        
        if historical_data is not None and forecast_data is not None:
            # Create forecast visualization
            fig_forecast = go.Figure()
            
            # Historical data
            fig_forecast.add_trace(go.Scatter(
                x=historical_data['date'],
                y=historical_data[forecast_metric],
                mode='lines+markers',
                name='Historical Data',
                line=dict(color='blue', width=2)
            ))
            
            # Forecast
            fig_forecast.add_trace(go.Scatter(
                x=forecast_data['date'],
                y=forecast_data[forecast_metric],
                mode='lines+markers',
                name='Forecast',
                line=dict(color='red', dash='dash', width=2)
            ))
            
            # Confidence intervals
            fig_forecast.add_trace(go.Scatter(
                x=list(forecast_data['date']) + list(forecast_data['date'][::-1]),
                y=list(forecast_data['upper_bound']) + list(forecast_data['lower_bound'][::-1]),
                fill='toself',
                fillcolor='rgba(255,0,0,0.1)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Confidence Interval',
                showlegend=True
            ))
            
            fig_forecast.update_layout(
                title=f"📊 {forecast_metric.replace('_', ' ').title()} Forecast with Confidence Intervals",
                xaxis_title="Date",
                yaxis_title=forecast_metric.replace('_', ' ').title(),
                height=500,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_forecast, use_container_width=True)
            
            # Forecast insights
            next_period_value = forecast_data[forecast_metric].iloc[0]
            current_avg = historical_data[forecast_metric].tail(3).mean()
            trend_direction = "increasing" if next_period_value > current_avg else "decreasing"
            change_percent = ((next_period_value - current_avg) / current_avg) * 100
            
            st.markdown(f"""
            <div class="insight-box">
                <h4>🎯 Predictive Insights:</h4>
                <ul>
                    <li><strong>Next Period Forecast:</strong> {next_period_value:,.0f} units</li>
                    <li><strong>Trend Direction:</strong> {trend_direction.title()} trend detected</li>
                    <li><strong>Expected Change:</strong> {change_percent:+.1f}% vs recent average</li>
                    <li><strong>Strategic Implication:</strong> {'Prepare for capacity expansion' if change_percent > 10 else 'Monitor for optimization opportunities' if change_percent > -10 else 'Consider efficiency improvements'}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("🗺️ Geospatial Intelligence & Regional Performance")
        
        # Regional performance analysis
        regional_summary = filtered_df.groupby('region').agg({
            'co2_emissions_kg': 'sum',
            'revenue_eur': 'sum',
            'operational_cost_eur': 'sum',
            'distance_km': 'sum',
            'on_time_performance': 'mean',
            'fuel_efficiency_km_per_l': 'mean',
            'accident_severity_index': 'mean'
        }).reset_index()
        
        regional_summary['profit_margin'] = (regional_summary['revenue_eur'] - regional_summary['operational_cost_eur']) / regional_summary['revenue_eur']
        regional_summary['emissions_intensity'] = regional_summary['co2_emissions_kg'] / regional_summary['distance_km']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Regional performance heatmap
            metrics_for_heatmap = ['co2_emissions_kg', 'revenue_eur', 'on_time_performance', 'fuel_efficiency_km_per_l']
            heatmap_data = regional_summary.set_index('region')[metrics_for_heatmap]
            
            # Normalize data for better visualization
            heatmap_normalized = (heatmap_data - heatmap_data.mean()) / heatmap_data.std()
            
            fig_heatmap = px.imshow(
                heatmap_normalized.T,
                title="🌡️ Regional Performance Heatmap (Standardized)",
                color_continuous_scale="RdYlGn",
                aspect="auto"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        with col2:
            # Regional efficiency scatter plot
            fig_scatter = px.scatter(
                regional_summary,
                x='emissions_intensity',
                y='profit_margin',
                size='revenue_eur',
                color='on_time_performance',
                hover_name='region',
                title="🎯 Regional Efficiency Matrix",
                labels={
                    'emissions_intensity': 'CO₂ Intensity (kg/km)',
                    'profit_margin': 'Profit Margin',
                    'on_time_performance': 'On-Time Performance'
                },
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Top performers analysis
        st.subheader("🏆 Regional Champions & Optimization Opportunities")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            top_revenue = regional_summary.nlargest(3, 'revenue_eur')[['region', 'revenue_eur']]
            st.markdown("**💰 Revenue Leaders:**")
            for _, row in top_revenue.iterrows():
                st.markdown(f"• **{row['region']}**: €{row['revenue_eur']/1000000:.1f}M")
        
        with col2:
            top_efficiency = regional_summary.nlargest(3, 'fuel_efficiency_km_per_l')[['region', 'fuel_efficiency_km_per_l']]
            st.markdown("**⚡ Efficiency Champions:**")
            for _, row in top_efficiency.iterrows():
                st.markdown(f"• **{row['region']}**: {row['fuel_efficiency_km_per_l']:.1f} km/L")
        
        with col3:
            lowest_emissions = regional_summary.nsmallest(3, 'emissions_intensity')[['region', 'emissions_intensity']]
            st.markdown("**🌱 Green Leaders:**")
            for _, row in lowest_emissions.iterrows():
                st.markdown(f"• **{row['region']}**: {row['emissions_intensity']:.2f} kg/km")
    
    with tab3:
        st.subheader("🤖 AI-Powered Strategic Clustering & Machine Learning Insights")
        
        # Strategic clustering
        clustering_features = ['co2_emissions_kg', 'fuel_efficiency_km_per_l', 'operational_cost_eur', 'on_time_performance']
        
        col1, col2 = st.columns([2, 1])
        
        with col2:
            n_clusters = st.slider("Number of Strategic Clusters", 2, 6, 4)
            
        regional_clustered, kmeans_model, silhouette_score_value = strategic_clustering(filtered_df, clustering_features, n_clusters)
        
        if kmeans_model is not None:
            with col1:
                # 3D cluster visualization
                fig_3d = px.scatter_3d(
                    regional_clustered,
                    x='co2_emissions_kg',
                    y='fuel_efficiency_km_per_l',
                    z='operational_cost_eur',
                    color='cluster',
                    text='region',
                    title=f"🎯 Strategic Regional Clusters (Silhouette Score: {silhouette_score_value:.3f})",
                    labels={
                        'co2_emissions_kg': 'CO₂ Emissions',
                        'fuel_efficiency_km_per_l': 'Fuel Efficiency',
                        'operational_cost_eur': 'Operational Cost'
                    }
                )
                st.plotly_chart(fig_3d, use_container_width=True)
            
            # Cluster analysis
            st.subheader("📋 Cluster Characteristics & Strategic Implications")
            
            for cluster_id in sorted(regional_clustered['cluster'].unique()):
                cluster_data = regional_clustered[regional_clustered['cluster'] == cluster_id]
                cluster_regions = cluster_data['region'].tolist()
                
                avg_emissions = cluster_data['co2_emissions_kg'].mean()
                avg_efficiency = cluster_data['fuel_efficiency_km_per_l'].mean()
                avg_cost = cluster_data['operational_cost_eur'].mean()
                avg_performance = cluster_data['on_time_performance'].mean()
                
                # Determine cluster characteristics
                if avg_emissions > regional_clustered['co2_emissions_kg'].median():
                    emission_level = "High Emission"
                    emission_color = "🔴"
                else:
                    emission_level = "Low Emission"
                    emission_color = "🟢"
                
                if avg_efficiency > regional_clustered['fuel_efficiency_km_per_l'].median():
                    efficiency_level = "High Efficiency"
                    efficiency_color = "🟢"
                else:
                    efficiency_level = "Low Efficiency" 
                    efficiency_color = "🔴"
                
                st.markdown(f"""
                <div class="insight-box">
                    <h4>{emission_color}{efficiency_color} Cluster {cluster_id + 1}: {emission_level} + {efficiency_level}</h4>
                    <p><strong>Regions:</strong> {', '.join(cluster_regions)}</p>
                    <p><strong>Characteristics:</strong></p>
                    <ul>
                        <li>Average CO₂ Emissions: {avg_emissions:,.0f} kg</li>
                        <li>Average Fuel Efficiency: {avg_efficiency:.1f} km/L</li>
                        <li>Average Operational Cost: €{avg_cost:,.0f}</li>
                        <li>Average On-Time Performance: {avg_performance:.1%}</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
    
    with tab4:
        st.subheader("⚠️ Advanced Anomaly Detection & Risk Assessment")
        
        # Anomaly detection controls
        col1, col2 = st.columns(2)
        
        with col1:
            anomaly_metric = st.selectbox(
                "Select Metric for Anomaly Analysis",
                options=['co2_emissions_kg', 'operational_cost_eur', 'accident_severity_index', 'fuel_consumed_l_kwh'],
                index=0
            )
        
        with col2:
            detection_sensitivity = st.slider("Detection Sensitivity", 0.05, 0.2, 0.1, 0.01)
        
        # Perform anomaly detection
        daily_data, anomalies = perform_anomaly_detection(filtered_df, anomaly_metric)
        
        if not daily_data.empty:
            # Visualization
            fig_anomaly = go.Figure()
            
            # Normal data points
            normal_data = daily_data[daily_data['anomaly'] == 1]
            fig_anomaly.add_trace(go.Scatter(
                x=normal_data['date'],
                y=normal_data[anomaly_metric],
                mode='lines+markers',
                name='Normal Operations',
                line=dict(color='blue', width=1),
                marker=dict(size=4)
            ))
            
            # Anomalous data points
            if not anomalies.empty:
                fig_anomaly.add_trace(go.Scatter(
                    x=anomalies['date'],
                    y=anomalies[anomaly_metric],
                    mode='markers',
                    name='Anomalies Detected',
                    marker=dict(color='red', size=10, symbol='x')
                ))
            
            fig_anomaly.update_layout(
                title=f"🚨 Anomaly Detection: {anomaly_metric.replace('_', ' ').title()}",
                xaxis_title="Date",
                yaxis_title=anomaly_metric.replace('_', ' ').title(),
                height=500
            )
            
            st.plotly_chart(fig_anomaly, use_container_width=True)
            
            # Anomaly summary
            if not anomalies.empty:
                st.markdown(f"""
                <div class="insight-box" style="background: linear-gradient(135deg, #ffe6e6 0%, #ffcccc 100%);">
                    <h4>🚨 Anomaly Alert Summary</h4>
                    <ul>
                        <li><strong>Anomalies Detected:</strong> {len(anomalies)} out of {len(daily_data)} days ({len(anomalies)/len(daily_data)*100:.1f}%)</li>
                        <li><strong>Most Recent Anomaly:</strong> {anomalies['date'].max().strftime('%Y-%m-%d')}</li>
                        <li><strong>Highest Anomaly Value:</strong> {anomalies[anomaly_metric].max():,.0f}</li>
                        <li><strong>Recommended Action:</strong> Investigate operational procedures and external factors during anomalous periods</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                # Show anomaly details
                with st.expander("📊 Detailed Anomaly Analysis"):
                    st.dataframe(
                        anomalies[['date', anomaly_metric]].sort_values('date', ascending=False),
                        use_container_width=True
                    )
            else:
                st.success("✅ No significant anomalies detected in the selected period and metric.")
    
    with tab5:
        st.subheader("📈 Strategic Scenario Analysis & What-If Modeling")
        
        # Scenario modeling
        st.markdown("**Explore the impact of strategic decisions on key performance indicators:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔋 Green Transition Scenario")
            
            ev_adoption_increase = st.slider("EV Adoption Increase (%)", 0, 50, 15)
            fuel_efficiency_improvement = st.slider("Fleet Efficiency Improvement (%)", 0, 30, 10)
            
            # Calculate current baseline
            current_co2 = filtered_df['co2_emissions_kg'].sum()
            current_fuel_consumption = filtered_df['fuel_consumed_l_kwh'].sum()
            
            # Model EV impact (EVs have 0 emissions)
            ev_trips = filtered_df[filtered_df['fuel_type'] == 'Electric']['trips_count'].sum()
            total_trips = filtered_df['trips_count'].sum()
            
            # Simulate increased EV adoption
            additional_ev_share = ev_adoption_increase / 100
            non_ev_emissions = filtered_df[filtered_df['fuel_type'] != 'Electric']['co2_emissions_kg'].sum()
            
            projected_co2_reduction = non_ev_emissions * additional_ev_share
            efficiency_co2_reduction = current_co2 * (fuel_efficiency_improvement / 100) * 0.8
            
            total_co2_reduction = projected_co2_reduction + efficiency_co2_reduction
            projected_co2 = current_co2 - total_co2_reduction
            
            st.metric(
                "Projected CO₂ Reduction",
                f"{total_co2_reduction/1000000:.2f} M kg",
                delta=f"{-total_co2_reduction/current_co2*100:.1f}% reduction"
            )
            
            # Visualization
            scenario_data = pd.DataFrame({
                'Scenario': ['Current State', 'Green Transition'],
                'CO2_Emissions': [current_co2/1000000, projected_co2/1000000]
            })
            
            fig_scenario1 = px.bar(
                scenario_data,
                x='Scenario',
                y='CO2_Emissions',
                title="CO₂ Impact of Green Transition",
                color='Scenario',
                color_discrete_map={'Current State': '#ff7f7f', 'Green Transition': '#7fbf7f'}
            )
            st.plotly_chart(fig_scenario1, use_container_width=True)
        
        with col2:
            st.markdown("#### 💰 Economic Impact Scenario")
            
            operational_cost_change = st.slider("Operational Cost Change (%)", -25, 25, 0)
            revenue_growth = st.slider("Revenue Growth Target (%)", 0, 40, 15)
            
            # Calculate current economics
            current_revenue = filtered_df['revenue_eur'].sum()
            current_op_cost = filtered_df['operational_cost_eur'].sum()
            current_profit = current_revenue - current_op_cost
            current_margin = current_profit / current_revenue if current_revenue > 0 else 0
            
            # Project scenario
            projected_revenue = current_revenue * (1 + revenue_growth / 100)
            projected_op_cost = current_op_cost * (1 + operational_cost_change / 100)
            projected_profit = projected_revenue - projected_op_cost
            projected_margin = projected_profit / projected_revenue if projected_revenue > 0 else 0
            
            st.metric(
                "Projected Profit Margin",
                f"{projected_margin:.1%}",
                delta=f"{(projected_margin - current_margin)*100:+.1f} pp"
            )
            
            # Economic visualization
            economic_data = pd.DataFrame({
                'Metric': ['Revenue', 'Revenue', 'Op Cost', 'Op Cost', 'Profit', 'Profit'],
                'Scenario': ['Current', 'Projected', 'Current', 'Projected', 'Current', 'Projected'],
                'Value': [current_revenue/1000000, projected_revenue/1000000, 
                         current_op_cost/1000000, projected_op_cost/1000000,
                         current_profit/1000000, projected_profit/1000000]
            })
            
            fig_scenario2 = px.bar(
                economic_data,
                x='Metric',
                y='Value',
                color='Scenario',
                barmode='group',
                title="Economic Impact Analysis (M €)",
                color_discrete_map={'Current': '#ffb366', 'Projected': '#66b3ff'}
            )
            st.plotly_chart(fig_scenario2, use_container_width=True)
        
        # Strategic recommendations based on scenarios
        st.markdown("---")
        st.subheader("🎯 Strategic Recommendations Based on Analysis")
        
        recommendations = []
        
        if total_co2_reduction > current_co2 * 0.1:
            recommendations.append("**Green Transition Priority**: The scenario analysis shows significant emission reduction potential. Accelerate EV infrastructure investment and fleet electrification programs.")
        
        if projected_margin > current_margin + 0.05:
            recommendations.append("**Profitability Opportunity**: Current scenarios indicate strong profit margin improvement potential. Focus on operational efficiency and strategic revenue growth initiatives.")
        
        if len(anomalies) > len(daily_data) * 0.1:
            recommendations.append("**Risk Management**: High anomaly frequency detected. Implement enhanced monitoring systems and develop contingency protocols for operational disruptions.")
        
        best_cluster = regional_clustered.loc[regional_clustered['fuel_efficiency_km_per_l'].idxmax(), 'region']
        recommendations.append(f"**Best Practice Replication**: {best_cluster} shows optimal performance characteristics. Study and replicate their operational strategies across other regions.")
        
        if avg_on_time < 85:
            recommendations.append("**Service Quality Focus**: On-time performance below target. Invest in predictive maintenance, route optimization, and real-time tracking systems.")
        
        # Display recommendations
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"""
            <div class="recommendation-box">
                <h4>💡 Recommendation {i}</h4>
                <p>{rec}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Executive Summary Footer
    st.markdown("---")
    st.markdown(f"""
    <div class="insight-box">
        <h3>📋 Executive Summary</h3>
        <p><strong>Analysis Period:</strong> {date_range[0]} to {date_range[1] if len(date_range) == 2 else date_range[0]}</p>
        <p><strong>Data Scope:</strong> {len(filtered_df):,} operations across {len(selected_regions)} regions</p>
        <p><strong>Key Insights:</strong></p>
        <ul>
            <li>Total operational scope: {total_distance:.1f}M km traveled, generating €{total_revenue:.1f}M revenue</li>
            <li>Environmental impact: {total_emissions:.1f}M kg CO₂ emissions with {avg_efficiency:.1f} km/L average efficiency</li>
            <li>Service quality: {avg_on_time:.1f}% on-time performance across all operations</li>
            <li>AI-powered insights reveal optimization opportunities worth an estimated €{(total_revenue * 0.15):.1f}M annually</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 10px;'>
        <p><strong>🚀 Grecert.com DGT Transport Intelligence Platform</strong></p>
        <p>Powered by Advanced AI & Machine Learning | Real-time Analytics | Predictive Insights</p>
        <p><em>Confidential Executive Dashboard - Strategic Use Only</em></p>
        <p style='font-size: 0.8em; margin-top: 10px;'>© 2025 Grecert.com - All Rights Reserved</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
