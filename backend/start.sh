#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

until check-db-connection | grep -q "^success"; do
    >&2 echo "MySQL is still unavailable"
    sleep 1
done
echo "Connection to MySQL successfully"

alembic upgrade head

cd /srv/testproject/backend
echo "Starting the server"

uvicorn --host 0.0.0.0 --port 8000 --reload app.asgi:app
