# Sistemas Distribuidos - Load Balancer con Nginx

## Arquitectura del Proyecto

```
                    ┌─────────────┐
                    │  Navegador  │
                    │ (Dashboard) │
                    └──────┬──────┘
                           │ HTTP :8080
                           ▼
                    ┌─────────────┐
                    │   Nginx LB  │ ← Balanceador de carga
                    │   :80/:8000 │
                    └──────┬──────┘
                           │ proxy_pass
              ┌────────────┴────────────┐
              ▼                         ▼
       ┌─────────────┐          ┌─────────────┐
       │ Backend 5001│          │ Backend 5002│
       │  (Node.js)  │          │  (Node.js)  │
       └──────┬──────┘          └──────┬──────┘
              │                        │
              └────────────┬───────────┘
                           ▼
                    ┌─────────────┐
                    │    Redis    │ ← Store compartido
                    │   :6379     │
                    └─────────────┘
```

**Flujo:** El navegador hace peticiones a Nginx (load balancer), que distribuye las peticiones entre los dos backends usando un algoritmo. Los backends almacenan contadores en Redis (store compartido) para mantener el estado global.

---

## Conceptos Teóricos

### ¿Qué es un Load Balancer?

Un load balanceador distribuye el tráfico entrante entre múltiples servidores (backends) para:
- **Alto rendimiento:** más peticiones simultáneas
- **Alta disponibilidad:** si un backend falla, las peticiones van al otro
- **Escalabilidad:** se pueden agregar más backends fácilmente

### Algoritmos de Balanceo

#### 1. Round Robin (por defecto)
Las peticiones se distribuyen en orden cíclico: 1ra al primero, 2da al segundo, 3ra al primero, etc.

**Cuándo usarlo:** Cuando todos los backends tienen similar capacidad y las peticiones tienen duración similar.

#### 2. Least Connections
La petición va al backend que tenga **menos conexiones activas**.

**Cuándo usarlo:** Cuando las peticiones tienen duración variable (algunas rápidas, otras lentas). Evita sobrecargar un backend que esté procesando peticiones pesadas.

#### 3. IP Hash
Se calcula un hash de la IP del cliente y se asigna al backend correspondiente. El **mismo cliente siempre va al mismo backend**.

**Cuándo usarlo:** Cuando necesitás **sesiones persistentes** (sticky sessions). No es ideal para balanceo real si hay pocas IPs.

### Failover y Resiliencia

El failover es la capacidad de **saltar al siguiente backend** cuando uno falla. Nginx lo maneja con:

- `proxy_next_upstream`: Qué errores provocan el salto al siguiente backend
- `proxy_next_upstream_tries`: Cuántos reintentos máximo
- `proxy_connect_timeout`: Tiempo máximo para conectar (si falla, reintenta rápido)

### Redis como Store Compartido

Redis actúa como **almacenamiento centralizado** para:
- `total_peticiones`: contador global de todas las peticiones
- `peticiones_nodo_{port}`: contador por backend

Sin Redis, cada backend solo conocería sus propias peticiones. Con Redis, ambos backends comparten el mismo estado.

---

## Instalación Paso a Paso

### 1. Instalar dependencias del sistema

```bash
# Node.js y npm (si no están instalados)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Redis
sudo apt update
sudo apt install redis-server -y
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Nginx
sudo apt install nginx -y

# PM2 (gestor de procesos)
npm install -g pm2
```

### 2. Clonar el proyecto

```bash
git clone <url-del-repositorio>
cd sistemas-distribuidos
```

### 3. Instalar dependencias del backend

```bash
cd backend
npm install
cd ..
```

### 4. Configurar Nginx

```bash
# Copiar la configuración del load balancer
sudo cp balancer.conf /etc/nginx/sites-available/balancer.conf

# Crear enlace simbólico en sites-enabled
sudo ln -sf /etc/nginx/sites-available/balancer.conf /etc/nginx/sites-enabled/

# Verificar que no haya errores de configuración
sudo nginx -t

# Recargar Nginx
sudo systemctl reload nginx
```

### 5. Levantar todo

```bash
# Opción A: Usar el script
chmod +x start.sh
./start.sh

# Opción B: Manual
redis-server --daemonize yes
pm2 start backend/ecosystem.config.js
python3 -m http.server 8080 --directory frontend &
```

### 6. Verificar que funciona

```bash
# Verificar Redis
redis-cli ping
# Debe responder: PONG

# Verificar backends
pm2 status
# Deben aparecer: backend-5001 y backend-5002 con status "online"

# Probar backend directamente
curl http://localhost:5001/status
# Debe retornar JSON con estado UP

# Probar Nginx
curl http://localhost:80/
# Debe responder con JSON de uno de los backends

# Abrir dashboard
# http://localhost:8080
```

---

## Parámetros de Nginx Explicados

### Configuración de Backends

```nginx
upstream backend_servers_1 {
    server 127.0.0.1:5001 max_fails=1 fail_timeout=5s;
    server 127.0.0.1:5002 max_fails=1 fail_timeout=5s;
}
```

| Parámetro | Significado |
|-----------|-------------|
| `max_fails=1` | Marca el backend como caído después de **1 fallo** |
| `fail_timeout=5s` | Si falla, no envía peticiones por **5 segundos** |

### Proxy y Failover

```nginx
proxy_next_upstream error timeout http_500 http_502 http_503 http_504;
proxy_next_upstream_tries 2;
proxy_next_upstream_timeout 2s;
```

| Parámetro | Significado |
|-----------|-------------|
| `proxy_next_upstream` | Qué errores provocan reintentar con otro backend |
| `proxy_next_upstream_tries 2` | Máximo **2 intentos** (el original + 1 reintento) |
| `proxy_next_upstream_timeout 2s` | Tiempo total máximo para reintentar |

### Timeouts

```nginx
proxy_connect_timeout 1s;
proxy_read_timeout 2s;
proxy_send_timeout 2s;
```

| Parámetro | Significado |
|-----------|-------------|
| `proxy_connect_timeout 1s` | Tiempo máximo para **conectar** al backend |
| `proxy_read_timeout 2s` | Tiempo máximo para **leer** la respuesta |
| `proxy_send_timeout 2s` | Tiempo máximo para **enviar** la petición |

**Nota:** Los timeouts están en 1-2 segundos para detectar caídas rápidamente en el chaos test.

---

## Cómo Cambiar el Algoritmo

Editá `/etc/nginx/sites-available/balancer.conf` y cambiá la línea `proxy_pass`:

```nginx
location / {
    # Round Robin (default)
    proxy_pass http://backend_servers_1;

    # Least Connections
    # proxy_pass http://backend_servers_2;

    # IP Hash
    # proxy_pass http://backend_servers_3;
}
```

Después recargá Nginx:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

---

## Simular Caída de un Nodo (Chaos Test)

### Detener un backend

```bash
# Detener solo el backend 5001
pm2 stop backend-5001

# O detener todos
pm2 stop all
```

### Verificar el failover

```bash
# Hacer peticiones al load balancer
for i in $(seq 1 10); do curl -s http://localhost:80/ | jq .nodo; done

# Deberías ver respuestas solo del backend que sigue arriba
```

### Verificar en el dashboard

Abrí http://localhost:8080 y verás:
- El nodo caído muestra "DOWN"
- El badge del cluster cambia a "DEGRADADO"
- Las peticiones van todas al nodo activo

### Reanudar el backend

```bash
pm2 start backend-5001
```

### Verificar reconexión

```bash
pm2 status
# Ambos backends deben estar "online"

# El dashboard debe volver a mostrar "SALUDABLE"
```

---

## Comandos Útiles

```bash
# --- Redis ---
redis-cli ping                          # Verificar conexión
redis-cli get total_peticiones          # Ver total global
redis-cli get peticiones_nodo_5001      # Ver peticiones del nodo 5001
redis-cli monitor                       # Monitorear queries en tiempo real
redis-cli set total_peticiones 0        # Resetear contador global
redis-cli set peticiones_nodo_5001 0    # Resetear contador del nodo 5001

# --- PM2 ---
pm2 status                              # Ver estado de procesos
pm2 logs                                # Ver logs en tiempo real
pm2 logs backend-5001                   # Logs solo del nodo 5001
pm2 restart backend-5001                # Reiniciar un nodo
pm2 stop backend-5001                   # Detener un nodo
pm2 delete backend-5001                 # Eliminar un nodo

# --- Nginx ---
sudo nginx -t                           # Testear configuración
sudo systemctl reload nginx             # Recargar configuración
sudo systemctl status nginx             # Estado del servicio
```

---

## Troubleshooting

### Error: "Address already in use" en el puerto 80

El site default de Nginx usa el puerto 80. Solución:

```bash
# Desactivar el site default
sudo unlink /etc/nginx/sites-enabled/default
sudo systemctl reload nginx
```

### Error: "Connection refused" en Redis

```bash
# Verificar si Redis está corriendo
sudo systemctl status redis-server

# Si no está corriendo, iniciarlo
sudo systemctl start redis-server
```

### Error: Backends no aparecen en PM2

```bash
# Verificar que las dependencias estén instaladas
cd backend && npm install

# Verificar el archivo ecosystem.config.js
cat backend/ecosystem.config.js
```

### Dashboard no muestra datos

1. Verificar que los backends estén corriendo: `pm2 status`
2. Verificar Redis: `redis-cli ping`
3. Verificar CORS: los backends deben tener el middleware de CORS (ya está incluido)
4. Abrir consola del navegador (F12) y ver si hay errores

### Nginx retorna error 502 o 503

```bash
# Verificar logs de Nginx
sudo tail -f /var/log/nginx/error.log

# Verificar que los backends estén escuchando
curl http://localhost:5001/status
curl http://localhost:5002/status
```

---

## Estructura del Proyecto

```
sistemas-distribuidos/
├── README.md              # Esta documentación
├── balancer.conf          # Configuración de Nginx (load balancer)
├── start.sh               # Script para levantar todo
├── stop.sh                # Script para detener todo
├── frontend/
│   └── index.html         # Dashboard (polling cada 1s)
└── backend/
    ├── server.js          # Servidor Express + Redis
    ├── ecosystem.config.js # Configuración PM2 (2 instancias)
    └── package.json
```
