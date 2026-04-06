FROM python:3.13-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/instance /tmp/nginx-client-body /tmp/nginx-proxy /tmp/nginx-fastcgi /tmp/nginx-uwsgi /tmp/nginx-scgi
RUN chgrp -R 0 /app && chmod -R g=u /app
RUN chgrp -R 0 /var/lib/nginx /var/log/nginx /etc/nginx /tmp && chmod -R g=u /var/lib/nginx /var/log/nginx /etc/nginx /tmp

EXPOSE 8080

CMD ["supervisord", "-c", "/app/deploy/supervisord.conf"]
