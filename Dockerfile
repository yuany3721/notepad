FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
COPY frontend/pnpm-lock.yaml ./
RUN npm install -g pnpm
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
ARG APP_NAME=Notepad
RUN VITE_API_BASE_URL=/api VITE_WS_HOST= VITE_APP_TITLE=$APP_NAME pnpm build

FROM python:3.12-slim AS backend-prep
WORKDIR /app
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*
COPY --from=backend-prep /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=backend-prep /usr/local/bin /usr/local/bin
COPY backend/ ./
COPY --from=frontend-build /app/frontend/dist ./frontend/dist
RUN mkdir -p /app/data/notes /var/log/supervisor /var/log/nginx
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/default.conf /etc/nginx/sites-available/default
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-80}/notepad/health || exit 1
EXPOSE ${PORT:-80}
CMD ["/app/docker-entrypoint.sh"]