#!/bin/bash

export BACKEND_PORT=${BACKEND_PORT:-7025}
export NOTES_DIR=${NOTES_DIR:-./data}

mkdir -p /app/data/notes
chown -R www-data:www-data /app/data/notes
chown -R www-data:www-data /app/frontend/dist

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf