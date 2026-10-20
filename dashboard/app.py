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
from pathlib import Path
import warnings

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import sys

# Silenciar warnings
warnings.filterwarnings("ignore")

# Setup paths
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src import data_processing as dp  # noqa: E402
from src import feature_engineering as fe  # noqa: E402
from dashboard.formato import fn0, fn1, fn2, fni, grafico  # noqa: E402
from dashboard.marca import ICONO, cabecera, pie  # noqa: E402

# Paths
FIG_DIR = ROOT / 'reports' / 'figures'
FEAT_PATH = ROOT / 'data' / 'processed' / 'model_features.csv'
CLEAN_PATH = ROOT / 'data' / 'processed' / 'cleaned_data.csv'
RAW_PATH = ROOT / 'data' / 'raw' / 'movie_theatre_sales.csv'
METRICS_JSON = FIG_DIR / 'model_metrics.json'
KPIS_JSON = FIG_DIR / 'financial_kpis.json'
PRICING_CSV = FIG_DIR / 'pricing_results.csv'
EXPORT_SCRIPT = ROOT / 'presentations' / 'export_figures.py'

# Config
st.set_page_config(
    page_title='Estrategia de suscripción para un cine · CMSR92',
    page_icon=ICONO,
    layout='wide',
    initial_sidebar_state='collapsed'
)

# Custom CSS adaptable al tema del sistema
st.markdown("""
<style>
    /* Variables de color según tema */
    :root {
        --text-primary: #1f1f1f;
        --bg-insight: #e3f2fd;
        --bg-success: #e8f5e9;
        --bg-warning: #fff8e1;
        --border-insight: #1976d2;
        --border-success: #43a047;
        --border-warning: #f57c00;
    }

    @media (prefers-color-scheme: dark) { :root {
        --text-primary: #ffffff;
        --bg-insight: #1a2332;
        --bg-success: #1b2e1f;
        --bg-warning: #2e2418;
        --border-insight: #64b5f6;
        --border-success: #81c784;
        --border-warning: #ffb74d;
    } }

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

cabecera("Estrategia de suscripción para un cine",
         "Análisis basado en datos para fijar el precio y proyectar el impacto financiero")

def nombrar_segmentos(profiles):
    """Perfil de cada segmento según en qué destaca frente a los demás (no con umbrales fijos: con edades medias de
    37-41 años, los umbrales daban el mismo nombre a casi todos). Cada perfil se asigna a un solo segmento."""
    arquetipos = [
        ("Ticket_Price", "max", "💎 **Mayor gasto**: plan premium con extras."),
        ("Number_of_Person", "max", "👨‍👩‍👧 **Grupos grandes**: plan familiar con beneficios grupales."),
        ("Age", "min", "🎯 **Público más joven**: plan estándar con precio de entrada."),
        ("Number_of_Person", "min", "🎭 **Individuales y parejas**: plan con contenido exclusivo."),
    ]
    libres = list(profiles.index)
    perfiles = {}
    for col, sentido, texto in arquetipos:
        if col not in profiles.columns or not libres:
            continue
        valores = profiles.loc[libres, col]
        seg = valores.idxmax() if sentido == "max" else valores.idxmin()
        perfiles[seg] = texto
        libres.remove(seg)
    return perfiles


# Load data
df = load_data()
kpis = load_kpis()
model_metrics = load_model_metrics()

# ============================================================================
# EXECUTIVE DASHBOARD - Vista Principal
# ============================================================================

st.markdown("---")
st.markdown("## 📊 Resumen Ejecutivo")

# KPIs principales: tarjetas nativas con borde (se adaptan solas al tema claro y oscuro)
if kpis:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Precio óptimo de suscripción", f"${kpis.get('price', 180)} / año", border=True)
    col2.metric("Suscriptores para el punto de equilibrio", fni(int(kpis.get("break_even_subs", 0))), border=True)
    col3.metric("Retorno de la inversión (año 1)", f"{fn0(kpis.get('roi_percent', 0))}%", border=True)
    col4.metric("Recuperación de la inversión", f"{fn1(kpis.get('payback_months', 0))} meses", border=True)
else:
    st.info("⚙️ Ejecuta el pipeline para generar KPIs financieros")

st.markdown("---")

# Problema y Solución
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 🎯 Diagnóstico de la Situación Actual")
    st.markdown("""
    <div class="warning-box">
    <h4>📉 Qué le pasa al cine</h4>
    <ul>
        <li><strong>Va menos gente</strong>: los hábitos de ocio han cambiado</li>
        <li>Las plataformas de streaming compiten por el mismo tiempo libre</li>
        <li>Los ingresos suben y bajan mucho, y es difícil planificar</li>
        <li>No hay nada que anime a los clientes a volver</li>
    </ul>
    <p>Hace falta una razón para que los clientes vuelvan con regularidad.</p>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("### 💡 Estrategia Recomendada")
    st.markdown("""
    <div class="success-box">
    <h4>🎬 Una suscripción anual</h4>
    <ul>
        <li><strong>$180 al año</strong> ($15 al mes), un precio fácil de entender</li>
        <li>Películas ilimitadas y ventajas solo para suscriptores</li>
        <li>Ingresos fijos cada mes en lugar de depender de la taquilla</li>
        <li>Un motivo para que los mejores clientes sigan viniendo</li>
    </ul>
    <p>Con una base de suscriptores, los ingresos son más estables y el cine depende menos de cada estreno.</p>
    </div>
    """, unsafe_allow_html=True)

# Tabs para análisis detallado
st.markdown("---")
# La pestaña de configuración ejecuta el pipeline: solo se muestra en local con CINE_ADMIN=1, no a los visitantes
ADMIN = os.environ.get("CINE_ADMIN") == "1"
tabs = st.tabs([
    "📈 Análisis de Negocio",
    "👥 Segmentación de Clientes",
    "💰 Optimización de Precios",
    "📊 Proyecciones Financieras",
] + (["🔧 Configuración"] if ADMIN else []))

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
            metric_card("Total Transacciones", f"{fni(len(df))}")
        with col2:
            avg_ticket = df['Ticket_Price'].mean()
            metric_card("Precio Promedio Ticket", f"${fn2(avg_ticket)}")
        with col3:
            avg_group = df['Number_of_Person'].mean()
            metric_card("Personas por Compra", f"{fn1(avg_group)}")
        with col4:
            retention = (df['Purchase_Again'].sum() / len(df) * 100)
            metric_card("Tasa de Retención", f"{fn1(retention)}%")

        st.markdown("---")

        # Visualizaciones interactivas
        col_viz1, col_viz2 = st.columns(2)

        with col_viz1:
            st.markdown("#### Distribución de Precios de Tickets")
            fig_price = px.histogram(
                df,
                x='Ticket_Price',
                nbins=30,
                color_discrete_sequence=['#0A8CA2'],
                labels={
                    'Ticket_Price': 'Precio del Ticket (USD)',
                    'count': 'Frecuencia'
                }
            )
            fig_price.update_layout(
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
                annotation_text=f"Promedio: ${fn2(avg_ticket)}",
                annotation_position="top"
            )
            # Mejorar tooltips
            fig_price.update_traces(
                hovertemplate='<b>Precio:</b> $%{x:.2f}<br><b>Transacciones:</b> %{y}<extra></extra>'
            )
            grafico(fig_price, width="stretch")

            st.markdown(f"""
            <div class="insight-box">
            <strong>💡 Dato:</strong> la entrada media cuesta <strong>${fn2(avg_ticket)}</strong>, así que la
            suscripción de $180 al año se amortiza con unas {fn0(180/avg_ticket)} películas. Sale a cuenta a
            quien va al cine a menudo.
            </div>
            """, unsafe_allow_html=True)

        with col_viz2:
            st.markdown("#### Tamaño de Grupos")
            group_dist = df['Number_of_Person'].value_counts().sort_index()
            fig_group = px.bar(
                x=group_dist.index,
                y=group_dist.values,
                color_discrete_sequence=['#0A8CA2'],
                labels={
                    'x': 'Número de Personas por Grupo',
                    'y': 'Cantidad de Transacciones',
                    'color': 'Frecuencia'
                }
            )
            fig_group.update_layout(
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
            grafico(fig_group, width="stretch")

            most_common = group_dist.idxmax()
            st.markdown(f"""
            <div class="insight-box">
            <strong>💡 Dato:</strong> lo más habitual es ir en grupos de <strong>{fn0(most_common)} personas</strong>.
            Un plan familiar o de grupo podría encajar como complemento.
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
        genre_analysis.columns = ['Transacciones', 'Ingresos totales', 'Precio Promedio', 'Tasa Retención']
        genre_analysis = genre_analysis.sort_values('Ingresos totales', ascending=False)

        col_genre1, col_genre2 = st.columns(2)

        with col_genre1:
            fig_genre_rev = px.bar(
                genre_analysis.reset_index(),
                x='Movie_Genre',
                y='Ingresos totales',
                color='Tasa Retención',
                color_continuous_scale='Tealgrn',
                labels={
                    'Movie_Genre': 'Género de Película',
                    'Ingresos totales': 'Ingresos Totales (USD)',
                    'Tasa Retención': 'Tasa de Retención'
                }
            )
            fig_genre_rev.update_layout(
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
            grafico(fig_genre_rev, width="stretch")

        with col_genre2:
            # Preparar datos para tooltips personalizados
            genre_data = genre_analysis.reset_index()

            fig_genre_ret = px.scatter(
                genre_data,
                x='Transacciones',
                y='Tasa Retención',
                size='Ingresos totales',
                color='Movie_Genre',
                custom_data=['Movie_Genre', 'Precio Promedio', 'Ingresos totales'],
                labels={
                    'Transacciones': 'Volumen de Transacciones',
                    'Tasa Retención': 'Tasa de Retención (%)',
                    'Movie_Genre': 'Género',
                    'Precio Promedio': 'Precio Promedio (USD)',
                    'Ingresos totales': 'Ingresos Totales'
                }
            )
            fig_genre_ret.update_traces(
                hovertemplate='<b>Género:</b> %{customdata[0]}<br><b>Transacciones:</b> %{x:,}<br><b>Retención:</b> %{y:.1%}<br><b>Precio Promedio:</b> $%{customdata[1]:.2f}<br><b>Ingresos:</b> $%{customdata[2]:,.0f}<extra></extra>'
            )
            fig_genre_ret.update_layout(
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
            grafico(fig_genre_ret, width="stretch")

        st.markdown("""
        <div class="insight-box">
        <strong>💡 Recomendación:</strong> centrar la promoción de la suscripción en los géneros
        que más público repite y más entradas venden, y usar estrenos o pases exclusivos de esos
        géneros como gancho.
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
            marker_color='#0A8CA2',
            hovertemplate='<b>Tipo de Asiento:</b> %{x}<br><b>Ingresos:</b> $%{y:,.0f}<extra></extra>'
        ))
        fig_seat.add_trace(go.Scatter(
            name='Precio Promedio por Ticket',
            x=seat_analysis.index,
            y=seat_analysis['Ticket_Price'],
            yaxis='y2',
            marker_color='#D97706',
            mode='lines+markers',
            line=dict(width=3),
            marker=dict(size=10),
            hovertemplate='<b>Tipo de Asiento:</b> %{x}<br><b>Precio Promedio:</b> $%{y:.2f}<extra></extra>'
        ))
        fig_seat.update_layout(
            yaxis=dict(
                title='Ingresos Totales (USD)',
                tickformat='$,.0f'
            ),
            yaxis2=dict(
                title='Precio Promedio por Ticket (USD)',
                overlaying='y',
                side='right',
                tickformat='$,.2f',
                showgrid=False
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
        grafico(fig_seat, width="stretch")

        st.markdown("""
        <div class="insight-box">
        <strong>💡 Idea:</strong> dar ventajas según el tipo de asiento; por ejemplo, que los
        suscriptores puedan pasar gratis a un asiento Premium una vez al mes.
        </div>
        """, unsafe_allow_html=True)

    else:
        st.warning("⚠️ No hay datos disponibles. Verifica que exista el archivo de datos limpios.")

# ============================================================================
# TAB 2: SEGMENTACIÓN DE CLIENTES
# ============================================================================
with tabs[1]:
    st.markdown("## 👥 Segmentación de Clientes")
    st.markdown("Agrupamos a los clientes por perfiles parecidos para adaptar la oferta a cada uno.")

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
                grafico(fig_seg, width="stretch")

                st.markdown("""
                <div class="insight-box">
                <strong>🔍 Cómo leer este gráfico</strong><br>
                Cada punto es un cliente y el color indica su segmento (calculado con K-Means). Para poder
                dibujarlos en un plano, sus datos se resumen en dos ejes con PCA. Si los grupos de colores quedan
                separados, los segmentos se comportan de forma distinta y tiene sentido tratarlos por separado.
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

                    perfiles = nombrar_segmentos(profiles)
                    for idx, (seg_id, row) in enumerate(profiles.iterrows()):
                        with cols[idx]:
                            st.markdown(f"#### Segmento {seg_id + 1}")
                            st.metric("Clientes", f"{fni(int(row['Tamaño']))}",
                                      help=f"{fn1(row['% del Total'])}% del total")

                            if 'Age' in row:
                                st.metric("Edad Promedio", f"{fn0(row['Age'])} años")
                            if 'Ticket_Price' in row:
                                st.metric("Gasto Promedio", f"${fn2(row['Ticket_Price'])}")
                            if 'Number_of_Person' in row:
                                st.metric("Tamaño Grupo", f"{fn1(row['Number_of_Person'])}")

                            if seg_id in perfiles:
                                st.markdown(perfiles[seg_id])

                # Insights generales
                st.markdown("---")
                st.markdown("""
                <div class="success-box">
                <h4>💡 Qué hacer con estos segmentos</h4>
                <ul>
                    <li><strong>Empezar por el mejor:</strong> lanzar la suscripción primero al segmento que más
                    gasta y más repite</li>
                    <li><strong>Hablar a cada uno a su manera:</strong> ventajas y mensajes según el perfil</li>
                    <li><strong>Varios planes:</strong> individual, pareja y familiar</li>
                    <li><strong>Que se queden:</strong> ventajas pensadas para cada segmento</li>
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
    st.markdown("Prueba distintos precios y mira cuántos suscriptores harían falta para que salga rentable.")

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
            'Ingresos': revenue,
            'Costos Variables': var_costs,
            'Margen Contribución': contribution,
            'Beneficio': profit,
            'Margen %': margin,
            'Punto de equilibrio': break_even
        })

    results_df = pd.DataFrame(results)

    # Visualización comparativa
    col_viz1, col_viz2 = st.columns(2)

    with col_viz1:
        fig_revenue = go.Figure()
        fig_revenue.add_trace(go.Bar(
            name='Ingresos Anuales',
            x=results_df['Precio'],
            y=results_df['Ingresos'],
            marker_color='#0A8CA2',
            text=results_df['Ingresos'].apply(lambda x: f'${fn0(x)}'),
            textposition='outside',
            hovertemplate='<b>Precio:</b> $%{x}<br><b>Ingresos:</b> $%{y:,.0f}<extra></extra>'
        ))
        fig_revenue.add_trace(go.Scatter(
            name='Suscriptores Esperados',
            x=results_df['Precio'],
            y=results_df['Suscriptores'],
            yaxis='y2',
            mode='lines+markers',
            marker=dict(size=12, color='#D97706'),
            line=dict(width=4, color='#D97706'),
            hovertemplate='<b>Precio:</b> $%{x}<br><b>Suscriptores:</b> %{y:,}<extra></extra>'
        ))
        fig_revenue.update_layout(
            title='Análisis de Ingresos y Adopción por Precio',
            yaxis=dict(
                title='Ingresos Anuales (USD)',
                tickformat='$,.0f'
            ),
            yaxis2=dict(
                title='Número de Suscriptores',
                overlaying='y',
                side='right',
                tickformat=',.0f',
                showgrid=False
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
        grafico(fig_revenue, width="stretch")

    with col_viz2:
        fig_profit = go.Figure()
        colors = ['#1F9D55' if x > 0 else '#D64545' for x in results_df['Beneficio']]
        fig_profit.add_trace(go.Bar(
            x=results_df['Precio'],
            y=results_df['Beneficio'],
            marker_color=colors,
            text=results_df['Beneficio'].apply(lambda x: f'${fn0(x)}'),
            textposition='outside',
            hovertemplate='<b>Precio:</b> $%{x}<br><b>Beneficio:</b> $%{y:,.0f}<br><b>Estado:</b> %{customdata}<extra></extra>',
            customdata=['Rentable' if x > 0 else 'No Rentable' for x in results_df['Beneficio']]
        ))
        fig_profit.add_hline(
            y=0,
            line_dash="dash",
            line_color="gray",
            annotation_text="Punto de equilibrio",
            annotation_position="right"
        )
        fig_profit.update_layout(
            title='Beneficio Neto por Escenario de Precio',
            yaxis_title='Beneficio Anual (USD)',
            yaxis=dict(tickformat='$,.0f'),
            xaxis_title='Precio de Suscripción Anual (USD)',
            xaxis=dict(tickformat='$,.0f'),
            height=480,
            margin=dict(l=70, r=40, t=60, b=60),
            showlegend=False
        )
        grafico(fig_profit, width="stretch")

    # Tabla detallada
    st.markdown("### 📋 Tabla Comparativa de Escenarios")

    # Formatear tabla
    display_df = results_df.copy()
    for col in ['Precio', 'Ingresos', 'Costos Variables', 'Margen Contribución', 'Beneficio']:
        display_df[col] = display_df[col].apply(lambda x: f'${fn0(x)}')
    display_df['Margen %'] = display_df['Margen %'].apply(lambda x: f'{fn1(x)}%')
    display_df['Punto de equilibrio'] = display_df['Punto de equilibrio'].apply(lambda x: fni(int(x)) if x != float('inf') else '∞')

    st.dataframe(display_df, width="stretch", height=300, hide_index=True)

    # Análisis del escenario seleccionado
    st.markdown("---")
    st.markdown(f"### 🎯 Análisis de Tu Escenario: ${price_selected}/año")

    selected_result = results_df[results_df['Precio'] == price_selected].iloc[-1]

    col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)

    with col_metric1:
        metric_card("Ingresos año 1", f"${fn0(selected_result['Ingresos'])}")
    with col_metric2:
        metric_card("Margen Contribución", f"${fn0(selected_result['Margen Contribución'])}")
    with col_metric3:
        profit_val = selected_result['Beneficio']
        metric_card("Beneficio Neto", f"${fn0(profit_val)}",
                   delta="Rentable" if profit_val > 0 else "No rentable",
                   delta_color="normal" if profit_val > 0 else "inverse")
    with col_metric4:
        be = selected_result['Punto de equilibrio']
        metric_card("Punto de equilibrio", f"{fni(int(be))} suscriptores" if be != float('inf') else "∞")

    # Recomendación
    if selected_result['Beneficio'] > 0:
        if selected_result['Margen %'] > 40:
            recommendation = "success-box"
            icon = "✅"
            message = "Buen margen: con este precio el programa es claramente rentable."
        else:
            recommendation = "insight-box"
            icon = "📊"
            message = "Es rentable, pero con poco margen: conviene revisar el precio o los costes."
    else:
        recommendation = "warning-box"
        icon = "⚠️"
        message = "Así no es rentable: haría falta subir el precio o bajar los costes."

    st.markdown(f"""
    <div class="{recommendation}">
    <h4>{icon} Evaluación del Escenario</h4>
    <p>{message}</p>
    <ul>
        <li><strong>Margen de contribución:</strong> {fn1(selected_result['Margen %'])}%</li>
        <li><strong>Necesitas alcanzar:</strong> {fni(int(selected_result['Punto de equilibrio']))} suscriptores para el punto de equilibrio</li>
        <li><strong>Actualmente proyectas:</strong> {fni(int(selected_result['Suscriptores']))} suscriptores</li>
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
            colorscale='RdBu',
            zmid=0,
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
            height=600,
            margin=dict(l=80, r=120, t=80, b=80)
        )

        grafico(fig_sens, width="stretch")

        st.markdown("""
        <div class="insight-box">
        <strong>💡 Cómo interpretar este análisis:</strong>
        <ul>
            <li><strong>Azul:</strong> hay beneficio, y cuanto más oscuro, más</li>
            <li><strong>Blanco:</strong> punto de equilibrio, los ingresos apenas cubren los costes</li>
            <li><strong>Rojo:</strong> pérdidas, los costes superan a los ingresos</li>
            <li><strong>Lo que se busca:</strong> un precio que atraiga a suficiente gente y un número de suscriptores que sea realista conseguir</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# TAB 4: PROYECCIONES FINANCIERAS
# ============================================================================
with tabs[3]:
    st.markdown("## 📊 Proyecciones Financieras a 3 Años")
    st.markdown("Cómo podrían evolucionar los suscriptores, los ingresos y el beneficio en los próximos tres años.")

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
                'Ingresos por suscripción': 0,
                'Ingresos por taquilla': baseline_revenue,
                'Ingresos totales': baseline_revenue,
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

            # Los ingresos por taquilla decrecen con suscripción (asumimos 50% de suscriptores hubieran venido igual)
            trad_revenue = baseline_revenue * (1 - 0.5 * subs / (subs + baseline_revenue / (df['Ticket_Price'].mean() * df['Number_of_Person'].mean()) if df is not None else 1000))

            total_revenue = sub_revenue + trad_revenue
            total_costs = fixed_costs + (variable_cost * subs)
            profit = total_revenue - total_costs

            projection_data.append({
                'Año': f'Año {year}',
                'Suscriptores': int(subs),
                'Precio': price,
                'Ingresos por suscripción': sub_revenue,
                'Ingresos por taquilla': trad_revenue,
                'Ingresos totales': total_revenue,
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
            y=proj_df['Ingresos por suscripción'],
            name='Ingresos por Suscripción',
            fill='tonexty',
            line=dict(color='#0A8CA2', width=3),
            hovertemplate='<b>%{x}</b><br>Suscripción: $%{y:,.0f}<extra></extra>'
        ))

        fig_revenue_proj.add_trace(go.Scatter(
            x=proj_df['Año'],
            y=proj_df['Ingresos por taquilla'],
            name='Ingresos Tradicionales',
            fill='tozeroy',
            line=dict(color='#D97706', width=3),
            hovertemplate='<b>%{x}</b><br>Tradicional: $%{y:,.0f}<extra></extra>'
        ))

        fig_revenue_proj.add_trace(go.Scatter(
            x=proj_df['Año'],
            y=proj_df['Ingresos totales'],
            name='Ingresos Totales',
            line=dict(color='#1F9D55', width=4, dash='dash'),
            hovertemplate='<b>%{x}</b><br>Total: $%{y:,.0f}<extra></extra>'
        ))

        fig_revenue_proj.update_layout(
            title='Evolución Proyectada de Ingresos por Canal',
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

        grafico(fig_revenue_proj, width="stretch")

    with col_proj2:
        fig_profit_proj = go.Figure()

        colors = ['#1F9D55' if x > 0 else '#D64545' for x in proj_df['Beneficio']]

        fig_profit_proj.add_trace(go.Bar(
            x=proj_df['Año'],
            y=proj_df['Beneficio'],
            marker_color=colors,
            text=proj_df['Beneficio'].apply(lambda x: f'${fn0(x)}'),
            textposition='outside',
            name='Beneficio Neto',
            hovertemplate='<b>%{x}</b><br>Beneficio: $%{y:,.0f}<br><b>Estado:</b> %{customdata}<extra></extra>',
            customdata=['Rentable' if x > 0 else 'Pérdida' for x in proj_df['Beneficio']]
        ))

        fig_profit_proj.add_hline(
            y=0,
            line_dash="dash",
            line_color="gray",
            annotation_text="Punto de equilibrio",
            annotation_position="right"
        )

        fig_profit_proj.update_layout(
            title='Proyección de Beneficio Neto a 3 Años',
            yaxis_title='Beneficio Anual (USD)',
            yaxis=dict(tickformat='$,.0f'),
            xaxis_title='Período',
            height=480,
            showlegend=False,
            margin=dict(l=70, r=40, t=60, b=60)
        )

        grafico(fig_profit_proj, width="stretch")

    # Gráfico de crecimiento de suscriptores
    fig_subs = go.Figure()

    fig_subs.add_trace(go.Scatter(
        x=proj_df['Año'][1:],
        y=proj_df['Suscriptores'][1:],
        mode='lines+markers',
        line=dict(color='#2F80C8', width=4),
        marker=dict(size=14, color='#2F80C8', line=dict(width=2, color='white')),
        text=proj_df['Suscriptores'][1:].apply(lambda x: f'{fni(int(x))}'),
        textposition='top center',
        textfont=dict(size=12, color='#2F80C8'),
        hovertemplate='<b>%{x}</b><br>Suscriptores: %{y:,}<extra></extra>'
    ))

    fig_subs.update_layout(
        title='Crecimiento Proyectado de Base de Suscriptores',
        yaxis_title='Número Total de Suscriptores Activos',
        yaxis=dict(tickformat=','),
        xaxis_title='Período',
        height=420,
        margin=dict(l=70, r=40, t=60, b=60),
        showlegend=False
    )

    grafico(fig_subs, width="stretch")

    # Tabla resumen
    st.markdown("---")
    st.markdown("### 📋 Tabla Resumen de Proyecciones")

    display_proj = proj_df.copy()
    for col in ['Precio', 'Ingresos por suscripción', 'Ingresos por taquilla', 'Ingresos totales', 'Costos Totales', 'Beneficio']:
        if col in display_proj.columns:
            display_proj[col] = display_proj[col].apply(lambda x: f'${fn0(x)}')
    display_proj['Suscriptores'] = display_proj['Suscriptores'].apply(lambda x: f'{fni(x)}' if x > 0 else '-')

    st.dataframe(display_proj, width="stretch", height=250, hide_index=True)

    # KPIs finales
    st.markdown("---")
    st.markdown("### 🎯 KPIs de Impacto (Año 3)")

    year3 = proj_df[proj_df['Año'] == 'Año 3'].iloc[0]
    baseline = proj_df[proj_df['Año'] == 'Actual'].iloc[0]

    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

    revenue_growth = ((year3['Ingresos totales'] - baseline['Ingresos totales']) / baseline['Ingresos totales'] * 100)
    profit_growth = ((year3['Beneficio'] - baseline['Beneficio']) / abs(baseline['Beneficio']) * 100) if baseline['Beneficio'] != 0 else 0

    with col_kpi1:
        metric_card("Ingresos año 3", f"${fn0(year3['Ingresos totales'])}",
                   delta=f"+{fn1(revenue_growth)}% vs. actual")
    with col_kpi2:
        metric_card("Beneficio Año 3", f"${fn0(year3['Beneficio'])}",
                   delta=f"+{fn0(profit_growth)}% vs. actual")
    with col_kpi3:
        metric_card("Suscriptores Año 3", f"{fni(year3['Suscriptores'])}")
    with col_kpi4:
        ltv = year3['Precio'] * 3 * (1 - churn_rate / 100)  # LTV simplificado
        metric_card("Valor de vida estimado (LTV)", f"${fn0(ltv)}")

    # Conclusiones
    st.markdown("---")
    st.markdown("""
    <div class="success-box">
    <h4>💡 Conclusiones</h4>
    <ul>
        <li><strong>Sale a cuenta:</strong> con estos supuestos, los ingresos y el beneficio crecen año a año</li>
        <li><strong>Menos dependencia de la taquilla:</strong> una parte de los ingresos pasa a ser fija</li>
        <li><strong>Mejor con más suscriptores:</strong> los costes fijos se reparten y el margen mejora</li>
    </ul>
    <p><strong>Siguiente paso:</strong> una prueba piloto para comprobar cuánta gente se apunta y cuánta se da de baja de verdad.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# TAB 5: CONFIGURACIÓN Y UTILIDADES
# ============================================================================
if ADMIN:
    with tabs[4]:
        st.markdown("## 🔧 Configuración y Utilidades")

        st.markdown("### 📊 Pipeline de Datos")

        col_util1, col_util2 = st.columns(2)

        with col_util1:
            if st.button('🔄 Actualizar Figuras y Métricas', width="stretch"):
                with st.spinner('Regenerando figuras...'):
                    try:
                        py = sys.executable
                        subprocess.check_call([py, str(EXPORT_SCRIPT)])
                        st.success('✅ Figuras actualizadas correctamente')
                        st.rerun()
                    except Exception as e:
                        st.error(f'❌ Error: {e}')

        with col_util2:
            if st.button('▶️ Ejecutar Pipeline Completo (Notebooks)', width="stretch"):
                with st.spinner('Ejecutando pipeline... esto puede tardar varios minutos'):
                    try:
                        py = sys.executable
                        subprocess.check_call([py, str(ROOT / 'presentations' / 'run_notebooks.py')])
                        st.success('✅ Pipeline completado')
                        st.rerun()
                    except Exception as e:
                        st.error(f'❌ Error: {e}')


        st.markdown("---")
        st.markdown("### 📊 Estado de Datos")

        status_data = []

        files_to_check = [
            ('Datos originales', RAW_PATH),
            ('Datos limpios', CLEAN_PATH),
            ('Variables del modelo', FEAT_PATH),
            ('Métricas del modelo', METRICS_JSON),
            ('KPIs financieros', KPIS_JSON)
        ]

        for name, path in files_to_check:
            exists = path.exists()
            size = path.stat().st_size if exists else 0
            status_data.append({
                'Archivo': name,
                'Estado': '✅ Disponible' if exists else '❌ Faltante',
                'Tamaño': f'{fn1(size / 1024)} KB' if exists else '-'
            })

        st.dataframe(pd.DataFrame(status_data), width="stretch", height=250)

        st.markdown("---")
        st.markdown("### ℹ️ Información del Sistema")

        col_info1, col_info2, col_info3 = st.columns(3)

        with col_info1:
            st.metric("Registros en Dataset", f"{fni(len(df))}" if df is not None else "N/A")
        with col_info2:
            st.metric("Entorno de Python", Path(sys.prefix).name)
        with col_info3:
            st.metric("Versión del dashboard", "2.0")

pie("Estrategia de suscripción para un cine")
