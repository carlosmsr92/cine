# 🎬 Optimizar suscripciones de cine

Dashboard interactivo profesional para análisis y optimización de estrategia de suscripción de cines utilizando Data Science, Machine Learning y Business Intelligence.

## 🌐 Acceso al dashboard

🔗 [Ver Dashboard](https://proyecto-cine.streamlit.app/)

## 📊 Descripción

Proyecto completo de análisis de datos para optimizar la estrategia de suscripción de un cine mediante:

- **Análisis Exploratorio de Datos (EDA)**: Visualización y comprensión de patrones
- **Segmentación de Clientes**: K-Means + PCA para identificar perfiles de clientes
- **Modelado Predictivo**: Predicción de conversión y retención
- **Optimización de Precios**: Estrategia de pricing basada en datos
- **Proyecciones Financieras**: ROI, VAN, TIR y simulaciones

## ✨ Características del Dashboard

- 📈 **4 Tabs Interactivos**: Resumen Ejecutivo, Análisis de Datos, Segmentación, Proyecciones
- 🎨 **Tema Adaptativo**: Modo claro/oscuro automático
- 📱 **Responsive Design**: Optimizado para desktop y móvil
- ⚡ **Visualizaciones Interactivas**: Plotly para gráficos dinámicos
- 🎯 **Insights Automáticos**: Cajas de insight con recomendaciones
- 💡 **Tooltips Informativos**: Información contextual en todos los gráficos

## 🛠️ Stack Tecnológico

### Data Science & ML
- Python 3.11+
- Pandas, NumPy (análisis de datos)
- Scikit-learn (Machine Learning, PCA, K-Means)
- Plotly (visualizaciones interactivas)

### Dashboard
- Streamlit 1.28+ (framework web)
- HTML/CSS custom (estilos profesionales)

### Notebooks
- Jupyter (análisis exploratorio)
- 6 notebooks completos (01-06)

## 📦 Estructura del Proyecto

```
cinema-subscription-optimization/
├── dashboard/
│   ├── app.py                    # 🚀 Aplicación principal Streamlit
│   ├── requirements.txt          # Dependencias del dashboard
│   └── assets/
│       └── styles.css            # Estilos personalizados
├── data/
│   ├── raw/
│   │   └── movie_theatre_sales.csv    # Datos originales
│   └── processed/
│       ├── cleaned_data.csv           # Datos limpios
│       ├── customer_segments.csv      # Segmentos de clientes
│       └── model_features.csv         # Features para modelos
├── src/
│   ├── data_processing.py        # Procesamiento de datos
│   ├── feature_engineering.py    # Creación de features
│   ├── modeling.py               # Modelos ML
│   ├── pricing_optimization.py   # Optimización de precios
│   └── visualization.py          # Funciones de visualización
├── notebooks/
│   ├── 01_exploratory_data_analysis.ipynb
│   ├── 02_data_cleaning_preparation.ipynb
│   ├── 03_customer_segmentation.ipynb
│   ├── 04_predictive_modeling.ipynb
│   ├── 05_pricing_optimization.ipynb
│   └── 06_financial_projections.ipynb
├── reports/
│   └── figures/
│       ├── financial_kpis.json
│       ├── model_metrics.json
│       └── pricing_results.csv
├── .streamlit/
│   └── config.toml              # Configuración Streamlit
├── requirements.txt             # Dependencias del proyecto completo
└── README.md
```
## 📊 Datos

### Dataset
- **Fuente**: Ventas de cine (ficticio para demostración)
- **Registros**: ~1000 transacciones
- **Features**: Edad, género de película, tamaño de grupo, precio, etc.

### Variables Clave
- `Customer_Age`: Edad del cliente
- `Movie_Genre`: Género de película visto
- `Group_Size`: Tamaño del grupo
- `Ticket_Price`: Precio del ticket
- `Total_Spend`: Gasto total en concesiones
- `Loyalty_Member`: Miembro del programa de lealtad

## 🎯 Resultados Clave

### Segmentación
- **3 Segmentos identificados**: Familias, Jóvenes, Seniors
- **PCA**: Visualización en 2 dimensiones
- **Perfiles detallados**: Por edad, gasto, frecuencia

### Pricing Óptimo
- **Precio recomendado**: $XX.XX/mes
- **Incremento de ingresos**: +XX%
- **Tasa de conversión esperada**: XX%

### Proyecciones Financieras
- **ROI**: XX% en 12 meses
- **VAN**: $XXX,XXX
- **Payback period**: X meses
  
## 📈 Métricas del Proyecto

- **Líneas de código**: ~1,500+
- **Notebooks**: 6 completos
- **Visualizaciones**: 15+ gráficos interactivos
- **Modelos ML**: Clasificación + Regresión
- **Tiempo de desarrollo**: 2 semanas

## 🤝 Contribuciones

## 📄 Licencia

© 2025 CMSR92. Todos los derechos reservados.

Este proyecto es de código abierto para fines educativos.

## 📧 Contacto

- **Desarrollador**: CMSR92
- **LinkedIn**: [linkedin.com/in/cmsr92](https://linkedin.com/in/cmsr92)
- **Portfolio**: [cmsr92.github.io](https://carlosmsr92.github.io/cmsr92/)

## 🙏 Agradecimientos

- Dataset inspirado en análisis de industria cinematográfica
- Visualizaciones con Plotly
- Framework Streamlit para deployment rápido

---

Desarrollado con 💙 por CMSR92 | Noviembre 2025
