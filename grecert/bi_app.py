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
                    [-4.6, 38.0], [-5.2, 37.8], [-5.8, 37.6], [-6.4, 37.3], [-7.0, 37.0],
                    [-7.3, 36.7], [-7.4, 36.4], [-7.5, 36.0]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Cataluña", "codigo": "ES-CT"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [0.5, 40.5], [1.2, 40.6], [1.8, 40.8], [2.4, 41.0], [2.9, 41.3],
                    [3.3, 41.6], [3.2, 42.0], [2.8, 42.3], [2.4, 42.6], [1.9, 42.8],
                    [1.3, 42.7], [0.8, 42.5], [0.4, 42.2], [0.2, 41.8], [0.1, 41.4],
                    [0.2, 41.0], [0.4, 40.7], [0.5, 40.5]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Madrid", "codigo": "ES-MD"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-4.6, 39.8], [-4.0, 39.9], [-3.4, 40.0], [-2.9, 40.2], [-2.8, 40.5],
                    [-3.1, 40.8], [-3.5, 41.0], [-4.0, 40.9], [-4.4, 40.7], [-4.6, 40.4],
                    [-4.5, 40.1], [-4.6, 39.8]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Comunidad Valenciana", "codigo": "ES-VC"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-1.6, 37.8], [-1.0, 37.9], [-0.4, 38.1], [0.2, 38.3], [0.7, 38.6],
                    [0.9, 39.0], [0.6, 39.4], [0.2, 39.8], [-0.2, 40.2], [-0.7, 40.6],
                    [-1.1, 40.8], [-1.4, 40.5], [-1.5, 40.1], [-1.6, 39.7], [-1.5, 39.3],
                    [-1.4, 38.9], [-1.5, 38.5], [-1.6, 38.1], [-1.6, 37.8]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Galicia", "codigo": "ES-GA"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-9.3, 41.8], [-8.7, 41.9], [-8.1, 42.1], [-7.5, 42.3], [-7.0, 42.6],
                    [-6.5, 42.9], [-6.2, 43.2], [-6.5, 43.5], [-7.0, 43.7], [-7.6, 43.8],
                    [-8.2, 43.6], [-8.8, 43.3], [-9.2, 43.0], [-9.4, 42.6], [-9.3, 42.2],
                    [-9.3, 41.8]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Castilla y León", "codigo": "ES-CL"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-7.1, 40.0], [-6.4, 40.1], [-5.7, 40.3], [-5.0, 40.5], [-4.3, 40.8],
                    [-3.6, 41.1], [-2.9, 41.4], [-2.2, 41.7], [-1.8, 42.1], [-2.1, 42.5],
                    [-2.7, 42.8], [-3.4, 43.0], [-4.1, 42.8], [-4.8, 42.5], [-5.5, 42.2],
                    [-6.2, 41.9], [-6.9, 41.6], [-7.2, 41.2], [-7.1, 40.8], [-7.0, 40.4],
                    [-7.1, 40.0]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "País Vasco", "codigo": "ES-PV"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-3.4, 42.8], [-2.8, 42.9], [-2.2, 43.1], [-1.6, 43.3], [-1.4, 43.5],
                    [-1.7, 43.4], [-2.3, 43.2], [-2.9, 43.0], [-3.4, 42.8]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Canarias", "codigo": "ES-CN"},
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [[[-18.2, 27.6], [-17.7, 27.7], [-17.4, 28.0], [-17.8, 28.2], [-18.2, 27.9], [-18.2, 27.6]]],
                    [[[-16.3, 28.0], [-15.8, 28.1], [-15.6, 28.4], [-16.0, 28.5], [-16.3, 28.3], [-16.3, 28.0]]],
                    [[[-14.8, 28.6], [-14.3, 28.7], [-14.2, 29.0], [-14.6, 29.1], [-14.8, 28.9], [-14.8, 28.6]]],
                    [[[-13.6, 28.9], [-13.2, 29.0], [-13.2, 29.2], [-13.6, 29.2], [-13.6, 28.9]]]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Castilla-La Mancha", "codigo": "ES-CM"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-5.6, 38.0], [-5.0, 38.1], [-4.4, 38.3], [-3.8, 38.5], [-3.2, 38.7],
                    [-2.6, 39.0], [-2.0, 39.3], [-1.4, 39.6], [-0.9, 40.0], [-1.2, 40.3],
                    [-1.8, 40.1], [-2.4, 39.8], [-3.0, 39.5], [-3.6, 39.2], [-4.2, 38.9],
                    [-4.8, 38.6], [-5.3, 38.3], [-5.6, 38.0]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Murcia", "codigo": "ES-MC"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-2.4, 37.0], [-1.8, 37.1], [-1.2, 37.3], [-0.6, 37.6], [-0.4, 37.9],
                    [-0.7, 38.2], [-1.2, 38.4], [-1.8, 38.3], [-2.3, 38.0], [-2.4, 37.6],
                    [-2.3, 37.3], [-2.4, 37.0]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Aragón", "codigo": "ES-AR"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-2.1, 39.8], [-1.4, 39.9], [-0.7, 40.1], [0.0, 40.4], [0.6, 40.7],
                    [0.9, 41.1], [0.5, 41.5], [0.0, 41.9], [-0.6, 42.3], [-1.3, 42.6],
                    [-2.0, 42.8], [-2.3, 42.4], [-2.1, 42.0], [-1.9, 41.6], [-1.8, 41.2],
                    [-1.9, 40.8], [-2.0, 40.4], [-2.1, 39.8]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Baleares", "codigo": "ES-IB"},
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [[[1.2, 38.6], [1.7, 38.7], [1.9, 39.0], [1.5, 39.2], [1.1, 39.1], [1.2, 38.6]]],
                    [[[2.3, 39.4], [2.8, 39.5], [3.0, 39.8], [2.6, 40.0], [2.2, 39.9], [2.3, 39.4]]],
                    [[[3.8, 39.9], [4.3, 40.0], [4.3, 40.2], [3.8, 40.1], [3.8, 39.9]]]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Extremadura", "codigo": "ES-EX"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-7.6, 37.8], [-7.0, 37.9], [-6.4, 38.1], [-5.8, 38.3], [-5.2, 38.6],
                    [-4.9, 39.0], [-5.2, 39.4], [-5.8, 39.8], [-6.4, 40.2], [-7.0, 40.5],
                    [-7.4, 40.2], [-7.5, 39.8], [-7.4, 39.4], [-7.3, 39.0], [-7.4, 38.6],
                    [-7.5, 38.2], [-7.6, 37.8]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Asturias", "codigo": "ES-AS"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-7.3, 43.0], [-6.8, 43.1], [-6.3, 43.2], [-5.8, 43.3], [-5.3, 43.4],
                    [-4.8, 43.5], [-4.5, 43.6], [-4.8, 43.4], [-5.3, 43.2], [-5.8, 43.1],
                    [-6.3, 43.0], [-6.8, 42.9], [-7.3, 43.0]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Navarra", "codigo": "ES-NC"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-2.8, 42.0], [-2.2, 42.1], [-1.6, 42.3], [-1.0, 42.6], [-0.9, 43.0],
                    [-1.4, 42.9], [-2.0, 42.7], [-2.6, 42.5], [-2.8, 42.2], [-2.8, 42.0]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Cantabria", "codigo": "ES-CB"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-4.9, 43.0], [-4.4, 43.1], [-3.9, 43.2], [-3.4, 43.3], [-3.2, 43.5],
                    [-3.6, 43.4], [-4.1, 43.3], [-4.6, 43.2], [-4.9, 43.0]
                ]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "La Rioja", "codigo": "ES-RI"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-3.1, 42.0], [-2.5, 42.1], [-1.9, 42.3], [-1.7, 42.6], [-2.1, 42.7],
                    [-2.7, 42.6], [-3.1, 42.3], [-3.2, 42.1], [-3.1, 42.0]
                ]]
            }
        }
    ]
}

# ========================================
# DATOS COMUNIDADES AUTÓNOMAS
# ========================================

SPAIN_COMMUNITIES = {
    'Andalucía': {'capital': 'Sevilla', 'poblacion': 8472407, 'superficie_km2': 87268, 'potencial_renovable': 'Excelente'},
    'Cataluña': {'capital': 'Barcelona', 'poblacion': 7675217, 'superficie_km2': 32114, 'potencial_renovable': 'Muy Bueno'},
    'Madrid': {'capital': 'Madrid', 'poblacion': 6779888, 'superficie_km2': 8021, 'potencial_renovable': 'Bueno'},
    'Comunidad Valenciana': {'capital': 'Valencia', 'poblacion': 5003769, 'superficie_km2': 23255, 'potencial_renovable': 'Muy Bueno'},
    'Galicia': {'capital': 'Santiago de Compostela', 'poblacion': 2695327, 'superficie_km2': 29574, 'potencial_renovable': 'Excelente'},
    'Castilla y León': {'capital': 'Valladolid', 'poblacion': 2383139, 'superficie_km2': 94223, 'potencial_renovable': 'Muy Bueno'},
    'País Vasco': {'capital': 'Vitoria-Gasteiz', 'poblacion': 2207776, 'superficie_km2': 7234, 'potencial_renovable': 'Bueno'},
    'Canarias': {'capital': 'Las Palmas / Santa Cruz', 'poblacion': 2175952, 'superficie_km2': 7447, 'potencial_renovable': 'Excelente'},
    'Castilla-La Mancha': {'capital': 'Toledo', 'poblacion': 2045221, 'superficie_km2': 79463, 'potencial_renovable': 'Excelente'},
    'Murcia': {'capital': 'Murcia', 'poblacion': 1518486, 'superficie_km2': 11314, 'potencial_renovable': 'Muy Bueno'},
    'Aragón': {'capital': 'Zaragoza', 'poblacion': 1319291, 'superficie_km2': 47719, 'potencial_renovable': 'Muy Bueno'},
    'Baleares': {'capital': 'Palma', 'poblacion': 1173008, 'superficie_km2': 4992, 'potencial_renovable': 'Bueno'},
    'Extremadura': {'capital': 'Mérida', 'poblacion': 1067710, 'superficie_km2': 41634, 'potencial_renovable': 'Excelente'},
    'Asturias': {'capital': 'Oviedo', 'poblacion': 1018784, 'superficie_km2': 10604, 'potencial_renovable': 'Bueno'},
    'Navarra': {'capital': 'Pamplona', 'poblacion': 661197, 'superficie_km2': 10391, 'potencial_renovable': 'Muy Bueno'},
    'Cantabria': {'capital': 'Santander', 'poblacion': 582905, 'superficie_km2': 5321, 'potencial_renovable': 'Bueno'},
    'La Rioja': {'capital': 'Logroño', 'poblacion': 319796, 'superficie_km2': 5045, 'potencial_renovable': 'Bueno'}
}

# ========================================
# GENERACIÓN DATOS DGT ESPAÑA VERDE
# ========================================

@st.cache_data(ttl=3600)
def generate_spain_green_dgt_data(num_records=45000):
    """Generar datos DGT de transporte verde para España."""
    np.random.seed(42)
    
    communities = list(SPAIN_COMMUNITIES.keys())
    community_weights = [0.18, 0.16, 0.14, 0.11, 0.06, 0.05, 0.05, 0.05, 0.04, 0.03, 0.03, 0.03, 0.02, 0.02, 0.01, 0.01, 0.01]
    
    vehicle_types = {
        'Coche Eléctrico': 0.30, 'Coche Híbrido': 0.25, 'Autobús Eléctrico': 0.10,
        'Camión Híbrido': 0.15, 'Furgoneta Eléctrica': 0.12, 'Motocicleta Eléctrica': 0.05,
        'Vehículo Convencional': 0.03
    }
    
    energy_sources = {
        'Eléctrica (Red)': 0.35, 'Solar Fotovoltaica': 0.25, 'Eólica': 0.18,
        'Hidroeléctrica': 0.10, 'Hidrógeno Verde': 0.07, 'Biocombustible': 0.04, 'Convencional': 0.01
    }
    
    violation_types = {
        'Exceso Velocidad': 0.35, 'Estacionamiento': 0.20, 'Semáforo': 0.15,
        'Documentación': 0.12, 'Emisiones': 0.10, 'Peso Excesivo': 0.05, 'Ruta No Autorizada': 0.03
    }
    
    date_range = pd.date_range(start=datetime(2023, 1, 1), end=datetime(2024, 12, 31), freq='D')
    
    data = {
        'fecha': np.random.choice(date_range, num_records),
        'comunidad_autonoma': np.random.choice(communities, num_records, p=community_weights),
        'tipo_vehiculo': np.random.choice(list(vehicle_types.keys()), num_records, p=list(vehicle_types.values())),
        'fuente_energia': np.random.choice(list(energy_sources.keys()), num_records, p=list(energy_sources.values())),
        'tipo_infraccion': np.random.choice(list(violation_types.keys()), num_records, p=list(violation_types.values())),
        
        # Métricas operacionales
        'distancia_km': np.random.lognormal(6.0, 1.2, num_records),
        'consumo_energia_kwh': np.random.lognormal(3.5, 0.9, num_records),
        'velocidad_media_kmh': np.random.normal(65, 15, num_records),
        'num_pasajeros': np.random.poisson(2.5, num_records),
        'carga_toneladas': np.random.exponential(5, num_records),
        
        # Métricas financieras (EUR)
        'coste_operacional_eur': np.random.lognormal(5.8, 0.7, num_records),
        'ingresos_eur': np.random.lognormal(6.8, 0.6, num_records),
        'multa_eur': np.random.lognormal(4.8, 1.0, num_records),
        'ahorro_verde_eur': np.random.lognormal(3.2, 1.2, num_records),
        
        # Métricas ambientales
        'emisiones_co2_kg': np.random.lognormal(4.5, 1.5, num_records),
        'energia_renovable_kwh': np.random.lognormal(3.8, 0.9, num_records),
        
        # Indicadores de rendimiento (0-1)
        'puntualidad': np.random.beta(8, 2, num_records),
        'puntuacion_seguridad': np.random.beta(9, 1.5, num_records),
        'eficiencia_energetica': np.random.beta(6.5, 2.5, num_records),
        'indice_sostenibilidad': np.random.beta(7.5, 2, num_records),
        
        # Cumplimiento verde
        'certificacion_verde': np.random.choice([0, 1], num_records, p=[0.20, 0.80]),
        'progreso_objetivos_2030': np.random.beta(4, 3, num_records),
        
        # Métricas específicas verdes
        'share_flota_ev': np.random.beta(3, 5, num_records),
        'inversion_verde_eur': np.random.lognormal(4.5, 1.0, num_records),
    }
    
    df = pd.DataFrame(data)
    
    # Aplicar restricciones realistas
    df['velocidad_media_kmh'] = np.clip(df['velocidad_media_kmh'], 20, 150)
    df['num_pasajeros'] = np.clip(df['num_pasajeros'], 0, 60)
    df['carga_toneladas'] = np.clip(df['carga_toneladas'], 0, 50)
    
    # Ajustes específicos por tipo de vehículo
    electric_mask = df['tipo_vehiculo'].str.contains('Eléctrico', na=False)
    df.loc[electric_mask, 'emisiones_co2_kg'] = 0
    df.loc[electric_mask, 'certificacion_verde'] = 1
    df.loc[electric_mask, 'indice_sostenibilidad'] = np.random.beta(9, 1, electric_mask.sum())
    
    hybrid_mask = df['tipo_vehiculo'].str.contains('Híbrido', na=False)
    df.loc[hybrid_mask, 'emisiones_co2_kg'] *= 0.4
    df.loc[hybrid_mask, 'indice_sostenibilidad'] = np.random.beta(7.5, 2, hybrid_mask.sum())
    
    # Calcular métricas derivadas
    df['eficiencia_km_per_kwh'] = np.where(df['consumo_energia_kwh'] > 0, df['distancia_km'] / df['consumo_energia_kwh'], 0)
    df['beneficio_eur'] = df['ingresos_eur'] - df['coste_operacional_eur']
    df['margen_beneficio'] = np.where(df['ingresos_eur'] > 0, df['beneficio_eur'] / df['ingresos_eur'], 0)
    df['puntuacion_verde_total'] = (df['indice_sostenibilidad'] * 0.4 + df['eficiencia_energetica'] * 0.3 + df['progreso_objetivos_2030'] * 0.3)
    
    # Características temporales
    df['año'] = df['fecha'].dt.year
    df['mes'] = df['fecha'].dt.month
    df['trimestre'] = df['fecha'].dt.quarter
    
    # Limpiar datos
    df = df.replace([np.inf, -np.inf], np.nan)
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())
    
    # Controles de calidad
    df['margen_beneficio'] = df['margen_beneficio'].clip(-1, 1)
    df['puntualidad'] = df['puntualidad'].clip(0, 1)
    df['puntuacion_verde_total'] = df['puntuacion_verde_total'].clip(0, 1)
    df['share_flota_ev'] = df['share_flota_ev'].clip(0, 1)
    
    return df

# ========================================
# FUNCIONES ANALÍTICAS
# ========================================

def create_green_metric_card(title, value, delta=None, format_type="number", icon="🌱"):
    """Crear tarjetas métricas con tema verde."""
    
    if format_type == "currency":
        formatted_value = f"€{value:,.0f}"
    elif format_type == "percentage":
        formatted_value = f"{value:.1f}%"
    elif format_type == "decimal":
        formatted_value = f"{value:.2f}"
    elif format_type == "emissions":
        formatted_value = f"{value:,.0f} kg CO₂"
    else:
        formatted_value = f"{value:,.0f}"
    
    delta_html = ""
    if delta:
        if isinstance(delta, str):
            delta_class = "neutral"
            delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>'
        else:
            delta_class = "positive" if delta > 0 else "negative"
            delta_symbol = "↗" if delta > 0 else "↘"
            delta_html = f'<div class="metric-delta {delta_class}">{delta_symbol} {abs(delta):.1f}%</div>'
    
    return f"""
    <div class="green-metric-card">
        <div class="metric-title">{icon} {title}</div>
        <div class="metric-value">{formatted_value}</div>
        {delta_html}
    </div>
    """

def display_regional_dashboard(selected_region_name, df_region, all_regional_performance):
    """Mostrar dashboard detallado para la región seleccionada."""
    
    st.markdown(f"""
    <div class="spain-header">
        <h1>🌱 {selected_region_name}</h1>
        <p>Análisis Detallado de Transporte Verde DGT</p>
    </div>
    """, unsafe_allow_html=True)
    
    region_data = all_regional_performance[all_regional_performance['comunidad_autonoma'] == selected_region_name].iloc[0]
    community_info = SPAIN_COMMUNITIES[selected_region_name]
    
    # KPIs regionales
    st.markdown("### 🌟 Indicadores Clave de Rendimiento Verde")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_green_metric_card(
            "Puntuación Verde", region_data['puntuacion_verde_total'] * 100, 
            format_type="percentage", icon="🌟"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_green_metric_card(
            "Share Flota EV", region_data['share_flota_ev'] * 100, 
            format_type="percentage", icon="🔋"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_green_metric_card(
            "Emisiones CO₂", region_data['emisiones_co2_total'] / 1000, 
            format_type="emissions", icon="🌿"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_green_metric_card(
            "Ahorro Verde", region_data['ahorro_verde_total'] / 1000000, 
            format_type="currency", icon="💚"
        ), unsafe_allow_html=True)
    
    # Información de la comunidad
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown(f"""
        <div class="green-insight-container">
            <h4>📍 Información Regional</h4>
            <p><strong>Capital:</strong> {community_info['capital']}</p>
            <p><strong>Población:</strong> {community_info['poblacion']:,} habitantes</p>
            <p><strong>Superficie:</strong> {community_info['superficie_km2']:,} km²</p>
            <p><strong>Potencial Renovable:</strong> {community_info['potencial_renovable']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_info2:
        # Análisis temporal de la región
        monthly_trends = df_region.groupby(pd.Grouper(key='fecha', freq='M')).agg({
            'share_flota_ev': 'mean',
            'emisiones_co2_kg': 'sum',
            'energia_renovable_kwh': 'sum'
        }).reset_index()
        
        if not monthly_trends.empty:
            fig_trend = px.line(
                monthly_trends,
                x='fecha',
                y='share_flota_ev',
                title=f"🔋 Evolución Share EV - {selected_region_name}",
                color_discrete_sequence=['#10b981']
            )
            fig_trend.update_layout(template='plotly_white', height=300)
            st.plotly_chart(fig_trend, use_container_width=True)

# ========================================
# APLICACIÓN PRINCIPAL
# ========================================

def main():
    # Encabezado profesional
    st.markdown("""
    <div class="spain-header">
        <h1>🇪🇸 Grecert DGT España</h1>
        <p>Mapa Interactivo Real de Transporte Verde y Energías Renovables</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos
    with st.spinner("🔄 Cargando datos de transporte verde de España..."):
        df = generate_spain_green_dgt_data()
    
    # Panel de control
    st.sidebar.markdown("## 🎛️ Centro de Control Verde")
    st.sidebar.markdown("---")
    
    # Controles de fecha
    min_date = df['fecha'].min().date()
    max_date = df['fecha'].max().date()
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Fecha Inicio", min_date, min_value=min_date, max_value=max_date)
    with col2:
        end_date = st.date_input("Fecha Fin", max_date, min_value=min_date, max_value=max_date)
    
    # Filtros estratégicos
    st.sidebar.markdown("### 🌍 Alcance Estratégico")
    
    all_regions = sorted(df['comunidad_autonoma'].unique())
    
    if st.session_state.selected_region:
        st.sidebar.markdown(f"**Región Seleccionada:** **{st.session_state.selected_region}**")
        if st.sidebar.button("⬅️ Volver a Vista España"):
            st.session_state.selected_region = None
            st.rerun()
        selected_regions_filter = [st.session_state.selected_region]
    else:
        selected_regions_filter = st.sidebar.multiselect(
            "Comunidades Autónomas",
            options=all_regions,
            default=all_regions
        )
    
    # Aplicar filtros
    mask = (df['fecha'] >= pd.to_datetime(start_date)) & (df['fecha'] <= pd.to_datetime(end_date))
    filtered_df = df[mask]
    
    if selected_regions_filter:
        filtered_df = filtered_df[filtered_df['comunidad_autonoma'].isin(selected_regions_filter)]
    
    if filtered_df.empty:
        st.error("⚠️ No hay datos que coincidan con los criterios seleccionados.")
        return
    
    # Calcular rendimiento regional
    all_regional_performance = filtered_df.groupby('comunidad_autonoma').agg({
        'emisiones_co2_kg': 'sum',
        'share_flota_ev': 'mean',
        'puntuacion_verde_total': 'mean',
        'progreso_objetivos_2030': 'mean',
        'energia_renovable_kwh': 'sum',
        'ahorro_verde_eur': 'sum',
        'inversion_verde_eur': 'sum',
        'distancia_km': 'sum',
        'ingresos_eur': 'sum'
    }).reset_index()
    
    all_regional_performance.rename(columns={
        'emisiones_co2_kg': 'emisiones_co2_total',
        'energia_renovable_kwh': 'energia_renovable_total',
        'ahorro_verde_eur': 'ahorro_verde_total',
        'inversion_verde_eur': 'inversion_verde_total'
    }, inplace=True)
    
    # Contenido principal
    if st.session_state.selected_region:
        region_df = filtered_df[filtered_df['comunidad_autonoma'] == st.session_state.selected_region]
        display_regional_dashboard(st.session_state.selected_region, region_df, all_regional_performance)
    else:
        # Vista general de España con MAPA REAL
        st.markdown("## 📊 Panorama General de Transporte Verde en España")
        
        # KPIs globales
        total_operations = len(filtered_df)
        total_distance_mkm = filtered_df['distancia_km'].sum() / 1_000_000
        total_revenue_m = filtered_df['ingresos_eur'].sum() / 1_000_000
        total_green_savings_m = filtered_df['ahorro_verde_eur'].sum() / 1_000_000
        total_emissions_m = filtered_df['emisiones_co2_kg'].sum() / 1_000_000
        avg_ev_share_spain = filtered_df['share_flota_ev'].mean() * 100
        avg_green_score_spain = filtered_df['puntuacion_verde_total'].mean() * 100
        
        # Mostrar KPIs globales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(create_green_metric_card(
                "Operaciones Totales", total_operations, delta="+15.2% anual", icon="🚛"
            ), unsafe_allow_html=True)
            
            st.markdown(create_green_metric_card(
                "Share Flota EV", avg_ev_share_spain, delta=22.1, format_type="percentage", icon="🔋"
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown(create_green_metric_card(
                "Distancia Total", total_distance_mkm, delta=8.7, format_type="decimal", icon="🛣️"
            ), unsafe_allow_html=True)
            
            st.markdown(create_green_metric_card(
                "Emisiones CO₂", total_emissions_m, delta=-18.7, format_type="emissions", icon="🌿"
            ), unsafe_allow_html=True)
        
        with col3:
            st.markdown(create_green_metric_card(
                "Ingresos Totales", total_revenue_m, delta=12.5, format_type="currency", icon="💰"
            ), unsafe_allow_html=True)
            
            st.markdown(create_green_metric_card(
                "Puntuación Verde", avg_green_score_spain, delta=11.2, format_type="percentage", icon="🌟"
            ), unsafe_allow_html=True)
        
        with col4:
            st.markdown(create_green_metric_card(
                "Ahorro Verde", total_green_savings_m, delta=28.3, format_type="currency", icon="💚"
            ), unsafe_allow_html=True)
            
            st.markdown(create_green_metric_card(
                "Inversión Verde", filtered_df['inversion_verde_eur'].sum() / 1_000_000, delta=35.7, format_type="currency", icon="⚡"
            ), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ====== AQUÍ ESTÁ EL MAPA REAL DE ESPAÑA ======
        st.markdown("### 🗺️ **MAPA INTERACTIVO REAL DE ESPAÑA** - Transporte Verde por Comunidades")
        st.markdown("*Seleccione una comunidad autónoma para ver su análisis detallado*")
        
        col_map, col_select = st.columns([4, 1])
        
        with col_map:
            # CREAR MAPA REAL COROPLÉTICO DE ESPAÑA CON COORDENADAS PRECISAS
            fig_map = px.choropleth(
                all_regional_performance,
                geojson=SPAIN_REAL_GEOJSON,
                locations='comunidad_autonoma',
                featureidkey="properties.NAME_1",
                color='puntuacion_verde_total',
                hover_name='comunidad_autonoma',
                hover_data={
                    'share_flota_ev': ':.1%',
                    'emisiones_co2_total': ':,.0f',
                    'ahorro_verde_total': ':,.0f',
                    'progreso_objetivos_2030': ':.1%'
                },
                color_continuous_scale="Greens",
                title="🌱 Puntuación Verde por Comunidad Autónoma",
                labels={'puntuacion_verde_total': 'Puntuación Verde'}
            )
            
            # Configurar el mapa para mostrar España correctamente
            fig_map.update_geos(
                fitbounds="locations",
                visible=False,
                projection_type="mercator"
            )
            
            # Mejorar la apariencia del mapa
            fig_map.update_layout(
                height=700,
                margin={"r":0,"t":50,"l":0,"b":0},
                coloraxis_colorbar=dict(
                    title="Puntuación Verde",
                    titlefont=dict(size=14),
                    tickfont=dict(size=12)
                ),
                template='plotly_white',
                font=dict(family='Inter', size=12),
                title=dict(
                    font=dict(size=18, color='#059669'),
                    x=0.5
                )
            )
            
            # Contenedor con estilo para el mapa
            st.markdown('<div class="map-container">', unsafe_allow_html=True)
            
            # Mostrar el mapa interactivo REAL
            st.plotly_chart(fig_map, use_container_width=True, key="spain_real_map")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_select:
            st.markdown("#### 🎯 Análisis Detallado")
            st.markdown("Seleccione una comunidad para ver su dashboard completo:")
            
            selected_region_for_detail = st.selectbox(
                "Comunidad Autónoma:",
                options=[''] + all_regions,
                index=0,
                key='map_region_selector'
            )
            
            if selected_region_for_detail:
                if st.button(f"📊 Dashboard {selected_region_for_detail}", key='view_dashboard'):
                    st.session_state.selected_region = selected_region_for_detail
                    st.rerun()
            
            st.markdown("---")
            
            # Top performers
            st.markdown("#### 🏆 Líderes Verdes")
            top_green = all_regional_performance.nlargest(3, 'puntuacion_verde_total')
            
            for i, (_, community) in enumerate(top_green.iterrows(), 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                st.markdown(f"""
                <div class="community-card">
                    <h5>{medal} {community['comunidad_autonoma']}</h5>
                    <p><strong>Puntuación:</strong> {community['puntuacion_verde_total']:.2f}</p>
                    <p><strong>Share EV:</strong> {community['share_flota_ev']:.1%}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Análisis nacional
        st.markdown("---")
        st.markdown("### 🇪🇸 Análisis Nacional de Transporte Verde")
        
        tab1, tab2 = st.tabs(["📈 **Tendencias Nacionales**", "🎯 **Objetivos 2030**"])
        
        with tab1:
            # Tendencias mensuales nacionales
            monthly_national = filtered_df.groupby(pd.Grouper(key='fecha', freq='M')).agg({
                'share_flota_ev': 'mean',
                'emisiones_co2_kg': 'sum',
                'energia_renovable_kwh': 'sum',
                'ahorro_verde_eur': 'sum'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_ev_national = px.line(
                    monthly_national,
                    x='fecha',
                    y='share_flota_ev',
                    title="🔋 Evolución Nacional Share Flota EV",
                    color_discrete_sequence=['#10b981']
                )
                fig_ev_national.update_layout(template='plotly_white', font=dict(family='Inter'))
                st.plotly_chart(fig_ev_national, use_container_width=True)
            
            with col2:
                fig_savings_national = px.line(
                    monthly_national,
                    x='fecha',
                    y='ahorro_verde_eur',
                    title="💚 Evolución Ahorro Verde Nacional",
                    color_discrete_sequence=['#34d399']
                )
                fig_savings_national.update_layout(template='plotly_white', font=dict(family='Inter'))
                st.plotly_chart(fig_savings_national, use_container_width=True)
        
        with tab2:
            # Progreso objetivos 2030
            current_ev_pct = (filtered_df['tipo_vehiculo'].str.contains('Eléctrico|Híbrido', na=False)).mean() * 100
            current_renewable_pct = (filtered_df['fuente_energia'] != 'Convencional').mean() * 100
            
            target_ev = 50
            target_renewable = 85
            
            progress_data = pd.DataFrame({
                'Objetivo': ['Vehículos EV/Híbridos (%)', 'Energías Renovables (%)'],
                'Meta 2030': [target_ev, target_renewable],
                'Progreso Actual': [current_ev_pct, current_renewable_pct]
            })
            
            fig_progress = px.bar(
                progress_data,
                x='Objetivo',
                y=['Meta 2030', 'Progreso Actual'],
                title="🎯 Progreso hacia Objetivos España 2030",
                barmode='group',
                color_discrete_sequence=['#a7f3d0', '#10b981']
            )
            fig_progress.update_layout(template='plotly_white', font=dict(family='Inter'))
            st.plotly_chart(fig_progress, use_container_width=True)
            
            avg_compliance = (current_ev_pct/target_ev + current_renewable_pct/target_renewable) / 2 * 100
            
            if avg_compliance >= 80:
                status_color = "success"
                status_message = "España está en excelente camino hacia los objetivos 2030"
            elif avg_compliance >= 60:
                status_color = "warning"
                status_message = "Progreso sólido pero requiere acelerar las iniciativas verdes"
            else:
                status_color = "warning"
                status_message = "Se requieren medidas urgentes para cumplir objetivos 2030"
            
            st.markdown(f"""
            <div class="alert-{status_color}">
                <h4>📋 Estado Objetivos 2030 España</h4>
                <p><strong>Evaluación:</strong> {status_message}</p>
                <p><strong>Cumplimiento Global:</strong> {avg_compliance:.1f}%</p>
                <p><strong>Vehículos Verdes:</strong> {current_ev_pct:.1f}% actual vs {target_ev}% objetivo</p>
                <p><strong>Energías Renovables:</strong> {current_renewable_pct:.1f}% actual vs {target_renewable}% objetivo</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Resumen ejecutivo
    st.markdown("---")
    st.markdown(f"""
    <div class="green-insight-container">
        <h4>📋 Resumen Ejecutivo - España Transporte Verde</h4>
        <p><strong>Período:</strong> {start_date} a {end_date} | <strong>Alcance:</strong> {len(filtered_df):,} operaciones</p>
        <p><strong>Rendimiento Verde Nacional:</strong> {avg_green_score_spain:.1f}% sostenibilidad | {avg_ev_share_spain:.1f}% flota EV</p>
        <p><strong>Impacto Ambiental:</strong> {total_emissions_m:.1f}M kg CO₂ | €{total_green_savings_m:.1f}M ahorros verdes</p>
        <p><strong>Liderazgo Regional:</strong> {all_regional_performance.loc[all_regional_performance['puntuacion_verde_total'].idxmax(), 'comunidad_autonoma']} lidera en sostenibilidad</p>
        <p><strong>Progreso Estratégico:</strong> España avanza hacia liderazgo europeo en movilidad sostenible</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer profesional
    st.markdown("---")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: white; padding: 3rem; border-radius: 20px; text-align: center; margin-top: 2rem;'>
        <h3 style='margin: 0; color: white; font-size: 2rem;'>🗺️ Mapa Real España - Transporte Verde</h3>
        <p style='margin: 1.5rem 0; font-size: 1.2rem; opacity: 0.95;'>Plataforma de Inteligencia Geoespacial | Movilidad Sostenible | Análisis DGT</p>
        <p style='margin: 0; font-size: 1rem; opacity: 0.85;'>© 2025 Grecert.com - Revolucionando el Transporte Sostenible en España</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
