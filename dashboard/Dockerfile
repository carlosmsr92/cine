# Imagen del dashboard. Se construye desde la raíz del repositorio, porque la app usa src/, data/ y reports/:
#   docker build -f dashboard/Dockerfile -t cine-dashboard .
#   docker run -p 8501:8501 cine-dashboard
FROM python:3.11-slim

WORKDIR /app

# Solo las dependencias del dashboard (las de los notebooks están en el requirements.txt de la raíz)
COPY dashboard/requirements.txt dashboard/requirements.txt
RUN pip install --no-cache-dir -r dashboard/requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--browser.gatherUsageStats=false"]
