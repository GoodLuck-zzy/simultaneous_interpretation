import os


bind = "0.0.0.0:15000"

app_module = "app:app"

workers = int(os.environ.get("WORKER_NUM", 1))

worker_class = os.environ.get("WORKER_CLASS", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker")

threads = int(os.environ.get("gunicorn.threads", 30))

timeout = 600

# The maximum size of HTTP request line in bytes.
limit_request_line = 4096

# Limit the number of HTTP headers fields in a request.
limit_request_fields = 100

# Limit the allowed size of an HTTP request header field.
limit_request_field_size = 8190

graceful_timeout = 5

# reload = False


# chdir = '/opt/pangu'

# access_logfile = ''

# access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# error_logfile=''

log_level = "info"

proc_name = "flaskapp"

keepalive = int(os.environ.get("KEEPALIVE_TIMEOUT", 30))
