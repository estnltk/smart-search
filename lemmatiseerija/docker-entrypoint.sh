#!/bin/sh
export WORKERS=${WORKERS:-1}
export TIMEOUT=${TIMEOUT:-30}
export WORKER_CLASS=${WORKER_CLASS:-sync}

exec /usr/bin/tini -- venv/bin/gunicorn --bind=0.0.0.0:7000 \
    "--workers=${WORKERS}" \
    "--timeout=${TIMEOUT}" \
    "--worker-class=${WORKER_CLASS}" \
    --worker-tmp-dir=/dev/shm "$@" \
    flask_lemmatiseerija:app
