"""
Dashboard Profesional — Optimización de Suscripción de Cine
Autor: CMSR92
Fecha: Noviembre 2025

Dashboard ejecutivo que presenta el análisis completo de suscripción de cine
con storytelling de datos, visualizaciones interactivas y proyecciones financieras.
"""

import os
import json
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
import warnings

import pandas as pd
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import sys

# Silenciar warnings
warnings.filterwarnings("ignore")

# Setup paths
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.pricing_optimization import simulate_pricing_scenarios
from src import data_processing as dp
from src import feature_engineering as fe

# Paths
ASSETS_DIR = Path(__file__).parent / 'assets'
FIG_DIR = ROOT / 'reports' / 'figures'
LOGO_PNG = FIG_DIR / 'logo_cmsr92.png'
FEAT_PATH = ROOT / 'data' / 'processed' / 'model_features.csv'
CLEAN_PATH = ROOT / 'data' / 'processed' / 'cleaned_data.csv'
RAW_PATH = ROOT / 'data' / 'raw' / 'movie_theatre_sales.csv'
METRICS_JSON = FIG_DIR / 'model_metrics.json'
KPIS_JSON = FIG_DIR / 'financial_kpis.json'
PRICING_CSV = FIG_DIR / 'pricing_results.csv'
EXPORT_SCRIPT = ROOT / 'presentations' / 'export_figures.py'
VENV_PY = ROOT / '.venv' / 'Scripts' / 'python.exe'

# Config
st.set_page_config(
    page_title='Cinema Subscription Strategy — CMSR92',
    page_icon='🎬',
    layout='wide',
    initial_sidebar_state='collapsed'
)

# Custom CSS adaptable al tema del sistema
st.markdown("""
<style>
    /* Variables de color según tema */
    :root {
        --text-primary: #1f1f1f;
        --text-secondary: #666;
        --bg-insight: #e3f2fd;
        --bg-success: #e8f5e9;
        --bg-warning: #fff8e1;
        --border-insight: #1976d2;
        --border-success: #43a047;
        --border-warning: #f57c00;
        --shadow: rgba(0,0,0,0.1);
    }
    
    [data-theme="dark"] {
        --text-primary: #ffffff;
        --text-secondary: #b0b0b0;
        --bg-insight: #1a2332;
        --bg-success: #1b2e1f;
        --bg-warning: #2e2418;
        --border-insight: #64b5f6;
        --border-success: #81c784;
        --border-warning: #ffb74d;
        --shadow: rgba(255,255,255,0.1);
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: var(--text-secondary);
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px var(--shadow);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
        color: white;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.95;
        color: white;
    }
    
    /* Cajas informativas adaptables */
    .insight-box {
        background: var(--bg-insight);
        border-left: 4px solid var(--border-insight);
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        color: var(--text-primary);
    }
    
    .insight-box strong {
        color: var(--text-primary);
    }
    
    .success-box {
        background: var(--bg-success);
        border-left: 4px solid var(--border-success);
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        color: var(--text-primary);
    }
    
    .success-box strong, .success-box h4 {
        color: var(--text-primary);
    }
    
    .warning-box {
        background: var(--bg-warning);
        border-left: 4px solid var(--border-warning);
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        color: var(--text-primary);
    }
    
    .warning-box strong, .warning-box h4 {
        color: var(--text-primary);
    }
    
    /* Mejorar contraste de texto en cajas */
    .insight-box ul, .success-box ul, .warning-box ul {
        color: var(--text-primary);
        padding-left: 1.5rem;
    }
    
    .insight-box ul li, .success-box ul li, .warning-box ul li {
        margin: 0.5rem 0;
    }
    
    .insight-box p, .success-box p, .warning-box p {
        color: var(--text-primary);
        margin: 0.5rem 0;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Script para detectar y aplicar tema automáticamente usando components
components.html("""
<script>
    (function() {
        // Detectar tema del sistema
        function applyTheme() {
            const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
            const streamlitDoc = window.parent.document;
            
            if (streamlitDoc) {
                if (isDark) {
                    streamlitDoc.documentElement.setAttribute('data-theme', 'dark');
                } else {
                    streamlitDoc.documentElement.setAttribute('data-theme', 'light');
                }
            }
        }
        
        // Aplicar tema al cargar
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', applyTheme);
        } else {
            applyTheme();
        }
        
        // Detectar cambios en el tema del sistema
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme);
        }
    })();
</script>
""", height=0)

# Helper functions
def load_data():
    """Cargar y preparar datos"""
    try:
        if CLEAN_PATH.exists():
            df = pd.read_csv(CLEAN_PATH)
        else:
            df_raw = dp.load_data(str(RAW_PATH))
            df = dp.basic_clean(df_raw)
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None

def load_kpis():
    """Cargar KPIs financieros"""
    try:
        if KPIS_JSON.exists():
            return json.loads(KPIS_JSON.read_text(encoding='utf-8'))
        return None
    except Exception:
        return None

def load_model_metrics():
    """Cargar métricas del modelo"""
    try:
        if METRICS_JSON.exists():
            return json.loads(METRICS_JSON.read_text(encoding='utf-8'))
        return None
    except Exception:
        return None

def metric_card(label, value, delta=None, delta_color="normal"):
    """Crear una métrica estilizada"""
    return st.metric(label=label, value=value, delta=delta, delta_color=delta_color)

def plotly_theme():
    """Tema consistente para gráficos basado en el tema de Streamlit"""
    try:
        # Intentar detectar el tema de Streamlit configurado
        theme = st.get_option('theme.base')
        if theme == 'dark':
            return 'plotly_dark'
        elif theme == 'light':
            return 'plotly_white'
        else:
            # Si no está configurado, usar plotly_white por defecto
            return 'plotly_white'
    except:
        # Fallback seguro
        return 'plotly_white'

# Header
if LOGO_PNG.exists():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(str(LOGO_PNG), width=300)
st.markdown('<div class="main-header">🎬 Estrategia de Suscripción de Cine</div>', unsafe_allow_html=True)

st.markdown('<div class="sub-header">Análisis Data-Driven para Optimización de Precios y Proyecciones Financieras</div>', unsafe_allow_html=True)

# Load data
df = load_data()
kpis = load_kpis()
model_metrics = load_model_metrics()

# ============================================================================
# EXECUTIVE DASHBOARD - Vista Principal
# ============================================================================

st.markdown("---")
st.markdown("## 📊 Resumen Ejecutivo")

# KPIs principales en cards
def kpi_card(col, label, value, note, background=None):
    """Tarjeta KPI en un solo bloque HTML: si se abre el <div> en un st.markdown y se cierra en otro, Streamlit
    los pinta como elementos separados y la tarjeta sale vacía."""
    style = f' style="background: {background};"' if background else ""
    col.markdown(f'''<div class="metric-card"{style}>
<div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-label">{note}</div>
</div>''', unsafe_allow_html=True)


if kpis:
    col1, col2, col3, col4 = st.columns(4)
    kpi_card(col1, "Precio Óptimo de Suscripción", f"${kpis.get('price', 180)}", "por año")
    kpi_card(col2, "Suscriptores para Punto de Equilibrio", int(kpis.get("break_even_subs", 0)), "requeridos",
             "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)")
    kpi_card(col3, "Retorno de Inversión (ROI)", f"{kpis.get('roi_percent', 0):.0f}%", "proyectado año 1",
             "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)")
    kpi_card(col4, "Tiempo de Recuperación de la Inversión", f"{kpis.get('payback_months', 0):.1f}", "meses estimados",
             "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)")
else:
    st.info("⚙️ Ejecuta el pipeline para generar KPIs financieros")

st.markdown("---")

# Problema y Solución
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 🎯 Diagnóstico de la Situación Actual")
    st.markdown("""
    <div class="warning-box">
    <h4>📉 Retos Estratégicos del Cine</h4>
    <ul>
        <li><strong>Descenso del 15% en la asistencia anual</strong> por cambios en hábitos de consumo</li>
        <li>Competencia intensificada por plataformas de streaming líderes</li>
        <li>Volatilidad en ingresos y dificultad para proyectar resultados</li>
        <li>Falta de mecanismos efectivos de fidelización y retención</li>
    </ul>
    <p>La industria enfrenta la necesidad de reinventar su propuesta de valor para sostener el crecimiento y la rentabilidad.</p>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("### 💡 Estrategia Recomendada")
    st.markdown("""
    <div class="success-box">
    <h4>🎬 Programa de Suscripción Anual</h4>
    <ul>
        <li><strong>$180/año</strong> ($15/mes): posicionamiento competitivo y accesible</li>
        <li>Acceso ilimitado a películas y beneficios exclusivos para suscriptores</li>
        <li>Transformación de ingresos variables en flujos recurrentes y predecibles</li>
        <li>Fidelización de clientes de alto valor mediante experiencias diferenciadas</li>
    </ul>
    <p>La suscripción permite construir una base sólida de clientes, optimizar la rentabilidad y fortalecer la resiliencia ante cambios de mercado.</p>
    </div>
    """, unsafe_allow_html=True)

# Tabs para análisis detallado
st.markdown("---")
tabs = st.tabs([
    "📈 Análisis de Negocio",
    "👥 Segmentación de Clientes", 
    "💰 Optimización de Precios",
    "📊 Proyecciones Financieras",
    "🔧 Configuración"
])

# ============================================================================
# TAB 1: ANÁLISIS DE NEGOCIO
# ============================================================================
with tabs[0]:
    st.markdown("## 📈 Análisis del Comportamiento de Clientes")
    
    if df is not None and len(df) > 0:
        # Estadísticas clave
        st.markdown("### 📊 Datos Clave del Negocio")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            metric_card("Total Transacciones", f"{len(df):,}")
        with col2:
            avg_ticket = df['Ticket_Price'].mean()
            metric_card("Precio Promedio Ticket", f"${avg_ticket:.2f}")
        with col3:
            avg_group = df['Number_of_Person'].mean()
            metric_card("Personas por Compra", f"{avg_group:.1f}")
        with col4:
            retention = (df['Purchase_Again'].sum() / len(df) * 100)
            metric_card("Tasa de Retención", f"{retention:.1f}%")
        
        st.markdown("---")
        
        # Visualizaciones interactivas
        col_viz1, col_viz2 = st.columns(2)
        
        with col_viz1:
            st.markdown("#### Distribución de Precios de Tickets")
            fig_price = px.histogram(
                df, 
                x='Ticket_Price',
                nbins=30,
                color_discrete_sequence=['#667eea'],
                labels={
                    'Ticket_Price': 'Precio del Ticket (USD)', 
                    'count': 'Frecuencia'
                }
            )
            fig_price.update_layout(
                template=plotly_theme(),
                showlegend=False,
                height=400,
                xaxis_title='Precio del Ticket (USD)',
                yaxis_title='Número de Transacciones',
                margin=dict(l=60, r=40, t=40, b=60)
            )
            fig_price.update_xaxes(tickformat='$,.2f')
            fig_price.add_vline(
                x=avg_ticket, 
                line_dash="dash", 
                line_color="red",
                annotation_text=f"Promedio: ${avg_ticket:.2f}",
                annotation_position="top"
            )
            # Mejorar tooltips
            fig_price.update_traces(
                hovertemplate='<b>Precio:</b> $%{x:.2f}<br><b>Transacciones:</b> %{y}<extra></extra>'
            )
            st.plotly_chart(fig_price, use_container_width=True)
            
            st.markdown(f"""
            <div class="insight-box">
            <strong>💡 Insight:</strong> El precio promedio es <strong>${avg_ticket:.2f}</strong>. 
            La suscripción a $180/año equivale a ~{180/avg_ticket:.0f} películas, 
            excelente valor para clientes frecuentes.
            </div>
            """, unsafe_allow_html=True)
        
        with col_viz2:
            st.markdown("#### Tamaño de Grupos")
            group_dist = df['Number_of_Person'].value_counts().sort_index()
            fig_group = px.bar(
                x=group_dist.index,
                y=group_dist.values,
                color=group_dist.values,
                color_continuous_scale='Viridis',
                labels={
                    'x': 'Número de Personas por Grupo', 
                    'y': 'Cantidad de Transacciones',
                    'color': 'Frecuencia'
                }
            )
            fig_group.update_layout(
                template=plotly_theme(),
                showlegend=False,
                height=400,
                xaxis_title='Número de Personas por Grupo',
                yaxis_title='Cantidad de Transacciones',
                margin=dict(l=60, r=40, t=40, b=60),
                coloraxis_showscale=False
            )
            # Mejorar tooltips
            fig_group.update_traces(
                hovertemplate='<b>Tamaño del Grupo:</b> %{x} personas<br><b>Transacciones:</b> %{y}<extra></extra>'
            )
            st.plotly_chart(fig_group, use_container_width=True)
            
            most_common = group_dist.idxmax()
            st.markdown(f"""
            <div class="insight-box">
            <strong>💡 Insight:</strong> El tamaño más común es <strong>{most_common:.0f} personas</strong>. 
            Considerar planes familiares o grupales como complemento.
            </div>
            """, unsafe_allow_html=True)
        
        # Análisis por género
        st.markdown("---")
        st.markdown("#### 🎭 Análisis de Preferencias por Género")
        
        df_revenue = df.copy()
        df_revenue['revenue_est'] = df_revenue['Ticket_Price'] * df_revenue['Number_of_Person']
        genre_analysis = df_revenue.groupby('Movie_Genre').agg({
            'Ticket_ID': 'count',
            'revenue_est': 'sum',
            'Ticket_Price': 'mean',
            'Purchase_Again': 'mean'
        }).round(2)
        genre_analysis.columns = ['Transacciones', 'Revenue Total', 'Precio Promedio', 'Tasa Retención']
        genre_analysis = genre_analysis.sort_values('Revenue Total', ascending=False)
        
        col_genre1, col_genre2 = st.columns(2)
        
        with col_genre1:
            fig_genre_rev = px.bar(
                genre_analysis.reset_index(),
                x='Movie_Genre',
                y='Revenue Total',
                color='Tasa Retención',
                color_continuous_scale='RdYlGn',
                labels={
                    'Movie_Genre': 'Género de Película', 
                    'Revenue Total': 'Ingresos Totales (USD)',
                    'Tasa Retención': 'Tasa de Retención'
                }
            )
            fig_genre_rev.update_layout(
                template=plotly_theme(), 
                height=450,
                xaxis_title='Género de Película',
                yaxis_title='Ingresos Totales (USD)',
                margin=dict(l=60, r=40, t=40, b=80),
                coloraxis_colorbar=dict(
                    title='Retención<br>(%)',
                    tickformat='.0%'
                )
            )
            fig_genre_rev.update_yaxes(tickformat='$,.0f')
            fig_genre_rev.update_xaxes(tickangle=-45)
            # Mejorar tooltips
            fig_genre_rev.update_traces(
                hovertemplate='<b>Género:</b> %{x}<br><b>Ingresos:</b> $%{y:,.0f}<br><b>Retención:</b> %{marker.color:.1%}<extra></extra>'
            )
            st.plotly_chart(fig_genre_rev, use_container_width=True)
        
        with col_genre2:
            # Preparar datos para tooltips personalizados
            genre_data = genre_analysis.reset_index()
            
            fig_genre_ret = px.scatter(
                genre_data,
                x='Transacciones',
                y='Tasa Retención',
                size='Revenue Total',
                color='Movie_Genre',
                custom_data=['Movie_Genre', 'Precio Promedio', 'Revenue Total'],
                labels={
                    'Transacciones': 'Volumen de Transacciones', 
                    'Tasa Retención': 'Tasa de Retención (%)',
                    'Movie_Genre': 'Género',
                    'Precio Promedio': 'Precio Promedio (USD)',
                    'Revenue Total': 'Ingresos Totales'
                }
            )
            fig_genre_ret.update_traces(
                hovertemplate='<b>Género:</b> %{customdata[0]}<br><b>Transacciones:</b> %{x:,}<br><b>Retención:</b> %{y:.1%}<br><b>Precio Promedio:</b> $%{customdata[1]:.2f}<br><b>Ingresos:</b> $%{customdata[2]:,.0f}<extra></extra>'
            )
            fig_genre_ret.update_layout(
                template=plotly_theme(), 
                height=450,
                xaxis_title='Volumen de Transacciones',
                yaxis_title='Tasa de Retención (%)',
                margin=dict(l=60, r=40, t=40, b=60),
                legend=dict(
                    title='Género',
                    orientation='v',
                    yanchor='top',
                    y=1,
                    xanchor='left',
                    x=1.02
                )
            )
            fig_genre_ret.update_yaxes(tickformat='.0%')
            st.plotly_chart(fig_genre_ret, use_container_width=True)
        
        st.markdown("""
        <div class="insight-box">
        <strong>💡 Recomendación:</strong> Focalizar marketing de suscripción en géneros con 
        mayor tasa de retención y alto volumen. Usar contenido exclusivo de estos géneros 
        como incentivo de inscripción.
        </div>
        """, unsafe_allow_html=True)
        
        # Análisis por tipo de asiento
        st.markdown("---")
        st.markdown("#### 🪑 Análisis por Tipo de Asiento")
        
        seat_analysis = df_revenue.groupby('Seat_Type').agg({
            'Ticket_ID': 'count',
            'revenue_est': 'sum',
            'Ticket_Price': 'mean'
        }).round(2)
        
        fig_seat = go.Figure()
        fig_seat.add_trace(go.Bar(
            name='Ingresos Totales',
            x=seat_analysis.index,
            y=seat_analysis['revenue_est'],
            marker_color='#667eea',
            hovertemplate='<b>Tipo de Asiento:</b> %{x}<br><b>Ingresos:</b> $%{y:,.0f}<extra></extra>'
        ))
        fig_seat.add_trace(go.Scatter(
            name='Precio Promedio por Ticket',
            x=seat_analysis.index,
            y=seat_analysis['Ticket_Price'],
            yaxis='y2',
            marker_color='#f5576c',
            mode='lines+markers',
            line=dict(width=3),
            marker=dict(size=10),
            hovertemplate='<b>Tipo de Asiento:</b> %{x}<br><b>Precio Promedio:</b> $%{y:.2f}<extra></extra>'
        ))
        fig_seat.update_layout(
            template=plotly_theme(),
            yaxis=dict(
                title='Ingresos Totales (USD)',
                tickformat='$,.0f'
            ),
            yaxis2=dict(
                title='Precio Promedio por Ticket (USD)', 
                overlaying='y', 
                side='right',
                tickformat='$,.2f'
            ),
            xaxis_title='Tipo de Asiento',
            height=450,
            hovermode='x unified',
            margin=dict(l=60, r=80, t=40, b=60),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            )
        )
        st.plotly_chart(fig_seat, use_container_width=True)
        
        st.markdown("""
        <div class="insight-box">
        <strong>💡 Estrategia:</strong> Ofrecer beneficios diferenciados por tipo de asiento 
        (ej: upgrade gratuito a Premium una vez al mes para suscriptores).
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.warning("⚠️ No hay datos disponibles. Verifica que exista el archivo de datos limpios.")

# ============================================================================
# TAB 2: SEGMENTACIÓN DE CLIENTES
# ============================================================================
with tabs[1]:
    st.markdown("## 👥 Segmentación de Clientes")
    st.markdown("Identificación de perfiles de clientes mediante clustering para personalizar la estrategia.")
    
    try:
        # Cargar features
        if FEAT_PATH.exists():
            feat_df = pd.read_csv(FEAT_PATH)
        elif df is not None:
            feat_df, _ = fe.build_features_pipeline(df)
        else:
            feat_df = None
        
        if feat_df is not None and len(feat_df) > 0:
            # Preparar datos para clustering
            num_cols = feat_df.select_dtypes(include=['int64', 'float64']).fillna(0)
            
            if len(num_cols.columns) >= 2:
                # PCA para visualización
                pca = PCA(n_components=2, random_state=42)
                Z = pca.fit_transform(num_cols)
                
                # KMeans clustering
                n_clusters = 4
                kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
                clusters = kmeans.fit_predict(num_cols)
                
                # Añadir clusters al dataframe
                feat_df['Segmento'] = clusters
                
                # Visualización de segmentos
                st.markdown("### 🎯 Visualización de Segmentos (PCA)")
                
                df_viz = pd.DataFrame({
                    'PC1': Z[:, 0],
                    'PC2': Z[:, 1],
                    'Segmento': [f'Segmento {c}' for c in clusters]
                })
                
                # Preparar datos con custom_data para tooltips
                df_viz_plot = df_viz.copy()
                df_viz_plot['Segmento_Label'] = 'Segmento ' + df_viz_plot['Segmento'].astype(str)
                
                fig_seg = px.scatter(
                    df_viz_plot,
                    x='PC1',
                    y='PC2',
                    color='Segmento',
                    color_discrete_sequence=px.colors.qualitative.Bold,
                    custom_data=['Segmento_Label'],
                    labels={
                        'PC1': 'Componente Principal 1 (PCA)', 
                        'PC2': 'Componente Principal 2 (PCA)',
                        'Segmento': 'Segmento de Cliente'
                    },
                    title='Visualización de Segmentos (PCA)'
                )
                fig_seg.update_traces(
                    marker=dict(size=10, opacity=0.7, line=dict(width=0.5, color='white')),
                    hovertemplate='<b>%{customdata[0]}</b><br>Componente 1: %{x:.2f}<br>Componente 2: %{y:.2f}<extra></extra>'
                )
                fig_seg.update_layout(
                    template=plotly_theme(), 
                    height=550,
                    xaxis_title='Componente Principal 1 (PCA)',
                    yaxis_title='Componente Principal 2 (PCA)',
                    margin=dict(l=60, r=60, t=60, b=60),
                    legend=dict(
                        title='Segmentos',
                        orientation='v',
                        yanchor='top',
                        y=1,
                        xanchor='left',
                        x=1.02
                    )
                )
                st.plotly_chart(fig_seg, use_container_width=True)
                
                st.markdown("""
                <div class="insight-box">
                <strong>🔍 ¿Qué vemos en este gráfico?</strong><br>
                Este gráfico utiliza PCA (Análisis de Componentes Principales) para visualizar los segmentos de clientes 
                en 2 dimensiones. Cada punto representa un cliente, y los colores indican a qué segmento pertenece 
                según el algoritmo K-Means. Los grupos bien diferenciados (clústeres separados) indican patrones de 
                comportamiento distintos entre segmentos, lo que permite estrategias de marketing personalizadas.
                </div>
                """, unsafe_allow_html=True)
                
                # Perfiles de segmentos
                st.markdown("---")
                st.markdown("### 📋 Perfiles de Segmentos")
                
                # Calcular promedios por segmento
                key_features = ['Age', 'Ticket_Price', 'Number_of_Person']
                available_features = [f for f in key_features if f in feat_df.columns]
                
                if available_features:
                    profiles = feat_df.groupby('Segmento')[available_features].mean().round(2)
                    
                    # Añadir tamaño de cada segmento
                    profiles['Tamaño'] = feat_df.groupby('Segmento').size()
                    profiles['% del Total'] = (profiles['Tamaño'] / len(feat_df) * 100).round(1)
                    
                    # Mostrar en columnas
                    cols = st.columns(n_clusters)
                    
                    for idx, (seg_id, row) in enumerate(profiles.iterrows()):
                        with cols[idx]:
                            st.markdown(f"#### Segmento {seg_id}")
                            st.metric("Clientes", f"{int(row['Tamaño']):,}", 
                                     delta=f"{row['% del Total']:.1f}% del total")
                            
                            if 'Age' in row:
                                st.metric("Edad Promedio", f"{row['Age']:.0f} años")
                            if 'Ticket_Price' in row:
                                st.metric("Gasto Promedio", f"${row['Ticket_Price']:.2f}")
                            if 'Number_of_Person' in row:
                                st.metric("Tamaño Grupo", f"{row['Number_of_Person']:.1f}")
                            
                            # Recomendación por segmento
                            if 'Age' in row and 'Number_of_Person' in row:
                                age = row['Age']
                                group_size = row['Number_of_Person']
                                
                                if age < 35 and group_size < 3:
                                    recommendation = "🎯 **Target Principal**: Jóvenes individuales/parejas. Plan estándar."
                                elif age < 35 and group_size >= 3:
                                    recommendation = "👨‍👩‍👧‍👦 **Familias Jóvenes**: Plan familiar con beneficios grupales."
                                elif age >= 35 and group_size >= 4:
                                    recommendation = "👨‍👩‍👧 **Familias Maduras**: Plan premium con extras."
                                else:
                                    recommendation = "🎭 **Entusiastas**: Plan con contenido exclusivo."
                                
                                st.markdown(recommendation)
                
                # Insights generales
                st.markdown("---")
                st.markdown("""
                <div class="success-box">
                <h4>💡 Insights Clave de Segmentación</h4>
                <ul>
                    <li><strong>Segmento objetivo principal:</strong> Identificar el segmento con mayor frecuencia 
                    y gasto promedio para focalizar el lanzamiento</li>
                    <li><strong>Personalización:</strong> Adaptar beneficios y comunicación según perfil demográfico</li>
                    <li><strong>Estrategia de precios:</strong> Considerar tiers diferenciados 
                    (individual, pareja, familiar)</li>
                    <li><strong>Retención:</strong> Programas de fidelización específicos por segmento</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Necesitas al menos 2 variables numéricas para segmentación.")
        else:
            st.warning("⚠️ Datos de features no disponibles. Ejecuta el pipeline de preparación de datos.")
    
    except Exception as e:
        st.error(f"Error en segmentación: {e}")

# ============================================================================
# TAB 3: OPTIMIZACIÓN DE PRECIOS
# ============================================================================
with tabs[2]:
    st.markdown("## 💰 Simulador de Precios y Rentabilidad")
    st.markdown("Análisis de escenarios para encontrar el punto óptimo de precio vs. volumen.")
    
    # Controles de simulación
    st.markdown("### ⚙️ Parámetros del Escenario")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        price_selected = st.slider('Precio Anual ($)', 90, 300, 180, 10, 
                                   help="Precio de la suscripción anual")
    with col2:
        subs_selected = st.number_input('Suscriptores Estimados', 50, 5000, 350, 10,
                                        help="Número estimado de suscriptores en año 1")
    with col3:
        fixed_costs = st.number_input('Costos Fijos Anuales ($)', 0, 100000, 25000, 1000,
                                      help="Costos fijos totales del programa")
    with col4:
        variable_cost = st.number_input('Costo Variable por Cliente ($)', 0, 150, 80, 5,
                                        help="Costo variable por suscriptor")
    
    st.markdown("---")
    
    # Simulación de escenarios
    st.markdown("### 📊 Análisis de Escenarios")
    
    # Definir escenarios de precio con adopción estimada
    scenarios = [
        {'price': 120, 'subs': 485, 'description': 'Precio bajo - Alta adopción'},
        {'price': 150, 'subs': 420, 'description': 'Precio moderado-bajo'},
        {'price': 180, 'subs': 350, 'description': 'Precio óptimo (recomendado)'},
        {'price': 210, 'subs': 260, 'description': 'Precio moderado-alto'},
        {'price': 240, 'subs': 180, 'description': 'Precio premium - Baja adopción'},
        {'price': price_selected, 'subs': subs_selected, 'description': 'Tu escenario personalizado'}
    ]
    
    # Calcular métricas para cada escenario
    results = []
    for s in scenarios:
        revenue = s['price'] * s['subs']
        var_costs = variable_cost * s['subs']
        contribution = revenue - var_costs
        profit = contribution - fixed_costs
        margin = (contribution / revenue * 100) if revenue > 0 else 0
        break_even = fixed_costs / (s['price'] - variable_cost) if (s['price'] - variable_cost) > 0 else float('inf')
        
        results.append({
            'Escenario': s['description'],
            'Precio': s['price'],
            'Suscriptores': s['subs'],
            'Revenue': revenue,
            'Costos Variables': var_costs,
            'Margen Contribución': contribution,
            'Beneficio': profit,
            'Margen %': margin,
            'Break-Even': break_even
        })
    
    results_df = pd.DataFrame(results)
    
    # Visualización comparativa
    col_viz1, col_viz2 = st.columns(2)
    
    with col_viz1:
        fig_revenue = go.Figure()
        fig_revenue.add_trace(go.Bar(
            name='Ingresos Anuales',
            x=results_df['Precio'],
            y=results_df['Revenue'],
            marker_color='#667eea',
            text=results_df['Revenue'].apply(lambda x: f'${x:,.0f}'),
            textposition='outside',
            hovertemplate='<b>Precio:</b> $%{x}<br><b>Ingresos:</b> $%{y:,.0f}<extra></extra>'
        ))
        fig_revenue.add_trace(go.Scatter(
            name='Suscriptores Esperados',
            x=results_df['Precio'],
            y=results_df['Suscriptores'],
            yaxis='y2',
            mode='lines+markers',
            marker=dict(size=12, color='#f5576c'),
            line=dict(width=4, color='#f5576c'),
            hovertemplate='<b>Precio:</b> $%{x}<br><b>Suscriptores:</b> %{y:,}<extra></extra>'
        ))
        fig_revenue.update_layout(
            title='Análisis de Ingresos y Adopción por Precio',
            template=plotly_theme(),
            yaxis=dict(
                title='Ingresos Anuales (USD)',
                tickformat='$,.0f'
            ),
            yaxis2=dict(
                title='Número de Suscriptores', 
                overlaying='y', 
                side='right',
                tickformat=','
            ),
            height=480,
            xaxis_title='Precio de Suscripción Anual (USD)',
            xaxis=dict(tickformat='$,.0f'),
            margin=dict(l=70, r=80, t=60, b=60),
            hovermode='x unified',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            )
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col_viz2:
        fig_profit = go.Figure()
        colors = ['#28a745' if x > 0 else '#dc3545' for x in results_df['Beneficio']]
        fig_profit.add_trace(go.Bar(
            x=results_df['Precio'],
            y=results_df['Beneficio'],
            marker_color=colors,
            text=results_df['Beneficio'].apply(lambda x: f'${x:,.0f}'),
            textposition='outside',
            hovertemplate='<b>Precio:</b> $%{x}<br><b>Beneficio:</b> $%{y:,.0f}<br><b>Estado:</b> %{customdata}<extra></extra>',
            customdata=['Rentable' if x > 0 else 'No Rentable' for x in results_df['Beneficio']]
        ))
        fig_profit.add_hline(
            y=0, 
            line_dash="dash", 
            line_color="gray",
            annotation_text="Break-Even",
            annotation_position="right"
        )
        fig_profit.update_layout(
            title='Beneficio Neto por Escenario de Precio',
            template=plotly_theme(),
            yaxis_title='Beneficio Anual (USD)',
            yaxis=dict(tickformat='$,.0f'),
            xaxis_title='Precio de Suscripción Anual (USD)',
            xaxis=dict(tickformat='$,.0f'),
            height=480,
            margin=dict(l=70, r=40, t=60, b=60),
            showlegend=False
        )
        st.plotly_chart(fig_profit, use_container_width=True)
    
    # Tabla detallada
    st.markdown("### 📋 Tabla Comparativa de Escenarios")
    
    # Formatear tabla
    display_df = results_df.copy()
    for col in ['Precio', 'Revenue', 'Costos Variables', 'Margen Contribución', 'Beneficio']:
        display_df[col] = display_df[col].apply(lambda x: f'${x:,.0f}')
    display_df['Margen %'] = display_df['Margen %'].apply(lambda x: f'{x:.1f}%')
    display_df['Break-Even'] = display_df['Break-Even'].apply(lambda x: f'{int(x)}' if x != float('inf') else '∞')
    
    st.dataframe(display_df, use_container_width=True, height=300)
    
    # Análisis del escenario seleccionado
    st.markdown("---")
    st.markdown(f"### 🎯 Análisis de Tu Escenario: ${price_selected}/año")
    
    selected_result = results_df[results_df['Precio'] == price_selected].iloc[-1]
    
    col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
    
    with col_metric1:
        metric_card("Revenue Año 1", f"${selected_result['Revenue']:,.0f}")
    with col_metric2:
        metric_card("Margen Contribución", f"${selected_result['Margen Contribución']:,.0f}")
    with col_metric3:
        profit_val = selected_result['Beneficio']
        metric_card("Beneficio Neto", f"${profit_val:,.0f}", 
                   delta="Rentable" if profit_val > 0 else "No rentable",
                   delta_color="normal" if profit_val > 0 else "inverse")
    with col_metric4:
        be = selected_result['Break-Even']
        metric_card("Break-Even", f"{int(be)} subs" if be != float('inf') else "∞")
    
    # Recomendación
    if selected_result['Beneficio'] > 0:
        if selected_result['Margen %'] > 40:
            recommendation = "success-box"
            icon = "✅"
            message = "Excelente margen de rentabilidad. Este precio ofrece un balance óptimo."
        else:
            recommendation = "insight-box"
            icon = "📊"
            message = "Escenario rentable, pero considera optimizar para mejorar márgenes."
    else:
        recommendation = "warning-box"
        icon = "⚠️"
        message = "Este escenario no es rentable. Aumenta el precio o reduce costos."
    
    st.markdown(f"""
    <div class="{recommendation}">
    <h4>{icon} Evaluación del Escenario</h4>
    <p>{message}</p>
    <ul>
        <li><strong>Margen de contribución:</strong> {selected_result['Margen %']:.1f}%</li>
        <li><strong>Necesitas alcanzar:</strong> {int(selected_result['Break-Even'])} suscriptores para break-even</li>
        <li><strong>Actualmente proyectas:</strong> {selected_result['Suscriptores']} suscriptores</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Análisis de sensibilidad
    st.markdown("---")
    st.markdown("### 📈 Análisis de Sensibilidad")
    
    with st.expander("Ver análisis detallado"):
        # Crear matriz de sensibilidad precio vs suscriptores
        price_range = np.linspace(120, 280, 9)
        subs_range = np.linspace(150, 550, 9)
        
        sensitivity_matrix = np.zeros((len(price_range), len(subs_range)))
        
        for i, p in enumerate(price_range):
            for j, s in enumerate(subs_range):
                revenue = p * s
                costs = variable_cost * s + fixed_costs
                profit = revenue - costs
                sensitivity_matrix[i, j] = profit
        
        fig_sens = go.Figure(data=go.Heatmap(
            z=sensitivity_matrix,
            x=subs_range.astype(int),
            y=price_range.astype(int),
            colorscale='RdYlGn',
            colorbar=dict(
                title='Beneficio<br>Anual (USD)',
                tickformat='$,.0f',
                len=0.9
            ),
            text=sensitivity_matrix.astype(int),
            texttemplate='$%{text:,}',
            textfont={"size": 9},
            hovertemplate='<b>Precio:</b> $%{y}<br><b>Suscriptores:</b> %{x:,}<br><b>Beneficio:</b> $%{z:,.0f}<extra></extra>'
        ))
        
        fig_sens.update_layout(
            title='Mapa de Calor de Sensibilidad: Beneficio según Precio y Volumen',
            xaxis_title='Número de Suscriptores Esperados',
            yaxis_title='Precio Anual de Suscripción (USD)',
            xaxis=dict(tickformat=','),
            yaxis=dict(tickformat='$,.0f'),
            template=plotly_theme(),
            height=600,
            margin=dict(l=80, r=120, t=80, b=80)
        )
        
        st.plotly_chart(fig_sens, use_container_width=True)
        
        st.markdown("""
        <div class="insight-box">
        <strong>💡 Cómo interpretar este análisis:</strong>
        <ul>
            <li><strong>Zonas verdes:</strong> Máxima rentabilidad — estos puntos representan combinaciones óptimas de precio y volumen</li>
            <li><strong>Zonas amarillas:</strong> Punto de equilibrio — ingresos cubren costos pero con margen bajo</li>
            <li><strong>Zonas rojas:</strong> No rentable — los costos superan los ingresos en estos escenarios</li>
            <li><strong>Objetivo:</strong> Encontrar el balance entre un precio competitivo (que maximice adopción) y un volumen alcanzable (realista según tu mercado)</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# TAB 4: PROYECCIONES FINANCIERAS
# ============================================================================
with tabs[3]:
    st.markdown("## 📊 Proyecciones Financieras a 3 Años")
    st.markdown("Modelos de crecimiento y proyección de impacto financiero del programa de suscripción.")
    
    # Parámetros de proyección
    st.markdown("### ⚙️ Supuestos de Crecimiento")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        growth_rate_subs = st.slider('Crecimiento Anual Suscriptores (%)', 10, 50, 25, 5,
                                     help="% de crecimiento de base de suscriptores año a año")
    with col2:
        churn_rate = st.slider('Tasa de Churn Anual (%)', 5, 30, 15, 5,
                              help="% de suscriptores que cancelan cada año")
    with col3:
        price_increase = st.slider('Incremento Precio Anual (%)', 0, 10, 3, 1,
                                   help="% de incremento en precio de suscripción cada año")
    
    st.markdown("---")
    
    # Calcular proyecciones
    years = 3
    projection_data = []
    
    # Año 0 (baseline sin suscripción)
    baseline_revenue = len(df) * df['Ticket_Price'].mean() * df['Number_of_Person'].mean() if df is not None else 150000
    
    current_price = price_selected
    current_subs = subs_selected
    
    for year in range(years + 1):
        if year == 0:
            # Baseline
            projection_data.append({
                'Año': 'Actual',
                'Suscriptores': 0,
                'Precio': 0,
                'Revenue Suscripción': 0,
                'Revenue Traditional': baseline_revenue,
                'Revenue Total': baseline_revenue,
                'Costos Totales': fixed_costs * 0.7,  # costos actuales menores
                'Beneficio': baseline_revenue - (fixed_costs * 0.7)
            })
        else:
            # Crecimiento con suscripción
            if year == 1:
                subs = current_subs
                price = current_price
            else:
                # Aplicar crecimiento neto (crecimiento - churn)
                net_growth = (growth_rate_subs - churn_rate) / 100
                subs = projection_data[-1]['Suscriptores'] * (1 + net_growth)
                price = projection_data[-1]['Precio'] * (1 + price_increase / 100)
            
            sub_revenue = subs * price
            
            # Revenue tradicional decrece con suscripción (asumimos 50% de suscriptores hubieran venido igual)
            trad_revenue = baseline_revenue * (1 - 0.5 * subs / (subs + baseline_revenue / (df['Ticket_Price'].mean() * df['Number_of_Person'].mean()) if df is not None else 1000))
            
            total_revenue = sub_revenue + trad_revenue
            total_costs = fixed_costs + (variable_cost * subs)
            profit = total_revenue - total_costs
            
            projection_data.append({
                'Año': f'Año {year}',
                'Suscriptores': int(subs),
                'Precio': price,
                'Revenue Suscripción': sub_revenue,
                'Revenue Traditional': trad_revenue,
                'Revenue Total': total_revenue,
                'Costos Totales': total_costs,
                'Beneficio': profit
            })
    
    proj_df = pd.DataFrame(projection_data)
    
    # Visualización de proyecciones
    st.markdown("### 📈 Evolución Proyectada")
    
    col_proj1, col_proj2 = st.columns(2)
    
    with col_proj1:
        fig_revenue_proj = go.Figure()
        
        fig_revenue_proj.add_trace(go.Scatter(
            x=proj_df['Año'],
            y=proj_df['Revenue Suscripción'],
            name='Ingresos por Suscripción',
            fill='tonexty',
            line=dict(color='#667eea', width=3),
            hovertemplate='<b>%{x}</b><br>Suscripción: $%{y:,.0f}<extra></extra>'
        ))
        
        fig_revenue_proj.add_trace(go.Scatter(
            x=proj_df['Año'],
            y=proj_df['Revenue Traditional'],
            name='Ingresos Tradicionales',
            fill='tozeroy',
            line=dict(color='#f5576c', width=3),
            hovertemplate='<b>%{x}</b><br>Tradicional: $%{y:,.0f}<extra></extra>'
        ))
        
        fig_revenue_proj.add_trace(go.Scatter(
            x=proj_df['Año'],
            y=proj_df['Revenue Total'],
            name='Ingresos Totales',
            line=dict(color='#43e97b', width=4, dash='dash'),
            hovertemplate='<b>%{x}</b><br>Total: $%{y:,.0f}<extra></extra>'
        ))
        
        fig_revenue_proj.update_layout(
            title='Evolución Proyectada de Ingresos por Canal',
            template=plotly_theme(),
            yaxis_title='Ingresos Anuales (USD)',
            yaxis=dict(tickformat='$,.0f'),
            xaxis_title='Período',
            height=480,
            hovermode='x unified',
            margin=dict(l=70, r=40, t=60, b=60),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            )
        )
        
        st.plotly_chart(fig_revenue_proj, use_container_width=True)
    
    with col_proj2:
        fig_profit_proj = go.Figure()
        
        colors = ['#28a745' if x > 0 else '#dc3545' for x in proj_df['Beneficio']]
        
        fig_profit_proj.add_trace(go.Bar(
            x=proj_df['Año'],
            y=proj_df['Beneficio'],
            marker_color=colors,
            text=proj_df['Beneficio'].apply(lambda x: f'${x:,.0f}'),
            textposition='outside',
            name='Beneficio Neto',
            hovertemplate='<b>%{x}</b><br>Beneficio: $%{y:,.0f}<br><b>Estado:</b> %{customdata}<extra></extra>',
            customdata=['Rentable' if x > 0 else 'Pérdida' for x in proj_df['Beneficio']]
        ))
        
        fig_profit_proj.add_hline(
            y=0, 
            line_dash="dash", 
            line_color="gray",
            annotation_text="Break-Even",
            annotation_position="right"
        )
        
        fig_profit_proj.update_layout(
            title='Proyección de Beneficio Neto a 3 Años',
            template=plotly_theme(),
            yaxis_title='Beneficio Anual (USD)',
            yaxis=dict(tickformat='$,.0f'),
            xaxis_title='Período',
            height=480,
            showlegend=False,
            margin=dict(l=70, r=40, t=60, b=60)
        )
        
        st.plotly_chart(fig_profit_proj, use_container_width=True)
    
    # Gráfico de crecimiento de suscriptores
    fig_subs = go.Figure()
    
    fig_subs.add_trace(go.Scatter(
        x=proj_df['Año'][1:],
        y=proj_df['Suscriptores'][1:],
        mode='lines+markers',
        line=dict(color='#4facfe', width=4),
        marker=dict(size=14, color='#4facfe', line=dict(width=2, color='white')),
        text=proj_df['Suscriptores'][1:].apply(lambda x: f'{int(x):,}'),
        textposition='top center',
        textfont=dict(size=12, color='#4facfe'),
        hovertemplate='<b>%{x}</b><br>Suscriptores: %{y:,}<extra></extra>'
    ))
    
    fig_subs.update_layout(
        title='Crecimiento Proyectado de Base de Suscriptores',
        template=plotly_theme(),
        yaxis_title='Número Total de Suscriptores Activos',
        yaxis=dict(tickformat=','),
        xaxis_title='Período',
        height=420,
        margin=dict(l=70, r=40, t=60, b=60),
        showlegend=False
    )
    
    st.plotly_chart(fig_subs, use_container_width=True)
    
    # Tabla resumen
    st.markdown("---")
    st.markdown("### 📋 Tabla Resumen de Proyecciones")
    
    display_proj = proj_df.copy()
    for col in ['Precio', 'Revenue Suscripción', 'Revenue Traditional', 'Revenue Total', 'Costos Totales', 'Beneficio']:
        if col in display_proj.columns:
            display_proj[col] = display_proj[col].apply(lambda x: f'${x:,.0f}')
    display_proj['Suscriptores'] = display_proj['Suscriptores'].apply(lambda x: f'{x:,}' if x > 0 else '-')
    
    st.dataframe(display_proj, use_container_width=True, height=250)
    
    # KPIs finales
    st.markdown("---")
    st.markdown("### 🎯 KPIs de Impacto (Año 3)")
    
    year3 = proj_df[proj_df['Año'] == 'Año 3'].iloc[0]
    baseline = proj_df[proj_df['Año'] == 'Actual'].iloc[0]
    
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    
    revenue_growth = ((year3['Revenue Total'] - baseline['Revenue Total']) / baseline['Revenue Total'] * 100)
    profit_growth = ((year3['Beneficio'] - baseline['Beneficio']) / abs(baseline['Beneficio']) * 100) if baseline['Beneficio'] != 0 else 0
    
    with col_kpi1:
        metric_card("Revenue Año 3", f"${year3['Revenue Total']:,.0f}",
                   delta=f"+{revenue_growth:.1f}% vs. actual")
    with col_kpi2:
        metric_card("Beneficio Año 3", f"${year3['Beneficio']:,.0f}",
                   delta=f"+{profit_growth:.0f}% vs. actual")
    with col_kpi3:
        metric_card("Suscriptores Año 3", f"{year3['Suscriptores']:,}")
    with col_kpi4:
        ltv = year3['Precio'] * 3 * (1 - churn_rate / 100)  # LTV simplificado
        metric_card("LTV Estimado", f"${ltv:,.0f}")
    
    # Conclusiones
    st.markdown("---")
    st.markdown("""
    <div class="success-box">
    <h4>💡 Conclusiones Estratégicas</h4>
    <ul>
        <li><strong>Viabilidad:</strong> El modelo de suscripción genera crecimiento sostenible en revenue y beneficio</li>
        <li><strong>Diversificación:</strong> Reduce dependencia de ingresos por ticket tradicional</li>
        <li><strong>Valor vitalicio:</strong> LTV de suscriptores supera ampliamente el CAC esperado</li>
        <li><strong>Escalabilidad:</strong> Margen mejora con escala debido a costos fijos diluidos</li>
    </ul>
    <p><strong>Recomendación:</strong> Proceder con lanzamiento piloto para validar supuestos de adopción y churn.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# TAB 5: CONFIGURACIÓN Y UTILIDADES
# ============================================================================
with tabs[4]:
    st.markdown("## 🔧 Configuración y Utilidades")
    
    st.markdown("### 📊 Pipeline de Datos")
    
    col_util1, col_util2 = st.columns(2)
    
    with col_util1:
        if st.button('🔄 Actualizar Figuras y Métricas', use_container_width=True):
            with st.spinner('Regenerando figuras...'):
                try:
                    py = str(VENV_PY) if VENV_PY.exists() else 'python'
                    subprocess.check_call([py, str(EXPORT_SCRIPT)])
                    st.success('✅ Figuras actualizadas correctamente')
                    st.rerun()
                except Exception as e:
                    st.error(f'❌ Error: {e}')
    
    with col_util2:
        if st.button('▶️ Ejecutar Pipeline Completo (Notebooks)', use_container_width=True):
            with st.spinner('Ejecutando pipeline... esto puede tardar varios minutos'):
                try:
                    py = str(VENV_PY) if VENV_PY.exists() else 'python'
                    subprocess.check_call([py, str(ROOT / 'presentations' / 'run_notebooks.py')])
                    st.success('✅ Pipeline completado')
                    st.rerun()
                except Exception as e:
                    st.error(f'❌ Error: {e}')
    
    
    st.markdown("---")
    st.markdown("### 📊 Estado de Datos")
    
    status_data = []
    
    files_to_check = [
        ('Raw Data', RAW_PATH),
        ('Cleaned Data', CLEAN_PATH),
        ('Features', FEAT_PATH),
        ('Model Metrics', METRICS_JSON),
        ('Financial KPIs', KPIS_JSON)
    ]
    
    for name, path in files_to_check:
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        status_data.append({
            'Archivo': name,
            'Estado': '✅ Disponible' if exists else '❌ Faltante',
            'Tamaño': f'{size / 1024:.1f} KB' if exists else '-'
        })
    
    st.dataframe(pd.DataFrame(status_data), use_container_width=True, height=250)
    
    st.markdown("---")
    st.markdown("### ℹ️ Información del Sistema")
    
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.metric("Registros en Dataset", f"{len(df):,}" if df is not None else "N/A")
    with col_info2:
        st.metric("Python Env", "Activo" if VENV_PY.exists() else "Sistema")
    with col_info3:
        st.metric("Versión Dashboard", "2.0 Professional")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>Cinema Subscription Optimization Dashboard</strong></p>
    <p>Desarrollado por CMSR92 | Noviembre 2025</p>
    <p>🎬 Dashboard profesional con análisis data-driven end-to-end</p>
</div>
""", unsafe_allow_html=True)
