FROM python:3.13-slim

WORKDIR /app

COPY auxiliary_service/requirements.txt /tmp/aux-requirements.txt
RUN pip install --no-cache-dir -r /tmp/aux-requirements.txt

COPY . .

EXPOSE 8080

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --worker-tmp-dir /tmp auxiliary_service.wsgi:app"]
