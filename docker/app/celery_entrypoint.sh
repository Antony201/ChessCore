#!/bin/bash

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi


python3 -m celery -A config.celery worker -l INFO --concurrency=10 &

python3 -m celery -A config.celery beat --pidfile= -l INFO -s /app/runtime/celerybeat-schedule

exec "$@"
