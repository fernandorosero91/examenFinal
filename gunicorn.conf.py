# Configuración de Gunicorn para DocPloy
import multiprocessing
import os

# Configuración del servidor
bind = "0.0.0.0:8000"
workers = min(2, multiprocessing.cpu_count())
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Configuración de requests
max_requests = 1000
max_requests_jitter = 100

# Preload para mejor rendimiento
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configuración de procesos
daemon = False
pidfile = None
tmp_upload_dir = None

# Configuración SSL (si es necesario)
# keyfile = None
# certfile = None

# Configuración de memoria
max_worker_memory = 200 * 1024 * 1024  # 200MB por worker

def when_ready(server):
    server.log.info("Servidor Gunicorn listo para recibir conexiones")

def worker_int(worker):
    worker.log.info("Worker recibió INT o QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker received SIGABRT signal")