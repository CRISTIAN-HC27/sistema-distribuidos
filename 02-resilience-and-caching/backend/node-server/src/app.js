import express from 'express';
import api from './routes/api.js';
import status from './routes/status.js';

function crearApp() {
  const app = express();

  // CORS para que un dashboard pueda leer estas rutas
  app.use((req, res, next) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    if (req.method === 'OPTIONS') return res.sendStatus(204);
    next();
  });

  app.use('/api', api);
  app.use('/status', status);

  return app;
}

export { crearApp };