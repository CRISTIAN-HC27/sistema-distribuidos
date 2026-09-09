FROM python:3.12-alpine
WORKDIR /app

# Dependencias dentro de un entorno virtual (aisla el "site-packages")
COPY requirements.txt ./
RUN python -m venv venv && venv/bin/pip install --no-cache-dir -r requirements.txt

# Código fuente
COPY src ./src

ENV DB_PATH=/app/data/db.sqlite
EXPOSE 5003

CMD ["/app/venv/bin/python", "-u", "src/main.py"]