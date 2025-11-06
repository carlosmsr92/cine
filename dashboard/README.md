# 🎬 Cinema Subscription Dashboard — Versión Profesional

Dashboard ejecutivo interactivo que presenta el análisis completo de optimización de precios para programa de suscripción de cine, con storytelling de datos, visualizaciones interactivas y proyecciones financieras.

## 🌟 Características Principales

### 📊 Resumen Ejecutivo
- **KPIs visuales en cards profesionales**: Precio recomendado, Break-even, ROI, Payback
- **Problema vs. Solución**: Presentación clara del desafío de negocio y la estrategia propuesta
- **Métricas de impacto**: Datos clave actualizados en tiempo real

### 📈 Análisis de Negocio
- Distribución de precios de tickets con análisis estadístico
- Análisis de tamaño de grupos y patrones de compra
- Análisis por género de película y tipo de asiento
- Insights accionables automáticos basados en datos

### 👥 Segmentación de Clientes
- **Clustering K-Means** con visualización PCA interactiva
- Perfiles detallados de cada segmento (edad, gasto, tamaño grupo)
- Recomendaciones estratégicas personalizadas por segmento
- Identificación automática del target principal

### 💰 Optimización de Precios
- **Simulador interactivo** de escenarios de precio
- Análisis comparativo de múltiples puntos de precio
- Visualizaciones de Revenue, Beneficio y Break-even
- **Mapa de calor de sensibilidad** precio vs. suscriptores
- Evaluación automática de rentabilidad del escenario seleccionado

### 📊 Proyecciones Financieras
- Proyecciones a 3 años con supuestos configurables
- Modelado de crecimiento, churn y aumentos de precio
- Gráficos de evolución de revenue por canal
- Cálculo de LTV (Lifetime Value) de suscriptores
- KPIs de impacto comparando baseline vs. escenario con suscripción

### 🔧 Configuración y Utilidades
- Pipeline completo de regeneración de datos y figuras
- Generación de presentación ejecutiva (PPTX)
- Estado del sistema y archivos de datos
- Panel de control centralizado

## 🚀 Cómo Usar

### 1. Instalación de Dependencias

```powershell
# Navega al directorio del dashboard
cd "c:\Users\Carlos\OneDrive\Desktop\Proyecto Cine\cinema-subscription-optimization\dashboard"

# Instala las dependencias
pip install -r requirements.txt
```

### 2. Ejecutar el Dashboard

```powershell
streamlit run app.py
```

El dashboard se abrirá automáticamente en tu navegador en `http://localhost:8501`

### 3. Flujo de Uso Recomendado

1. **Primera ejecución**: Ve a la pestaña "Configuración" y ejecuta:
   - "Ejecutar Pipeline Completo" para generar todos los datos procesados
   - "Actualizar Figuras y Métricas" para generar KPIs

2. **Análisis exploratorio**:
   - Revisa el "Resumen Ejecutivo" para los KPIs clave
   - Explora "Análisis de Negocio" para entender el comportamiento actual
   - Analiza "Segmentación de Clientes" para identificar targets

3. **Optimización de estrategia**:
   - Usa "Optimización de Precios" para simular diferentes escenarios
   - Ajusta los parámetros (precio, suscriptores, costos) en tiempo real
   - Revisa el análisis de sensibilidad para encontrar el punto óptimo

4. **Proyecciones**:
   - Configura supuestos de crecimiento en "Proyecciones Financieras"
   - Analiza el impacto a 3 años
   - Descarga la presentación ejecutiva para stakeholders

## 📁 Estructura de Archivos

```
dashboard/
├── app.py                  # Dashboard principal (versión profesional)
├── app_backup.py          # Backup de versión anterior
├── requirements.txt       # Dependencias Python
├── README.md             # Este archivo
└── assets/
    └── styles.css        # Estilos personalizados
```

## 🎨 Características Técnicas

### Visualizaciones Interactivas
- **Plotly**: Todos los gráficos son interactivos (zoom, pan, hover)
- **Responsive**: Layout adaptable a diferentes tamaños de pantalla
- **Profesional**: Colores y estilos consistentes con identidad de marca

### Storytelling de Datos
- Flujo narrativo claro: Problema → Análisis → Solución → Proyección
- Insights automáticos basados en datos reales
- Recomendaciones accionables en cada sección

### Rendimiento
- Caché de datos para carga rápida
- Cálculos optimizados
- Actualización selectiva de componentes

## 🎯 Casos de Uso

### Para Ejecutivos
- Vista rápida de KPIs principales en el resumen ejecutivo
- Evaluación de viabilidad financiera del programa
- Proyecciones de impacto a 3 años
- Descarga de presentación para board/inversores

### Para Analistas
- Análisis detallado de comportamiento de clientes
- Segmentación y perfilamiento
- Simulación de múltiples escenarios de pricing
- Análisis de sensibilidad

### Para Equipos de Marketing
- Identificación de segmentos target
- Insights de preferencias por género/asiento
- Recomendaciones de estrategia por segmento
- Análisis de retención y LTV

### Para CFO/Finanzas
- Modelado financiero a 3 años
- Análisis de break-even y ROI
- Proyecciones de revenue y beneficio
- Evaluación de diferentes estructuras de costos

## 💡 Tips de Uso

1. **Experimenta con parámetros**: El simulador de precios permite probar múltiples escenarios en tiempo real
2. **Revisa el mapa de calor**: Te muestra visualmente la zona óptima de precio vs. volumen
3. **Compara escenarios**: La tabla comparativa te permite evaluar múltiples precios simultáneamente
4. **Ajusta supuestos**: En proyecciones, modifica crecimiento y churn para ver sensibilidad
5. **Descarga la presentación**: Perfecta para compartir con stakeholders sin acceso técnico

## 🔄 Actualización de Datos

El dashboard consume datos de:
- `data/processed/cleaned_data.csv` - Datos limpios de transacciones
- `data/processed/model_features.csv` - Features engineered para modelos
- `reports/figures/financial_kpis.json` - KPIs financieros calculados
- `reports/figures/model_metrics.json` - Métricas de modelos predictivos

Para actualizar con nuevos datos:
1. Coloca nuevos datos raw en `data/raw/movie_theatre_sales.csv`
2. Ejecuta "Pipeline Completo" en la pestaña Configuración
3. Los gráficos y KPIs se actualizarán automáticamente

## 🆘 Troubleshooting

**Dashboard no carga datos:**
- Verifica que existan los archivos en `data/processed/`
- Ejecuta el pipeline completo desde Configuración

**Gráficos no se ven:**
- Asegúrate de tener conexión a internet (Plotly usa CDN)
- Actualiza el navegador
- Prueba en modo incógnito

**KPIs muestran "N/A":**
- Ejecuta "Actualizar Figuras y Métricas" en Configuración
- Verifica que los notebooks se hayan ejecutado correctamente

## 📞 Soporte

Desarrollado por: **CMSR92**  
Versión: **2.0 Professional**  
Fecha: **Noviembre 2025**

---

**¡Disfruta explorando los datos y optimizando la estrategia de suscripción! 🎬📊**
