# 🎬 Estrategia de suscripción para un cine

Dashboard interactivo en Streamlit que analiza las ventas de un cine y evalúa un programa de suscripción anual:
comportamiento de clientes, segmentación con K-Means, escenarios de precio y proyección financiera.

🔗 **Dashboard:** [proyecto-cine.streamlit.app](https://proyecto-cine.streamlit.app/)

## Qué incluye

- **Análisis de negocio:** transacciones, precio medio del ticket, tamaño de grupo y tasa de recompra.
- **Segmentación de clientes:** K-Means con 4 segmentos y visualización en 2D con PCA.
- **Optimización de precios:** simulador de escenarios con punto de equilibrio y margen de contribución.
- **Proyecciones financieras:** ROI y plazo de recuperación de la inversión del escenario elegido.
- **Tema claro y oscuro** según la preferencia del navegador.

## Resultados

Los resultados de precio salen de un **escenario simulado**: la curva de adopción (cuántos suscriptores habría a cada
precio), los costes fijos (25.000 $) y el coste variable por suscriptor (80 $) son supuestos de partida, no datos reales.

| Precio anual | Suscriptores (supuesto) | Ingresos | Margen de contribución | Punto de equilibrio |
|---:|---:|---:|---:|---:|
| 120 $ | 485 | 58.200 $ | 19.400 $ | 625 suscriptores (no rentable) |
| 150 $ | 420 | 63.000 $ | 29.400 $ | 357 suscriptores |
| **180 $** | **350** | **63.000 $** | **35.000 $** | **250 suscriptores** |
| 210 $ | 260 | 54.600 $ | 33.800 $ | 192 suscriptores |
| 240 $ | 180 | 43.200 $ | 28.800 $ | 156 suscriptores |

- **Precio recomendado:** 180 $ al año (15 $ al mes), el de mayor margen de contribución.
- **Punto de equilibrio:** 250 suscriptores.
- **ROI del primer año:** 40 %, con recuperación de la inversión en unos 30 meses.

## Datos

- **Fuente:** dataset ficticio de ventas de un cine, para demostración.
- **Tamaño:** 1.440 registros en bruto; 745 transacciones tras la limpieza.
- **Variables:** edad, género de la película, tipo de asiento, número de personas, precio del ticket y recompra.

## Estructura

```
cine/
├── dashboard/
│   ├── app.py                 # Aplicación Streamlit
│   ├── requirements.txt       # Dependencias del dashboard
│   ├── marca.py               # Cabecera, pie e icono comunes CMSR92
│   ├── assets/                # Logo y símbolo de marca
│   └── Dockerfile             # Imagen del dashboard (se construye desde la raíz)
├── data/
│   ├── raw/                   # Datos originales
│   └── processed/             # Datos limpios, segmentos y features
├── notebooks/                 # Exploración, limpieza, segmentación, modelado, precios y proyecciones
├── src/                       # Procesamiento, features, modelos, precios y visualización
├── presentations/             # Exportación de figuras y ejecución de notebooks
├── reports/figures/           # Figuras, KPIs y resultados de precios
└── requirements.txt           # Dependencias del proyecto completo
```

## Ejecutar en local

```bash
pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py
```

## Ejecutar con Docker

La imagen se construye desde la raíz del repositorio, porque el dashboard usa `src/`, `data/` y `reports/`:

```bash
docker build -f dashboard/Dockerfile -t cine-dashboard .
docker run -p 8501:8501 cine-dashboard
```

En cada push, GitHub Actions construye la imagen y comprueba que el dashboard responde
([`.github/workflows/docker.yml`](.github/workflows/docker.yml)).

## Tecnologías

Python, pandas, NumPy, scikit-learn (K-Means, PCA), Plotly y Streamlit.

## Licencia

[MIT](LICENSE) © 2025 Carlos Manuel Suárez Rivero (CMSR92)

## Autor

**Carlos Manuel Suárez Rivero (CMSR92)** · [LinkedIn](https://www.linkedin.com/in/cmsr92) · [Portfolio](https://carlosmsr92.github.io/cmsr92/)
