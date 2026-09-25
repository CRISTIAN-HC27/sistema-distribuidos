FROM python:3.12-alpine
WORKDIR /app

COPY requirements.txt ./
RUN python -m venv venv && venv/bin/pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV PORT=6003
EXPOSE 6003

CMD ["/app/venv/bin/python", "-u", "app/main.py"]