"""Visualizaciones (en español)

Funciones de apoyo para gráficos con Seaborn/Matplotlib y Plotly.
Autor: CMSR92
"""
from __future__ import annotations
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

sns.set(style="whitegrid")


def _apply_plotly_style(fig, title: str | None = None):
    fig.update_layout(
        template="plotly_white",
        title=title if title else fig.layout.title.text,
        font=dict(family="Segoe UI, Roboto, Arial", size=13),
        legend=dict(title_text=None),
        margin=dict(l=60, r=30, t=60, b=50)
    )
    return fig


def _format_currency_axes(fig, x_currency: bool = False, y_currency: bool = True):
    if x_currency:
        fig.update_xaxes(tickformat="$,.0f", ticks="outside")
    if y_currency:
        fig.update_yaxes(tickformat="$,.0f", ticks="outside")
    return fig


def plot_price_sensitivity(df: pd.DataFrame, price_col: str = "Ticket_Price"):
    """Histograma/ KDE de precios pagados"""
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.histplot(df[price_col], kde=True, ax=ax, color="#6C2CF2")
    ax.set_title("Distribución de precio de ticket (USD)")
    ax.set_xlabel("Precio (USD)")
    return fig


def plot_segments_scatter(df: pd.DataFrame, x: str, y: str, color: str, labels: dict | None = None):
    """Diagrama de dispersión interactivo por segmento."""
    base_labels = {x: x.replace('_', ' ').capitalize(), y: y.replace('_', ' ').capitalize(), color: 'Segmento'}
    if labels:
        base_labels.update(labels)
    fig = px.scatter(df, x=x, y=y, color=color, opacity=0.7,
                     title="Segmentación de clientes", labels=base_labels)
    _apply_plotly_style(fig)
    return fig


def plot_pricing_results(results):
    """Bar chart de ingresos por precio (con formato profesional)."""
    df = pd.DataFrame(results)
    fig = px.bar(
        df, x="price", y="revenue", text="subscribers",
        title="Ingresos por escenario de precio",
        labels={"price": "Precio (USD)", "revenue": "Ingresos (USD)", "subscribers": "Suscriptores"}
    )
    fig.update_traces(
        marker_color="#19C37D",
        textposition="outside",
        texttemplate="%{text:,} suscriptores"
    )
    _apply_plotly_style(fig)
    _format_currency_axes(fig, x_currency=True, y_currency=True)
    return fig
