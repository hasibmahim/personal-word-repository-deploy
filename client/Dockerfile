FROM python:3.13-slim

WORKDIR /app

COPY client/requirements.txt /tmp/client-requirements.txt
RUN pip install --no-cache-dir -r /tmp/client-requirements.txt

COPY . .

EXPOSE 8080

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --worker-tmp-dir /tmp client.wsgi:app"]
