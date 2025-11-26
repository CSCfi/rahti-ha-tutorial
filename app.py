"""
    Shows all tables, and its data, of the connected DB
"""
import os
import time
from flask import Flask, render_template, abort, request, Response
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.exc import OperationalError
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/postgres')
engine = create_engine(DATABASE_URL)
metadata = MetaData()

def reflect_tables():
    metadata.reflect(bind=engine)
    return metadata.tables

@app.route('/')
def index():
    try:
        tables = reflect_tables()
    except OperationalError as err:
        return f"Database not ready. {err}", 503
    table_names = sorted(tables.keys())
    return render_template('index.html', tables=table_names)

@app.route('/table/<path:table_name>')
def view_table(table_name):
    try:
        tables = reflect_tables()
    except OperationalError:
        return "Database not ready.", 503

    if table_name not in tables:
        abort(404, description=f"Table '{table_name}' not found")

    table = Table(table_name, metadata, autoload_with=engine)
    stmt = select(table)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        rows = [dict(r._mapping) for r in result]
        columns = result.keys()

    return render_template('table.html', table_name=table_name, columns=columns, rows=rows)

# --- Prometheus Metrics ---
REQUEST_COUNT = Counter(
    'flask_app_request_count',
    'Total number of requests',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'flask_app_request_latency_seconds',
    'Histogram of request latency',
    ['endpoint']
)
# ---------------------------

# Middleware to measure metrics
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    latency = time.time() - request.start_time

    REQUEST_LATENCY.labels(request.path).observe(latency)
    REQUEST_COUNT.labels(
        request.method,
        request.path,
        response.status_code
    ).inc()

    return response


# ---- Prometheus Metrics Endpoint ----
@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
# -------------------------------------



if __name__ == '__main__':
    retry = int(os.environ.get('APP_RETRY', '15'))
    for i in range(retry):
        try:
            with engine.connect():
                break
        except OperationalError:
            time.sleep(1)
    app.run(host='0.0.0.0', port=5000)
