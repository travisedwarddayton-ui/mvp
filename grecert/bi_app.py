import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import warnings

warnings.filterwarnings('ignore')

# ========================================
# CONFIGURACIÓN PROFESIONAL
# ========================================

st.set_page_config(
    page_title="Grecert DGT España - Transporte Verde",
    page_icon="🇪🇸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar estado de sesión
if 'selected_region' not in st.session_state:
    st.session_state.selected_region = None

# ========================================
# TEMA CSS ENERGÍA VERDE PROFESIONAL
# ========================================

def load_green_energy_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Configuración Global Verde */
        .main {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 50%, #f0fdf4 100%);
            color: #1f2937;
        }
        
        /* Ocultar marca Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Encabezado España Verde */
        .spain-header {
            background: linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%);
            color: white;
            padding: 3rem 2rem;
            margin: -1rem -1rem 2rem -1rem;
            text-align: center;
            border-radius: 0 0 25px 25px;
            box-shadow: 0 12px 40px rgba(5, 150, 105, 0.3);
            position: relative;
            overflow: hidden;
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
            font-weight: 400;
        }
        
        /* Tarjetas Métricas Verde */
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
            overflow: hidden;
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
            border-color: #10b981;
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
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
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
        
        .metric-delta.neutral {
            background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
            color: white !important;
        }
        
        /* Contenedores de Insights Verde */
        .green-insight-container {
            background: linear-gradient(135deg, white 0%, #f0fdf4 100%);
            border: 2px solid #a7f3d0;
            border-left: 6px solid #10b981;
            border-radius: 15px;
            padding: 2.5rem;
            margin: 2rem 0;
            box-shadow: 0 6px 25px rgba(16, 185, 129, 0.1);
            position: relative;
        }
        
        .green-insight-container::before {
            content: '🌱';
            position: absolute;
            top: 1.5rem;
            right: 2rem;
            font-size: 2.5rem;
            opacity: 0.4;
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
        
        .green-insight-container strong {
            color: #059669 !important;
            font-weight: 600;
        }
        
        /* Contenedores de Recomendaciones */
        .green-recommendation-container {
            background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
            border: 2px solid #6ee7b7;
            border-left: 6px solid #10b981;
            border-radius: 15px;
            padding: 2.5rem;
            margin: 2rem 0;
            box-shadow: 0 8px 30px rgba(16, 185, 129, 0.15);
            position: relative;
        }
        
        .green-recommendation-container::before {
            content: '⚡';
            position: absolute;
            top: 1.5rem;
            right: 2rem;
            font-size: 2.5rem;
            opacity: 0.5;
        }
        
        .green-recommendation-container h4 {
            color: #047857 !important;
            font-weight: 600;
            font-size: 1.5rem;
            margin-bottom: 1.2rem;
        }
        
        .green-recommendation-container p,
        .green-recommendation-container li {
            color: #1f2937 !important;
            font-size: 1.1rem;
            line-height: 1.7;
        }
        
        /* Alertas Verde */
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
        
        .alert-danger {
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            border: 2px solid #ef4444;
            color: #991b1b !important;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1.5rem 0;
        }
        
        /* Pestañas Verde */
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
            background: transparent;
            margin-bottom: 2rem;
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
            transition: all 0.3s ease !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, #a7f3d0 0%, #6ee7b7 100%) !important;
            color: white !important;
            transform: translateY(-3px);
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
            color: white !important;
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(5, 150, 105, 0.4);
        }
        
        /* Sidebar Verde */
        .css-1d391kg {
            background: linear-gradient(135deg, #064e3b 0%, #059669 100%);
        }
        
        /* Contenedor Mapa */
        .map-container {
            border: 3px solid #10b981;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(16, 185, 129, 0.2);
            margin: 2rem 0;
        }
        
        /* Tarjetas Comunidad */
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
            border-color: #10b981;
        }
        
        /* Texto legible */
        .stMarkdown p,
        .stMarkdown li,
        .stMarkdown h1,
        .stMarkdown h2,
        .stMarkdown h3,
        .stMarkdown h4 {
            color: #1f2937 !important;
        }
        
        /* Diseño Responsivo */
        @media (max-width: 768px) {
            .spain-header h1 {
                font-size: 2.5rem;
            }
            .green-metric-card {
                padding: 1.5rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

load_green_energy_css()

# ========================================
# DATOS COMUNIDADES AUTÓNOMAS ESPAÑOLAS
# ========================================

SPAIN_COMMUNITIES = {
    'Andalucía': {
        'capital': 'Sevilla',
        'poblacion': 8472407,
        'superficie_km2': 87268,
        'potencial_renovable': 'Excelente',
        'renovables_principales': ['Solar', 'Eólica', 'Biomasa'],
        'coordenadas': [37.3886, -5.9823]
    },
    'Cataluña': {
        'capital': 'Barcelona',
        'poblacion': 7675217,
        'superficie_km2': 32114,
        'potencial_renovable': 'Muy Bueno',
        'renovables_principales': ['Solar', 'Eólica', 'Hidráulica'],
        'coordenadas': [41.3851, 2.1734]
    },
    'Madrid': {
        'capital': 'Madrid',
        'poblacion': 6779888,
        'superficie_km2': 8021,
        'potencial_renovable': 'Bueno',
        'renovables_principales': ['Solar', 'Biomasa'],
        'coordenadas': [40.4168, -3.7038]
    },
    'Comunidad Valenciana': {
        'capital': 'Valencia',
        'poblacion': 5003769,
        'superficie_km2': 23255,
        'potencial_renovable': 'Muy Bueno',
        'renovables_principales': ['Solar', 'Eólica'],
        'coordenadas': [39.4699, -0.3763]
    },
    'Galicia': {
        'capital': 'Santiago de Compostela',
        'poblacion': 2695327,
        'superficie_km2': 29574,
        'potencial_renovable': 'Excelente',
        'renovables_principales': ['Eólica', 'Hidráulica', 'Biomasa'],
        'coordenadas': [42.8805, -8.5456]
    },
    'Castilla y León': {
        'capital': 'Valladolid',
        'poblacion': 2383139,
        'superficie_km2': 94223,
        'potencial_renovable': 'Muy Bueno',
        'renovables_principales': ['Eólica', 'Solar', 'Biomasa'],
        'coordenadas': [41.6518, -4.7245]
    },
    'País Vasco': {
        'capital': 'Vitoria-Gasteiz',
        'poblacion': 2207776,
        'superficie_km2': 7234,
        'potencial_renovable': 'Bueno',
        'renovables_principales': ['Eólica', 'Hidráulica'],
        'coordenadas': [42.8467, -2.6716]
    },
    'Canarias': {
        'capital': 'Las Palmas / Santa Cruz',
        'poblacion': 2175952,
        'superficie_km2': 7447,
        'potencial_renovable': 'Excelente',
        'renovables_principales': ['Solar', 'Eólica', 'Geotérmica'],
        'coordenadas': [28.2916, -16.6291]
    },
    'Castilla-La Mancha': {
        'capital': 'Toledo',
        'poblacion': 2045221,
        'superficie_km2': 79463,
        'potencial_renovable': 'Excelente',
        'renovables_principales': ['Solar', 'Eólica'],
        'coordenadas': [39.8628, -4.0273]
    },
    'Murcia': {
        'capital': 'Murcia',
        'poblacion': 1518486,
        'superficie_km2': 11314,
        'potencial_renovable': 'Muy Bueno',
        'renovables_principales': ['Solar', 'Biomasa'],
        'coordenadas': [37.9922, -1.1307]
    },
    'Aragón': {
        'capital': 'Zaragoza',
        'poblacion': 1319291,
        'superficie_km2': 47719,
        'potencial_renovable': 'Muy Bueno',
        'renovables_principales': ['Eólica', 'Solar', 'Hidráulica'],
        'coordenadas': [41.6488, -0.8891]
    },
    'Baleares': {
        'capital': 'Palma',
        'poblacion': 1173008,
        'superficie_km2': 4992,
        'potencial_renovable': 'Bueno',
        'renovables_principales': ['Solar', 'Eólica'],
        'coordenadas': [39.5696, 2.6502]
    },
    'Extremadura': {
        'capital': 'Mérida',
        'poblacion': 1067710,
        'superficie_km2': 41634,
        'potencial_renovable': 'Excelente',
        'renovables_principales': ['Solar', 'Biomasa'],
        'coordenadas': [38.9165, -6.3425]
    },
    'Asturias': {
        'capital': 'Oviedo',
        'poblacion': 1018784,
        'superficie_km2': 10604,
        'potencial_renovable': 'Bueno',
        'renovables_principales': ['Hidráulica', 'Eólica', 'Biomasa'],
        'coordenadas': [43.3614, -5.8593]
    },
    'Navarra': {
        'capital': 'Pamplona',
        'poblacion': 661197,
        'superficie_km2': 10391,
        'potencial_renovable': 'Muy Bueno',
        'renovables_principales': ['Eólica', 'Solar', 'Hidráulica'],
        'coordenadas': [42.8125, -1.6458]
    },
    'Cantabria': {
        'capital': 'Santander',
        'poblacion': 582905,
        'superficie_km2': 5321,
        'potencial_renovable': 'Bueno',
        'renovables_principales': ['Hidráulica', 'Eólica'],
        'coordenadas': [43.4623, -3.8099]
    },
    'La Rioja': {
        'capital': 'Logroño',
        'poblacion': 319796,
        'superficie_km2': 5045,
        'potencial_renovable': 'Bueno',
        'renovables_principales': ['Eólica', 'Solar'],
        'coordenadas': [42.4627, -2.4449]
    }
}

# ========================================
# GENERACIÓN DE DATOS DGT ESPAÑA VERDE
# ========================================

@st.cache_data(ttl=3600)
def generate_spain_green_dgt_data(num_records=60000):
    """Generar datos DGT de transporte verde para España."""
    np.random.seed(42)
    
    # Comunidades con pesos realistas
    communities = list(SPAIN_COMMUNITIES.keys())
    community_weights = [
        0.18, 0.16, 0.14, 0.11, 0.06, 0.05, 0.05, 0.05, 0.04, 0.03,
        0.03, 0.03, 0.02, 0.02, 0.01, 0.01, 0.01
    ]
    
    # Tipos de vehículos verdes
    vehicle_types = {
        'Coche Eléctrico': 0.30,
        'Coche Híbrido': 0.25,
        'Autobús Eléctrico': 0.10,
        'Camión Híbrido': 0.15,
        'Furgoneta Eléctrica': 0.12,
        'Motocicleta Eléctrica': 0.05,
        'Vehículo Convencional': 0.03
    }
    
    # Fuentes de energía verde
    energy_sources = {
        'Eléctrica (Red)': 0.35,
        'Solar Fotovoltaica': 0.25,
        'Eólica': 0.18,
        'Hidroeléctrica': 0.10,
        'Hidrógeno Verde': 0.07,
        'Biocombustible': 0.04,
        'Convencional': 0.01
    }
    
    # Tipos de infracciones DGT
    violation_types = {
        'Exceso Velocidad': 0.35,
        'Estacionamiento': 0.20,
        'Semáforo': 0.15,
        'Documentación': 0.12,
        'Emisiones': 0.10,
        'Peso Excesivo': 0.05,
        'Ruta No Autorizada': 0.03
    }
    
    # Rango de fechas (24 meses)
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Crear dataset
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
        'duracion_viaje_horas': np.random.exponential(2.0, num_records),
        'num_pasajeros': np.random.poisson(2.5, num_records),
        'carga_toneladas': np.random.exponential(5, num_records),
        
        # Métricas financieras (EUR)
        'coste_operacional_eur': np.random.lognormal(5.8, 0.7, num_records),
        'coste_mantenimiento_eur': np.random.lognormal(4.0, 0.8, num_records),
        'coste_energia_eur': np.random.lognormal(4.2, 0.6, num_records),
        'ingresos_eur': np.random.lognormal(6.8, 0.6, num_records),
        'multa_eur': np.random.lognormal(4.8, 1.0, num_records),
        'ahorro_verde_eur': np.random.lognormal(3.2, 1.2, num_records),
        
        # Métricas ambientales
        'emisiones_co2_kg': np.random.lognormal(4.5, 1.5, num_records),
        'emisiones_nox_g': np.random.lognormal(2.5, 1.0, num_records),
        'particulas_pm_g': np.random.lognormal(1.0, 1.2, num_records),
        'energia_renovable_kwh': np.random.lognormal(3.8, 0.9, num_records),
        
        # Indicadores de rendimiento (0-1)
        'puntualidad': np.random.beta(8, 2, num_records),
        'puntuacion_seguridad': np.random.beta(9, 1.5, num_records),
        'satisfaccion_conductor': np.random.beta(7, 2.5, num_records),
        'eficiencia_energetica': np.random.beta(6.5, 2.5, num_records),
        'indice_sostenibilidad': np.random.beta(7.5, 2, num_records),
        
        # Cumplimiento verde
        'certificacion_verde': np.random.choice([0, 1], num_records, p=[0.20, 0.80]),
        'inspeccion_emisiones_ok': np.random.choice([0, 1], num_records, p=[0.05, 0.95]),
        'cumple_euro6': np.random.choice([0, 1], num_records, p=[0.10, 0.90]),
        'estacion_carga_disponible': np.random.choice([0, 1], num_records, p=[0.30, 0.70]),
        
        # Métricas específicas verdes
        'share_flota_ev': np.random.beta(3, 5, num_records),
        'puntos_carga_accesibles': np.random.randint(0, 50, num_records),
        'inversion_verde_eur': np.random.lognormal(4.5, 1.0, num_records),
        'progreso_objetivos_2030': np.random.beta(4, 3, num_records),
        
        # Factores externos
        'condiciones_climaticas': np.random.choice(['Soleado', 'Nublado', 'Lluvia', 'Viento'], num_records, p=[0.6, 0.25, 0.12, 0.03]),
        'densidad_trafico': np.random.beta(4, 4, num_records),
        'disponibilidad_renovables': np.random.beta(6, 3, num_records),
    }
    
    df = pd.DataFrame(data)
    
    # Aplicar restricciones realistas
    df['velocidad_media_kmh'] = np.clip(df['velocidad_media_kmh'], 20, 150)
    df['duracion_viaje_horas'] = np.clip(df['duracion_viaje_horas'], 0.2, 24)
    df['num_pasajeros'] = np.clip(df['num_pasajeros'], 0, 60)
    df['carga_toneladas'] = np.clip(df['carga_toneladas'], 0, 50)
    
    # Ajustes específicos por tipo de vehículo
    electric_mask = df['tipo_vehiculo'].str.contains('Eléctrico', na=False)
    df.loc[electric_mask, 'emisiones_co2_kg'] = 0
    df.loc[electric_mask, 'emisiones_nox_g'] = 0
    df.loc[electric_mask, 'particulas_pm_g'] = 0
    df.loc[electric_mask, 'coste_energia_eur'] *= 0.25
    df.loc[electric_mask, 'certificacion_verde'] = 1
    df.loc[electric_mask, 'indice_sostenibilidad'] = np.random.beta(9, 1, electric_mask.sum())
    
    hybrid_mask = df['tipo_vehiculo'].str.contains('Híbrido', na=False)
    df.loc[hybrid_mask, 'emisiones_co2_kg'] *= 0.4
    df.loc[hybrid_mask, 'emisiones_nox_g'] *= 0.5
    df.loc[hybrid_mask, 'coste_energia_eur'] *= 0.6
    df.loc[hybrid_mask, 'indice_sostenibilidad'] = np.random.beta(7.5, 2, hybrid_mask.sum())
    
    # Ajustes por fuente de energía
    solar_mask = df['fuente_energia'] == 'Solar Fotovoltaica'
    df.loc[solar_mask, 'ahorro_verde_eur'] *= 1.8
    df.loc[solar_mask, 'indice_sostenibilidad'] = np.random.beta(9, 1, solar_mask.sum())
    
    wind_mask = df['fuente_energia'] == 'Eólica'
    df.loc[wind_mask, 'ahorro_verde_eur'] *= 1.6
    df.loc[wind_mask, 'indice_sostenibilidad'] = np.random.beta(8.5, 1.2, wind_mask.sum())
    
    hydrogen_mask = df['fuente_energia'] == 'Hidrógeno Verde'
    df.loc[hydrogen_mask, 'ahorro_verde_eur'] *= 2.2
    df.loc[hydrogen_mask, 'indice_sostenibilidad'] = np.random.beta(9.5, 0.8, hydrogen_mask.sum())
    
    # Impacto del clima en renovables
    sunny_mask = df['condiciones_climaticas'] == 'Soleado'
    df.loc[sunny_mask, 'energia_renovable_kwh'] *= 1.5
    df.loc[sunny_mask, 'disponibilidad_renovables'] = np.random.beta(8, 2, sunny_mask.sum())
    
    windy_mask = df['condiciones_climaticas'] == 'Viento'
    df.loc[windy_mask, 'energia_renovable_kwh'] *= 1.7
    df.loc[windy_mask, 'disponibilidad_renovables'] = np.random.beta(9, 1, windy_mask.sum())
    
    # Calcular métricas derivadas
    df['eficiencia_km_per_kwh'] = np.where(
        df['consumo_energia_kwh'] > 0,
        df['distancia_km'] / df['consumo_energia_kwh'],
        0
    )
    df['emisiones_por_km'] = np.where(
        df['distancia_km'] > 0,
        df['emisiones_co2_kg'] / df['distancia_km'],
        0
    )
    df['coste_total_eur'] = (
        df['coste_operacional_eur'] +
        df['coste_mantenimiento_eur'] +
        df['coste_energia_eur']
    )
    df['beneficio_eur'] = df['ingresos_eur'] - df['coste_total_eur']
    df['margen_beneficio'] = np.where(
        df['ingresos_eur'] > 0,
        df['beneficio_eur'] / df['ingresos_eur'],
        0
    )
    df['puntuacion_verde_total'] = (
        df['indice_sostenibilidad'] * 0.4 +
        df['eficiencia_energetica'] * 0.3 +
        df['disponibilidad_renovables'] * 0.3
    )
    
    # Características temporales
    df['año'] = df['fecha'].dt.year
    df['mes'] = df['fecha'].dt.month
    df['trimestre'] = df['fecha'].dt.quarter
    df['dia_semana'] = df['fecha'].dt.day_name()
    df['es_fin_semana'] = df['fecha'].dt.weekday >= 5
    df['estacion'] = df['mes'].map({
        12: 'Invierno', 1: 'Invierno', 2: 'Invierno',
        3: 'Primavera', 4: 'Primavera', 5: 'Primavera',
        6: 'Verano', 7: 'Verano', 8: 'Verano',
        9: 'Otoño', 10: 'Otoño', 11: 'Otoño'
    })
    
    # Limpiar y validar datos
    df = df.replace([np.inf, -np.inf], np.nan)
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())
    
    # Controles de calidad final
    df['margen_beneficio'] = df['margen_beneficio'].clip(-1, 1)
    df['puntualidad'] = df['puntualidad'].clip(0, 1)
    df['puntuacion_seguridad'] = df['puntuacion_seguridad'].clip(0, 1)
    df['indice_sostenibilidad'] = df['indice_sostenibilidad'].clip(0, 1)
    df['puntuacion_verde_total'] = df['puntuacion_verde_total'].clip(0, 1)
    df['share_flota_ev'] = df['share_flota_ev'].clip(0, 1)
    df['progreso_objetivos_2030'] = df['progreso_objetivos_2030'].clip(0, 1)
    
    return df

# ========================================
# FUNCIONES ANALÍTICAS AVANZADAS
# ========================================

def perform_green_anomaly_detection(df, metric_column, contamination=0.08):
    """Detección de anomalías centrada en métricas verdes."""
    try:
        daily_data = df.groupby('fecha').agg({
            metric_column: ['sum', 'mean', 'std', 'count']
        }).reset_index()
        
        daily_data.columns = ['fecha', f'{metric_column}_sum', f'{metric_column}_mean', 
                             f'{metric_column}_std', f'{metric_column}_count']
        
        if len(daily_data) < 10:
            return daily_data, pd.DataFrame()
        
        features = [f'{metric_column}_sum', f'{metric_column}_mean']
        feature_data = daily_data[features].fillna(daily_data[features].median())
        
        iso_forest = IsolationForest(
            contamination=contamination, 
            random_state=42,
            n_estimators=200
        )
        daily_data['anomaly_flag'] = iso_forest.fit_predict(feature_data)
        daily_data['anomaly_score'] = iso_forest.score_samples(feature_data)
        
        anomalies = daily_data[daily_data['anomaly_flag'] == -1].copy()
        
        return daily_data, anomalies
        
    except Exception as e:
        st.error(f"Error en detección de anomalías: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

def green_forecasting_engine(df, metric_column, periods=6):
    """Motor de predicción para métricas verdes."""
    try:
        monthly_data = df.groupby(pd.Grouper(key='fecha', freq='M')).agg({
            metric_column: ['sum', 'mean', 'count']
        }).reset_index()
        
        monthly_data.columns = ['fecha', f'{metric_column}_sum', f'{metric_column}_mean', f'{metric_column}_count']
        
        if len(monthly_data) < 6:
            return None, None
        
        monthly_data['month_index'] = range(len(monthly_data))
        monthly_data['seasonal'] = monthly_data['fecha'].dt.month
        
        X = monthly_data[['month_index', 'seasonal']].values
        y = monthly_data[f'{metric_column}_sum'].values
        
        models = {
            'linear': LinearRegression(),
            'rf': RandomForestRegressor(n_estimators=150, random_state=42, max_depth=10)
        }
        
        predictions = {}
        for name, model in models.items():
            model.fit(X, y)
            predictions[name] = model
        
        last_month_index = monthly_data['month_index'].max()
        future_features = []
        
        for i in range(1, periods + 1):
            future_month = monthly_data['fecha'].max() + pd.DateOffset(months=i)
            future_features.append([
                last_month_index + i,
                future_month.month
            ])
        
        future_features = np.array(future_features)
        
        ensemble_predictions = []
        for features in future_features:
            pred_values = []
            for model in predictions.values():
                pred_values.append(model.predict([features])[0])
            ensemble_predictions.append(np.mean(pred_values))
        
        prediction_std = []
        for features in future_features:
            pred_values = []
            for model in predictions.values():
                pred_values.append(model.predict([features])[0])
            prediction_std.append(np.std(pred_values))
        
        last_date = monthly_data['fecha'].max()
        future_dates = [last_date + pd.DateOffset(months=i) for i in range(1, periods + 1)]
        
        forecast_df = pd.DataFrame({
            'fecha': future_dates,
            'prediction': ensemble_predictions,
            'lower_bound': [p - 1.96 * s for p, s in zip(ensemble_predictions, prediction_std)],
            'upper_bound': [p + 1.96 * s for p, s in zip(ensemble_predictions, prediction_std)],
            'confidence_width': [2 * 1.96 * s for s in prediction_std]
        })
        
        return monthly_data, forecast_df
        
    except Exception as e:
        st.error(f"Error en predicción: {str(e)}")
        return None, None

def create_green_metric_card(title, value, delta=None, format_type="number", icon="🌱"):
    """Crear tarjetas métricas con tema verde."""
    
    if format_type == "currency":
        formatted_value = f"€{value:,.0f}"
    elif format_type == "percentage":
        formatted_value = f"{value:.1f}%"
    elif format_type == "decimal":
        formatted_value = f"{value:.2f}"
    elif format_type == "energy":
        formatted_value = f"{value:,.0f} kWh"
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
    <div class="green-metric-card">
        <div class="metric-title">{icon} {title}</div>
        <div class="metric-value">{formatted_value}</div>
        {delta_html}
    </div>
    """

# ========================================
# GEOJSON ESPAÑA (EMBEBIDO)
# ========================================

SPAIN_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"NAME_1": "Andalucía", "id": "AN"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-7.5, 38.5], [-2.5, 38.5], [-2.5, 36.0], [-7.5, 36.0], [-7.5, 38.5]]]
            }
        },
        {
            "type": "Feature", 
            "properties": {"NAME_1": "Cataluña", "id": "CT"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[0.5, 42.8], [3.3, 42.8], [3.3, 40.5], [0.5, 40.5], [0.5, 42.8]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Madrid", "id": "MD"},
            "geometry": {
                "type": "Polygon", 
                "coordinates": [[[-4.5, 41.0], [-3.0, 41.0], [-3.0, 39.8], [-4.5, 39.8], [-4.5, 41.0]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Comunidad Valenciana", "id": "VC"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-1.5, 40.8], [0.8, 40.8], [0.8, 37.8], [-1.5, 37.8], [-1.5, 40.8]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Galicia", "id": "GA"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-9.5, 43.8], [-6.5, 43.8], [-6.5, 41.8], [-9.5, 41.8], [-9.5, 43.8]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Castilla y León", "id": "CL"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-7.0, 43.0], [-2.0, 43.0], [-2.0, 40.0], [-7.0, 40.0], [-7.0, 43.0]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "País Vasco", "id": "PV"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-3.5, 43.5], [-1.5, 43.5], [-1.5, 42.8], [-3.5, 42.8], [-3.5, 43.5]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Canarias", "id": "CN"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-18.2, 28.8], [-13.4, 28.8], [-13.4, 27.6], [-18.2, 27.6], [-18.2, 28.8]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Castilla-La Mancha", "id": "CM"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-5.5, 40.0], [-1.0, 40.0], [-1.0, 38.0], [-5.5, 38.0], [-5.5, 40.0]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Murcia", "id": "MC"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-2.3, 38.5], [-0.6, 38.5], [-0.6, 37.0], [-2.3, 37.0], [-2.3, 38.5]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Aragón", "id": "AR"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-2.0, 42.8], [0.8, 42.8], [0.8, 39.8], [-2.0, 39.8], [-2.0, 42.8]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Baleares", "id": "IB"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[1.2, 40.1], [4.3, 40.1], [4.3, 38.6], [1.2, 38.6], [1.2, 40.1]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Extremadura", "id": "EX"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-7.5, 40.5], [-4.8, 40.5], [-4.8, 37.8], [-7.5, 37.8], [-7.5, 40.5]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Asturias", "id": "AS"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-7.2, 43.6], [-4.5, 43.6], [-4.5, 43.0], [-7.2, 43.0], [-7.2, 43.6]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Navarra", "id": "NC"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-2.7, 43.0], [-1.0, 43.0], [-1.0, 42.0], [-2.7, 42.0], [-2.7, 43.0]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "Cantabria", "id": "CB"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-4.8, 43.5], [-3.2, 43.5], [-3.2, 43.0], [-4.8, 43.0], [-4.8, 43.5]]]
            }
        },
        {
            "type": "Feature",
            "properties": {"NAME_1": "La Rioja", "id": "RI"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-3.0, 42.7], [-1.8, 42.7], [-1.8, 42.0], [-3.0, 42.0], [-3.0, 42.7]]]
            }
        }
    ]
}

# ========================================
# DASHBOARD REGIONAL
# ========================================

def display_regional_dashboard(selected_region_name, df_region, all_regional_performance):
    """Mostrar dashboard detallado para la región seleccionada."""
    
    st.markdown(f"""
    <div class="spain-header">
        <h1>🌱 {selected_region_name}</h1>
        <p>Análisis Detallado de Transporte Verde</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Datos de la región
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
            "Ahorro Verde", region_data['ahorro_verde_total'] / 1000, 
            format_type="currency", icon="💚"
        ), unsafe_allow_html=True)
    
    # Información de la comunidad
    st.markdown("---")
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
        st.markdown(f"""
        <div class="green-insight-container">
            <h4>⚡ Energías Renovables Principales</h4>
            <p><strong>Fuentes Principales:</strong></p>
            <ul>
        """)
        for renewable in community_info['renovables_principales']:
            st.markdown(f"<li>{renewable}</li>")
        st.markdown(f"""
            </ul>
            <p><strong>Progreso Objetivos 2030:</strong> {region_data['progreso_objetivos_2030'] * 100:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Pestañas de análisis
    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 **Tendencias Verde**",
        "🔮 **Predicciones IA**", 
        "⚠️ **Detección Anomalías**",
        "🎯 **Estrategia Verde**"
    ])
    
    with tab1:
        st.markdown(f"### 📈 Tendencias de Transporte Verde - {selected_region_name}")
        
        # Tendencias mensuales
        monthly_trends = df_region.groupby(pd.Grouper(key='fecha', freq='M')).agg({
            'share_flota_ev': 'mean',
            'emisiones_co2_kg': 'sum',
            'energia_renovable_kwh': 'sum',
            'ahorro_verde_eur': 'sum',
            'puntuacion_verde_total': 'mean'
        }).reset_index()
        
        fig_trends = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Evolución Share Flota EV (%)", 
                "Emisiones CO₂ Mensuales (kg)",
                "Energía Renovable (kWh)", 
                "Ahorro Verde Acumulado (€)"
            )
        )
        
        fig_trends.add_trace(
            go.Scatter(
                x=monthly_trends['fecha'], 
                y=monthly_trends['share_flota_ev'] * 100,
                mode='lines+markers', 
                name='Share EV (%)', 
                line=dict(color='#10b981', width=3)
            ), row=1, col=1
        )
        
        fig_trends.add_trace(
            go.Scatter(
                x=monthly_trends['fecha'], 
                y=monthly_trends['emisiones_co2_kg'],
                mode='lines+markers', 
                name='CO₂ (kg)', 
                line=dict(color='#ef4444', width=3)
            ), row=1, col=2
        )
        
        fig_trends.add_trace(
            go.Scatter(
                x=monthly_trends['fecha'], 
                y=monthly_trends['energia_renovable_kwh'],
                mode='lines+markers', 
                name='Renovable (kWh)', 
                line=dict(color='#3b82f6', width=3)
            ), row=2, col=1
        )
        
        fig_trends.add_trace(
            go.Scatter(
                x=monthly_trends['fecha'], 
                y=monthly_trends['ahorro_verde_eur'],
                mode='lines+markers', 
                name='Ahorro (€)', 
                line=dict(color='#f59e0b', width=3)
            ), row=2, col=2
        )
        
        fig_trends.update_layout(
            height=600, 
            title_text=f"Tendencias Transporte Verde - {selected_region_name}",
            showlegend=False, 
            template='plotly_white', 
            font=dict(family='Inter')
        )
        
        st.plotly_chart(fig_trends, use_container_width=True)
        
        # Análisis de tendencias
        ev_growth = ((monthly_trends['share_flota_ev'].iloc[-1] / monthly_trends['share_flota_ev'].iloc[0]) - 1) * 100
        co2_change = ((monthly_trends['emisiones_co2_kg'].iloc[-1] / monthly_trends['emisiones_co2_kg'].iloc[0]) - 1) * 100
        
        st.markdown(f"""
        <div class="green-insight-container">
            <h4>📊 Análisis de Tendencias</h4>
            <p><strong>Crecimiento Flota EV:</strong> {ev_growth:+.1f}% en el período analizado</p>
            <p><strong>Cambio Emisiones CO₂:</strong> {co2_change:+.1f}% respecto al inicio</p>
            <p><strong>Evaluación:</strong> {'Excelente progreso hacia movilidad sostenible' if ev_growth > 15 and co2_change < -10 else 'Progreso moderado, acelerar iniciativas verdes' if ev_growth > 5 else 'Requiere intervención urgente en políticas verdes'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown(f"### 🔮 Predicciones IA - {selected_region_name}")
        
        # Predicción de emisiones CO₂
        co2_historical, co2_forecast = green_forecasting_engine(df_region, 'emisiones_co2_kg', periods=6)
        
        if co2_historical is not None and co2_forecast is not None:
            fig_forecast = go.Figure()
            
            fig_forecast.add_trace(go.Scatter(
                x=co2_historical['fecha'],
                y=co2_historical['emisiones_co2_kg_sum'] / 1000,
                mode='lines+markers',
                name='Histórico CO₂ (tons)',
                line=dict(color='#10b981', width=3)
            ))
            
            fig_forecast.add_trace(go.Scatter(
                x=co2_forecast['fecha'],
                y=co2_forecast['prediction'] / 1000,
                mode='lines+markers',
                name='Predicción CO₂ (tons)',
                line=dict(color='#34d399', width=3, dash='dash')
            ))
            
            fig_forecast.add_trace(go.Scatter(
                x=list(co2_forecast['fecha']) + list(co2_forecast['fecha'][::-1]),
                y=list(co2_forecast['upper_bound'] / 1000) + list(co2_forecast['lower_bound'] / 1000)[::-1],
                fill='toself',
                fillcolor='rgba(52, 211, 153, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Intervalo Confianza',
                showlegend=True
            ))
            
            fig_forecast.update_layout(
                title=f"Predicción Emisiones CO₂ - {selected_region_name}",
                xaxis_title="Fecha",
                yaxis_title="CO₂ (Toneladas)",
                template='plotly_white',
                height=500,
                font=dict(family='Inter')
            )
            
            st.plotly_chart(fig_forecast, use_container_width=True)
            
            # Insight de predicción
            current_co2_avg = co2_historical['emisiones_co2_kg_sum'].tail(3).mean()
            next_co2_forecast = co2_forecast['prediction'].iloc[0]
            co2_change_percent = ((next_co2_forecast - current_co2_avg) / current_co2_avg) * 100 if current_co2_avg else 0
            
            st.markdown(f"""
            <div class="green-insight-container">
                <h4>🎯 Insight Predictivo</h4>
                <p>Las emisiones CO₂ proyectadas para {selected_region_name} muestran un <strong>{co2_change_percent:+.1f}%</strong> de cambio el próximo período.</p>
                <p><strong>Interpretación:</strong> {'Tendencia positiva hacia reducción de emisiones, continuar políticas verdes actuales.' if co2_change_percent < -5 else 'Estabilización de emisiones, evaluar nuevas medidas de reducción.' if abs(co2_change_percent) < 5 else 'Aumento preocupante, implementar medidas correctivas urgentes.'}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Datos insuficientes para predicción confiable. Amplíe el período de análisis.")
    
    with tab3:
        st.markdown(f"### ⚠️ Detección de Anomalías - {selected_region_name}")
        
        # Detección de anomalías en inversión verde
        green_investment_daily, green_investment_anomalies = perform_green_anomaly_detection(
            df_region, 'inversion_verde_eur', contamination=0.1
        )
        
        if not green_investment_anomalies.empty:
            st.markdown(f"""
            <div class="alert-warning">
                <h4>⚠️ Anomalías en Inversión Verde Detectadas</h4>
                <p>Se identificaron <strong>{len(green_investment_anomalies)}</strong> días con patrones anómalos en inversión verde para {selected_region_name}.</p>
                <p><strong>Recomendación:</strong> Investigar estos períodos para identificar causas y asegurar financiación estable para iniciativas verdes.</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("Ver fechas de anomalías detalladas"):
                st.dataframe(
                    green_investment_anomalies[['fecha', 'inversion_verde_eur_sum']],
                    use_container_width=True
                )
        else:
            st.markdown("""
            <div class="alert-success">
                <h4>✅ Inversión Verde Estable</h4>
                <p>No se detectaron anomalías significativas en los patrones de inversión verde. Las iniciativas muestran consistencia operacional.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Detección de anomalías en eficiencia energética
        efficiency_daily, efficiency_anomalies = perform_green_anomaly_detection(
            df_region, 'eficiencia_km_per_kwh', contamination=0.08
        )
        
        if not efficiency_anomalies.empty:
            st.markdown(f"""
            <div class="alert-danger">
                <h4>🚨 Anomalías en Eficiencia Energética</h4>
                <p><strong>{len(efficiency_anomalies)}</strong> días con eficiencia energética anómala detectados.</p>
                <p><strong>Impacto:</strong> Posibles problemas en infraestructura o gestión de flota eléctrica.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown(f"### 🎯 Estrategia Verde Personalizada - {selected_region_name}")
        
        # Benchmarking nacional
        national_avg = all_regional_performance.agg({
            'share_flota_ev': 'mean',
            'puntuacion_verde_total': 'mean',
            'progreso_objetivos_2030': 'mean'
        })
        
        # Generar recomendaciones estratégicas
        recommendations = []
        
        if region_data['share_flota_ev'] < national_avg['share_flota_ev'] * 0.8:
            recommendations.append({
                "prioridad": "Alta",
                "categoria": "Electrificación Flota",
                "titulo": "Programa Acelerado de Transición Eléctrica",
                "descripcion": f"El share de flota EV de {selected_region_name} ({region_data['share_flota_ev']:.1%}) está significativamente por debajo de la media nacional. Implementar incentivos agresivos y campañas de concienciación.",
                "impacto_financiero": "Inversión estimada: €8-15M, beneficio potencial: €25M a largo plazo",
                "cronograma": "Acción inmediata, impacto en 6-12 meses"
            })
        
        if region_data['puntuacion_verde_total'] < national_avg['puntuacion_verde_total'] * 0.85:
            recommendations.append({
                "prioridad": "Media",
                "categoria": "Mejora Integral Sostenibilidad",
                "titulo": "Plan Integral de Movilidad Sostenible",
                "descripcion": f"Puntuación verde general ({region_data['puntuacion_verde_total']:.2f}) requiere mejora. Enfocar en infraestructura de carga y energías renovables.",
                "impacto_financiero": "Inversión: €5-12M en infraestructura verde",
                "cronograma": "Implementación en 12-18 meses"
            })
        
        if region_data['progreso_objetivos_2030'] < 0.6:
            recommendations.append({
                "prioridad": "Alta",
                "categoria": "Objetivos 2030",
                "titulo": "Aceleración Urgente hacia Objetivos 2030",
                "descripcion": f"Progreso actual ({region_data['progreso_objetivos_2030']:.1%}) insuficiente para cumplir objetivos 2030. Requiere intervención estratégica inmediata.",
                "impacto_financiero": "Riesgo de sanciones + oportunidades perdidas",
                "cronograma": "Acción inmediata, revisión trimestral"
            })
        
        if not recommendations:
            recommendations.append({
                "prioridad": "Baja",
                "categoria": "Optimización Continua",
                "titulo": "Mantener Liderazgo en Transporte Verde",
                "descripcion": f"{selected_region_name} muestra excelente rendimiento verde. Enfocar en innovación y compartir mejores prácticas.",
                "impacto_financiero": "Ventaja competitiva sostenida",
                "cronograma": "Mejora continua"
            })
        
        # Mostrar recomendaciones
        for i, rec in enumerate(recommendations, 1):
            priority_colors = {"Alta": "#ef4444", "Media": "#f59e0b", "Baja": "#10b981"}
            priority_color = priority_colors.get(rec["prioridad"], "#6b7280")
            
            st.markdown(f"""
            <div class="green-recommendation-container">
                <h4>💡 Iniciativa Estratégica {i}: {rec['titulo']} 
                    <span style="background: {priority_color}; color: white; padding: 6px 15px; border-radius: 20px; font-size: 0.9rem; margin-left: 15px; font-weight: 600;">
                        Prioridad {rec['prioridad']}
                    </span>
                </h4>
                <p><strong>Categoría:</strong> {rec['categoria']}</p>
                <p><strong>Diagnóstico:</strong> {rec['descripcion']}</p>
                <p><strong>Impacto Financiero:</strong> {rec['impacto_financiero']}</p>
                <p><strong>Cronograma:</strong> {rec['cronograma']}</p>
            </div>
            """, unsafe_allow_html=True)

# ========================================
# APLICACIÓN PRINCIPAL
# ========================================

def main():
    # Encabezado profesional
    st.markdown("""
    <div class="spain-header">
        <h1>🇪🇸 Grecert DGT España</h1>
        <p>Plataforma de Inteligencia de Transporte Verde y Energías Renovables</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos
    with st.spinner("🔄 Cargando datos de transporte verde de España..."):
        df = generate_spain_green_dgt_data()
    
    # Panel de control ejecutivo
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
        if not selected_regions_filter:
            selected_regions_filter = all_regions
            st.sidebar.warning("Seleccione al menos una comunidad.")
    
    selected_vehicles = st.sidebar.multiselect(
        "Tipos de Vehículos",
        options=df['tipo_vehiculo'].unique(),
        default=df['tipo_vehiculo'].unique()
    )
    
    selected_energy = st.sidebar.multiselect(
        "Fuentes de Energía",
        options=df['fuente_energia'].unique(),
        default=df['fuente_energia'].unique()
    )
    
    # Filtros verdes avanzados
    st.sidebar.markdown("### ⚡ Filtros Energía Verde")
    min_green_score = st.sidebar.slider("Puntuación Verde Mínima", 0.0, 1.0, 0.0, 0.1)
    only_certified = st.sidebar.checkbox("Solo Vehículos Certificados Verde", value=False)
    
    # Aplicar filtros
    mask = (df['fecha'] >= pd.to_datetime(start_date)) & (df['fecha'] <= pd.to_datetime(end_date))
    filtered_df = df[mask]
    
    if selected_regions_filter:
        filtered_df = filtered_df[filtered_df['comunidad_autonoma'].isin(selected_regions_filter)]
    if selected_vehicles:
        filtered_df = filtered_df[filtered_df['tipo_vehiculo'].isin(selected_vehicles)]
    if selected_energy:
        filtered_df = filtered_df[filtered_df['fuente_energia'].isin(selected_energy)]
    
    filtered_df = filtered_df[filtered_df['puntuacion_verde_total'] >= min_green_score]
    
    if only_certified:
        filtered_df = filtered_df[filtered_df['certificacion_verde'] == 1]
    
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
    
    # Renombrar columnas para consistencia
    all_regional_performance.rename(columns={
        'emisiones_co2_kg': 'emisiones_co2_total',
        'energia_renovable_kwh': 'energia_renovable_total',
        'ahorro_verde_eur': 'ahorro_verde_total',
        'inversion_verde_eur': 'inversion_verde_total'
    }, inplace=True)
    
    # Área de contenido principal
    if st.session_state.selected_region:
        # Mostrar dashboard detallado para la región seleccionada
        region_df = filtered_df[filtered_df['comunidad_autonoma'] == st.session_state.selected_region]
        display_regional_dashboard(st.session_state.selected_region, region_df, all_regional_performance)
    else:
        # Mostrar vista general de España
        st.markdown("## 📊 Panorama General de Transporte Verde en España")
        
        # KPIs globales
        total_operations = len(filtered_df)
        total_distance_mkm = filtered_df['distancia_km'].sum() / 1_000_000
        total_revenue_m = filtered_df['ingresos_eur'].sum() / 1_000_000
        total_green_savings_m = filtered_df['ahorro_verde_eur'].sum() / 1_000_000
        total_emissions_m = filtered_df['emisiones_co2_kg'].sum() / 1_000_000
        avg_ev_share_spain = filtered_df['share_flota_ev'].mean() * 100
        avg_green_score_spain = filtered_df['puntuacion_verde_total'].mean() * 100
        avg_2030_progress_spain = filtered_df['progreso_objetivos_2030'].mean() * 100
        
        # Mostrar KPIs globales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(create_green_metric_card(
                "Operaciones Totales", total_operations, delta="+15.2% anual", icon="🚛"
            ), unsafe_allow_html=True)
            
            st.markdown(create_green_metric_card(
                "Distancia Total", total_distance_mkm, delta=8.7, format_type="decimal", icon="🛣️"
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown(create_green_metric_card(
                "Ingresos Totales", total_revenue_m, delta=12.5, format_type="currency", icon="💰"
            ), unsafe_allow_html=True)
            
            st.markdown(create_green_metric_card(
                "Ahorro Verde", total_green_savings_m, delta=28.3, format_type="currency", icon="💚"
            ), unsafe_allow_html=True)
        
        with col3:
            st.markdown(create_green_metric_card(
                "Share Flota EV", avg_ev_share_spain, delta=22.1, format_type="percentage", icon="🔋"
            ), unsafe_allow_html=True)
            
            st.markdown(create_green_metric_card(
                "Emisiones CO₂", total_emissions_m, delta=-18.7, format_type="emissions", icon="🌿"
            ), unsafe_allow_html=True)
        
        with col4:
            st.markdown(create_green_metric_card(
                "Puntuación Verde", avg_green_score_spain, delta=11.2, format_type="percentage", icon="🌟"
            ), unsafe_allow_html=True)
            
            st.markdown(create_green_metric_card(
                "Progreso 2030", avg_2030_progress_spain, delta=15.8, format_type="percentage", icon="🎯"
            ), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Mapa interactivo de España
        st.markdown("### 🗺️ Mapa Interactivo de Transporte Verde por Comunidades")
        
        col_map, col_select = st.columns([3, 1])
        
        with col_map:
            # Crear mapa coroplético
            fig_map = px.choropleth(
                all_regional_performance,
                geojson=SPAIN_GEOJSON,
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
                title="🌱 Puntuación Verde por Comunidad Autónoma"
            )
            
            fig_map.update_geos(
                fitbounds="locations", 
                visible=False
            )
            
            fig_map.update_layout(
                height=600,
                margin={"r":0,"t":50,"l":0,"b":0},
                coloraxis_colorbar=dict(title="Puntuación Verde"),
                template='plotly_white',
                font=dict(family='Inter')
            )
            
            st.markdown('<div class="map-container">', unsafe_allow_html=True)
            st.plotly_chart(fig_map, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_select:
            st.markdown("#### 🎯 Seleccionar Comunidad")
            selected_region_for_detail = st.selectbox(
                "Elige una Comunidad Autónoma:",
                options=[''] + all_regions,
                index=0,
                key='map_region_selector'
            )
            
            if selected_region_for_detail:
                if st.button(f"Ver Dashboard {selected_region_for_detail}", key='view_dashboard'):
                    st.session_state.selected_region = selected_region_for_detail
                    st.rerun()
            
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
        
        st.markdown("---")
        
        # Análisis nacional
        st.markdown("### 🇪🇸 Análisis Nacional de Transporte Verde")
        
        tab1, tab2, tab3 = st.tabs([
            "📈 **Tendencias Nacionales**",
            "🏆 **Ranking Comunidades**",
            "🎯 **Objetivos 2030**"
        ])
        
        with tab1:
            st.markdown("### 📈 Tendencias Nacionales de Movilidad Verde")
            
            # Tendencias mensuales nacionales
            monthly_national = filtered_df.groupby(pd.Grouper(key='fecha', freq='M')).agg({
                'share_flota_ev': 'mean',
                'emisiones_co2_kg': 'sum',
                'energia_renovable_kwh': 'sum',
                'ahorro_verde_eur': 'sum'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_ev_trend = px.line(
                    monthly_national,
                    x='fecha',
                    y='share_flota_ev',
                    title="🔋 Evolución Nacional Share Flota EV",
                    color_discrete_sequence=['#10b981']
                )
                fig_ev_trend.update_layout(
                    template='plotly_white',
                    font=dict(family='Inter'),
                    yaxis_title="Share Flota EV"
                )
                st.plotly_chart(fig_ev_trend, use_container_width=True)
            
            with col2:
                fig_co2_trend = px.line(
                    monthly_national,
                    x='fecha',
                    y='emisiones_co2_kg',
                    title="🌿 Evolución Nacional Emisiones CO₂",
                    color_discrete_sequence=['#ef4444']
                )
                fig_co2_trend.update_layout(
                    template='plotly_white',
                    font=dict(family='Inter'),
                    yaxis_title="Emisiones CO₂ (kg)"
                )
                st.plotly_chart(fig_co2_trend, use_container_width=True)
            
            # Insights nacionales
            ev_growth = ((monthly_national['share_flota_ev'].iloc[-1] / monthly_national['share_flota_ev'].iloc[0]) - 1) * 100
            co2_reduction = ((monthly_national['emisiones_co2_kg'].iloc[0] / monthly_national['emisiones_co2_kg'].iloc[-1]) - 1) * 100
            
            st.markdown(f"""
            <div class="green-insight-container">
                <h4>🇪🇸 Tendencias Nacionales</h4>
                <p><strong>Crecimiento Flota EV:</strong> {ev_growth:+.1f}% en el período analizado</p>
                <p><strong>Reducción Emisiones CO₂:</strong> {co2_reduction:+.1f}% respecto al inicio del período</p>
                <p><strong>Ahorro Verde Nacional:</strong> €{monthly_national['ahorro_verde_eur'].sum()/1000000:.1f}M acumulado</p>
                <p><strong>Evaluación General:</strong> {'España lidera la transición hacia movilidad sostenible en Europa' if ev_growth > 20 else 'Progreso sólido que requiere acelerar políticas verdes' if ev_growth > 10 else 'Necesario reforzar urgentemente estrategias de electrificación'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tab2:
            st.markdown("### 🏆 Ranking Nacional de Comunidades Verdes")
            
            # Crear ranking
            ranking_data = all_regional_performance.copy()
            ranking_data['ranking_verde'] = ranking_data['puntuacion_verde_total'].rank(ascending=False)
            ranking_data = ranking_data.sort_values('puntuacion_verde_total', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🥇 Top 5 Comunidades Verdes")
                for i, (_, community) in enumerate(ranking_data.head(5).iterrows(), 1):
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🏅"
                    st.markdown(f"""
                    <div class="community-card">
                        <h5>{medal} #{i} {community['comunidad_autonoma']}</h5>
                        <p><strong>Puntuación Verde:</strong> {community['puntuacion_verde_total']:.3f}</p>
                        <p><strong>Share Flota EV:</strong> {community['share_flota_ev']:.1%}</p>
                        <p><strong>Progreso 2030:</strong> {community['progreso_objetivos_2030']:.1%}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                # Gráfico de ranking
                fig_ranking = px.bar(
                    ranking_data.head(10),
                    x='puntuacion_verde_total',
                    y='comunidad_autonoma',
                    orientation='h',
                    title="📊 Top 10 Puntuación Verde",
                    color='puntuacion_verde_total',
                    color_continuous_scale='Greens'
                )
                fig_ranking.update_layout(
                    template='plotly_white',
                    font=dict(family='Inter'),
                    height=600
                )
                st.plotly_chart(fig_ranking, use_container_width=True)
        
        with tab3:
            st.markdown("### 🎯 Progreso hacia Objetivos España 2030")
            
            # Calcular estado actual vs objetivos 2030
            current_ev_pct = (filtered_df['tipo_vehiculo'].str.contains('Eléctrico|Híbrido', na=False)).mean() * 100
            current_renewable_pct = (filtered_df['fuente_energia'] != 'Convencional').mean() * 100
            current_green_investment = filtered_df['inversion_verde_eur'].sum() / 1_000_000
            
            # Objetivos 2030
            target_ev = 50  # 50% vehículos eléctricos/híbridos
            target_renewable = 85  # 85% energías renovables
            target_co2_reduction = 55  # 55% reducción CO₂
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de progreso
                progress_data = pd.DataFrame({
                    'Objetivo': ['Vehículos EV/Híbridos', 'Energías Renovables', 'Reducción CO₂'],
                    'Meta 2030': [target_ev, target_renewable, target_co2_reduction],
                    'Progreso Actual': [current_ev_pct, current_renewable_pct, co2_reduction],
                    'Cumplimiento': [
                        current_ev_pct / target_ev * 100,
                        current_renewable_pct / target_renewable * 100,
                        co2_reduction / target_co2_reduction * 100
                    ]
                })
                
                fig_progress = px.bar(
                    progress_data,
                    x='Objetivo',
                    y=['Meta 2030', 'Progreso Actual'],
                    title="🎯 Progreso hacia Objetivos 2030",
                    barmode='group',
                    color_discrete_sequence=['#a7f3d0', '#10b981']
                )
                fig_progress.update_layout(
                    template='plotly_white',
                    font=dict(family='Inter')
                )
                st.plotly_chart(fig_progress, use_container_width=True)
            
            with col2:
                # Indicador de cumplimiento
                avg_compliance = progress_data['Cumplimiento'].mean()
                
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = avg_compliance,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "📊 Cumplimiento Global 2030"},
                    delta = {'reference': 100},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#10b981"},
                        'steps': [
                            {'range': [0, 50], 'color': "#fef2f2"},
                            {'range': [50, 80], 'color': "#fffbeb"},
                            {'range': [80, 100], 'color': "#ecfdf5"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                fig_gauge.update_layout(
                    template='plotly_white',
                    font=dict(family='Inter')
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Evaluación de cumplimiento
            if avg_compliance < 60:
                urgency = "CRÍTICA"
                color = "danger"
                action = "Requiere medidas extraordinarias e inversión masiva en movilidad verde"
            elif avg_compliance < 80:
                urgency = "ALTA"
                color = "warning"
                action = "Acelerar significativamente las iniciativas de transporte sostenible"
            else:
                urgency = "MODERADA"
                color = "success"
                action = "Mantener ritmo actual con optimizaciones específicas"
            
            st.markdown(f"""
            <div class="alert-{color}">
                <h4>🚨 Estado Objetivos 2030 - Prioridad {urgency}</h4>
                <p><strong>Cumplimiento Global:</strong> {avg_compliance:.1f}% de los objetivos</p>
                <p><strong>Vehículos EV/Híbridos:</strong> {current_ev_pct:.1f}% actual vs {target_ev}% objetivo</p>
                <p><strong>Energías Renovables:</strong> {current_renewable_pct:.1f}% actual vs {target_renewable}% objetivo</p>
                <p><strong>Acción Requerida:</strong> {action}</p>
                <p><strong>Inversión Verde Actual:</strong> €{current_green_investment:.1f}M (requiere duplicar para 2030)</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Resumen ejecutivo
    st.markdown("---")
    st.markdown(f"""
    <div class="green-insight-container">
        <h4>📋 Resumen Ejecutivo - Transporte Verde España</h4>
        <p><strong>Período de Análisis:</strong> {start_date} a {end_date} | <strong>Alcance:</strong> {len(filtered_df):,} operaciones en {len(selected_regions_filter if not st.session_state.selected_region else [st.session_state.selected_region])} comunidades</p>
        <p><strong>Rendimiento Verde Nacional:</strong> {avg_green_score_spain:.1f}% puntuación sostenibilidad | {avg_ev_share_spain:.1f}% share flota EV</p>
        <p><strong>Impacto Ambiental:</strong> {total_emissions_m:.1f}M kg CO₂ | €{total_green_savings_m:.1f}M ahorros verdes acumulados</p>
        <p><strong>Progreso Estratégico:</strong> {avg_2030_progress_spain:.1f}% avance hacia objetivos 2030 | Liderazgo europeo en movilidad sostenible</p>
        <p><strong>Oportunidades Identificadas:</strong> Potencial €{(total_green_savings_m * 3.5):.1f}M adicionales con electrificación completa del transporte</p>
        <p><strong>Próximas Acciones:</strong> {'Acelerar despliegue infraestructura carga rápida y políticas incentivos' if avg_ev_share_spain < 60 else 'Optimizar redes inteligentes y explorar hidrógeno verde' if avg_ev_share_spain < 80 else 'Liderar innovación en movilidad autónoma sostenible'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer profesional
    st.markdown("---")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: white; padding: 3rem; border-radius: 20px; text-align: center; margin-top: 2rem;'>
        <h3 style='margin: 0; color: white; font-size: 2rem;'>🌱 Grecert DGT España - Transporte Verde</h3>
        <p style='margin: 1.5rem 0; font-size: 1.2rem; opacity: 0.95;'>Plataforma de Inteligencia Ejecutiva | Movilidad Sostenible | Futuro Verde</p>
        <p style='margin: 0; font-size: 1rem; opacity: 0.85;'>© 2025 Grecert.com - Liderando la Revolución del Transporte Sostenible en España | Todos los Derechos Reservados</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
