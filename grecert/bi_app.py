import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.linear_model import LinearRegression
import warnings

warnings.filterwarnings('ignore')

# ========================================
# CONFIGURACIÓN PROFESIONAL
# ========================================

st.set_page_config(
    page_title="Grecert DGT España - Mapa Interactivo Verde",
    page_icon="🇪🇸",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'selected_region' not in st.session_state:
    st.session_state.selected_region = None

# ========================================
# TEMA CSS ENERGÍA VERDE PROFESIONAL
# ========================================

def load_green_energy_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        .main {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 50%, #f0fdf4 100%);
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        .spain-header {
            background: linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%);
            color: white;
            padding: 3rem 2rem;
            margin: -1rem -1rem 2rem -1rem;
            text-align: center;
            border-radius: 0 0 25px 25px;
            box-shadow: 0 12px 40px rgba(5, 150, 105, 0.3);
            position: relative;
        }
        
        .spain-header::before {
            content: '🇪🇸';
            position: absolute;
            top: 1rem;
            right: 2rem;
            font-size: 3rem;
            opacity: 0.3;
        }
        
        .spain-header h1 {
            font-size: 3.5rem;
            font-weight: 700;
            margin: 0;
            color: white !important;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        }
        
        .spain-header p {
            font-size: 1.4rem;
            margin: 1rem 0 0 0;
            color: rgba(255,255,255,0.95) !important;
        }
        
        .green-metric-card {
            background: linear-gradient(135deg, white 0%, #f0fdf4 100%);
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 8px 30px rgba(5, 150, 105, 0.15);
            border: 2px solid #a7f3d0;
            margin-bottom: 1.5rem;
            transition: all 0.4s ease;
            text-align: center;
            position: relative;
        }
        
        .green-metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: linear-gradient(90deg, #059669 0%, #10b981 50%, #34d399 100%);
        }
        
        .green-metric-card:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 15px 40px rgba(5, 150, 105, 0.25);
        }
        
        .metric-title {
            font-size: 0.9rem;
            color: #059669 !important;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.8rem;
        }
        
        .metric-value {
            font-size: 2.8rem;
            font-weight: 700;
            color: #064e3b !important;
            margin: 0.5rem 0;
        }
        
        .metric-delta {
            font-size: 1rem;
            font-weight: 600;
            padding: 0.4rem 1rem;
            border-radius: 25px;
            display: inline-block;
            margin-top: 0.5rem;
        }
        
        .metric-delta.positive {
            background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
            color: white !important;
        }
        
        .metric-delta.negative {
            background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
            color: white !important;
        }
        
        .green-insight-container {
            background: linear-gradient(135deg, white 0%, #f0fdf4 100%);
            border: 2px solid #a7f3d0;
            border-left: 6px solid #10b981;
            border-radius: 15px;
            padding: 2.5rem;
            margin: 2rem 0;
            box-shadow: 0 6px 25px rgba(16, 185, 129, 0.1);
        }
        
        .green-insight-container h4 {
            color: #059669 !important;
            font-weight: 600;
            font-size: 1.5rem;
            margin-bottom: 1.2rem;
        }
        
        .green-insight-container p,
        .green-insight-container li {
            color: #1f2937 !important;
            font-size: 1.1rem;
            line-height: 1.7;
        }
        
        .alert-success {
            background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
            border: 2px solid #10b981;
            color: #064e3b !important;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1.5rem 0;
        }
        
        .alert-warning {
            background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
            border: 2px solid #f59e0b;
            color: #92400e !important;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1.5rem 0;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 65px;
            padding: 0px 30px;
            background: linear-gradient(135deg, white 0%, #f0fdf4 100%) !important;
            border: 2px solid #a7f3d0 !important;
            border-radius: 15px 15px 0px 0px !important;
            color: #059669 !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
            color: white !important;
            box-shadow: 0 8px 25px rgba(5, 150, 105, 0.4);
        }
        
        .map-container {
            border: 3px solid #10b981;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 15px 50px rgba(16, 185, 129, 0.25);
            margin: 2rem 0;
            background: white;
        }
        
        .community-card {
            background: linear-gradient(135deg, white 0%, #f0fdf4 100%);
            border: 2px solid #a7f3d0;
            border-radius: 15px;
            padding: 1.8rem;
            margin: 1rem 0;
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.1);
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .community-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 30px rgba(16, 185, 129, 0.2);
        }
        
        .stMarkdown p, .stMarkdown li, .stMarkdown h1, .stMarkdown h2, 
        .stMarkdown h3, .stMarkdown h4 {
            color: #1f2937 !important;
        }
    </style>
    """, unsafe_allow_html=True)

load_green_energy_css()

# ========================================
# GEOJSON REAL DE ESPAÑA - COORDENADAS PRECISAS
# ========================================

SPAIN_REAL_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"NAME_1": "Andalucía", "codigo": "ES-AN"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-7.5, 36.0], [-6.8, 36.0], [-6.2, 36.1], [-5.6, 36.0], [-5.0, 36.1],
                    [-4.4, 36.2], [-3.8, 36.4], [-3.2, 36.6], [-2.6, 36.8], [-2.0, 37.1],
                    [-1.4, 37.4], [-0.8, 37.7], [-0.3, 38.0], [-0.5, 38.4], [-1.0, 38.7],
                    [-1.6, 38.9], [-2.2, 38.8], [-2.8, 38.6], [-3.4, 38.4], [-4.0, 38.2],
                    [-4.6, 38.0], [-<span class="cursor">█</span>
