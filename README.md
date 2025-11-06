# 🎬 Cinema Subscription Optimization

Dashboard interactivo profesional para análisis y optimización de estrategia de suscripción de cines utilizando Data Science, Machine Learning y Business Intelligence.

## 🌐 Demo en Vivo

🔗 [Ver Dashboard en Streamlit](https://cinema-subscription-optimization.streamlit.app)

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

## 🚀 Instalación Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/cinema-subscription-optimization.git
cd cinema-subscription-optimization
```

### 2. Crear entorno virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar dashboard
```bash
streamlit run dashboard/app.py
```

El dashboard se abrirá en `http://localhost:8501`

## 🌐 Despliegue en Streamlit Cloud

### Paso 1: Preparar repositorio GitHub
```bash
cd "C:\Users\Carlos\OneDrive\Desktop\Proyecto Cine\cinema-subscription-optimization"
git init
git add .
git commit -m "Initial commit: Cinema Subscription Optimization Dashboard"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/cinema-subscription-optimization.git
git push -u origin main
```

### Paso 2: Configurar Streamlit Cloud
1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Conecta tu cuenta GitHub
3. Click en "New app"
4. Configuración:
   - **Repository**: `TU_USUARIO/cinema-subscription-optimization`
   - **Branch**: `main`
   - **Main file path**: `dashboard/app.py`
   - **App URL**: `cinema-subscription-optimization` (o el que prefieras)
5. Click "Deploy"

### Paso 3: Configuración avanzada (opcional)
Si necesitas ajustes, crea `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#0CA5BE"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
```

Tu dashboard estará disponible en:
```
https://cinema-subscription-optimization.streamlit.app
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

## 🔧 Configuración

### Variables de entorno (opcional)
Si necesitas configurar claves API o secrets:

1. Crea `.streamlit/secrets.toml` (local)
2. En Streamlit Cloud: Settings → Secrets
```toml
# Ejemplo
[api_keys]
openai = "sk-..."
```

### Personalización
- **Colores**: Edita `dashboard/assets/styles.css`
- **Tema Streamlit**: Modifica `.streamlit/config.toml`
- **Datos**: Reemplaza `data/raw/movie_theatre_sales.csv`

## 📈 Métricas del Proyecto

- **Líneas de código**: ~1,500+
- **Notebooks**: 6 completos
- **Visualizaciones**: 15+ gráficos interactivos
- **Modelos ML**: Clasificación + Regresión
- **Tiempo de desarrollo**: 2 semanas

## 🐛 Troubleshooting

### Error: "No module named 'streamlit'"
```bash
pip install -r requirements.txt
```

### Error: "File not found"
Asegúrate de ejecutar desde la raíz del proyecto:
```bash
streamlit run dashboard/app.py
```

### Dashboard lento
- Reduce el número de registros en `data/raw/`
- Usa `@st.cache_data` para funciones pesadas

## 🤝 Contribuciones

Este es un proyecto educativo/portfolio. Si encuentras bugs o mejoras:
1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/mejora`)
3. Commit cambios (`git commit -m 'Añadir mejora'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abre un Pull Request

## 📄 Licencia

© 2025 Carlos Muñoz (CMSR92). Todos los derechos reservados.

Este proyecto es de código abierto para fines educativos.

## 📧 Contacto

- **Desarrollador**: Carlos Muñoz (CMSR92)
- **Email**: carlos@example.com
- **LinkedIn**: [linkedin.com/in/cmsr92](https://linkedin.com/in/cmsr92)
- **Portfolio**: [cmsr92.github.io](https://cmsr92.github.io)

## 🙏 Agradecimientos

- Dataset inspirado en análisis de industria cinematográfica
- Visualizaciones con Plotly
- Framework Streamlit para deployment rápido

---

Desarrollado con 💙 por CMSR92 | Noviembre 2025
