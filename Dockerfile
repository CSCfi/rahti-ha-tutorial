FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential libpq-dev netcat-openbsd --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
RUN chmod +x /app/wait-for-postgres.sh
ENV FLASK_APP=app.py
EXPOSE 5000
CMD ["/app/wait-for-postgres.sh", "db", "5432", "15", "python", "app.py"]
