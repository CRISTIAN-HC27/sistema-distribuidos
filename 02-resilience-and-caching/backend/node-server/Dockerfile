FROM node:22-alpine
WORKDIR /app

# Primero las dependencias (aprovecha la caché de capas de Docker)
COPY package*.json ./
RUN npm install --omit=dev

# Después el código fuente en src/
COPY src ./src

ENV DB_PATH=/app/data/db.sqlite
EXPOSE 5001

CMD ["node", "src/index.js"]